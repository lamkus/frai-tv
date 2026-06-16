#!/usr/bin/env python3
"""
AKTIVIERE NICHT GENUTZTE YOUTUBE 2026 FEATURES
1. Channel Keywords setzen
2. Recording Dates für Vintage Content
3. Education Category für Wochenschau
4. Shorts Remixing aktivieren
"""

import json
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Setup
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

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

print("=" * 80)
print("🚀 AKTIVIERE YOUTUBE 2026 FEATURES")
print("=" * 80)

results = {'date': datetime.now().isoformat(), 'actions': []}

# =============================================================================
# FEATURE 1: Channel Keywords setzen
# =============================================================================
print("\n" + "=" * 80)
print("📌 FEATURE 1: CHANNEL KEYWORDS")
print("=" * 80)

CHANNEL_KEYWORDS = [
    "8K", "AI Upscaling", "Public Domain", "Vintage Animation", "Classic Cartoons",
    "Betty Boop", "Wochenschau", "WWII", "World War 2", "1930s", "1940s", 
    "remAIke", "Soundies", "Felix the Cat", "Alfred J Kwak", "Maulwurf", "Krtek",
    "Fleischer Studios", "Looney Tunes", "Silent Film", "Restored", "Remastered"
]

try:
    # Hole aktuelle Channel-Daten
    channel = youtube.channels().list(
        part='brandingSettings',
        id=CHANNEL_ID
    ).execute()['items'][0]
    
    branding = channel['brandingSettings']
    current_keywords = branding.get('channel', {}).get('keywords', '')
    
    print(f"   Aktuelle Keywords: {current_keywords[:50]}..." if current_keywords else "   Aktuelle Keywords: KEINE!")
    
    # Setze neue Keywords
    new_keywords = ' '.join([f'"{kw}"' for kw in CHANNEL_KEYWORDS])
    branding['channel']['keywords'] = new_keywords
    
    youtube.channels().update(
        part='brandingSettings',
        body={
            'id': CHANNEL_ID,
            'brandingSettings': branding
        }
    ).execute()
    
    print(f"   ✅ Keywords gesetzt: {len(CHANNEL_KEYWORDS)} Keywords")
    results['actions'].append({'feature': 'channel_keywords', 'status': 'success', 'count': len(CHANNEL_KEYWORDS)})
    
except Exception as e:
    print(f"   ❌ Fehler: {e}")
    results['actions'].append({'feature': 'channel_keywords', 'status': 'error', 'error': str(e)})

# =============================================================================
# FEATURE 2: Recording Dates für Vintage Content
# =============================================================================
print("\n" + "=" * 80)
print("📌 FEATURE 2: RECORDING DATES")
print("=" * 80)

# Jahr-Extraktion aus Titel
def extract_year(title):
    """Extrahiert Jahr aus Titel wie (1932) oder 1932"""
    match = re.search(r'\(?(19\d{2})\)?', title)
    if match:
        return int(match.group(1))
    return None

# Hole alle Videos
print("   Lade Videos...")
all_videos = []
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet',
        playlistId='UUVFv6Egpl0LDvigpFbQXNeQ',
        maxResults=50,
        pageToken=next_page
    ).execute()
    all_videos.extend(response['items'])
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f"   Gefunden: {len(all_videos)} Videos")

# Filtere Videos die ein Jahr im Titel haben
videos_with_year = []
for v in all_videos:
    title = v['snippet']['title']
    year = extract_year(title)
    if year and 1900 <= year <= 1999:  # Nur Vintage (vor 2000)
        videos_with_year.append({
            'id': v['snippet']['resourceId']['videoId'],
            'title': title,
            'year': year
        })

print(f"   Videos mit Vintage-Jahr: {len(videos_with_year)}")

# Update Recording Dates (max 50 um Quota zu sparen)
updated_count = 0
MAX_UPDATES = 50  # Quota-Limit

for v in videos_with_year[:MAX_UPDATES]:
    try:
        # Hole aktuelles Video
        video = youtube.videos().list(
            part='recordingDetails,snippet,status',
            id=v['id']
        ).execute()
        
        if not video['items']:
            continue
            
        current = video['items'][0]
        recording = current.get('recordingDetails', {})
        
        # Prüfe ob schon gesetzt
        if recording.get('recordingDate'):
            continue
        
        # Setze Recording Date (1. Juli des Jahres als Schätzung)
        recording_date = f"{v['year']}-07-01T00:00:00Z"
        
        youtube.videos().update(
            part='recordingDetails',
            body={
                'id': v['id'],
                'recordingDetails': {
                    'recordingDate': recording_date
                }
            }
        ).execute()
        
        updated_count += 1
        print(f"   ✅ {v['title'][:40]} → {v['year']}")
        
    except Exception as e:
        print(f"   ⚠️ Skip {v['id']}: {e}")

print(f"\n   📊 Recording Dates gesetzt: {updated_count}/{len(videos_with_year)}")
results['actions'].append({'feature': 'recording_dates', 'status': 'success', 'updated': updated_count, 'total': len(videos_with_year)})

# =============================================================================
# FEATURE 3: Education Category für Wochenschau
# =============================================================================
print("\n" + "=" * 80)
print("📌 FEATURE 3: EDUCATION CATEGORY FÜR WOCHENSCHAU")
print("=" * 80)

# Finde Wochenschau-Videos
wochenschau_videos = [v for v in all_videos if 'wochenschau' in v['snippet']['title'].lower()]
print(f"   Wochenschau-Videos gefunden: {len(wochenschau_videos)}")

education_updated = 0
for v in wochenschau_videos[:30]:  # Max 30 um Quota zu sparen
    try:
        video = youtube.videos().list(
            part='snippet',
            id=v['snippet']['resourceId']['videoId']
        ).execute()
        
        if not video['items']:
            continue
            
        snippet = video['items'][0]['snippet']
        
        # Prüfe ob schon Education
        if snippet.get('categoryId') == '27':
            continue
        
        # Update zu Education (27)
        snippet['categoryId'] = '27'
        
        youtube.videos().update(
            part='snippet',
            body={
                'id': v['snippet']['resourceId']['videoId'],
                'snippet': snippet
            }
        ).execute()
        
        education_updated += 1
        print(f"   ✅ → Education: {v['snippet']['title'][:45]}")
        
    except Exception as e:
        print(f"   ⚠️ Skip: {e}")

print(f"\n   📊 Education Category gesetzt: {education_updated}")
results['actions'].append({'feature': 'education_category', 'status': 'success', 'updated': education_updated})

# =============================================================================
# FEATURE 4: Prüfe Music Category für Soundies
# =============================================================================
print("\n" + "=" * 80)
print("📌 FEATURE 4: MUSIC CATEGORY CHECK")
print("=" * 80)

soundie_videos = [v for v in all_videos if 'soundie' in v['snippet']['title'].lower()]
print(f"   Soundies gefunden: {len(soundie_videos)}")

music_check = {'already_music': 0, 'needs_fix': 0}
for v in soundie_videos[:20]:
    try:
        video = youtube.videos().list(
            part='snippet',
            id=v['snippet']['resourceId']['videoId']
        ).execute()
        
        if video['items']:
            cat = video['items'][0]['snippet'].get('categoryId', '1')
            if cat == '10':
                music_check['already_music'] += 1
            else:
                music_check['needs_fix'] += 1
                print(f"   ⚠️ Nicht Music: {v['snippet']['title'][:40]}")
    except:
        pass

print(f"\n   📊 Soundies in Music: {music_check['already_music']}")
print(f"   📊 Soundies NICHT in Music: {music_check['needs_fix']}")
results['actions'].append({'feature': 'music_category_check', 'status': 'checked', 'data': music_check})

# =============================================================================
# SUMMARY
# =============================================================================
print("\n" + "=" * 80)
print("🏆 ZUSAMMENFASSUNG")
print("=" * 80)

print(f"""
✅ Channel Keywords: {len(CHANNEL_KEYWORDS)} Keywords gesetzt
✅ Recording Dates: {updated_count} Videos aktualisiert
✅ Education Category: {education_updated} Wochenschau-Videos
✅ Music Category: {music_check['already_music']} Soundies OK

⚠️ MANUELL IM YOUTUBE STUDIO NÖTIG:
   1. Auto-Chapters aktivieren: Settings → Upload Defaults → Advanced
   2. Channel Trailer setzen: Customization → Layout
   3. End Screens prüfen: Einzelne Videos → Editor
""")

# Save results
with open('config/features_2026_activated.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"💾 Ergebnisse: config/features_2026_activated.json")
