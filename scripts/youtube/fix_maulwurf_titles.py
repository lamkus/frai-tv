#!/usr/bin/env python3
"""Kürze Maulwurf-Titel auf <60 Zeichen."""

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

# Mapping: Video-ID -> Neuer kurzer Titel
TITLE_FIXES = {
    'MlzpyJ6CyHw': 'Maulwurf: Der Frosch (1998) | 8K HQ | @remAIke_IT',  # E45
    'tMaYrApYlxc': 'Maulwurf: Die Flöte (1999) | 8K HQ | @remAIke_IT',   # E60
    'EZxjMpAY9Wk': 'Maulwurf: Die Quelle (1999) | 8K HQ | @remAIke_IT',  # E59
    'gGYWs-xw1VM': 'Maulwurf: Im Urlaub (Mix) | 8K HQ | @remAIke_IT',    # Bonus
    # Private (werden auch gefixt für später)
    '6MElwMSiT0E': 'Maulwurf: Der Frosch (Clip) (1998) | 8K | @remAIke_IT',  # E45b
    'wtq09EZfO20': 'Maulwurf: Als Gärtner (1969) | 8K HQ | @remAIke_IT',      # E08
    'xG_2AhK-sVI': 'Maulwurf: Die Rakete (1965) | 8K HQ | @remAIke_IT',       # E03
}

print("🔧 MAULWURF TITEL-FIX")
print("=" * 60)

for vid, new_title in TITLE_FIXES.items():
    print(f"\n📹 Video: {vid}")
    print(f"   NEU: {new_title} ({len(new_title)} chars)")
    
    try:
        # Hole aktuelle Video-Daten
        video = youtube.videos().list(
            part='snippet',
            id=vid
        ).execute()
        
        if not video['items']:
            print(f"   ❌ Video nicht gefunden!")
            continue
        
        snippet = video['items'][0]['snippet']
        old_title = snippet['title']
        print(f"   ALT: {old_title} ({len(old_title)} chars)")
        
        # Update nur wenn nötig
        if len(old_title) <= 60:
            print(f"   ⏭️  Bereits kurz genug!")
            continue
        
        # Update
        snippet['title'] = new_title
        youtube.videos().update(
            part='snippet',
            body={
                'id': vid,
                'snippet': snippet
            }
        ).execute()
        print(f"   ✅ Aktualisiert!")
        
    except Exception as e:
        print(f"   ❌ Fehler: {e}")

print("\n" + "=" * 60)
print("✅ Maulwurf-Titel gefixt!")
