#!/usr/bin/env python3
"""Get specific video via OAuth."""
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth laden
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Video T-EsdXGhqog holen
video_id = 'T-EsdXGhqog'
print(f"Hole Video {video_id}...")

response = youtube.videos().list(
    part='snippet,statistics,status',
    id=video_id
).execute()

if response.get('items'):
    v = response['items'][0]
    print()
    print("=" * 80)
    print("VIDEO GEFUNDEN!")
    print("=" * 80)
    print(f"ID: {v['id']}")
    print(f"Title: {v['snippet']['title']}")
    print(f"Views: {v['statistics'].get('viewCount', '?')}")
    print(f"Likes: {v['statistics'].get('likeCount', '?')}")
    print(f"Status: {v['status'].get('privacyStatus', '?')}")
    print()
    print("Description (first 500 chars):")
    print(v['snippet'].get('description', '')[:500])
else:
    print("Video nicht gefunden oder nicht zugänglich!")
    print(response)
