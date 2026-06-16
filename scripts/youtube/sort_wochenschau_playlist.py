#!/usr/bin/env python3
"""
Sort Wochenschau playlist chronologically by episode number.
"""
import json
import re
import requests
from pathlib import Path

OAUTH_FILE = Path("config/youtube_oauth.json")
PLAYLIST_ID = "PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg"

def refresh_token():
    with open(OAUTH_FILE, 'r') as f:
        oauth = json.load(f)
    resp = requests.post(oauth['token_uri'], data={
        'client_id': oauth['client_id'],
        'client_secret': oauth['client_secret'],
        'refresh_token': oauth['refresh_token'],
        'grant_type': 'refresh_token'
    })
    if resp.status_code == 200:
        return resp.json()['access_token']
    return oauth.get('token')

def get_playlist_items(token):
    headers = {'Authorization': f'Bearer {token}'}
    items = []
    page_token = None
    
    while True:
        params = {'part': 'snippet', 'playlistId': PLAYLIST_ID, 'maxResults': 50}
        if page_token:
            params['pageToken'] = page_token
        resp = requests.get('https://www.googleapis.com/youtube/v3/playlistItems', 
                          params=params, headers=headers)
        data = resp.json()
        items.extend(data.get('items', []))
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    return items

def extract_sort_key(title):
    """Extract sortable key from title."""
    # Wochenschau Nr. XXX
    match = re.search(r'[Nn]r\.?\s*(\d+)', title)
    if match:
        return (0, int(match.group(1)))  # Wochenschau: sort by number
    
    # Other newsreels - sort by year in title
    year_match = re.search(r'\((\d{4})', title)
    if year_match:
        return (1, int(year_match.group(1)))  # Other: sort by year
    
    return (2, 9999)  # Unknown: at end

def move_playlist_item(token, item_id, new_position):
    """Move a playlist item to new position."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    body = {
        'id': item_id,
        'snippet': {
            'playlistId': PLAYLIST_ID,
            'position': new_position,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': ''  # Will be filled from existing
            }
        }
    }
    
    # First get the video ID
    resp = requests.get(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        params={'part': 'snippet', 'id': item_id},
        headers={'Authorization': f'Bearer {token}'}
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get('items'):
            body['snippet']['resourceId']['videoId'] = data['items'][0]['snippet']['resourceId']['videoId']
    
    resp = requests.put(
        'https://www.googleapis.com/youtube/v3/playlistItems',
        params={'part': 'snippet'},
        headers=headers,
        json=body
    )
    
    return resp.status_code == 200

def main():
    print("🔄 WOCHENSCHAU PLAYLIST SORTIEREN")
    print("=" * 60)
    
    token = refresh_token()
    
    # Get all items
    print("\n📋 Lade Playlist...")
    items = get_playlist_items(token)
    print(f"   {len(items)} Videos gefunden")
    
    # Create sortable list
    sortable = []
    for item in items:
        title = item['snippet']['title']
        sort_key = extract_sort_key(title)
        sortable.append({
            'id': item['id'],
            'title': title,
            'sort_key': sort_key,
            'current_pos': item['snippet']['position']
        })
    
    # Sort by key
    sortable.sort(key=lambda x: x['sort_key'])
    
    # Show planned order
    print("\n📋 GEPLANTE REIHENFOLGE:")
    print("-" * 60)
    for i, item in enumerate(sortable):
        key_type = "Wochenschau" if item['sort_key'][0] == 0 else "Other"
        nr_or_year = item['sort_key'][1]
        current = item['current_pos']
        status = "✅" if current == i else "🔄"
        print(f"  {status} Pos {i:2d} (war {current:2d}): {item['title'][:50]}...")
    
    # Count moves needed
    moves = [(i, item) for i, item in enumerate(sortable) if item['current_pos'] != i]
    print(f"\n📊 {len(moves)} Videos müssen verschoben werden")
    
    if not moves:
        print("✅ Playlist ist bereits sortiert!")
        return
    
    # Apply moves
    print(f"\n🔄 Sortiere Playlist...")
    print(f"   💰 Quota: ~{len(moves) * 50} Units")
    
    success = 0
    failed = 0
    
    # Move items one by one, starting from position 0
    for new_pos, item in enumerate(sortable):
        if item['current_pos'] == new_pos:
            continue
        
        print(f"   Moving '{item['title'][:30]}...' to position {new_pos}")
        if move_playlist_item(token, item['id'], new_pos):
            success += 1
            print(f"      ✅")
        else:
            failed += 1
            print(f"      ❌")
    
    print(f"\n{'='*60}")
    print(f"✅ FERTIG: {success} verschoben, {failed} fehlgeschlagen")

if __name__ == '__main__':
    main()
