#!/usr/bin/env python3
"""
Update Maulwurf/Krtek Drafts mit perfekter deutscher SEO.
VERÖFFENTLICHT NICHTS!
"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Offizielle deutsche Episodentitel (Wikipedia)
EPISODE_DATA = {
    '03': {
        'title_de': 'Der Maulwurf und die Rakete',
        'title_cz': 'Krtek a raketa',
        'year': 1965
    },
    '08': {
        'title_de': 'Der Maulwurf als Gärtner',
        'title_cz': 'Krtek zahradníkem',
        'year': 1969
    },
    '45': {
        'title_de': 'Der Maulwurf und der Frosch',
        'title_cz': 'Krtek a žabka',
        'year': 1998
    },
    '45b': {  # Clip version
        'title_de': 'Der Maulwurf und der Frosch (Clip)',
        'title_cz': 'Krtek a žabka',
        'year': 1998
    },
    '59': {
        'title_de': 'Der Maulwurf und die Quelle',
        'title_cz': 'Krtek a pramen',
        'year': 1999
    },
    '60': {
        'title_de': 'Der Maulwurf und die Flöte',
        'title_cz': 'Krtek a flétna',
        'year': 1999
    },
    'bonus': {
        'title_de': 'Der kleine Maulwurf im Urlaub (Mix)',
        'title_cz': 'Krtek na dovolené',
        'year': 1998
    }
}

# SEO Description Template
DESC_TEMPLATE = """🎬 {title_de} ({year}) | Krtek - Der kleine Maulwurf

Originaltitel: {title_cz}
Jahr: {year}
Serie: Der kleine Maulwurf (Krtek/Krteček)
Regisseur: Zdeněk Miler

Der kleine Maulwurf ist eine legendäre tschechische Zeichentrickserie, die 1957 vom Prager Zeichner Zdeněk Miler erschaffen wurde. Die Serie wurde in über 80 Ländern ausgestrahlt und ist in Deutschland durch "Die Sendung mit der Maus" und das "Sandmännchen" bekannt geworden.

Diese Episode wurde in 8K AI-Upscaling restauriert für bestmögliche Bildqualität.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE wenn es dir gefallen hat!
💬 KOMMENTIERE deine Erinnerungen!
🔔 ABONNIERE für mehr Klassiker!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Mehr auf: https://frai.tv | @remAIke_IT

#DerKleineMaulwurf #Krtek #Maulwurf #ZdenekMiler #Zeichentrick #Klassiker #Kindheit #Nostalgie #80er #90er #8K #Restauriert"""

# Tags für deutsche SEO
TAGS = [
    "Der kleine Maulwurf",
    "Krtek",
    "Maulwurf",
    "Zdenek Miler",
    "Zeichentrick",
    "Tschechische Animation",
    "Kinderserie",
    "Klassiker",
    "Nostalgie",
    "Sendung mit der Maus",
    "Sandmännchen",
    "8K Restauriert",
    "remAIke"
]

# OAuth Setup
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

# Finde Maulwurf Drafts
maulwurf_drafts = []
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
        if status != 'private':
            continue
            
        vid = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        title_lower = title.lower()
        
        # Nur Maulwurf
        if any(kw in title_lower for kw in ['maulwurf', 'krtek']):
            # Extrahiere Episode
            match = re.search(r'e(\d{2}[ab]?)\s', title_lower)
            if match:
                ep = match.group(1)
            elif 'bonus' in title_lower or 'urlaub' in title_lower or 'mix' in title_lower:
                ep = 'bonus'
            else:
                ep = 'unknown'
            
            maulwurf_drafts.append({
                'id': vid,
                'old_title': title,
                'episode': ep
            })
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"🦔 MAULWURF DRAFTS: {len(maulwurf_drafts)}")
print("=" * 70)

# Update alle
updated = 0
for v in maulwurf_drafts:
    ep = v['episode']
    vid = v['id']
    old_title = v['old_title']
    
    if ep not in EPISODE_DATA:
        print(f"❓ {vid} | Episode '{ep}' nicht gefunden | {old_title}")
        continue
    
    data = EPISODE_DATA[ep]
    
    # Neuer SEO Titel
    new_title = f"Der kleine Maulwurf: {data['title_de']} ({data['year']}) | 8K | @remAIke_IT"
    if len(new_title) > 100:
        new_title = f"Maulwurf: {data['title_de']} ({data['year']}) | 8K | @remAIke_IT"
    
    # Description
    description = DESC_TEMPLATE.format(
        title_de=data['title_de'],
        title_cz=data['title_cz'],
        year=data['year']
    )
    
    print(f"\n📝 Episode {ep} | {vid}")
    print(f"   ALT: {old_title[:50]}")
    print(f"   NEU: {new_title}")
    
    # API Update - NUR snippet, KEIN status!
    try:
        youtube.videos().update(
            part='snippet',
            body={
                'id': vid,
                'snippet': {
                    'title': new_title,
                    'description': description,
                    'tags': TAGS,
                    'categoryId': '1',  # Film & Animation
                    'defaultLanguage': 'de'
                }
            }
        ).execute()
        print(f"   ✅ Updated!")
        updated += 1
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 70)
print(f"✅ Updated: {updated}/{len(maulwurf_drafts)}")
print(f"⚠️  NICHTS VERÖFFENTLICHT - Alle bleiben PRIVATE!")
