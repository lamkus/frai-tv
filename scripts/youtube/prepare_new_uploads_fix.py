#!/usr/bin/env python3
"""Prepare fixes for 5 new videos: 4 Wochenschau + 1 Alfred"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if creds.expired:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

# The 5 new videos
NEW_VIDEOS = {
    '2HZx5FumOo8': {
        'type': 'wochenschau',
        'nr': '552',
        'date': '02.04.1941',
        'event': 'Belgrade Coup',
        'title': 'Wochenschau 552: Belgrade Coup (02.04.1941) | 8K HQ (4K UHD)',
    },
    'Yhz7gsTVqNA': {
        'type': 'wochenschau',
        'nr': '567',
        'date': '16.07.1941',
        'event': 'Smolensk Pocket',
        'title': 'Wochenschau 567: Smolensk Pocket (16.07.1941) | 8K HQ (4K UHD)',
    },
    'suxhPHyaQHU': {
        'type': 'wochenschau',
        'nr': '569',
        'date': '30.07.1941',
        'event': 'Kiev Encirclement',
        'title': 'Wochenschau 569: Kiev Encirclement (30.07.1941) | 8K HQ (4K UHD)',
    },
    '6Mh7zjUCmHw': {
        'type': 'wochenschau',
        'nr': '749',
        'date': '10.01.1945',
        'event': 'Ardennes Fails',
        'title': 'Wochenschau 749: Ardennes Fails (10.01.1945) | 8K HQ (4K UHD)',
    },
    'mSKWu7zRtEM': {
        'type': 'alfred',
        'ep': 'E27',
        'title': 'Alfred J. Kwak (E27) Verliebt | DE | 8K HQ (4K UHD)',
    }
}

print("🔍 Checking current metadata for 5 new videos...\n")

# Fetch current metadata
video_ids = list(NEW_VIDEOS.keys())
resp = yt.videos().list(
    part='snippet,contentDetails',
    id=','.join(video_ids)
).execute()

current_data = {}
for item in resp['items']:
    vid = item['id']
    snippet = item['snippet']
    current_data[vid] = {
        'title': snippet['title'],
        'description': snippet.get('description', '')[:150],
        'tags': snippet.get('tags', []),
        'categoryId': snippet['categoryId'],
        'defaultLanguage': snippet.get('defaultLanguage', 'NONE')
    }

# Show what needs fixing
print("=" * 70)
for vid_id, plan in NEW_VIDEOS.items():
    cur = current_data.get(vid_id, {})
    print(f"\n{vid_id} | {plan['type'].upper()}")
    print(f"  Current:  {cur.get('title', 'N/A')[:60]}")
    print(f"  New:      {plan['title'][:60]}")
    
    issues = []
    if plan['title'] != cur.get('title'):
        issues.append("TITLE")
    if cur.get('categoryId') != '27' and plan['type'] == 'wochenschau':
        issues.append("CATEGORY (need 27)")
    if cur.get('categoryId') != '1' and plan['type'] == 'alfred':
        issues.append("CATEGORY (need 1)")
    if not cur.get('defaultLanguage'):
        issues.append("LANG")
    if len(cur.get('tags', [])) > 15:
        issues.append("TAGS>15")
    
    print(f"  Issues:   {', '.join(issues) if issues else '✅ OK'}")

print("\n" + "=" * 70)
print("\nSave plan to config/new_uploads_fix_plan.json")

# Save plan
with open('config/new_uploads_fix_plan.json', 'w', encoding='utf-8') as f:
    json.dump({
        'date': '2026-02-20',
        'videos': NEW_VIDEOS,
        'current': current_data
    }, f, indent=2, ensure_ascii=False)

print("✅ Done — review plan, then apply")
