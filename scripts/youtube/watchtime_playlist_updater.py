#!/usr/bin/env python3
"""
WATCHTIME PLAYLIST UPDATER
==========================
Aktualisiert YouTube Playlists basierend auf Watchtime-Optimierung.

VERWENDET OAuth für WRITE-Operationen!
"""

import json
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_DIR = 'd:/remaike.TV/config'
OAUTH_FILE = f'{CONFIG_DIR}/youtube_oauth.json'
WATCHTIME_FILE = f'{CONFIG_DIR}/watchtime_playlists.json'

# Playlist IDs (existierende Playlists auf dem Kanal)
EXISTING_PLAYLISTS = {
    'betty_boop_chronological': 'PL3d2Tsr13ihMNCgAFrHLvjx4YIoDCcx-o',  # Betty Boop Jazz Age
    'alfred_quack_chronological': 'PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL',  # Alfred Quack
    'superman_chronological': 'PL3d2Tsr13ihNGGfilho9PHb3gqsOrhksr',  # Superman
    'casper_chronological': 'PL3d2Tsr13ihNlMyu7m1gUrorwDsPL0Szf',  # Casper
    'porky_looney': 'PL3d2Tsr13ihNXcCH2-a7VZUyJS-Do8Sn0',  # Porky Pig
    'german_series_complete': 'PL3d2Tsr13ihPD7KZc4zP8KqNJzy1paDgL',  # Deutsche Klassiker
    'kids_watchtime': 'PL3d2Tsr13ihPSHCGv48UqQqZ5DbFupIZk',  # For Kids
}


def get_youtube_client():
    """Get authenticated YouTube client with auto-refresh"""
    with open(OAUTH_FILE, 'r') as f:
        oauth_data = json.load(f)
    
    creds = Credentials(
        token=oauth_data.get('token'),
        refresh_token=oauth_data.get('refresh_token'),
        token_uri=oauth_data.get('token_uri'),
        client_id=oauth_data.get('client_id'),
        client_secret=oauth_data.get('client_secret'),
        scopes=oauth_data.get('scopes'),
    )
    
    # Refresh if expired
    if creds.expired or not creds.valid:
        print("🔄 Token abgelaufen, refreshe...")
        creds.refresh(Request())
        
        # Save refreshed token
        oauth_data['token'] = creds.token
        oauth_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
        with open(OAUTH_FILE, 'w') as f:
            json.dump(oauth_data, f)
        print("✅ Token refreshed und gespeichert")
    
    return build('youtube', 'v3', credentials=creds)


def get_playlist_items(youtube, playlist_id):
    """Get all videos currently in playlist"""
    items = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response.get('items', []):
            items.append({
                'id': item['id'],
                'videoId': item['contentDetails']['videoId'],
                'position': item['snippet']['position'],
            })
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    return items


def clear_playlist(youtube, playlist_id):
    """Remove all items from playlist"""
    items = get_playlist_items(youtube, playlist_id)
    
    for item in items:
        try:
            youtube.playlistItems().delete(id=item['id']).execute()
        except HttpError as e:
            print(f"   ⚠️ Fehler beim Löschen: {e}")
    
    return len(items)


def add_video_to_playlist(youtube, playlist_id, video_id, position=None):
    """Add video to playlist at specific position"""
    body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id,
            },
        }
    }
    
    if position is not None:
        body['snippet']['position'] = position
    
    try:
        youtube.playlistItems().insert(
            part='snippet',
            body=body
        ).execute()
        return True
    except HttpError as e:
        if 'Video not found' in str(e) or 'videoNotFound' in str(e):
            print(f"   ⚠️ Video {video_id} nicht gefunden (evtl. gelöscht)")
        else:
            print(f"   ❌ Fehler: {e}")
        return False


def reorder_playlist(youtube, playlist_id, video_ids, playlist_name):
    """Reorder playlist to match video_ids order"""
    print(f"\n{'─'*60}")
    print(f"📋 {playlist_name}")
    print(f"   Playlist ID: {playlist_id}")
    print(f"   Ziel: {len(video_ids)} Videos in optimierter Reihenfolge")
    
    # Get current items
    current_items = get_playlist_items(youtube, playlist_id)
    current_video_ids = [item['videoId'] for item in current_items]
    
    print(f"   Aktuell: {len(current_items)} Videos")
    
    # Check if order is already correct
    if current_video_ids == video_ids:
        print(f"   ✅ Reihenfolge bereits korrekt!")
        return {'status': 'unchanged', 'videos': len(video_ids)}
    
    # Strategy: Clear and re-add in correct order
    # (More quota but guarantees correct order)
    print(f"   🔄 Lösche {len(current_items)} Videos...")
    cleared = clear_playlist(youtube, playlist_id)
    
    print(f"   ➕ Füge {len(video_ids)} Videos in optimierter Reihenfolge hinzu...")
    added = 0
    failed = 0
    
    for i, video_id in enumerate(video_ids):
        success = add_video_to_playlist(youtube, playlist_id, video_id, position=i)
        if success:
            added += 1
        else:
            failed += 1
        
        # Progress every 10 videos
        if (i + 1) % 10 == 0:
            print(f"      ... {i+1}/{len(video_ids)} Videos")
    
    print(f"   ✅ Fertig: {added} hinzugefügt, {failed} fehlgeschlagen")
    
    return {'status': 'updated', 'added': added, 'failed': failed}


def main():
    print('╔═══════════════════════════════════════════════════════════════╗')
    print('║  🎯 WATCHTIME PLAYLIST UPDATER                                ║')
    print('║  Aktualisiere YouTube Playlists für maximale Watch Time       ║')
    print('╚═══════════════════════════════════════════════════════════════╝')
    
    # Parse args
    import sys
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    playlist_filter = None
    for arg in args:
        if arg.startswith('--playlist='):
            playlist_filter = arg.split('=')[1]
    
    print(f"\n📋 Modus: {'DRY-RUN' if dry_run else '🔥 LIVE'}")
    
    # Load watchtime config
    with open(WATCHTIME_FILE, 'r', encoding='utf-8') as f:
        watchtime_data = json.load(f)
    
    playlists = watchtime_data.get('playlists', {})
    print(f"   {len(playlists)} Playlists konfiguriert")
    
    if dry_run:
        print("\n⚠️ DRY-RUN Modus - keine Änderungen werden durchgeführt")
        for pid, pdata in playlists.items():
            if pid in EXISTING_PLAYLISTS:
                print(f"\n   📋 {pdata['title'][:45]}...")
                print(f"      Videos: {pdata['video_count']}")
                print(f"      Watch Time: {pdata['total_duration_formatted']}")
        return
    
    # Connect to YouTube
    print("\n🔗 Verbinde mit YouTube API...")
    youtube = get_youtube_client()
    print("✅ Verbunden")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'updated': [],
        'skipped': [],
        'failed': [],
    }
    
    # Update each playlist
    for playlist_key, playlist_data in playlists.items():
        # Check if we have this playlist mapped
        if playlist_key not in EXISTING_PLAYLISTS:
            print(f"\n⏭️ Überspringe {playlist_key} (keine Playlist-ID gemappt)")
            results['skipped'].append({'key': playlist_key, 'reason': 'not_mapped'})
            continue
        
        # Filter if specified
        if playlist_filter and playlist_key != playlist_filter:
            continue
        
        playlist_id = EXISTING_PLAYLISTS[playlist_key]
        video_ids = playlist_data.get('video_ids', [])
        
        if not video_ids:
            print(f"\n⏭️ Überspringe {playlist_key} (keine Videos)")
            continue
        
        try:
            result = reorder_playlist(
                youtube, 
                playlist_id, 
                video_ids, 
                playlist_data['title']
            )
            results['updated'].append({
                'key': playlist_key,
                'playlist_id': playlist_id,
                **result
            })
        except Exception as e:
            print(f"\n❌ Fehler bei {playlist_key}: {e}")
            results['failed'].append({'key': playlist_key, 'error': str(e)})
    
    # Summary
    print('\n' + '═'*65)
    print('  📊 ERGEBNIS')
    print('═'*65)
    print(f"\n   ✅ Aktualisiert: {len(results['updated'])}")
    print(f"   ⏭️ Übersprungen: {len(results['skipped'])}")
    print(f"   ❌ Fehlgeschlagen: {len(results['failed'])}")
    
    # Save log
    log_path = f'{CONFIG_DIR}/playlist_update_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n   📄 Log: {log_path}")


if __name__ == '__main__':
    main()
