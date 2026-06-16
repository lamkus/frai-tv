#!/usr/bin/env python3
"""Alfred SEO Optimizer (quota-safe).

Goal: improve discoverability in Germany by ensuring Alfred name variants are present:
- Kwak + Quack spellings
- Jodokus/Jodocus variants
- Deutsch/German signals

Rules:
- READ via Public API (YOUTUBE_API_KEY) only.
- WRITE via OAuth only.
- No deletes.

Usage:
    python scripts/youtube/alfred_seo_optimizer.py --dry-run
    python scripts/youtube/alfred_seo_optimizer.py --dry-run --update-title
    python scripts/youtube/alfred_seo_optimizer.py --apply --limit 10

Outputs:
  config/alfred_seo_plan.json
  config/alfred_seo_apply_report.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
VIDEOS_CACHE = CONFIG_DIR / "videos.json"
TAGS_PLAN = CONFIG_DIR / "tags_plan.json"
OUT_PLAN = CONFIG_DIR / "alfred_seo_plan.json"
OUT_REPORT = CONFIG_DIR / "alfred_seo_apply_report.json"

OAUTH_FILE = CONFIG_DIR / "youtube_oauth.json"

YT_API_BASE = "https://youtube.googleapis.com/youtube/v3"

ALFRED_DESCRIPTION_BLOCK = (
    "\n\n"
    "🇩🇪 Alfred J. Kwak / Quack (Alfred Jodokus Quack) – Deutsche Zeichentrickserie (80er/90er).\n"
    "🇬🇧 Alfred J. Kwak / Quack (Alfred Jodokus Quack) – Classic animated series.\n"
    "\n"
    "Keywords: Alfred J. Kwak, Alfred Jodokus Quack, Alfred Jodocus Kwak, Kwak, Quack, Deutsch, German."
)


@dataclass
class VideoSnippet:
    video_id: str
    title: str
    description: str
    category_id: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def is_alfred_title(title: str) -> bool:
    t = (title or "").lower()
    return "alfred" in t and ("kwak" in t or "quack" in t)


def extract_episode_tuple(title: str) -> Tuple[Optional[int], Optional[int]]:
    m = re.search(r"\((\d+)\s*/\s*(\d+)\)", title)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))


def build_alfred_title(current_title: str) -> str:
    """Best-effort title enhancement.

    This is intentionally conservative to avoid disrupting existing naming.
    It only appends missing discovery terms and trims to ~70 chars.
    """

    title = (current_title or "").strip()
    if not title:
        return "Alfred J. Kwak / Quack | Deutsch"

    lower = title.lower()
    needs_kwak = "kwak" not in lower
    needs_quack = "quack" not in lower
    needs_de = "deutsch" not in lower and "german" not in lower

    additions: List[str] = []
    if needs_kwak:
        additions.append("Kwak")
    if needs_quack:
        additions.append("Quack")
    if needs_de:
        additions.append("Deutsch")

    if not additions:
        return title

    candidate = f"{title} | " + "/".join(additions)
    if len(candidate) > 70:
        candidate = candidate[:70].rstrip()
    return candidate


def ensure_description_has_block(description: str) -> str:
    d = description or ""
    # Avoid duplicates
    if "Keywords: Alfred J. Kwak" in d:
        return d
    return d.rstrip() + ALFRED_DESCRIPTION_BLOCK


def get_public_snippets(video_ids: List[str], api_key: str) -> Dict[str, VideoSnippet]:
    snippets: Dict[str, VideoSnippet] = {}

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        params = {
            "part": "snippet",
            "id": ",".join(batch),
            "key": api_key,
            "maxResults": 50,
        }
        r = requests.get(f"{YT_API_BASE}/videos", params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        for item in data.get("items", []):
            vid = item.get("id")
            sn = item.get("snippet", {})
            snippets[vid] = VideoSnippet(
                video_id=vid,
                title=sn.get("title", ""),
                description=sn.get("description", ""),
                category_id=sn.get("categoryId", "24"),
            )

    return snippets


def oauth_youtube() -> object:
    creds_data = load_json(OAUTH_FILE)
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes"),
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        creds_data["token"] = creds.token
        OAUTH_FILE.write_text(json.dumps(creds_data, indent=2), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Perform OAuth writes")
    parser.add_argument("--dry-run", action="store_true", help="No writes, just plan")
    parser.add_argument(
        "--update-title",
        action="store_true",
        help="Also update titles (off by default to avoid renaming disruptions)",
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit number of videos to apply")
    parser.add_argument("--sleep", type=float, default=1.2, help="Delay between writes")
    args = parser.parse_args()

    if not VIDEOS_CACHE.exists():
        raise SystemExit(f"Missing {VIDEOS_CACHE}")

    videos_data = load_json(VIDEOS_CACHE)
    videos = videos_data.get("videos", [])
    alfred_videos = [v for v in videos if is_alfred_title(v.get("title", ""))]

    if not alfred_videos:
        raise SystemExit("No Alfred videos found in config/videos.json")

    tags_plan = load_json(TAGS_PLAN) if TAGS_PLAN.exists() else {}
    tags_by_id = {v.get("id"): v for v in (tags_plan.get("videos") or [])}

    # For dry-run: use local cache (0 quota!)
    # For apply: we'll fetch fresh data via OAuth
    snippets: Dict[str, VideoSnippet] = {}
    for v in alfred_videos:
        snippets[v["id"]] = VideoSnippet(
            video_id=v["id"],
            title=v.get("title", ""),
            description=v.get("description", ""),
            category_id=v.get("categoryId", "24"),
        )
    
    alfred_ids = [v["id"] for v in alfred_videos]

    plan_items = []
    for vid in alfred_ids:
        sn = snippets.get(vid)
        if not sn:
            continue

        new_title = build_alfred_title(sn.title) if args.update_title else sn.title
        new_desc = ensure_description_has_block(sn.description)

        planned_tags = (tags_by_id.get(vid) or {}).get("suggested_tags")
        if not planned_tags:
            # fallback minimal
            planned_tags = ["Alfred J. Kwak", "Alfred Jodokus Quack", "Kwak", "Quack", "Deutsch", "German", "8K", "remAIke"]

        changed = {
            "title": new_title != sn.title,
            "description": new_desc != sn.description,
            "tags": True,
        }

        plan_items.append(
            {
                "id": vid,
                "old": {"title": sn.title, "categoryId": sn.category_id},
                "new": {"title": new_title, "categoryId": sn.category_id},
                "description_added": "Keywords: Alfred J. Kwak" not in sn.description,
                "tags_count": len(planned_tags),
                "tags_chars": len(",".join(planned_tags)),
                "changed": changed,
            }
        )

    OUT_PLAN.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(),
                "videos": len(plan_items),
                "estimated_write_units": len(plan_items) * 50,
                "items": plan_items,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Planned Alfred updates: {len(plan_items)}")
    print(f"Wrote plan: {OUT_PLAN}")
    print(f"Estimated write quota (videos.update): ~{len(plan_items) * 50} units")

    if args.dry_run or not args.apply:
        return

    youtube = oauth_youtube()

    applied = 0
    failed = 0
    errors: List[str] = []

    limit = args.limit if args.limit and args.limit > 0 else len(plan_items)

    for item in plan_items[:limit]:
        vid = item["id"]

        sn = snippets.get(vid)
        if not sn:
            failed += 1
            errors.append(f"Missing snippet for {vid}")
            continue

        planned_tags = (tags_by_id.get(vid) or {}).get("suggested_tags")
        if not planned_tags:
            planned_tags = ["Alfred J. Kwak", "Alfred Jodokus Quack", "Kwak", "Quack", "Deutsch", "German", "8K", "remAIke"]

        # Safety: enforce 500 chars total
        while planned_tags and len(",".join(planned_tags)) > 500:
            planned_tags = planned_tags[:-1]

        new_title = build_alfred_title(sn.title) if args.update_title else sn.title
        new_desc = ensure_description_has_block(sn.description)

        body = {
            "id": vid,
            "snippet": {
                "title": new_title,
                "description": new_desc,
                "tags": planned_tags,
                "categoryId": sn.category_id,
            },
        }

        try:
            youtube.videos().update(part="snippet", body=body).execute()
            applied += 1
            time.sleep(max(0.0, float(args.sleep)))
        except HttpError as e:
            msg = str(e)
            if "quotaExceeded" in msg:
                errors.append("quotaExceeded")
                break
            failed += 1
            errors.append(f"{vid}: {msg}")

    OUT_REPORT.write_text(
        json.dumps(
            {
                "applied_at": datetime.now().isoformat(),
                "planned": len(plan_items),
                "applied": applied,
                "failed": failed,
                "errors": errors[:50],
                "note": "Stops immediately on quotaExceeded.",
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Applied: {applied}, Failed: {failed}")
    print(f"Wrote report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
