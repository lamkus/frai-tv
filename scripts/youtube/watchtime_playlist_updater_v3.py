#!/usr/bin/env python3
"""
WATCHTIME PLAYLIST UPDATER v3 - QUOTA-KORREKT!
==============================================
✅ PUBLIC API für READ (eigenes Quota!)
✅ OAuth NUR für WRITE
❌ KEINE API-DELETES - User macht das im Studio (0 Quota)
"""

import json
import os
import requests
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_DIR = 'd:/remaike.TV/config'
OAUTH_FILE = f'{CONFIG_DIR}/youtube_oauth.json'
WATCHTIME_FILE = f'{CONFIG_DIR}/watchtime_playlists.json'

# ✅ PUBLIC API KEY - must come from env (do not hardcode secrets)
API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    raise RuntimeError('Missing env var: YOUTUBE_API_KEY')
YT_API_BASE = 'https://youtube.googleapis.com/youtube/v3'

# Playlist IDs - MIT SEO-OPTIMIERTEN TITELN
EXISTING_PLAYLISTS = {
    'betty_boop_chronological': {
        'id': 'PL3d2Tsr13ihMNCgAFrHLvjx4YIoDCcx-o',
        'title': '💋 Betty Boop - Complete Series (1930-1939) | 8K Restored'
    },
    'alfred_quack_chronological': {
        'id': 'PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL',
        'title': '🦆 Alfred J. Kwak / Quack - Alle 52 Folgen | Deutsch | 8K'
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


def get_playlist_items_PUBLIC(playlist_id):
    """
    ✅ PUBLIC API für READ - Separates Quota!
    Kostet 1 Unit pro 50 Videos aus PUBLIC Quota.
    """
    video_ids = []
    next_page = None
    
    while True:
        params = {
            'part': 'contentDetails',
            'playlistId': playlist_id,
            'maxResults': 50,
            'key': API_KEY,
        }
        if next_page:
            params['pageToken'] = next_page
        
        response = requests.get(f'{YT_API_BASE}/playlistItems', params=params)
        
        if response.status_code == 403:
            data = response.json()
            if 'quotaExceeded' in str(data):
                print("   🛑 PUBLIC API Quota erschöpft!")
                return None
            raise Exception(f"API Error: {data}")
        
        response.raise_for_status()
        data = response.json()
        
        for item in data.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page = data.get('nextPageToken')
        if not next_page:
            break
    
    return video_ids


def get_oauth_client():
    """OAuth Client NUR für WRITE-Operationen!"""
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
        print("🔄 OAuth Token refreshe...")
        creds.refresh(Request())
        oauth_data['token'] = creds.token
        oauth_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
        with open(OAUTH_FILE, 'w') as f:
            json.dump(oauth_data, f)
        print("✅ OAuth Token refreshed")
    
    return build('youtube', 'v3', credentials=creds)


def add_video_to_playlist(youtube, playlist_id, video_id, position=None):
    """WRITE-Operation - 50 Units OAuth Quota"""
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
        err = str(e)
        if 'duplicate' in err.lower() or 'videoAlreadyInPlaylist' in err:
            return 'duplicate'
        elif 'videoNotFound' in err:
            print(f"   ⚠️ Video {video_id} nicht gefunden")
            return False
        elif 'quotaExceeded' in err:
            print(f"   🛑 OAUTH QUOTA ERSCHÖPFT!")
            return 'quota'
        else:
            print(f"   ❌ Fehler: {e}")
            return False


def analyze_playlist(playlist_key, playlist_config, target_video_ids):
    """Analyse mit PUBLIC API - kein OAuth Quota verbraucht!"""
    playlist_id = playlist_config['id']
    
    print(f"\n{'─'*60}")
    print(f"📋 {playlist_config['title'][:55]}")
    print(f"   ID: {playlist_id}")
    
    # ✅ PUBLIC API für READ!
    current_ids = get_playlist_items_PUBLIC(playlist_id)
    
    if current_ids is None:
        return {'error': 'quota'}
    
    current_set = set(current_ids)
    target_set = set(target_video_ids)
    
    missing = [vid for vid in target_video_ids if vid not in current_set]
    extra = [vid for vid in current_ids if vid not in target_set]
    
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
    print('║  🎯 WATCHTIME PLAYLIST UPDATER v3                             ║')
    print('║  ✅ Public API für READ | OAuth nur für WRITE                 ║')
    print('║  ❌ Keine API-Deletes - User löscht im Studio (0 Quota)       ║')
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
        print("   --analyze         Zeige Status (PUBLIC API, kein OAuth Quota)")
        print("   --add             Füge fehlende Videos hinzu (OAuth WRITE)")
        print("   --playlist=KEY    Nur diese Playlist")
        print("\n   Beispiel:")
        print("   python watchtime_playlist_updater_v3.py --analyze")
        print("   python watchtime_playlist_updater_v3.py --add --playlist=alfred_quack_chronological")
        return
    
    # Load config
    with open(WATCHTIME_FILE, 'r', encoding='utf-8') as f:
        watchtime_data = json.load(f)
    
    playlists = watchtime_data.get('playlists', {})
    
    print(f"\n📊 {len(playlists)} Playlists in Config")
    print(f"🔑 API Key: {API_KEY[:15]}... (Public API für READ)")
    
    analyses = []
    
    # Analyze with PUBLIC API
    for playlist_key, playlist_data in playlists.items():
        if playlist_key not in EXISTING_PLAYLISTS:
            continue
        if playlist_filter and playlist_key != playlist_filter:
            continue
        
        analysis = analyze_playlist(
            playlist_key,
            EXISTING_PLAYLISTS[playlist_key],
            playlist_data.get('video_ids', [])
        )
        
        if 'error' in analysis:
            print("\n🛑 Quota-Problem - Abbruch")
            break
        
        analyses.append(analysis)
    
    # Summary
    print('\n' + '═'*65)
    print('  📊 ANALYSE ERGEBNIS (via Public API)')
    print('═'*65)
    
    total_missing = sum(len(a['missing']) for a in analyses)
    total_extra = sum(len(a['extra']) for a in analyses)
    
    print(f"\n   ➕ Gesamt fehlend: {total_missing} Videos")
    print(f"   ➖ Gesamt zu viel: {total_extra} Videos")
    print(f"\n   💰 Quota für INSERT: {total_missing * 50} Units (OAuth)")
    
    if total_extra > 0:
        print(f"\n   ⚠️ MANUELLE AKTION NÖTIG (0 Quota im Studio!):")
        for a in analyses:
            if a['extra']:
                print(f"\n   📋 {a['title'][:40]}")
                print(f"      ➖ {len(a['extra'])} Videos entfernen:")
                for vid in a['extra'][:5]:
                    print(f"         https://youtu.be/{vid}")
                if len(a['extra']) > 5:
                    print(f"         ... und {len(a['extra'])-5} weitere")
    
    # Add missing if requested
    if add_missing and total_missing > 0:
        print(f"\n🚀 FÜGE {total_missing} FEHLENDE VIDEOS HINZU (OAuth)...")
        
        youtube = get_oauth_client()
        
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
                    pass
                else:
                    failed += 1
                
                if (i + 1) % 10 == 0:
                    print(f"      ... {i+1}/{len(analysis['missing'])}")
        
        print(f"\n   ✅ Hinzugefügt: {added}")
        print(f"   ❌ Fehlgeschlagen: {failed}")
        if quota_hit:
            print(f"   🛑 OAuth Quota erschöpft - Rest morgen nach 09:00 MEZ")
    
    elif analyze_only:
        print(f"\n   ℹ️ Analyse-Modus (Public API - kein OAuth verbraucht)")
        print(f"   Zum Hinzufügen: python watchtime_playlist_updater_v3.py --add")


if __name__ == '__main__':
    main()
