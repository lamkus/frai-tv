#!/usr/bin/env python3
"""Setze Recording Dates für ALLE Vintage Videos (Batch 2)"""

import json
import re
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

def extract_year(title):
    match = re.search(r'\(?(19\d{2})\)?', title)
    return int(match.group(1)) if match else None

print("📅 RECORDING DATES - BATCH 2")
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

# Filtere Vintage Videos
vintage = []
for v in all_videos:
    year = extract_year(v['snippet']['title'])
    if year and 1900 <= year <= 1999:
        vintage.append({
            'id': v['snippet']['resourceId']['videoId'],
            'title': v['snippet']['title'],
            'year': year
        })

print(f"Vintage Videos: {len(vintage)}")

# Prüfe welche schon Recording Date haben
needs_update = []
for v in vintage:
    try:
        video = youtube.videos().list(part='recordingDetails', id=v['id']).execute()
        if video['items']:
            if not video['items'][0].get('recordingDetails', {}).get('recordingDate'):
                needs_update.append(v)
    except:
        pass

print(f"Brauchen Update: {len(needs_update)}")

# Update alle (max 100 pro Run wegen Quota)
MAX = 100
updated = 0
for v in needs_update[:MAX]:
    try:
        youtube.videos().update(
            part='recordingDetails',
            body={
                'id': v['id'],
                'recordingDetails': {'recordingDate': f"{v['year']}-07-01T00:00:00Z"}
            }
        ).execute()
        updated += 1
        if updated % 20 == 0:
            print(f"   ... {updated} aktualisiert")
    except Exception as e:
        print(f"   ⚠️ {v['id']}: {e}")

print(f"\n✅ Recording Dates gesetzt: {updated}")
print(f"📊 Noch offen: {len(needs_update) - updated}")
