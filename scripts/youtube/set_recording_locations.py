#!/usr/bin/env python3
"""
Setze Recording Location für alle Videos basierend auf historischen Daten.
YouTube Featured Places nutzt diese Daten für Geo-Search!
"""

import json
import re
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

# ============================================================================
# HISTORISCHE ORTE MAPPING
# ============================================================================

# Wochenschau: Ereignis → Koordinaten
WOCHENSCHAU_LOCATIONS = {
    # Westfront
    'frankreich': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'paris': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'dunkirk': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    'dünkirchen': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    'normandie': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    
    # Luftschlacht um England
    'england': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'london': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'britain': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'England'},
    'kanal': {'lat': 50.9, 'lng': 1.4, 'desc': 'English Channel'},
    
    # Ostfront
    'russland': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    'moskau': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'stalingrad': {'lat': 48.7080, 'lng': 44.5133, 'desc': 'Stalingrad (Volgograd), Russia'},
    'leningrad': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad (St. Petersburg), Russia'},
    'ukraine': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Ukraine'},
    'kiew': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'barbarossa': {'lat': 52.5200, 'lng': 13.4050, 'desc': 'Eastern Front'},
    
    # Afrika
    'afrika': {'lat': 32.0853, 'lng': 20.0000, 'desc': 'North Africa'},
    'rommel': {'lat': 32.0853, 'lng': 20.0000, 'desc': 'North Africa'},
    'el alamein': {'lat': 30.8333, 'lng': 28.9500, 'desc': 'El Alamein, Egypt'},
    'tobruk': {'lat': 32.0833, 'lng': 23.9500, 'desc': 'Tobruk, Libya'},
    'tunesien': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunisia'},
    
    # Mittelmeer
    'italien': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'sizilien': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'griechenland': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Greece'},
    'kreta': {'lat': 35.2401, 'lng': 24.8093, 'desc': 'Crete, Greece'},
    'balkan': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Balkans'},
    
    # Deutschland
    'berlin': {'lat': 52.5200, 'lng': 13.4050, 'desc': 'Berlin, Germany'},
    'münchen': {'lat': 48.1351, 'lng': 11.5820, 'desc': 'Munich, Germany'},
    'nürnberg': {'lat': 49.4521, 'lng': 11.0767, 'desc': 'Nuremberg, Germany'},
    'hamburg': {'lat': 53.5511, 'lng': 9.9937, 'desc': 'Hamburg, Germany'},
    'reich': {'lat': 52.5200, 'lng': 13.4050, 'desc': 'Germany'},
    'führer': {'lat': 52.5200, 'lng': 13.4050, 'desc': 'Berlin, Germany'},
    
    # Skandinavien
    'norwegen': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Norway'},
    'narvik': {'lat': 68.4385, 'lng': 17.4272, 'desc': 'Narvik, Norway'},
    'finnland': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    
    # Pazifik (selten in dt. Wochenschau)
    'japan': {'lat': 35.6762, 'lng': 139.6503, 'desc': 'Japan'},
    'pearl harbor': {'lat': 21.3643, 'lng': -157.9493, 'desc': 'Pearl Harbor, Hawaii'},
    
    # U-Boot Krieg
    'atlantik': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    'u-boot': {'lat': 54.3233, 'lng': 10.1228, 'desc': 'Kiel, Germany'},
}

# Betty Boop / Fleischer Studios
FLEISCHER_LOCATION = {'lat': 40.7128, 'lng': -74.0060, 'desc': 'New York City, USA (Fleischer Studios)'}

# Soundies - Filmed in NYC/Hollywood
SOUNDIES_LOCATIONS = {
    'default': {'lat': 40.7128, 'lng': -74.0060, 'desc': 'New York City, USA'},
    'hollywood': {'lat': 34.0928, 'lng': -118.3287, 'desc': 'Hollywood, Los Angeles, USA'},
}

# Der kleine Maulwurf - Prague
MAULWURF_LOCATION = {'lat': 50.0755, 'lng': 14.4378, 'desc': 'Prague, Czech Republic (Krátký Film Praha)'}

# Alfred J. Kwak - Netherlands/Germany
ALFRED_LOCATION = {'lat': 52.3676, 'lng': 4.9041, 'desc': 'Amsterdam, Netherlands'}

# Felix the Cat - NYC
FELIX_LOCATION = {'lat': 40.7128, 'lng': -74.0060, 'desc': 'New York City, USA'}

# Looney Tunes - Hollywood
LOONEY_LOCATION = {'lat': 34.0928, 'lng': -118.3287, 'desc': 'Hollywood, USA (Warner Bros.)'}

# Superman - Fleischer
SUPERMAN_LOCATION = {'lat': 40.7128, 'lng': -74.0060, 'desc': 'New York City, USA (Fleischer Studios)'}


def find_wochenschau_location(title, description):
    """Finde den historischen Ort für Wochenschau-Videos."""
    text = (title + ' ' + description).lower()
    
    # Priorität: Spezifische Orte zuerst
    priority_keywords = [
        'stalingrad', 'el alamein', 'tobruk', 'dunkirk', 'dünkirchen',
        'moskau', 'leningrad', 'kiew', 'narvik', 'pearl harbor',
        'paris', 'london', 'berlin', 'münchen', 'nürnberg'
    ]
    
    for kw in priority_keywords:
        if kw in text:
            return WOCHENSCHAU_LOCATIONS[kw]
    
    # Dann allgemeine Regionen
    for kw, loc in WOCHENSCHAU_LOCATIONS.items():
        if kw in text:
            return loc
    
    # Default: Berlin (Produktionsort)
    return {'lat': 52.5200, 'lng': 13.4050, 'desc': 'Berlin, Germany'}


def determine_location(title, description):
    """Bestimme Location basierend auf Video-Typ."""
    title_lower = title.lower()
    
    # Wochenschau
    if 'wochenschau' in title_lower or 'newsreel' in title_lower:
        return find_wochenschau_location(title, description)
    
    # Maulwurf
    if 'maulwurf' in title_lower or 'krtek' in title_lower:
        return MAULWURF_LOCATION
    
    # Alfred J. Kwak
    if 'alfred' in title_lower and ('kwak' in title_lower or 'quack' in title_lower):
        return ALFRED_LOCATION
    
    # Betty Boop
    if 'betty boop' in title_lower:
        return FLEISCHER_LOCATION
    
    # Soundies
    if 'soundie' in title_lower:
        return SOUNDIES_LOCATIONS['default']
    
    # Felix
    if 'felix' in title_lower and 'cat' in title_lower:
        return FELIX_LOCATION
    
    # Superman / Fleischer
    if 'superman' in title_lower or 'fleischer' in title_lower:
        return SUPERMAN_LOCATION
    
    # Looney Tunes
    if any(x in title_lower for x in ['looney', 'merrie melodies', 'bugs bunny', 'daffy']):
        return LOONEY_LOCATION
    
    return None


# ============================================================================
# MAIN
# ============================================================================

print("=" * 70)
print("🌍 RECORDING LOCATION UPDATE")
print("=" * 70)

# Hole alle Videos
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

print(f"📹 {len(all_videos)} Videos gefunden")

# Hole Details und update
video_ids = [v['snippet']['resourceId']['videoId'] for v in all_videos]
updated = 0
skipped = 0
no_location = 0

for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    
    response = youtube.videos().list(
        part='snippet,recordingDetails,status',
        id=','.join(batch)
    ).execute()
    
    for video in response['items']:
        vid = video['id']
        title = video['snippet']['title']
        desc = video['snippet'].get('description', '')
        status = video['status']['privacyStatus']
        
        # Überspringe private Videos
        if status == 'private':
            skipped += 1
            continue
        
        # Prüfe ob schon Location gesetzt
        existing_loc = video.get('recordingDetails', {}).get('location')
        if existing_loc and existing_loc.get('latitude'):
            skipped += 1
            continue
        
        # Bestimme Location
        location = determine_location(title, desc)
        
        if not location:
            no_location += 1
            continue
        
        # Update
        try:
            youtube.videos().update(
                part='recordingDetails',
                body={
                    'id': vid,
                    'recordingDetails': {
                        'location': {
                            'latitude': location['lat'],
                            'longitude': location['lng']
                        },
                        'locationDescription': location['desc']
                    }
                }
            ).execute()
            print(f"✅ {title[:45]:45} → {location['desc']}")
            updated += 1
        except Exception as e:
            print(f"❌ {title[:30]}: {e}")

print("\n" + "=" * 70)
print(f"✅ Updated: {updated}")
print(f"⏭️  Skipped (private/already set): {skipped}")
print(f"❓ No location mapping: {no_location}")
print("=" * 70)
