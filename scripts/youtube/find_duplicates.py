#!/usr/bin/env python3
"""Findet Duplikate: Wochenschau-Nummern mit mehreren Videos."""

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

# Alle Videos sammeln (public + private)
all_videos = {}
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet,status',
        playlistId='UUVFv6Egpl0LDvigpFbQXNeQ',
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in response['items']:
        vid = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        status = item.get('status', {}).get('privacyStatus', '?')
        
        # Wochenschau-Nummer extrahieren
        match = re.search(r'Nr\.?(\d{3})', title) or re.search(r'Wochenschau\s*(\d{3})', title)
        if match:
            nr = match.group(1)
            if nr not in all_videos:
                all_videos[nr] = []
            all_videos[nr].append({
                'id': vid,
                'title': title[:60],
                'status': status
            })
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

# Duplikate finden
print('=' * 70)
print('DUPLIKAT-ANALYSE: Wochenschau-Nummern mit mehreren Videos')
print('=' * 70)

duplicates = {nr: vids for nr, vids in all_videos.items() if len(vids) > 1}

if duplicates:
    for nr in sorted(duplicates.keys()):
        print(f'\nNr.{nr} - {len(duplicates[nr])} VIDEOS:')
        for v in duplicates[nr]:
            emoji = '🟢' if v['status'] == 'public' else '🔴'
            status_str = v['status']
            print(f"  {emoji} [{status_str:7}] {v['id']} | {v['title']}")
    print(f'\n>>> TOTAL: {len(duplicates)} Nummern mit Duplikaten')
else:
    print('Keine Duplikate gefunden!')

# Speichern
with open('config/wochenschau_duplicates.json', 'w', encoding='utf-8') as f:
    json.dump(duplicates, f, ensure_ascii=False, indent=2)
print(f'\n💾 Details in config/wochenschau_duplicates.json')
