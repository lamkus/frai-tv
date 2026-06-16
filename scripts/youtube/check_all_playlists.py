#!/usr/bin/env python3
"""
🔍 CHECK ALL PLAYLISTS - Sortierung und fehlende Folgen
"""

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

def get_playlist_items(playlist_id):
    items = []
    next_page = None
    while True:
        response = youtube.playlistItems().list(
            part='snippet', 
            playlistId=playlist_id, 
            maxResults=50, 
            pageToken=next_page
        ).execute()
        items.extend(response['items'])
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    return items

def extract_episode(title):
    """Extrahiere Episoden-Nummer aus Titel"""
    patterns = [
        r'[Ee]\.?\s*(\d{1,2})',           # E01, E 1
        r'[Ee]pisode\s*(\d{1,2})',        # Episode 1
        r'[Ff]olge\s*(\d{1,2})',          # Folge 1
        r'#\s*(\d{1,2})',                 # #1
        r'(\d{1,2})\s*[-–:.]\s*[A-Z]',    # 01 - Title
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return int(match.group(1))
    return 0

# ========================================
# ALFRED J. KWAK
# ========================================
print("=" * 70)
print("🦆 ALFRED J. KWAK PLAYLIST")
print("=" * 70)

ALFRED_PLAYLIST = 'PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL'
items = get_playlist_items(ALFRED_PLAYLIST)

print(f"Videos in Playlist: {len(items)}")
print("-" * 70)

episodes = []
for i, item in enumerate(items, 1):
    title = item['snippet']['title']
    ep = extract_episode(title)
    episodes.append(ep)
    print(f"{i:2}. Ep.{ep:02d} | {title[:55]}")

# Fehlende Folgen (Alfred hat 52 Episoden)
found = set(e for e in episodes if e > 0)
missing = sorted(set(range(1, 53)) - found)

print(f"\n📊 ANALYSE:")
print(f"   Gefunden: {len(found)}/52 Episoden")
if missing:
    print(f"   FEHLEND ({len(missing)}): {missing}")
else:
    print(f"   FEHLEND: Keine - KOMPLETT!")

# Sortierung prüfen
ep_list = [e for e in episodes if e > 0]
is_sorted = ep_list == sorted(ep_list)
print(f"   Sortiert: {'✅ Ja' if is_sorted else '❌ NEIN'}")

# ========================================
# BRAVESTARR
# ========================================
print("\n" + "=" * 70)
print("🤠 BRAVESTARR PLAYLIST")
print("=" * 70)

BRAVESTARR_PLAYLIST = 'PL3d2Tsr13ihOHV7IckAv3tDxpPdw4WHQf'
items = get_playlist_items(BRAVESTARR_PLAYLIST)

print(f"Videos in Playlist: {len(items)}")
for i, item in enumerate(items, 1):
    title = item['snippet']['title']
    print(f"{i:2}. {title[:60]}")

print(f"\n📊 BraveStarr hat 65 Episoden - {len(items)} online")
