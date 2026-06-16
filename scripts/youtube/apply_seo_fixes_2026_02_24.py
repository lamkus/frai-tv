"""Apply SEO fixes from reports/seo_fix_targets.json.

Fixes:
1) status.embeddable = True for target videos
2) description line 1 replacement when line1 == title
3) trim hashtags to max 5 for flagged videos

Usage:
  python scripts/youtube/apply_seo_fixes_2026_02_24.py --apply
  python scripts/youtube/apply_seo_fixes_2026_02_24.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[2]
TARGETS_FILE = ROOT / "reports" / "seo_fix_targets.json"
REPORT_FILE = ROOT / "reports" / "seo_fix_apply_2026_02_24.json"
TOKEN_FILE = ROOT / "token.json"


def load_targets() -> dict:
    with TARGETS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def chunked(items: List[str], size: int = 50):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def build_hook(title: str, category_id: str | None) -> str:
    t = title.lower()
    if "wochenschau" in t:
        return "🎬 Deutsche Wochenschau WWII archival footage, AI remastered in 8K HQ (4K UHD) for historical documentation and education."
    if "soundie" in t or category_id == "10":
        return "🎬 Vintage Soundie performance from the 1940s, AI remastered in 8K HQ (4K UHD) with restored classic audio."
    if "alfred j. kwak" in t or "alfred" in t or "quack" in t:
        return "🎬 Alfred J. Kwak complete episode in 8K HQ (4K UHD), carefully restored for modern screens."
    if "maulwurf" in t:
        return "🎬 Der kleine Maulwurf classic animation episode, AI remastered in 8K HQ (4K UHD)."
    return "🎬 Classic public domain footage, AI remastered in 8K HQ (4K UHD) with restored detail and clarity."


def trim_hashtags(description: str, keep: int = 5) -> tuple[str, int]:
    words = description.split()
    kept = 0
    removed = 0
    output = []
    for word in words:
        if word.startswith("#") and re.search(r"\w", word):
            if kept < keep:
                output.append(word)
                kept += 1
            else:
                removed += 1
                continue
        else:
            output.append(word)

    fixed = " ".join(output)
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    return fixed, removed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    apply_changes = args.apply and not args.dry_run

    targets = load_targets()

    not_embeddable_ids = sorted({item["id"] for item in targets.get("not_embeddable", [])})
    desc_eq_title_ids = sorted({item["id"] for item in targets.get("desc_eq_title", [])})
    hashtag_ids = sorted({item["id"] for item in targets.get("too_many_hashtags", [])})
    all_ids = sorted(set(not_embeddable_ids + desc_eq_title_ids + hashtag_ids))

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
    yt = build("youtube", "v3", credentials=creds)

    videos: Dict[str, dict] = {}
    for batch in chunked(all_ids, 50):
        resp = yt.videos().list(part="snippet,status", id=",".join(batch), maxResults=50).execute()
        for item in resp.get("items", []):
            if item.get("status", {}).get("privacyStatus") == "public":
                videos[item["id"]] = item

    report = {
        "scanned_targets": len(all_ids),
        "public_loaded": len(videos),
        "embeddable_fix": {"target": len(not_embeddable_ids), "updated": 0, "skipped": 0, "errors": []},
        "description_fix": {"target": len(desc_eq_title_ids), "updated": 0, "skipped": 0, "errors": []},
        "hashtag_fix": {"target": len(hashtag_ids), "updated": 0, "skipped": 0, "errors": []},
        "mode": "apply" if apply_changes else "dry-run",
    }

    # 1) embeddable fix (status update)
    for vid in not_embeddable_ids:
        item = videos.get(vid)
        if not item:
            report["embeddable_fix"]["skipped"] += 1
            continue

        status = item.get("status", {}).copy()
        if status.get("embeddable", True):
            report["embeddable_fix"]["skipped"] += 1
            continue

        status["embeddable"] = True

        if not apply_changes:
            report["embeddable_fix"]["updated"] += 1
            continue

        try:
            yt.videos().update(part="status", body={"id": vid, "status": status}).execute()
            report["embeddable_fix"]["updated"] += 1
        except Exception as exc:
            report["embeddable_fix"]["errors"].append({"id": vid, "error": str(exc)})

    # 2) description line 1 fix (+ hashtag trim when in hashtag list)
    for vid in sorted(set(desc_eq_title_ids + hashtag_ids)):
        item = videos.get(vid)
        if not item:
            report["description_fix"]["skipped"] += int(vid in desc_eq_title_ids)
            report["hashtag_fix"]["skipped"] += int(vid in hashtag_ids)
            continue

        snippet = item.get("snippet", {}).copy()
        title = (snippet.get("title") or "").strip()
        description = snippet.get("description") or ""
        category_id = snippet.get("categoryId")

        lines = description.split("\n") if description else [""]
        first_line = (lines[0] if lines else "").strip()

        changed_desc = False

        if vid in desc_eq_title_ids and first_line == title:
            lines[0] = build_hook(title, category_id)
            changed_desc = True

        new_description = "\n".join(lines)

        if vid in hashtag_ids:
            trimmed, removed = trim_hashtags(new_description, keep=5)
            if removed > 0:
                new_description = trimmed
                changed_desc = True

        if not changed_desc:
            if vid in desc_eq_title_ids:
                report["description_fix"]["skipped"] += 1
            if vid in hashtag_ids:
                report["hashtag_fix"]["skipped"] += 1
            continue

        snippet["description"] = new_description

        if not apply_changes:
            if vid in desc_eq_title_ids:
                report["description_fix"]["updated"] += 1
            if vid in hashtag_ids:
                report["hashtag_fix"]["updated"] += 1
            continue

        try:
            yt.videos().update(part="snippet", body={"id": vid, "snippet": snippet}).execute()
            if vid in desc_eq_title_ids:
                report["description_fix"]["updated"] += 1
            if vid in hashtag_ids:
                report["hashtag_fix"]["updated"] += 1
        except Exception as exc:
            if vid in desc_eq_title_ids:
                report["description_fix"]["errors"].append({"id": vid, "error": str(exc)})
            if vid in hashtag_ids:
                report["hashtag_fix"]["errors"].append({"id": vid, "error": str(exc)})

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nSaved report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
