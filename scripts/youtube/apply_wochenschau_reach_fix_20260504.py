#!/usr/bin/env python3
"""
Apply Wochenschau reach fix plan.

Reads:
- config/pending_updates/wochenschau_reach_fix_20260504.json

Dry-run by default. Use --apply to write via OAuth.
Never changes privacyStatus; videos remain public/private as they currently are.

Quota: 50 units per video update.
Examples:
  python scripts/youtube/apply_wochenschau_reach_fix_20260504.py
  python scripts/youtube/apply_wochenschau_reach_fix_20260504.py --limit 5
  python scripts/youtube/apply_wochenschau_reach_fix_20260504.py --apply --limit 5
  python scripts/youtube/apply_wochenschau_reach_fix_20260504.py --apply
"""
import argparse
import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
PLAN_PATH = Path("config/pending_updates/wochenschau_reach_fix_20260504.json")
REPORT_PATH = Path("config/wochenschau_reach_fix_20260504_apply_report.json")

def get_youtube():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds.expired:
        creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)

def load_plan():
    return json.loads(PLAN_PATH.read_text(encoding="utf-8"))

def validate_video(update):
    errors = []
    title = update["correct_title"]
    if "8K" not in title or "4K" not in title:
        errors.append("title_missing_8k_or_4k")
    if "@remAIke" in title:
        errors.append("title_contains_handle")
    if len(title) > 70:
        errors.append(f"title_too_long_{len(title)}")
    if update.get("correct_category") != "27":
        errors.append("category_not_27")
    if update.get("defaultAudioLanguage") != "de":
        errors.append("default_audio_not_de")
    if update.get("defaultLanguage") != "de":
        errors.append("default_language_not_de")
    if len(update.get("correct_tags", [])) > 15:
        errors.append("too_many_tags")
    desc_lower = update.get("correct_description", "").lower()
    if "frai.tv/watch/" not in desc_lower:
        errors.append("missing_frai_watch_link")
    if "remaike.it" not in desc_lower:
        errors.append("missing_remaike_it")
    if "youtube.com/@remaike_it" not in desc_lower:
        errors.append("missing_channel_link")
    for lang in ["de", "en", "es", "pt", "hi", "id"]:
        if lang not in update.get("localizations", {}):
            errors.append(f"missing_loc_{lang}")
    return errors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually update YouTube via OAuth")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of videos")
    args = parser.parse_args()

    plan = load_plan()
    videos = plan["videos"][:args.limit] if args.limit else plan["videos"]
    mode = "APPLY" if args.apply else "DRY-RUN"

    print(f"=== Wochenschau Reach Fix [{mode}] ===")
    print(f"Videos: {len(videos)}")
    print(f"Quota cost if applied: {len(videos) * 50}")
    print()

    validation_errors = []
    for update in videos:
        errors = validate_video(update)
        if errors:
            validation_errors.append({"videoId": update["videoId"], "errors": errors})

    if validation_errors:
        print("VALIDATION FAILED:")
        for item in validation_errors[:20]:
            print(f"  {item['videoId']}: {', '.join(item['errors'])}")
        print(f"Total validation failures: {len(validation_errors)}")
        sys.exit(1)

    yt = get_youtube() if args.apply else None
    results = []
    quota_used = 0

    for index, update in enumerate(videos, start=1):
        video_id = update["videoId"]
        print(f"[{index}/{len(videos)}] Nr.{update['video_nr']} {video_id}")
        print(f"  OLD: {update['current_title']}")
        print(f"  NEW: {update['correct_title']} ({update['title_length']} chars)")
        print(f"  LOCS: {', '.join(sorted(update['localizations'].keys()))}")

        if not args.apply:
            results.append({"videoId": video_id, "nr": update["video_nr"], "status": "dry_run"})
            print("  -> dry-run")
            continue

        try:
            yt.videos().update(
                part="snippet,localizations",
                body={
                    "id": video_id,
                    "snippet": {
                        "title": update["correct_title"],
                        "description": update["correct_description"],
                        "tags": update["correct_tags"],
                        "categoryId": update["correct_category"],
                        "defaultLanguage": update["defaultLanguage"],
                        "defaultAudioLanguage": update["defaultAudioLanguage"],
                    },
                    "localizations": update["localizations"],
                },
            ).execute()
            quota_used += 50
            results.append({"videoId": video_id, "nr": update["video_nr"], "status": "updated"})
            print("  -> updated")
        except Exception as exc:
            results.append({"videoId": video_id, "nr": update["video_nr"], "status": "error", "error": str(exc)})
            print(f"  -> ERROR: {exc}")

    report = {
        "date": "2026-05-04",
        "mode": mode,
        "videos_attempted": len(videos),
        "quota_used": quota_used,
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    updated = sum(1 for item in results if item["status"] == "updated")
    errors = sum(1 for item in results if item["status"] == "error")
    print()
    print(f"Results: {updated} updated, {errors} errors, quota used {quota_used}")
    print(f"Report: {REPORT_PATH}")

if __name__ == "__main__":
    main()
