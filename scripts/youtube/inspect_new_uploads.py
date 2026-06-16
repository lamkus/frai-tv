#!/usr/bin/env python3
"""Inspect the 4 new uploads - get full metadata for review."""
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

NEW_IDS = ['hvJsq7z3sjg', 'ndAzCIUxo-c', 'tk3DHvp9CFs', 'Q_hgdk3UaJs']

resp = youtube.videos().list(
    part='snippet,contentDetails,status',
    id=','.join(NEW_IDS)
).execute()

for v in resp.get('items', []):
    s = v['snippet']
    st = v['status']
    print("=" * 78)
    print(f"ID:          {v['id']}")
    print(f"Title:       {s['title']}")
    print(f"Title Len:   {len(s['title'])} chars")
    print(f"Published:   {s.get('publishedAt', 'N/A')}")
    print(f"Category:    {s.get('categoryId', '?')}")
    print(f"Privacy:     {st.get('privacyStatus', '?')}")
    print(f"Tags:        {s.get('tags', [])}")
    print(f"Tag Count:   {len(s.get('tags', []))}")
    desc = s.get('description', '')
    print(f"Description: ({len(desc)} chars)")
    if desc:
        for line in desc.split('\n')[:15]:
            print(f"  | {line}")
        if desc.count('\n') > 15:
            print(f"  | ... ({desc.count(chr(10))+1} lines total)")
    else:
        print("  | (EMPTY)")
    print(f"Duration:    {v['contentDetails'].get('duration', '?')}")
    print()
