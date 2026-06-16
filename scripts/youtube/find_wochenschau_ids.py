#!/usr/bin/env python3
"""Finde aktuelle Wochenschau Video IDs mit OAuth"""
import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OAUTH_FILE = os.path.join(BASE_DIR, 'config', 'youtube_oauth.json')
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Load OAuth
with open(OAUTH_FILE) as f:
    creds_data = json.load(f)

creds = Credentials(
    token=creds_data['token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

print("🔍 Scanning upload playlist for Wochenschau videos...")

# Get all videos
all_videos = []
next_page = None

while True:
    response = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=UPLOAD_PLAYLIST,
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    all_videos.extend(response.get('items', []))
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"\n📊 Total videos on channel: {len(all_videos)}")

# Filter Wochenschau
wochenschau_videos = []
for item in all_videos:
    vid = item['contentDetails']['videoId']
    title = item['snippet']['title']
    if 'Wochenschau' in title or 'wochenschau' in title.lower():
        # Extract number from title
        nr = None
        if 'Nr.' in title:
            try:
                nr = title.split('Nr.')[1].split()[0].strip()
            except:
                pass
        elif ': ' in title:
            try:
                nr = title.split(':')[0].replace('Wochenschau', '').strip()
            except:
                pass
        
        wochenschau_videos.append({
            'video_id': vid, 
            'title': title,
            'nr': nr
        })
        print(f"  {vid}: {title[:65]}")

print(f"\n✅ {len(wochenschau_videos)} Wochenschau videos found")

# Speichern
output = os.path.join(BASE_DIR, 'config', 'wochenschau_online_ids.json')
with open(output, 'w', encoding='utf-8') as f:
    json.dump(wochenschau_videos, f, indent=2, ensure_ascii=False)
print(f"💾 Saved to {output}")
