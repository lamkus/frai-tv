#!/usr/bin/env python3
"""
Soundie Renamer - Benennt alle unformatierten Soundies korrekt um
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth laden
with open('config/youtube_oauth.json', 'r') as f:
    oauth_data = json.load(f)

creds = Credentials(
    token=oauth_data['token'],
    refresh_token=oauth_data['refresh_token'],
    token_uri=oauth_data['token_uri'],
    client_id=oauth_data['client_id'],
    client_secret=oauth_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Die 7 unformatierten Soundies mit korrekten Song-Titeln
TO_RENAME = [
    {
        'id': 'gB_KUOpsNnM', 
        'old': 'soundie   heaven help a sailor on a night like thi sls 8K HQ', 
        'song': 'Heaven Help a Sailor on a Night Like This'
    },
    {
        'id': '2yGX3wy-4SQ', 
        'old': 'soundie   havana madrid show sls 8K HQ', 
        'song': 'Havana Madrid Show'
    },
    {
        'id': 'HvwtRYp43eU', 
        'old': 'soundie   got to be this or that sls 8K HQ', 
        'song': 'Got to Be This or That'
    },
    {
        'id': 'LJp-M01OI-8', 
        'old': 'soundie   chime bells sls 8K HQ', 
        'song': 'Chime Bells'
    },
    {
        'id': 'hIsTWWP-YkQ', 
        'old': 'soundie   once in a while sls 8K HQ', 
        'song': 'Once in a While'
    },
    {
        'id': 'D-LL4VuR5Pg', 
        'old': 'soundie   lullaby of broadway sls 8K HQ', 
        'song': 'Lullaby of Broadway'
    },
    {
        'id': 'mReDNz-Exdk', 
        'old': 'soundie   lamp of memory sls 8K HQ', 
        'song': 'Lamp of Memory'
    },
]

# Soundie SEO Description Template
DESCRIPTION_TEMPLATE = """🎵 {song_title}

📅 Original Soundie aus den 1940er Jahren
🎬 Remastered in 8K HQ (4K UHD) by remAIke

═══════════════════════════════════════════════
🎬 WAS SIND SOUNDIES?
═══════════════════════════════════════════════

Soundies waren kurze Musikfilme (3-4 Minuten), die von 1940-1947 für spezielle Musikautomaten namens "Panoram" produziert wurden. Diese Jukebox-ähnlichen Geräte standen in Bars, Restaurants und Nachtclubs in den USA.

🎹 GENRE: Vintage Music / Jazz / Swing

═══════════════════════════════════════════════
📺 MEHR AUF DIESEM KANAL
═══════════════════════════════════════════════

🎵 Alle Soundies: https://www.youtube.com/playlist?list=PLxxxxxxxxx
🎬 Channel: https://www.youtube.com/@remAIke_IT

👍 LIKE & SUBSCRIBE für mehr Vintage Music!

#Soundie #VintageMusic #1940s #Jazz #Swing #ClassicMusic #PublicDomain #8K #remAIke
"""

# Soundie Tags
SOUNDIE_TAGS = [
    "soundie", "soundies", "1940s", "1940s music", "vintage music",
    "jazz", "swing", "big band", "classic music", "public domain",
    "8K", "4K UHD", "AI upscaled", "remastered", "retro", "nostalgia",
    "panoram", "jukebox", "music video", "remAIke"
]

print("=" * 80)
print("SOUNDIE RENAMER - 7 Videos umbenennen")
print("=" * 80)
print()

for s in TO_RENAME:
    new_title = f"Soundie: {s['song']} | 8K HQ (4K UHD) | Vintage Music Film | @remAIke_IT"
    print(f"ID: {s['id']}")
    print(f"  ALT:  {s['old']}")
    print(f"  NEU:  {new_title}")
    print()

print("=" * 80)
print("Starte Umbenennung...")
print("=" * 80)
print()

success = 0
failed = 0

for s in TO_RENAME:
    video_id = s['id']
    new_title = f"Soundie: {s['song']} | 8K HQ (4K UHD) | Vintage Music Film | @remAIke_IT"
    new_description = DESCRIPTION_TEMPLATE.format(song_title=s['song'])
    
    # Hole aktuellen Stand
    try:
        response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            print(f"❌ {video_id}: Nicht gefunden")
            failed += 1
            continue
        
        item = response['items'][0]
        snippet = item['snippet']
        
        # Update
        snippet['title'] = new_title
        snippet['description'] = new_description
        snippet['tags'] = SOUNDIE_TAGS + [s['song']]
        snippet['categoryId'] = '10'  # Music
        
        youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        print(f"✅ {video_id}: {s['song']}")
        success += 1
        
    except Exception as e:
        print(f"❌ {video_id}: Fehler - {e}")
        failed += 1

print()
print("=" * 80)
print(f"ERGEBNIS: {success} erfolgreich, {failed} fehlgeschlagen")
print("=" * 80)
