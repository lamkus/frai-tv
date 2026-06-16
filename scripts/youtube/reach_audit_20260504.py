#!/usr/bin/env python3
"""
Reach Audit 2026-05-04: Check ALL Wochenschau videos for:
- Title: 4K + 8K both present?
- Description: First 2 lines keyword-rich?
- Tags: AEO/Geo keywords?
- DefaultLanguage / DefaultAudioLanguage set?
- Captions enabled?
- Localized titles/descriptions (Multi-Language)?
"""
import json
import os
import re
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
    yt = get_youtube()
    UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

    # Get ALL video IDs
    all_ids = []
    token = None
    while True:
        resp = yt.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOAD_PL,
            maxResults=50,
            pageToken=token
        ).execute()
        for it in resp['items']:
            all_ids.append(it['contentDetails']['videoId'])
        token = resp.get('nextPageToken')
        if not token:
            break

    print(f"Total videos in channel: {len(all_ids)}")

    # Fetch FULL metadata
    all_videos = []
    for i in range(0, len(all_ids), 50):
        resp = yt.videos().list(
            part='snippet,status,localizations,contentDetails',
            id=','.join(all_ids[i:i+50])
        ).execute()
        all_videos.extend(resp.get('items', []))

    print(f"Fetched: {len(all_videos)} videos")

    # Filter Wochenschau only
    ws_videos = []
    for v in all_videos:
        title = v['snippet'].get('title', '')
        if title.lower().startswith('wochenschau'):
            ws_videos.append(v)

    print(f"Wochenschau videos: {len(ws_videos)}\n")

    # Audit each
    issues = {
        'missing_4k_keyword': [],
        'missing_8k_keyword': [],
        'no_default_language': [],
        'no_default_audio_language': [],
        'no_localizations': [],
        'desc_line1_repeats_title': [],
        'wrong_category': [],
        'too_few_tags': [],
        'private_status': [],
    }

    full_audit = []

    for v in ws_videos:
        sn = v['snippet']
        st = v['status']
        title = sn.get('title', '')
        desc = sn.get('description', '')
        tags = sn.get('tags', [])
        cat = sn.get('categoryId', '')
        default_lang = sn.get('defaultLanguage', None)
        default_audio_lang = sn.get('defaultAudioLanguage', None)
        localizations = v.get('localizations', {})
        privacy = st.get('privacyStatus', 'unknown')

        vid_id = v['id']
        has_4k = bool(re.search(r'\b4K\b', title, re.IGNORECASE))
        has_8k = bool(re.search(r'\b8K\b', title, re.IGNORECASE))
        desc_line1 = desc.split('\n')[0].strip()
        title_in_line1 = title.lower()[:30] in desc_line1.lower()

        record = {
            'videoId': vid_id,
            'title': title,
            'privacy': privacy,
            'has_4k_in_title': has_4k,
            'has_8k_in_title': has_8k,
            'category': cat,
            'tags_count': len(tags),
            'default_lang': default_lang,
            'default_audio_lang': default_audio_lang,
            'localizations_count': len(localizations),
            'localizations_langs': list(localizations.keys()),
            'desc_line1': desc_line1[:100],
        }
        full_audit.append(record)

        if not has_4k:
            issues['missing_4k_keyword'].append(vid_id)
        if not has_8k:
            issues['missing_8k_keyword'].append(vid_id)
        if not default_lang:
            issues['no_default_language'].append(vid_id)
        if not default_audio_lang:
            issues['no_default_audio_language'].append(vid_id)
        if not localizations:
            issues['no_localizations'].append(vid_id)
        if title_in_line1:
            issues['desc_line1_repeats_title'].append(vid_id)
        if cat != '27':
            issues['wrong_category'].append({'id': vid_id, 'cat': cat})
        if len(tags) < 10:
            issues['too_few_tags'].append({'id': vid_id, 'count': len(tags)})
        if privacy != 'public':
            issues['private_status'].append({'id': vid_id, 'status': privacy})

    print("=" * 70)
    print("  REACH AUDIT RESULTS - Wochenschau")
    print("=" * 70)
    for issue_type, items in issues.items():
        print(f"  {issue_type}: {len(items)}")
    print()

    # Save
    out = {
        'audit_date': '2026-05-04',
        'total_channel_videos': len(all_videos),
        'wochenschau_count': len(ws_videos),
        'issues_summary': {k: len(v) for k, v in issues.items()},
        'issues_detail': issues,
        'full_audit': full_audit,
    }
    out_path = 'config/reach_audit_20260504.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Saved: {out_path}")
    print(f"Quota used: ~{len(all_ids)//50 + 10} read units")

if __name__ == '__main__':
    main()
