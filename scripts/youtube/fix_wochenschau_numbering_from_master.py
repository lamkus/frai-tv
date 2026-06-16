#!/usr/bin/env python3
"""
Fix Wochenschau draft/upload numbering using the researched master database.

Default mode is DRY-RUN (no API writes).
APPLY mode updates video snippets via OAuth and keeps videos private.

Sources:
- config/wochenschau_complete_upload_database.json (master baseline)
- config/wochenschau_events.json (event names)
- config/wochenschau_complete_locations.json (location notes)
- config/draft_scan_2026_02_23.json (private scan snapshot)
- config/new_uploads_2026_02_20.json (new upload snapshot)

Usage:
  python scripts/youtube/fix_wochenschau_numbering_from_master.py
  python scripts/youtube/fix_wochenschau_numbering_from_master.py --apply
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
PENDING = CONFIG / "pending_updates"

MASTER_DB = CONFIG / "wochenschau_complete_upload_database.json"
EVENTS_DB = CONFIG / "wochenschau_events.json"
LOCS_DB = CONFIG / "wochenschau_complete_locations.json"
DRAFT_SCAN = CONFIG / "draft_scan_2026_02_23.json"
NEW_UPLOADS = CONFIG / "new_uploads_2026_02_20.json"
TOKEN_FILE = ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

RAW_NR_PATTERNS = [
    re.compile(r"deutsche\s+wochenschau\s*nr\s*(\d{3})", re.IGNORECASE),
    re.compile(r"wochenschau\s*nr\.?\s*(\d{3})", re.IGNORECASE),
    re.compile(r"wochenschau\s*(\d{3})\s*:", re.IGNORECASE),
]

GOOD_TITLE_PATTERN = re.compile(
    r"^Wochenschau\s+\d{3}:\s+.+\(\d{2}\.\d{2}\.\d{4}\)\s+\|\s+8K HQ \(4K UHD\)$"
)

WS_TAGS = [
    "wochenschau",
    "deutsche wochenschau",
    "german newsreel",
    "world war 2",
    "wwii",
    "8K",
    "4K UHD",
    "remastered",
    "restored",
    "historical footage",
    "public domain",
    "vintage newsreel",
    "documentary",
    "AI enhanced",
    "history",
]


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def ddmmyyyy(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return date_str


def extract_nr(title: str) -> int | None:
    for pat in RAW_NR_PATTERNS:
        m = pat.search(title)
        if m:
            return int(m.group(1))
    return None


def build_master_index() -> dict[int, dict]:
    master = load_json(MASTER_DB)
    events = load_json(EVENTS_DB).get("events", {})
    locs = load_json(LOCS_DB)

    idx: dict[int, dict] = {}
    for nr_s, data in master.get("videos", {}).items():
        try:
            nr = int(nr_s)
        except Exception:
            continue

        date_iso = data.get("date", "")
        event_en = data.get("event_en", "")
        event_de = data.get("event_de", "")

        ev2 = events.get(str(nr), {})
        if ev2.get("event_en"):
            event_en = ev2.get("event_en")
        if ev2.get("event_de"):
            event_de = ev2.get("event_de")

        loc = locs.get(str(nr), {})
        location_desc = (
            loc.get("location", {}).get("desc")
            or data.get("location", "")
            or "Unknown"
        )
        hist_note = (
            loc.get("historical_note")
            or ev2.get("note")
            or data.get("historical_note")
            or "Historical archival footage."
        )

        idx[nr] = {
            "nr": nr,
            "date_iso": date_iso,
            "date_de": ddmmyyyy(date_iso),
            "event_en": event_en or "WWII Archive",
            "event_de": event_de or event_en or "WWII Archiv",
            "location": location_desc,
            "note": hist_note,
        }

    return idx


def collect_candidates() -> list[dict]:
    candidates: dict[str, dict] = {}

    if DRAFT_SCAN.exists():
        scan = load_json(DRAFT_SCAN)
        for v in scan.get("detailed_private", []):
            vid = v.get("id", "")
            title = v.get("title", "")
            if not vid or not title:
                continue
            if "wochenschau" not in title.lower():
                continue

            nr = extract_nr(title)
            candidates[vid] = {
                "id": vid,
                "title": title,
                "privacy": v.get("privacy", "private"),
                "nr": nr,
                "source": "draft_scan_2026_02_23",
            }

    if NEW_UPLOADS.exists():
        nu = load_json(NEW_UPLOADS)
        for v in nu.get("videos", []):
            vid = v.get("id", "")
            title = v.get("title", "")
            if not vid or not title:
                continue
            if "wochenschau" not in title.lower():
                continue

            nr = extract_nr(title)
            if vid in candidates and not candidates[vid].get("nr") and nr:
                candidates[vid]["nr"] = nr
                candidates[vid]["source"] += "+new_uploads"
                continue

            candidates.setdefault(
                vid,
                {
                    "id": vid,
                    "title": title,
                    "privacy": v.get("privacy", "private"),
                    "nr": nr,
                    "source": "new_uploads_2026_02_20",
                },
            )

    return list(candidates.values())


def build_title(meta: dict) -> str:
    return f"Wochenschau {meta['nr']}: {meta['event_en']} ({meta['date_de']}) | 8K HQ (4K UHD)"


def build_description(meta: dict) -> str:
    return (
        f"Classic German Newsreel Nr. {meta['nr']}, AI remastered in stunning 8K quality. "
        f"This edition covers {meta['event_en']} ({meta['date_de']}).\n\n"
        "WARNING: HISTORICAL DOCUMENT - EDUCATIONAL PURPOSES ONLY\n"
        "This footage contains historical propaganda material and is shown for documentation and education.\n\n"
        f"DE: Deutsche Wochenschau Nr. {meta['nr']} vom {meta['date_de']} - {meta['event_de']}.\n"
        f"Ort: {meta['location']}\n"
        f"Hinweis: {meta['note']}\n\n"
        "EN: German Weekly Newsreel archive footage, preserved and restored for historical research.\n\n"
        "LIKE if you found this valuable!\n"
        "COMMENT your thoughts!\n"
        "SUBSCRIBE for more vintage content!\n\n"
        "www.remaike.IT\n"
        "https://www.youtube.com/@remAIke_IT\n\n"
        "#Wochenschau #WWII #8K #History #PublicDomain"
    )


def get_youtube():
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write updates to YouTube")
    args = parser.parse_args()

    master_idx = build_master_index()
    candidates = collect_candidates()

    plan = []
    unresolved = []

    for c in candidates:
        title = c["title"]
        nr = c.get("nr")

        if title.strip().upper().startswith("DUPE"):
            unresolved.append({
                "id": c["id"],
                "title": title,
                "reason": "duplicate_marker",
                "source": c["source"],
            })
            continue

        if GOOD_TITLE_PATTERN.match(title):
            continue

        if not nr:
            unresolved.append({
                "id": c["id"],
                "title": title,
                "reason": "no_nr_extracted",
                "source": c["source"],
            })
            continue

        meta = master_idx.get(nr)
        if not meta:
            unresolved.append({
                "id": c["id"],
                "title": title,
                "reason": f"nr_{nr}_not_in_master",
                "source": c["source"],
            })
            continue

        plan.append({
            "id": c["id"],
            "source": c["source"],
            "privacy": c.get("privacy", "private"),
            "nr": nr,
            "old_title": title,
            "new_title": build_title(meta),
            "new_description": build_description(meta),
            "new_tags": WS_TAGS,
            "new_category": "27",
        })

    report = {
        "created": datetime.now().isoformat(),
        "mode": "apply" if args.apply else "dry_run",
        "total_candidates": len(candidates),
        "planned_updates": len(plan),
        "unresolved": unresolved,
        "updates": plan,
    }

    PENDING.mkdir(parents=True, exist_ok=True)
    report_path = PENDING / "wochenschau_numbering_master_plan.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Candidates: {len(candidates)}")
    print(f"Planned updates: {len(plan)}")
    print(f"Unresolved: {len(unresolved)}")
    print(f"Plan written: {report_path}")

    if not args.apply:
        print("Mode: DRY-RUN (no API writes)")
        return 0

    yt = get_youtube()
    ok = 0
    fail = 0

    for item in plan:
        try:
            current = yt.videos().list(part="snippet", id=item["id"]).execute()
            if not current.get("items"):
                fail += 1
                print(f"FAIL {item['id']}: not found")
                continue

            snippet = current["items"][0]["snippet"]
            snippet["title"] = item["new_title"]
            snippet["description"] = item["new_description"]
            snippet["tags"] = item["new_tags"]
            snippet["categoryId"] = item["new_category"]
            snippet["defaultLanguage"] = "de"

            yt.videos().update(part="snippet", body={"id": item["id"], "snippet": snippet}).execute()
            ok += 1
            print(f"OK {item['id']} -> Nr.{item['nr']}")
        except Exception as exc:
            fail += 1
            print(f"FAIL {item['id']}: {exc}")

    print(f"Applied: {ok} OK, {fail} FAIL")
    return 0 if fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
