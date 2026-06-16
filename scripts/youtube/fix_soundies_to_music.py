#!/usr/bin/env python3
"""Fix Soundies Category zu Music (10)"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    creds_data = json.load(f)
creds = Credentials(
    token=creds_data['token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

print("🎵 FIX SOUNDIES → MUSIC CATEGORY")
print("=" * 60)

# Hole alle Videos
all_videos = []
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet',
        playlistId='UUVFv6Egpl0LDvigpFbQXNeQ',
        maxResults=50,
        pageToken=next_page
    ).execute()
    all_videos.extend(response['items'])
    next_page = response.get('nextPageToken')
    if not next_page:
        break

# Finde Soundies
soundies = [v for v in all_videos if 'soundie' in v['snippet']['title'].lower()]
print(f"Soundies gefunden: {len(soundies)}")

fixed = 0
for v in soundies:
    vid = v['snippet']['resourceId']['videoId']
    title = v['snippet']['title']
    
    try:
        video = youtube.videos().list(part='snippet', id=vid).execute()
        if not video['items']:
            continue
            
        snippet = video['items'][0]['snippet']
        if snippet.get('categoryId') == '10':
            continue  # Schon Music
        
        # Fix to Music
        snippet['categoryId'] = '10'
        youtube.videos().update(
            part='snippet',
            body={'id': vid, 'snippet': snippet}
        ).execute()
        
        fixed += 1
        print(f"✅ → Music: {title[:50]}")
        
    except Exception as e:
        print(f"❌ Error: {title[:30]} - {e}")

print(f"\n📊 Gefixt: {fixed} Soundies → Music Category")
