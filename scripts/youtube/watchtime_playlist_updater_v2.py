#!/usr/bin/env python3
"""
WATCHTIME PLAYLIST UPDATER v2 - QUOTA-SPAREND!
===============================================
REGEL: NIEMALS per API löschen! User macht das im Studio.

Workflow:
1. Script zeigt welche Videos FEHLEN in der Playlist
2. User löscht manuell im Studio (0 Quota)
3. Script fügt nur NEUE Videos hinzu (50 Units/Video)
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

# Playlist IDs - MIT SEO-OPTIMIERTEN TITELN
EXISTING_PLAYLISTS = {
    'betty_boop_chronological': {
        'id': 'PL3d2Tsr13ihMNCgAFrHLvjx4YIoDCcx-o',
        'title': '💋 Betty Boop - Complete Series (1930-1939) | 8K Restored'
    },
    'alfred_quack_chronological': {
        'id': 'PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL',
        'title': '🦆 Alfred J. Kwak / Quack - Alle Folgen (1-52) | Deutsch | 8K'  # SEO: Kwak + Quack!
    },
    'superman_chronological': {
        'id': 'PL3d2Tsr13ihNGGfilho9PHb3gqsOrhksr',
        'title': '🦸 Superman Fleischer - All 17 Episodes (1941-1943) | 8K'
    },
    'casper_chronological': {
        'id': 'PL3d2Tsr13ihNlMyu7m1gUrorwDsPL0Szf',
        'title': '👻 Casper - Complete Collection | 8K Restored'
    },
    'porky_looney': {
        'id': 'PL3d2Tsr13ihNXcCH2-a7VZUyJS-Do8Sn0',
        'title': '🐷 Porky Pig & Looney Tunes | 8K Restored'
    },
    'german_series_complete': {
        'id': 'PL3d2Tsr13ihPD7KZc4zP8KqNJzy1paDgL',
        'title': '🇩🇪 Deutsche Zeichentrickserien | Komplett | 8K'
    },
    'kids_watchtime': {
        'id': 'PL3d2Tsr13ihPSHCGv48UqQqZ5DbFupIZk',
        'title': '👶 For Kids - Easy Start | 8K Cartoons'
    },
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
    
    if creds.expired or not creds.valid:
        print("🔄 Token abgelaufen, refreshe...")
        creds.refresh(Request())
        oauth_data['token'] = creds.token
        oauth_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
        with open(OAUTH_FILE, 'w') as f:
            json.dump(oauth_data, f)
        print("✅ Token refreshed")
    
    return build('youtube', 'v3', credentials=creds)


def get_playlist_items(youtube, playlist_id):
    """Get all video IDs currently in playlist - ONLY 1 UNIT per 50 videos!"""
    video_ids = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='contentDetails',  # Minimal - nur videoId!
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    return video_ids


def add_video_to_playlist(youtube, playlist_id, video_id, position=None):
    """Add video to playlist - 50 UNITS!"""
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
        youtube.playlistItems().insert(part='snippet', body=body).execute()
        return True
    except HttpError as e:
        if 'duplicate' in str(e).lower():
            return 'duplicate'
        elif 'videoNotFound' in str(e) or 'Video not found' in str(e):
            print(f"   ⚠️ Video {video_id} nicht gefunden")
            return False
        elif 'quotaExceeded' in str(e):
            print(f"   🛑 QUOTA ERSCHÖPFT - Abbruch!")
            return 'quota'
        else:
            print(f"   ❌ Fehler: {e}")
            return False


def analyze_playlist(youtube, playlist_key, playlist_config, target_video_ids):
    """Analyze what needs to be done - READ ONLY!"""
    playlist_id = playlist_config['id']
    
    print(f"\n{'─'*60}")
    print(f"📋 {playlist_config['title'][:55]}")
    print(f"   ID: {playlist_id}")
    
    # Get current state (1 Unit per 50 videos)
    current_ids = get_playlist_items(youtube, playlist_id)
    current_set = set(current_ids)
    target_set = set(target_video_ids)
    
    # Calculate differences
    missing = [vid for vid in target_video_ids if vid not in current_set]
    extra = [vid for vid in current_ids if vid not in target_set]
    
    # Check order (if same videos)
    order_correct = current_ids == target_video_ids if len(missing) == 0 and len(extra) == 0 else None
    
    print(f"   Aktuell: {len(current_ids)} Videos")
    print(f"   Ziel: {len(target_video_ids)} Videos")
    print(f"   ➕ Fehlen: {len(missing)}")
    print(f"   ➖ Zu viel: {len(extra)}")
    
    if order_correct is True:
        print(f"   ✅ Reihenfolge korrekt!")
    elif order_correct is False:
        print(f"   ⚠️ Reihenfolge stimmt nicht")
    
    return {
        'playlist_key': playlist_key,
        'playlist_id': playlist_id,
        'title': playlist_config['title'],
        'current': current_ids,
        'target': target_video_ids,
        'missing': missing,
        'extra': extra,
        'order_correct': order_correct,
    }


def main():
    print('╔═══════════════════════════════════════════════════════════════╗')
    print('║  🎯 WATCHTIME PLAYLIST UPDATER v2 - QUOTA-SPAREND!            ║')
    print('║  KEINE API-DELETES! User löscht manuell im Studio.            ║')
    print('╚═══════════════════════════════════════════════════════════════╝')
    
    import sys
    args = sys.argv[1:]
    analyze_only = '--analyze' in args
    add_missing = '--add' in args
    playlist_filter = None
    for arg in args:
        if arg.startswith('--playlist='):
            playlist_filter = arg.split('=')[1]
    
    if not analyze_only and not add_missing:
        print("\n📖 USAGE:")
        print("   --analyze         Zeige was zu tun ist (read-only)")
        print("   --add             Füge fehlende Videos hinzu")
        print("   --playlist=KEY    Nur diese Playlist bearbeiten")
        print("\n   Beispiel: python watchtime_playlist_updater_v2.py --analyze")
        print("             python watchtime_playlist_updater_v2.py --add --playlist=alfred_quack_chronological")
        return
    
    # Load config
    with open(WATCHTIME_FILE, 'r', encoding='utf-8') as f:
        watchtime_data = json.load(f)
    
    playlists = watchtime_data.get('playlists', {})
    
    # Connect
    print("\n🔗 Verbinde mit YouTube API...")
    youtube = get_youtube_client()
    print("✅ Verbunden")
    
    analyses = []
    
    # Analyze each playlist
    for playlist_key, playlist_data in playlists.items():
        if playlist_key not in EXISTING_PLAYLISTS:
            continue
        if playlist_filter and playlist_key != playlist_filter:
            continue
        
        analysis = analyze_playlist(
            youtube,
            playlist_key,
            EXISTING_PLAYLISTS[playlist_key],
            playlist_data.get('video_ids', [])
        )
        analyses.append(analysis)
    
    # Summary
    print('\n' + '═'*65)
    print('  📊 ANALYSE ERGEBNIS')
    print('═'*65)
    
    total_missing = sum(len(a['missing']) for a in analyses)
    total_extra = sum(len(a['extra']) for a in analyses)
    
    print(f"\n   ➕ Gesamt fehlend: {total_missing} Videos")
    print(f"   ➖ Gesamt zu viel: {total_extra} Videos")
    print(f"\n   💰 Quota für INSERT: {total_missing * 50} Units")
    
    if total_extra > 0:
        print(f"\n   ⚠️ MANUELLE AKTION NÖTIG:")
        print(f"   Öffne YouTube Studio und lösche {total_extra} Videos aus Playlists:")
        for a in analyses:
            if a['extra']:
                print(f"      - {a['title'][:40]}: {len(a['extra'])} Videos entfernen")
                # Show which videos
                for vid in a['extra'][:5]:
                    print(f"         https://youtu.be/{vid}")
                if len(a['extra']) > 5:
                    print(f"         ... und {len(a['extra'])-5} weitere")
    
    # Add missing if requested
    if add_missing and total_missing > 0:
        print(f"\n🚀 FÜGE {total_missing} FEHLENDE VIDEOS HINZU...")
        
        added = 0
        failed = 0
        quota_hit = False
        
        for analysis in analyses:
            if not analysis['missing'] or quota_hit:
                continue
            
            print(f"\n   📋 {analysis['title'][:45]}...")
            
            for i, video_id in enumerate(analysis['missing']):
                result = add_video_to_playlist(youtube, analysis['playlist_id'], video_id)
                
                if result == 'quota':
                    quota_hit = True
                    break
                elif result == True:
                    added += 1
                elif result == 'duplicate':
                    pass  # Already there, skip
                else:
                    failed += 1
                
                if (i + 1) % 10 == 0:
                    print(f"      ... {i+1}/{len(analysis['missing'])}")
        
        print(f"\n   ✅ Hinzugefügt: {added}")
        print(f"   ❌ Fehlgeschlagen: {failed}")
        if quota_hit:
            print(f"   🛑 Quota erreicht - Rest morgen nach 09:00 MEZ")
    
    elif analyze_only:
        print(f"\n   ℹ️ Analyse-Modus. Um Videos hinzuzufügen:")
        print(f"      python watchtime_playlist_updater_v2.py --add")


if __name__ == '__main__':
    main()
