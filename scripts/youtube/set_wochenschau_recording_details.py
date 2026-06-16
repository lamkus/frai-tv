#!/usr/bin/env python3
"""
Set Recording Locations & Dates für Wochenschau-Videos
Verwendet das vollständige Location-Mapping

WICHTIG: Quota-Verbrauch ~50 Units pro Video!
         252 Videos = 12.600 Units (braucht 2 Tage)
"""

import json
import os
import sys
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# === CONFIG ===
OAUTH_FILE = 'config/youtube_oauth.json'
LOCATIONS_FILE = 'config/wochenschau_complete_locations.json'
BATCH_SIZE = 200  # Pro Tag
DRY_RUN = '--apply' not in sys.argv

def load_credentials():
    """Lädt OAuth Credentials"""
    if not os.path.exists(OAUTH_FILE):
        print(f"❌ {OAUTH_FILE} nicht gefunden!")
        sys.exit(1)
    
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    
    return Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

def load_locations():
    """Lädt Location-Mapping"""
    with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_video_id_mapping(youtube, playlist_id='PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg'):
    """
    Holt Video-IDs aus der Wochenschau-Playlist
    Mappt Nr. → Video-ID basierend auf Titel
    """
    video_map = {}
    next_page = None
    
    print("📥 Lade Videos aus Playlist...")
    
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        )
        response = request.execute()
        
        for item in response.get('items', []):
            title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']
            
            # Extrahiere Nr. aus Titel: "Wochenschau: ... (Nr. XXX)"
            import re
            match = re.search(r'Nr\.\s*(\d+)', title)
            if match:
                nr = match.group(1)
                video_map[nr] = {
                    'video_id': video_id,
                    'title': title
                }
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    print(f"   ✅ {len(video_map)} Videos gefunden")
    return video_map

def set_recording_details(youtube, video_id, location, date_str, dry_run=True):
    """
    Setzt Recording Location und Date für ein Video
    
    Args:
        location: {'lat': float, 'lng': float, 'desc': str}
        date_str: 'YYYY-MM-DD'
    """
    if dry_run:
        return {'status': 'dry_run', 'video_id': video_id}
    
    try:
        # Hole aktuelle Video-Details
        video = youtube.videos().list(
            part='recordingDetails,snippet',
            id=video_id
        ).execute()
        
        if not video.get('items'):
            return {'status': 'not_found', 'video_id': video_id}
        
        # Update Recording Details
        update_body = {
            'id': video_id,
            'recordingDetails': {
                'location': {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'altitude': 0
                },
                'locationDescription': location['desc'],
                'recordingDate': date_str
            }
        }
        
        youtube.videos().update(
            part='recordingDetails',
            body=update_body
        ).execute()
        
        return {'status': 'success', 'video_id': video_id}
        
    except Exception as e:
        return {'status': 'error', 'video_id': video_id, 'error': str(e)}

def main():
    print("=" * 70)
    print("🎬 WOCHENSCHAU RECORDING DETAILS UPDATER")
    print("=" * 70)
    
    if DRY_RUN:
        print("\n⚠️  DRY RUN MODE - Keine Änderungen!")
        print("    Für echte Updates: python script.py --apply\n")
    else:
        print("\n🔴 LIVE MODE - Änderungen werden gespeichert!\n")
    
    # Lade Daten
    locations = load_locations()
    print(f"📍 {len(locations)} Episoden mit Locations geladen")
    
    if not DRY_RUN:
        creds = load_credentials()
        youtube = build('youtube', 'v3', credentials=creds)
        video_map = get_video_id_mapping(youtube)
    else:
        video_map = {}
        print("📍 (Video-IDs werden im Live-Modus geladen)")
    
    # Statistik
    results = {
        'success': 0,
        'error': 0,
        'skipped': 0,
        'dry_run': 0
    }
    
    # Batch-Verarbeitung
    processed = 0
    for nr, data in sorted(locations.items(), key=lambda x: int(x[0])):
        if processed >= BATCH_SIZE:
            print(f"\n⏸️  Batch-Limit ({BATCH_SIZE}) erreicht. Morgen weitermachen!")
            break
        
        location = data['location']
        date_str = data['date']
        event = data['event_en']
        
        if DRY_RUN:
            print(f"   [DRY] Nr. {nr}: {event} → {location['desc']} ({date_str})")
            results['dry_run'] += 1
        else:
            if nr not in video_map:
                print(f"   [SKIP] Nr. {nr}: Nicht in Playlist")
                results['skipped'] += 1
                continue
            
            video_id = video_map[nr]['video_id']
            result = set_recording_details(youtube, video_id, location, date_str, dry_run=False)
            
            if result['status'] == 'success':
                print(f"   [OK] Nr. {nr}: {event} → {location['desc']}")
                results['success'] += 1
            else:
                print(f"   [ERR] Nr. {nr}: {result.get('error', 'Unknown')}")
                results['error'] += 1
        
        processed += 1
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"   Verarbeitet: {processed}")
    if DRY_RUN:
        print(f"   Dry-Run:     {results['dry_run']}")
    else:
        print(f"   Erfolgreich: {results['success']}")
        print(f"   Fehler:      {results['error']}")
        print(f"   Übersprungen:{results['skipped']}")
    
    remaining = len(locations) - processed
    if remaining > 0:
        print(f"\n⏳ Noch {remaining} Videos verbleibend für nächsten Batch")
        print(f"   Geschätzte Quota: {remaining * 50} Units")

if __name__ == '__main__':
    main()
