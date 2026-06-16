#!/usr/bin/env python3
"""Erstelle Maulwurf-Playlist und füge alle Maulwurf-Videos hinzu."""

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

# 1. Prüfe ob Playlist schon existiert
print("🔍 Suche existierende Maulwurf-Playlist...")
existing_playlists = youtube.playlists().list(
    part='snippet',
    mine=True,
    maxResults=50
).execute()

maulwurf_playlist_id = None
for pl in existing_playlists.get('items', []):
    if 'maulwurf' in pl['snippet']['title'].lower() or 'krtek' in pl['snippet']['title'].lower():
        maulwurf_playlist_id = pl['id']
        print(f"   ✅ Gefunden: {pl['snippet']['title']} ({pl['id']})")
        break

# 2. Erstelle Playlist wenn nicht vorhanden
if not maulwurf_playlist_id:
    print("📝 Erstelle neue Playlist...")
    new_playlist = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': 'Der kleine Maulwurf | Krtek | 8K Collection',
                'description': '''🦔 Der kleine Maulwurf (Krtek) - Tschechische Zeichentrickserie von Zdeněk Miler

Diese Playlist enthält alle verfügbaren Episoden der legendären Serie "Der kleine Maulwurf" in 8K AI-Upscaling Qualität.

Die Serie wurde 1957 vom Prager Zeichner Zdeněk Miler erschaffen und in über 80 Ländern ausgestrahlt. In Deutschland bekannt durch "Die Sendung mit der Maus" und das "Sandmännchen".

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE wenn es dir gefällt!
💬 KOMMENTIERE deine Erinnerungen!
🔔 ABONNIERE für mehr Klassiker!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Mehr auf: https://frai.tv | @remAIke_IT

#DerKleineMaulwurf #Krtek #Maulwurf #ZdenekMiler #Zeichentrick #Klassiker''',
                'defaultLanguage': 'de'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
    ).execute()
    maulwurf_playlist_id = new_playlist['id']
    print(f"   ✅ Erstellt: {new_playlist['snippet']['title']} ({maulwurf_playlist_id})")

# 3. Finde alle Maulwurf-Videos (public + private)
print("\n🔍 Suche Maulwurf-Videos...")
maulwurf_videos = []
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
        
        # Nur Maulwurf-Videos
        title_lower = title.lower()
        if any(kw in title_lower for kw in ['maulwurf', 'krtek']):
            maulwurf_videos.append({
                'id': vid,
                'title': title,
                'status': status
            })
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"   Gefunden: {len(maulwurf_videos)} Maulwurf-Videos")

# 4. Prüfe welche schon in Playlist sind
print("\n🔍 Prüfe bestehende Playlist-Einträge...")
existing_in_playlist = set()
next_page = None
while True:
    try:
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=maulwurf_playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response.get('items', []):
            existing_in_playlist.add(item['snippet']['resourceId']['videoId'])
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    except:
        break

print(f"   Bereits in Playlist: {len(existing_in_playlist)}")

# 5. Füge fehlende Videos hinzu (nur PUBLIC!)
print("\n📥 Füge Videos zur Playlist hinzu...")
added = 0
skipped_private = 0
skipped_exists = 0

for v in maulwurf_videos:
    if v['id'] in existing_in_playlist:
        skipped_exists += 1
        continue
    
    if v['status'] != 'public':
        skipped_private += 1
        print(f"   ⏭️  PRIVATE: {v['title'][:40]}")
        continue
    
    try:
        youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': maulwurf_playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': v['id']
                    }
                }
            }
        ).execute()
        print(f"   ✅ Hinzugefügt: {v['title'][:45]}")
        added += 1
    except Exception as e:
        print(f"   ❌ Fehler: {v['title'][:30]} - {e}")

print("\n" + "=" * 70)
print(f"✅ Hinzugefügt: {added}")
print(f"⏭️  Übersprungen (schon drin): {skipped_exists}")
print(f"⏭️  Übersprungen (private): {skipped_private}")
print(f"\n🔗 Playlist: https://www.youtube.com/playlist?list={maulwurf_playlist_id}")
