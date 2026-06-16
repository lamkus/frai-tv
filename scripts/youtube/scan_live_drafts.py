#!/usr/bin/env python3
"""Scannt alle Private/Draft Videos und kategorisiert sie."""

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

# ALLE Videos durchgehen
all_private = []
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
        if status == 'private':
            vid = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            all_private.append({'id': vid, 'title': title})
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f'ALLE PRIVATE VIDEOS ({len(all_private)}):')
print('=' * 70)

# Kategorisieren
wochenschau_new = []  # Neue Wochenschau (STRIKE im Titel)
wochenschau_ready = []  # Schon mit SEO
other = []

for v in all_private:
    title = v['title']
    if 'STRIKE' in title or 'strike' in title:
        # Extrahiere Nummer
        match = re.search(r'Nr(\d{3})', title)
        nr = match.group(1) if match else '???'
        wochenschau_new.append({'nr': nr, **v})
    elif 'Wochenschau' in title:
        match = re.search(r'Wochenschau\s*(\d{3})', title)
        nr = match.group(1) if match else '???'
        wochenschau_ready.append({'nr': nr, **v})
    else:
        other.append(v)

print(f'\n🆕 NEUE WOCHENSCHAU (brauchen SEO) - {len(wochenschau_new)}:')
for v in sorted(wochenschau_new, key=lambda x: x['nr']):
    print(f"   Nr.{v['nr']} | {v['id']} | {v['title'][:45]}")

print(f'\n✅ WOCHENSCHAU MIT SEO (ready to publish) - {len(wochenschau_ready)}:')
for v in sorted(wochenschau_ready, key=lambda x: x['nr']):
    print(f"   Nr.{v['nr']} | {v['id']} | {v['title'][:45]}")

print(f'\n📦 ANDERE PRIVATE VIDEOS - {len(other)}:')
for v in other:
    print(f"   {v['id']} | {v['title'][:50]}")

# Speichern für nächsten Schritt
result = {
    'new_wochenschau': wochenschau_new,
    'ready_wochenschau': wochenschau_ready,
    'other': other
}
with open('config/live_draft_scan.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f'\n💾 Gespeichert in config/live_draft_scan.json')
