#!/usr/bin/env python3
"""Find YouTube Video IDs for specific Wochenschau drafts."""
import json, sys, io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth.get('access_token') or oauth.get('token'),
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

uploads_id = 'UUVFv6Egpl0LDvigpFbQXNeQ'
targets = ['nr553', 'nr554', 'nr752']
found = []
next_page = None
page = 0

while True:
    resp = youtube.playlistItems().list(
        part='snippet,contentDetails,status',
        playlistId=uploads_id,
        maxResults=50,
        pageToken=next_page
    ).execute()
    page += 1
    for item in resp['items']:
        title = item['snippet']['title'].lower()
        vid = item['contentDetails']['videoId']
        status = item.get('status', {}).get('privacyStatus', '?')
        for t in targets:
            if t in title:
                print(f"FOUND: {t} -> ID={vid} status={status}")
                print(f"  Title: {item['snippet']['title']}")
                found.append({
                    'nr': t,
                    'id': vid,
                    'status': status,
                    'title': item['snippet']['title']
                })
    next_page = resp.get('nextPageToken')
    if not next_page:
        break

print(f"\n--- Scanned {page} pages ---")
print(f"Found {len(found)} matches:")
for f in found:
    print(json.dumps(f, ensure_ascii=False))
if not found:
    print("NONE FOUND - videos may not be in uploads playlist")
