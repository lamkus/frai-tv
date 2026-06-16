#!/usr/bin/env python3
"""
Benennt ALLE Private Wochenschau-Videos ordentlich:
- Duplikate (schon public): "DUPE - [SEO Titel]"
- Neue: "[SEO Titel]"
VERÖFFENTLICHT NICHTS!
"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Lade OAuth
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

# Lade SEO-Datenbank
with open('config/wochenschau_complete_upload_database.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)
    db = raw.get('videos', raw)

# Lade Duplikat-Info
with open('config/wochenschau_duplicates.json', 'r', encoding='utf-8') as f:
    duplicates = json.load(f)

# Finde welche Nummern schon PUBLIC sind
public_nrs = set()
for nr, vids in duplicates.items():
    for v in vids:
        if v['status'] == 'public':
            public_nrs.add(nr)
            break

print(f"Nummern die schon PUBLIC sind: {sorted(public_nrs)}")
print("=" * 70)

# Hole alle Private Videos
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
            # Nur Wochenschau
            match = re.search(r'Nr\.?(\d{3})', title) or re.search(r'Wochenschau\s*(\d{3})', title)
            if match:
                nr = match.group(1)
                all_private.append({'id': vid, 'title': title, 'nr': nr})
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"\nGefunden: {len(all_private)} private Wochenschau-Videos\n")

# Update alle
updated = 0
skipped = 0

for v in sorted(all_private, key=lambda x: x['nr']):
    nr = v['nr']
    vid = v['id']
    old_title = v['title']
    
    # Skip wenn schon ordentlich benannt (kein STRIKE)
    if 'STRIKE' not in old_title and 'strike' not in old_title:
        print(f"⏭️  Nr.{nr} | {vid} | Schon benannt: {old_title[:40]}")
        skipped += 1
        continue
    
    # Hole SEO aus DB
    if nr not in db:
        print(f"❌ Nr.{nr} | {vid} | KEINE SEO-DATEN!")
        continue
    
    seo = db[nr]
    
    # Ist es ein Duplikat?
    is_dupe = nr in public_nrs
    
    if is_dupe:
        new_title = f"DUPE - {seo['title']}"
    else:
        new_title = seo['title']
    
    # Kürze auf max 100 Zeichen
    if len(new_title) > 100:
        new_title = new_title[:97] + "..."
    
    print(f"{'🔴 DUPE' if is_dupe else '🟢 NEU '} Nr.{nr} | {vid}")
    print(f"   ALT: {old_title[:50]}")
    print(f"   NEU: {new_title}")
    
    # Sanitize tags
    safe_tags = []
    for tag in seo.get('tags', []):
        try:
            tag.encode('ascii')
            safe_tags.append(tag)
        except UnicodeEncodeError:
            pass
    
    # API Update - NUR snippet, KEIN status!
    try:
        youtube.videos().update(
            part='snippet',
            body={
                'id': vid,
                'snippet': {
                    'title': new_title,
                    'description': seo['description'],
                    'tags': safe_tags[:15],
                    'categoryId': '27',
                    'defaultLanguage': 'de',
                    'defaultAudioLanguage': 'de'
                }
            }
        ).execute()
        print(f"   ✅ Updated!")
        updated += 1
    except Exception as e:
        print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 70)
print(f"✅ Updated: {updated}")
print(f"⏭️  Skipped (schon benannt): {skipped}")
print(f"⚠️  NICHTS VERÖFFENTLICHT - Alle bleiben PRIVATE!")
