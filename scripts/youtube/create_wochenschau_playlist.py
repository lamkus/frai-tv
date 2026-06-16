#!/usr/bin/env python3
"""Erstellt Wochenschau-Playlist und bereitet Draft-Updates vor."""
import json, sys, io
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth laden
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Wochenschau Videos laden
wochenschau = json.loads(Path('config/wochenschau_videos.json').read_text(encoding='utf-8'))

print("=" * 60)
print("🎬 WOCHENSCHAU PLAYLIST SETUP")
print("=" * 60)

# 1. Playlist-Beschreibung (trilingual)
PLAYLIST_TITLE = "Deutsche Wochenschau | Historisches Archiv | 8K"
PLAYLIST_DESC = """🇩🇪 Deutsche Wochenschau - Historisches Archivmaterial in 8K

Originale Kino-Wochenschauen aus dem Deutschen Reich (1933-1945) sowie internationale Newsreels der Ära. Diese Sammlung dient der historischen Dokumentation und Bildung.

⚠️ HINWEIS: Enthält zeitgenössisches Propagandamaterial.
Dieses Material wird in seinem historischen Kontext gezeigt.

🇬🇧 German Newsreels - Historical archive footage in 8K

Original cinema newsreels from Germany (1933-1945) and international newsreels of the era. This collection serves historical documentation and education purposes.

⚠️ NOTE: Contains contemporary propaganda material.
This footage is presented in its historical context.

🇪🇸 Noticieros Alemanes - Material de archivo histórico en 8K

Noticieros cinematográficos originales de Alemania (1933-1945) y noticieros internacionales de la época.

⚠️ AVISO: Contiene material de propaganda contemporáneo.

Public Domain • 8K restauriert • @remAIke_IT
www.FRai.TV

#Wochenschau #Newsreel #WWIIHistory #Archive #8K"""

print(f"\n📋 Erstelle Playlist: {PLAYLIST_TITLE}")

# Playlist erstellen
try:
    pl_response = youtube.playlists().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': PLAYLIST_TITLE,
                'description': PLAYLIST_DESC,
                'defaultLanguage': 'de'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
    ).execute()
    
    playlist_id = pl_response['id']
    print(f"✅ Playlist erstellt: {playlist_id}")
    print(f"   URL: https://www.youtube.com/playlist?list={playlist_id}")
except Exception as e:
    print(f"❌ Fehler: {e}")
    playlist_id = None

# 2. Draft-Titel-Fixes vorbereiten
print("\n" + "=" * 60)
print("📝 DRAFT-TITEL FIXES")
print("=" * 60)

draft_fixes = []
for v in wochenschau:
    if v['status'] == 'private':
        old_title = v['title']
        # Parse: "1945 01 25 wochenschau nr 750 sls 8K HQ"
        import re
        match = re.search(r'(\d{4})\s*(\d{2})\s*(\d{2}).*?nr\s*(\d+)', old_title, re.I)
        if match:
            year, month, day, nr = match.groups()
            new_title = f"Die Deutsche Wochenschau Nr. {nr} | {day}.{month}.{year} | Germany WWII Newsreel | 8K HQ | @remAIke_IT"
            
            # Neue Beschreibung
            new_desc = f"""WE HAVE THE BEST VERSION FOR YOU!
SHARE AND PUSH US TO GET THE WHOLE INTERNET UPGRADED :)

@remAIke_IT | www.remAIke.IT
www.FRai.TV - All videos organized....

DE:
Die Deutsche Wochenschau Nr. {nr} vom {day}.{month}.{year}.
Originale Kino-Wochenschau aus Deutschland mit zeitgenössischem Bild- und Tonmaterial.
Diese Ausgabe zeigt Ereignisse und Darstellungen aus dem Jahr {year},
so wie sie damals öffentlich gezeigt wurden.

⚠️ Historisches Archivmaterial - dient der Dokumentation und Bildung.

EN:
German Weekly Newsreel No. {nr}, dated {month}/{day}/{year}.
Original theatrical newsreel footage with contemporary image and sound material.
This edition documents events and visual reporting of {year}
as presented to cinema audiences at the time.

⚠️ Historical archive material - for documentation and educational purposes.

ES:
Noticiero Semanal Alemán Nr. {nr}, fechado {day}/{month}/{year}.
Material de archivo cinematográfico original con imágenes y sonido de la época.

⚠️ Material de archivo histórico - con fines documentales y educativos.

8K HQ Edition:
• stabilized archival source
• enhanced clarity for modern displays
• original visual and audio character preserved

LIKE • COMMENT • SUBSCRIBE @remAIke_IT
Explore more historical archives on www.FRai.TV

#Wochenschau #GermanNewsreel #WWIIHistory #{year} #ArchiveFootage #HistoricalFilm 
#Zeitgeschichte #WorldHistory #Europe{year} #8K #remAIke"""
            
            draft_fixes.append({
                'id': v['id'],
                'old_title': old_title,
                'new_title': new_title,
                'new_description': new_desc
            })
            
            print(f"\n🔧 {v['id']}")
            print(f"   ALT:  {old_title}")
            print(f"   NEU:  {new_title}")

# 3. Speichern
result = {
    'created_at': datetime.now().isoformat(),
    'playlist': {
        'id': playlist_id,
        'title': PLAYLIST_TITLE,
        'url': f"https://www.youtube.com/playlist?list={playlist_id}" if playlist_id else None
    },
    'videos': {
        'public': [v for v in wochenschau if v['status'] == 'public'],
        'drafts_to_fix': draft_fixes
    },
    'total_videos': len(wochenschau),
    'public_count': len([v for v in wochenschau if v['status'] == 'public']),
    'draft_count': len(draft_fixes)
}

out = Path('config/wochenschau_playlist_final.json')
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')

print("\n" + "=" * 60)
print("📊 ZUSAMMENFASSUNG")
print("=" * 60)
print(f"✅ Playlist erstellt: {playlist_id}")
print(f"📺 Public Videos: {result['public_count']}")
print(f"📝 Drafts zu fixen: {result['draft_count']}")
print(f"💾 Gespeichert: {out}")

# 4. Videos zur Playlist hinzufügen (nur public)
if playlist_id:
    print("\n" + "=" * 60)
    print("➕ FÜGE PUBLIC VIDEOS ZUR PLAYLIST HINZU")
    print("=" * 60)
    
    public_videos = [v for v in wochenschau if v['status'] == 'public']
    for v in public_videos:
        try:
            youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': v['id']
                        }
                    }
                }
            ).execute()
            print(f"   ✅ {v['title'][:50]}...")
        except Exception as e:
            print(f"   ❌ {v['id']}: {e}")
    
    print(f"\n✅ {len(public_videos)} Videos zur Playlist hinzugefügt")
