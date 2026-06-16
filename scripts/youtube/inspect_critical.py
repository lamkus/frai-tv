#!/usr/bin/env python3
"""
Inspect the remaining CRITICAL/HIGH priority videos for fixing.
Reads from the audit JSON and fetches live data for the worst videos.
"""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth.get('access_token') or oauth.get('token'),
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Already fixed in last batch
ALREADY_FIXED = {'hvJsq7z3sjg', 'ndAzCIUxo-c', 'tk3DHvp9CFs', 'Q_hgdk3UaJs'}

# Load audit - get videos with score < 90
audit = json.loads(Path('config/comprehensive_audit_2026_02_06.json').read_text(encoding='utf-8'))
critical_ids = []
for v in audit['videos']:
    if v['id'] in ALREADY_FIXED:
        continue
    if v['score'] < 90:
        critical_ids.append(v['id'])

print(f"📋 {len(critical_ids)} videos with score < 90 (excluding already fixed)")

# Fetch live data
all_videos = []
for i in range(0, len(critical_ids), 50):
    batch = critical_ids[i:i+50]
    resp = youtube.videos().list(
        part='snippet,status',
        id=','.join(batch)
    ).execute()
    all_videos.extend(resp.get('items', []))

# Print each one
for v in all_videos:
    s = v['snippet']
    # Find audit entry
    audit_entry = next((a for a in audit['videos'] if a['id'] == v['id']), None)
    score = audit_entry['score'] if audit_entry else '?'
    issues = audit_entry['issues'] if audit_entry else []
    
    print(f"\n{'=' * 78}")
    print(f"SCORE: {score}/100 | ID: {v['id']}")
    print(f"TITLE: {s['title']}")
    print(f"  Len: {len(s['title'])} | Cat: {s['categoryId']} | Privacy: {v['status']['privacyStatus']}")
    print(f"  Tags ({len(s.get('tags', []))}): {s.get('tags', [])[:10]}")
    desc = s.get('description', '')
    print(f"  Desc ({len(desc)} chars):")
    for line in desc.split('\n')[:8]:
        print(f"    | {line[:80]}")
    if desc.count('\n') > 8:
        print(f"    | ... ({desc.count(chr(10))+1} lines)")
    print(f"  ISSUES:")
    for i in issues:
        print(f"    ❌ [{i['severity']}] {i['code']}: {i['msg']}")
