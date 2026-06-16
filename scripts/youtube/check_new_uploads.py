#!/usr/bin/env python3
"""Check for new uploads in last 7 days"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if creds.expired:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

# Get videos from last 7 days
cutoff = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
uploads_pl = 'UUVFv6Egpl0LDvigpFbQXNeQ'

recent = []
next_token = None
for i in range(3):  # Check 150 videos
    resp = yt.playlistItems().list(
        part='contentDetails',
        playlistId=uploads_pl,
        maxResults=50,
        pageToken=next_token
    ).execute()
    
    for item in resp['items']:
        vid_id = item['contentDetails']['videoId']
        recent.append(vid_id)
    
    next_token = resp.get('nextPageToken')
    if not next_token:
        break

# Get details
print(f'Checking {len(recent)} recent videos...\n')
new_videos = []
for i in range(0, len(recent), 50):
    batch = recent[i:i+50]
    vresp = yt.videos().list(
        part='snippet,status',
        id=','.join(batch)
    ).execute()
    
    for v in vresp['items']:
        pub = v['snippet']['publishedAt']
        if pub >= cutoff:
            new_videos.append({
                'id': v['id'],
                'title': v['snippet']['title'],
                'published': pub,
                'privacy': v['status']['privacyStatus']
            })

new_videos.sort(key=lambda x: x['published'], reverse=True)
print(f'NEW UPLOADS (last 7 days): {len(new_videos)}\n')
for v in new_videos[:20]:  # Show max 20
    priv = v['privacy']
    title = v['title'][:70]
    pub = v['published'][:10]
    print(f"{pub} | {priv:7} | {title}")

with open('config/new_uploads_2026_02_20.json', 'w', encoding='utf-8') as f:
    json.dump({'date': '2026-02-20', 'count': len(new_videos), 'videos': new_videos}, f, indent=2, ensure_ascii=False)
print(f'\nSaved to config/new_uploads_2026_02_20.json')
