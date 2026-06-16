#!/usr/bin/env python3
"""Suche nach Maulwurf/Krtek Videos im Channel."""

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

# Suche nach Maulwurf-Videos (alle)
maulwurf = []
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet,status',
        playlistId='UUVFv6Egpl0LDvigpFbQXNeQ',
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in response['items']:
        status = item.get('status', {}).get('privacyStatus', '?')
        vid = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        title_lower = title.lower()
        
        # Suche nach Maulwurf/Krtek/Mole keywords
        keywords = ['maulwurf', 'krtek', 'mole', 'krtecek', 'krteček', 'cvrček', 'cvrcek']
        if any(kw in title_lower for kw in keywords):
            maulwurf.append({
                'id': vid,
                'title': title,
                'status': status
            })
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f'MAULWURF/KRTEK VIDEOS GEFUNDEN: {len(maulwurf)}')
print('=' * 70)

private_vids = []
public_vids = []

for v in maulwurf:
    if v['status'] == 'private':
        private_vids.append(v)
    else:
        public_vids.append(v)

print(f'\n🔴 PRIVATE/DRAFTS ({len(private_vids)}):')
for v in private_vids:
    print(f"   {v['id']} | {v['title']}")

print(f'\n🟢 PUBLIC ({len(public_vids)}):')
for v in public_vids:
    print(f"   {v['id']} | {v['title']}")
