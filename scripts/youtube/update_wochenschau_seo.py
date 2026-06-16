#!/usr/bin/env python3
"""
Update Wochenschau videos SEO on YouTube.
1. Scan current videos via OAuth API
2. Compare with optimized metadata
3. Create pending_updates JSON
4. Apply updates with --apply flag
"""
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# Paths
CONFIG_DIR = Path("config")
UPLOAD_DATA = CONFIG_DIR / "wochenschau_upload_data.json"
PENDING_UPDATES = CONFIG_DIR / "pending_updates"
OAUTH_FILE = CONFIG_DIR / "youtube_oauth.json"

# YouTube API
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOADS_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"  # Uploads playlist

def refresh_oauth_token():
    """Refresh OAuth token if needed."""
    with open(OAUTH_FILE, 'r') as f:
        data = json.load(f)
    
    # Try to refresh
    resp = requests.post(
        data['token_uri'],
        data={
            'client_id': data['client_id'],
            'client_secret': data['client_secret'],
            'refresh_token': data['refresh_token'],
            'grant_type': 'refresh_token'
        }
    )
    
    if resp.status_code == 200:
        new_token = resp.json()
        data['token'] = new_token['access_token']
        with open(OAUTH_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return data['token']
    else:
        print(f"❌ Token refresh failed: {resp.status_code}")
        return data.get('token')

def get_oauth_token():
    """Load OAuth token for API operations."""
    if not OAUTH_FILE.exists():
        print("❌ OAuth file not found!")
        return None
    
    # Always refresh to ensure valid token
    return refresh_oauth_token()

def search_wochenschau_videos():
    """Find all Wochenschau videos via playlist scan."""
    print("🔍 Scanning YouTube for Wochenschau videos...")
    
    token = get_oauth_token()
    if not token:
        return []
    
    headers = {'Authorization': f'Bearer {token}'}
    videos = []
    page_token = None
    
    # Get all videos from uploads playlist
    while True:
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': UPLOADS_PLAYLIST,
            'maxResults': 50
        }
        if page_token:
            params['pageToken'] = page_token
            
        resp = requests.get(
            'https://www.googleapis.com/youtube/v3/playlistItems',
            params=params,
            headers=headers
        )
        
        if resp.status_code != 200:
            print(f"❌ Playlist API error: {resp.status_code}")
            print(resp.text)
            break
            
        data = resp.json()
        
        for item in data.get('items', []):
            title = item['snippet']['title']
            video_id = item['contentDetails']['videoId']
            # Filter for Wochenschau videos
            if 'wochenschau' in title.lower():
                videos.append({
                    'id': video_id,
                    'title': title
                })
        
        page_token = data.get('nextPageToken')
        if not page_token:
            break
    
    print(f"✅ Found {len(videos)} Wochenschau videos")
    return videos

def get_video_details(video_ids):
    """Get full video details via OAuth API."""
    print(f"📋 Fetching details for {len(video_ids)} videos...")
    
    token = get_oauth_token()
    if not token:
        return []
    
    headers = {'Authorization': f'Bearer {token}'}
    details = []
    
    # Process in batches of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        
        params = {
            'part': 'snippet,statistics',
            'id': ','.join(batch)
        }
        
        resp = requests.get(
            'https://www.googleapis.com/youtube/v3/videos',
            params=params,
            headers=headers
        )
        
        if resp.status_code != 200:
            print(f"❌ Videos API error: {resp.status_code}")
            continue
            
        data = resp.json()
        
        for item in data.get('items', []):
            details.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'tags': item['snippet'].get('tags', []),
                'categoryId': item['snippet'].get('categoryId', ''),
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0))
            })
    
    return details

def extract_wochenschau_nr(title):
    """Extract Wochenschau number from title."""
    import re
    # Try patterns like "Nr. 516", "Nr 516", "#516", "nr516" (draft format)
    match = re.search(r'[Nn]r\.?\s*(\d+)|#(\d+)', title)
    if match:
        return match.group(1) or match.group(2)
    return None

def load_optimized_data():
    """Load optimized metadata from generated file."""
    with open(UPLOAD_DATA, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Index by video_nr
    return {item['video_nr']: item for item in data}

def compare_and_create_updates(current_videos, optimized_data):
    """Compare current vs optimized and create update list."""
    updates = []
    
    for video in current_videos:
        nr = extract_wochenschau_nr(video['title'])
        if not nr:
            print(f"⚠️ Could not extract Nr from: {video['title']}")
            continue
            
        if nr not in optimized_data:
            print(f"⚠️ No optimized data for Nr. {nr}")
            continue
            
        opt = optimized_data[nr]
        
        # Check what needs updating
        changes = []
        
        # Title check (SHORT format is better)
        if video['title'] != opt['title']:
            changes.append({
                'field': 'title',
                'current': video['title'],
                'optimized': opt['title']
            })
        
        # Description check
        if video['description'] != opt['description']:
            # Check if current description is missing key elements
            has_cta = 'LIKE' in video['description'] and 'SUBSCRIBE' in video['description']
            has_multilang = '🇺🇸' in video['description'] and '🇪🇸' in video['description']
            has_events = len(video['description']) > 500
            
            if not (has_cta and has_multilang and has_events):
                changes.append({
                    'field': 'description',
                    'current_preview': video['description'][:200] + '...',
                    'optimized_preview': opt['description'][:200] + '...',
                    'full_optimized': opt['description']
                })
        
        # Tags check
        current_tags = set(video.get('tags', []))
        opt_tags = set(opt['tags'])
        if current_tags != opt_tags:
            changes.append({
                'field': 'tags',
                'current': list(current_tags),
                'optimized': opt['tags']
            })
        
        if changes:
            updates.append({
                'video_id': video['id'],
                'video_nr': nr,
                'current_title': video['title'],
                'views': video['views'],
                'likes': video['likes'],
                'changes': changes,
                'optimized_title': opt['title'],
                'optimized_description': opt['description'],
                'optimized_tags': opt['tags'],
                'optimized_category': opt['category']
            })
    
    return updates

def apply_updates(updates):
    """Apply SEO updates via YouTube API."""
    token = get_oauth_token()
    if not token:
        print("❌ No OAuth token available!")
        return
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    success = 0
    failed = 0
    
    for update in updates:
        print(f"\n🔄 Updating Nr. {update['video_nr']} ({update['video_id']})...")
        
        # Build update body
        body = {
            'id': update['video_id'],
            'snippet': {
                'title': update['optimized_title'],
                'description': update['optimized_description'],
                'tags': update['optimized_tags'],
                'categoryId': update['optimized_category']
            }
        }
        
        resp = requests.put(
            'https://www.googleapis.com/youtube/v3/videos',
            params={'part': 'snippet'},
            headers=headers,
            json=body
        )
        
        if resp.status_code == 200:
            print(f"   ✅ Updated successfully!")
            success += 1
        else:
            print(f"   ❌ Failed: {resp.status_code}")
            print(f"   {resp.text[:200]}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS: {success} updated, {failed} failed")
    print(f"💰 Quota used: ~{success * 50} units")

def main():
    apply_mode = '--apply' in sys.argv
    
    # 1. Search for Wochenschau videos
    search_results = search_wochenschau_videos()
    video_ids = [v['id'] for v in search_results]
    
    # 2. Get full details
    current_videos = get_video_details(video_ids)
    
    # 3. Load optimized data
    print(f"\n📂 Loading optimized data from {UPLOAD_DATA}...")
    optimized_data = load_optimized_data()
    print(f"   {len(optimized_data)} optimized entries available")
    
    # 4. Compare and find updates needed
    print(f"\n🔍 Comparing current vs optimized...")
    updates = compare_and_create_updates(current_videos, optimized_data)
    
    # 5. Save pending updates
    PENDING_UPDATES.mkdir(exist_ok=True)
    pending_file = PENDING_UPDATES / f"wochenschau_seo_updates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(pending_file, 'w', encoding='utf-8') as f:
        json.dump({
            'generated': datetime.now().isoformat(),
            'total_videos_found': len(current_videos),
            'updates_needed': len(updates),
            'updates': updates
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"📊 SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Videos found: {len(current_videos)}")
    print(f"Updates needed: {len(updates)}")
    print(f"Pending file: {pending_file}")
    
    # Show summary of changes
    if updates:
        print(f"\n📋 CHANGES SUMMARY:")
        print("-" * 60)
        
        title_changes = sum(1 for u in updates if any(c['field'] == 'title' for c in u['changes']))
        desc_changes = sum(1 for u in updates if any(c['field'] == 'description' for c in u['changes']))
        tag_changes = sum(1 for u in updates if any(c['field'] == 'tags' for c in u['changes']))
        
        print(f"   Title changes (SHORT format): {title_changes}")
        print(f"   Description updates: {desc_changes}")
        print(f"   Tag updates: {tag_changes}")
        
        print(f"\n📝 VIDEOS TO UPDATE:")
        for u in updates[:10]:  # Show first 10
            print(f"   Nr. {u['video_nr']}: {u['current_title'][:50]}...")
            for c in u['changes']:
                print(f"      → {c['field']}")
        
        if len(updates) > 10:
            print(f"   ... and {len(updates) - 10} more")
        
        print(f"\n💰 ESTIMATED QUOTA: {len(updates) * 50} units (50 per video.update)")
        
        if apply_mode:
            print(f"\n🚀 APPLYING UPDATES...")
            apply_updates(updates)
        else:
            print(f"\n⚠️ DRY RUN - No changes applied.")
            print(f"   Run with --apply to apply changes")
            print(f"   Or review: {pending_file}")

if __name__ == '__main__':
    main()
