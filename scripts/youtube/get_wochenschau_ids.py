#!/usr/bin/env python3
"""Quick script to get all real Wochenschau video IDs from the playlist."""

import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'
playlist_id = 'PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg'

# Load OAuth credentials
with open(OAUTH_FILE, 'r') as f:
    creds_data = json.load(f)
    creds = Credentials.from_authorized_user_info(creds_data)

youtube = build('youtube', 'v3', credentials=creds)

all_videos = []
next_page = None

print(f"Fetching videos from playlist: {playlist_id}")

while True:
    request = youtube.playlistItems().list(
        part='snippet,contentDetails',
        playlistId=playlist_id,
        maxResults=50,
        pageToken=next_page
    )
    response = request.execute()
    
    for item in response.get('items', []):
        vid_id = item['contentDetails']['videoId']
        title = item['snippet']['title']
        all_videos.append({'id': vid_id, 'title': title})
        print(f"{vid_id}: {title[:70]}")
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"\n📊 Total videos found: {len(all_videos)}")
