#!/usr/bin/env python3
"""
🔄 SYNC WOCHENSCHAU PLAYLIST
============================
Stellt sicher dass alle Wochenschau-Videos in der Playlist sind
"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
SCAN_FILE = os.path.join(BASE_DIR, "config", "wochenschau_online_scan.json")

PLAYLIST_ID = 'PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg'

def load_credentials():
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
    return Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )

def main():
    print("=" * 70)
    print("🔄 SYNC WOCHENSCHAU PLAYLIST")
    print("=" * 70)
    
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Alle Videos in der Playlist holen
    print("\n📋 Checking playlist contents...")
    playlist_videos = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=PLAYLIST_ID,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response['items']:
            vid = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            playlist_videos.append({'id': vid, 'title': title})
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    print(f"   Videos in Playlist: {len(playlist_videos)}")
    
    # Lade Online-Scan
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        scan = json.load(f)
    
    online_wochenschau = [v for v in scan['videos'] if v.get('nr')]
    print(f"   Wochenschau Videos online: {len(online_wochenschau)}")
    
    online_ids = set(v['id'] for v in online_wochenschau)
    playlist_ids = set(v['id'] for v in playlist_videos)
    
    # Fehlende Videos
    missing = online_ids - playlist_ids
    if missing:
        print(f"\n⚠️  FEHLENDE VIDEOS IN PLAYLIST ({len(missing)}):")
        for v in online_wochenschau:
            if v['id'] in missing:
                print(f"   {v['id']}: Nr. {v.get('nr', '?')} - {v['title'][:50]}")
        
        # Hinzufügen
        print(f"\n➕ Füge {len(missing)} Videos zur Playlist hinzu...")
        added = 0
        for v in sorted(online_wochenschau, key=lambda x: int(x['nr']) if x['nr'] else 9999):
            if v['id'] in missing:
                try:
                    youtube.playlistItems().insert(
                        part='snippet',
                        body={
                            'snippet': {
                                'playlistId': PLAYLIST_ID,
                                'resourceId': {
                                    'kind': 'youtube#video',
                                    'videoId': v['id']
                                }
                            }
                        }
                    ).execute()
                    added += 1
                    print(f"   ✅ Nr. {v['nr']} hinzugefügt")
                except Exception as e:
                    print(f"   ❌ Nr. {v['nr']}: {str(e)[:50]}")
        
        print(f"\n   ✅ {added} Videos hinzugefügt!")
    else:
        print("\n✅ Alle Wochenschau-Videos sind bereits in der Playlist!")
    
    # Extras in Playlist?
    extras = playlist_ids - online_ids
    if extras:
        print(f"\n📌 EXTRA VIDEOS IN PLAYLIST ({len(extras)}):")
        for v in playlist_videos:
            if v['id'] in extras:
                print(f"   {v['id']}: {v['title'][:50]}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
