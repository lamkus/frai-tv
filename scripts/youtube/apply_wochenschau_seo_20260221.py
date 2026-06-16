#!/usr/bin/env python3
"""
Apply corrected SEO metadata to 7 Wochenschau uploads.
Reads from config/pending_updates/wochenschau_corrected_uploads_20260221.json

Quota: 7 videos x 50 = 350 units (WRITE via OAuth)
Usage:
  python apply_wochenschau_seo_20260221.py           # Dry-run
  python apply_wochenschau_seo_20260221.py --apply   # Apply changes
"""
import json
import sys
import os
from pathlib import Path

# OAuth setup
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def main():
    apply = '--apply' in sys.argv
    mode = 'APPLY' if apply else 'DRY-RUN'

    # Load corrected metadata
    data_path = Path('config/pending_updates/wochenschau_corrected_uploads_20260221.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    videos = data['videos']
    print(f"=== Wochenschau SEO Fix [{mode}] - {len(videos)} videos ===")
    print(f"    Quota cost: {len(videos) * 50} units\n")

    if apply:
        yt = get_youtube()

    quota_used = 0
    results = []

    for v in videos:
        vid_id = v['videoId']
        nr = v['video_nr']
        title = v['correct_title']
        desc = v['correct_description']
        tags = v['correct_tags']
        cat = v['correct_category']
        status = v.get('status', 'public')

        print(f"[Nr.{nr}] {vid_id} ({status})")
        print(f"  OLD: {v['current_title']}")
        print(f"  NEW: {title} ({v['title_length']} chars)")

        if apply:
            try:
                yt.videos().update(
                    part='snippet',
                    body={
                        'id': vid_id,
                        'snippet': {
                            'title': title,
                            'description': desc,
                            'tags': tags,
                            'categoryId': cat,
                            'defaultLanguage': 'de'
                        }
                    }
                ).execute()
                quota_used += 50
                print(f"  -> UPDATED!")
                results.append({'id': vid_id, 'nr': nr, 'status': 'updated'})
            except Exception as e:
                print(f"  -> ERROR: {e}")
                results.append({'id': vid_id, 'nr': nr, 'status': 'error', 'error': str(e)})
        else:
            print(f"  -> [DRY-RUN] Would update")
            results.append({'id': vid_id, 'nr': nr, 'status': 'dry_run'})
        print()

    updated = len([r for r in results if r['status'] == 'updated'])
    errors = len([r for r in results if r['status'] == 'error'])

    print("=" * 60)
    print(f"Results: {updated} updated, {errors} errors")
    print(f"Quota used: {quota_used} units")

    # Save report
    report_path = Path('config/wochenschau_seo_fix_20260221_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'date': '2026-02-21',
            'mode': mode,
            'quota_used': quota_used,
            'results': results
        }, f, indent=2, ensure_ascii=False)

    print(f"Report: {report_path}")

    if not apply:
        print("\n>>> Add --apply to execute changes <<<")

if __name__ == '__main__':
    main()
