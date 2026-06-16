#!/usr/bin/env python3
"""Manage Wochenschau playlist - add missing, remove non-Wochenschau, sort chronologically."""
import requests
import json
import re
import sys
from pathlib import Path

PLAYLIST_ID = 'PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg'
UPLOADS_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
OAUTH_FILE = Path('config/youtube_oauth.json')

def get_token():
    with open(OAUTH_FILE, 'r') as f:
        oauth = json.load(f)
    resp = requests.post(oauth['token_uri'], data={
        'client_id': oauth['client_id'],
        'client_secret': oauth['client_secret'],
        'refresh_token': oauth['refresh_token'],
        'grant_type': 'refresh_token'
    })
    return resp.json()['access_token']

def extract_nr(title):
    match = re.search(r'[Nn]r\.?\s*(\d+)|#(\d+)', title)
    if match:
        return int(match.group(1) or match.group(2))
    return None

def get_all_wochenschau_videos(token):
    """Get all Wochenschau videos from channel uploads."""
    headers = {'Authorization': f'Bearer {token}'}
    videos = []
    page_token = None
    
    while True:
        params = {'part': 'snippet,contentDetails', 'playlistId': UPLOADS_PL, 'maxResults': 50}
        if page_token:
            params['pageToken'] = page_token
        resp = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', params=params, headers=headers)
        data = resp.json()
        for item in data.get('items', []):
            title = item['snippet']['title']
            nr = extract_nr(title)
            if nr and 'wochenschau' in title.lower():
                videos.append({
                    'video_id': item['contentDetails']['videoId'],
                    'title': title,
                    'nr': nr
                })
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    
    return sorted(videos, key=lambda x: x['nr'])

def get_playlist_items(token):
    """Get all items currently in playlist."""
    headers = {'Authorization': f'Bearer {token}'}
    items = []
    page_token = None
    
    while True:
        params = {'part': 'snippet,contentDetails', 'playlistId': PLAYLIST_ID, 'maxResults': 50}
        if page_token:
            params['pageToken'] = page_token
        resp = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', params=params, headers=headers)
        data = resp.json()
        for item in data.get('items', []):
            items.append({
                'playlist_item_id': item['id'],
                'video_id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'position': item['snippet']['position'],
                'nr': extract_nr(item['snippet']['title'])
            })
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    
    return items

def add_video_to_playlist(token, video_id, position):
    """Add video to playlist at position."""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = {
        'snippet': {
            'playlistId': PLAYLIST_ID,
            'resourceId': {'kind': 'youtube#video', 'videoId': video_id},
            'position': position
        }
    }
    resp = requests.post(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        params={'part': 'snippet'},
        headers=headers,
        json=body
    )
    return resp.status_code == 200

def move_to_position(token, playlist_item_id, video_id, position):
    """Move item to new position in playlist."""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = {
        'id': playlist_item_id,
        'snippet': {
            'playlistId': PLAYLIST_ID,
            'resourceId': {'kind': 'youtube#video', 'videoId': video_id},
            'position': position
        }
    }
    resp = requests.put(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        params={'part': 'snippet'},
        headers=headers,
        json=body
    )
    return resp.status_code == 200

def remove_from_playlist(token, playlist_item_id):
    """Remove item from playlist."""
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.delete(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        params={'id': playlist_item_id},
        headers=headers
    )
    return resp.status_code == 204

def update_playlist_metadata(token):
    """Update playlist title and description."""
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    title = "Die Deutsche Wochenschau 1939-1945 | WWII German Newsreels | 8K Restored"
    description = """📽️ DIE DEUTSCHE WOCHENSCHAU (1939-1945) | Complete WWII German Newsreel Collection | 8K HQ

⚠️ HISTORICAL DOCUMENTS – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🎬 The complete German wartime newsreel series "Die Deutsche Wochenschau" restored in stunning 8K quality. Original propaganda footage from the Bundesarchiv (German Federal Archives).

🇩🇪 Die komplette Sammlung der Deutschen Wochenschau von 1939-1945 in 8K Qualität restauriert. Original NS-Propaganda aus dem Bundesarchiv - nur zu Bildungszwecken.

📅 CHRONOLOGICAL ORDER / CHRONOLOGISCHE REIHENFOLGE:
• 1939: Kriegsausbruch, Polen, Winterkrieg
• 1940: Westfeldzug, Dünkirchen, Paris, Luftschlacht um England
• 1941: Balkan, Barbarossa, Ostfront, Pearl Harbor
• 1942: Stalingrad, Nordafrika, El Alamein
• 1943: Stalingrad-Kapitulation, Kursk, Italien
• 1944: D-Day, Bagration, 20. Juli, Ardennen
• 1945: Weichsel-Oder, Dresden, Endkampf

🔍 KEYWORDS: Deutsche Wochenschau, German Newsreel, WWII, World War 2, Nazi Germany, Wehrmacht, Third Reich, Propaganda, Eastern Front, Western Front, D-Day, Stalingrad, Barbarossa

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE for historical archives! 🔔 SUBSCRIBE @remAIke_IT
📺 https://frai.tv | @remAIke_IT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#Wochenschau #WWII #WW2 #Wehrmacht #NaziGermany #HistoricalFootage #Bundesarchiv #8K"""
    
    body = {
        'id': PLAYLIST_ID,
        'snippet': {
            'title': title,
            'description': description
        }
    }
    
    resp = requests.put(
        'https://www.googleapis.com/youtube/v3/playlists',
        params={'part': 'snippet'},
        headers=headers,
        json=body
    )
    return resp.status_code == 200

def main():
    apply_mode = '--apply' in sys.argv
    
    print("🔍 Analyzing Wochenschau Playlist...")
    token = get_token()
    
    # Get all Wochenschau videos on channel
    all_videos = get_all_wochenschau_videos(token)
    print(f"\n📺 Wochenschau videos on channel: {len(all_videos)}")
    
    # Get current playlist items
    playlist_items = get_playlist_items(token)
    playlist_video_ids = {item['video_id'] for item in playlist_items}
    
    # Find Wochenschau videos in playlist
    wochenschau_in_playlist = [item for item in playlist_items if item['nr'] is not None and 'wochenschau' in item['title'].lower()]
    non_wochenschau = [item for item in playlist_items if item['nr'] is None or 'wochenschau' not in item['title'].lower()]
    
    print(f"📋 Current playlist: {len(playlist_items)} items")
    print(f"   - Wochenschau: {len(wochenschau_in_playlist)}")
    print(f"   - Other (will move to end): {len(non_wochenschau)}")
    
    # Find missing videos
    missing = [v for v in all_videos if v['video_id'] not in playlist_video_ids]
    
    if missing:
        print(f"\n❌ MISSING from playlist ({len(missing)}):")
        for v in missing:
            print(f"   Nr. {v['nr']}: {v['title'][:50]}")
    
    if non_wochenschau:
        print(f"\n📌 WILL MOVE TO END ({len(non_wochenschau)}):")
        for item in non_wochenschau:
            print(f"   {item['title'][:50]}")
    
    # Show planned order
    print(f"\n📋 PLANNED ORDER:")
    print("--- WOCHENSCHAU (chronological) ---")
    for i, v in enumerate(all_videos):
        status = "✓" if v['video_id'] in playlist_video_ids else "+"
        print(f"  {i+1:2}. Nr. {v['nr']:3} [{status}] {v['title'][:45]}")
    
    print(f"--- OTHER HISTORICAL DOCS (at end) ---")
    for i, item in enumerate(non_wochenschau):
        print(f"  {len(all_videos)+i+1:2}. {item['title'][:50]}")
    
    if not apply_mode:
        total_final = len(all_videos) + len(non_wochenschau)
        print(f"\n⚠️ DRY RUN")
        print(f"   - Will add {len(missing)} missing Wochenschau videos")
        print(f"   - Will move {len(non_wochenschau)} other videos to end")
        print(f"   - Will update playlist metadata")
        print(f"   - Final playlist size: {total_final} videos")
        print(f"\n💡 Run with --apply to make changes")
        return
    
    # Apply changes
    print(f"\n🚀 APPLYING CHANGES...")
    
    # 1. Add missing Wochenschau videos at their chronological position
    for v in missing:
        # Find correct position based on Nr
        position = 0
        for i, vid in enumerate(all_videos):
            if vid['nr'] < v['nr']:
                position = i + 1
            else:
                break
        print(f"➕ Adding Nr. {v['nr']} at position {position}...")
        if add_video_to_playlist(token, v['video_id'], position):
            print(f"   ✅ Added")
        else:
            print(f"   ❌ Failed")
    
    # 2. Move non-Wochenschau videos to end
    # First need to refresh playlist to get updated positions
    playlist_items = get_playlist_items(token)
    final_position = len(all_videos)  # After all Wochenschau videos
    
    for item in playlist_items:
        is_wochenschau = item['nr'] is not None and 'wochenschau' in item['title'].lower()
        if not is_wochenschau:
            print(f"📌 Moving to end: {item['title'][:40]}...")
            if move_to_position(token, item['playlist_item_id'], item['video_id'], final_position):
                print(f"   ✅ Moved to position {final_position}")
                final_position += 1
            else:
                print(f"   ❌ Failed")
    
    # 3. Update playlist metadata
    print(f"\n📝 Updating playlist metadata...")
    if update_playlist_metadata(token):
        print(f"   ✅ Metadata updated!")
    else:
        print(f"   ❌ Failed")
    
    print(f"\n✅ Done! Playlist organized: {len(all_videos)} Wochenschau (chronological) + {len(non_wochenschau)} other docs")

if __name__ == '__main__':
    main()
