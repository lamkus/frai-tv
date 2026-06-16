#!/usr/bin/env python3
"""
EMERGENCY FIX: Restore Wochenschau numbers to titles!
The global SEO update accidentally removed the episode numbers.
"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Mapping: Event name → Episode number
EVENT_TO_NUMBER = {
    'Poland Occupied': 477,
    'Bürgerbräukeller Bomb': 480,
    'Winter War Begins': 482,
    'Winter War': 483,
    'Phoney War': 488,
    'Dunkirk Pocket': 508,
    'Dunkirk Evacuation': 509,
    'Paris Falls': 511,
    'French Armistice': 512,
    'Channel Islands': 513,
    'Battle of Britain': 516,
    'London Blitz': 521,  # First one (07.09)
    'Berlin Raid': 522,
    'Sea Lion Cancelled': 524,
    'Kharkov Retaken': 652,
    'Tunisia Battles': 654,
    'V1 Flying Bombs': 720,
    'Bagration Begins': 721,
    'Bagration': 722,
    'Battle of Bulge': 746,
    'Vistula Offensive': 750,
    'Eastern Collapse': 751,
    'Yalta Conference': 753,
    'Dresden Bombed': 754,
}

# Special cases with same event name but different dates
DATE_TO_NUMBER = {
    'London Blitz': {
        '07.09.1940': 521,
        '21.09.1940': 523,
    }
}

def get_youtube():
    with open('config/youtube_oauth.json', 'r') as f:
        td = json.load(f)
    return build('youtube', 'v3', credentials=Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    ))

def extract_event_and_date(title):
    """Extract event name and date from title like 'Wochenschau: Event (DD.MM.YYYY)'"""
    # Match: Wochenschau: Event (DD.MM.YYYY)
    match = re.match(r'Wochenschau:\s*(.+?)\s*\((\d{2}\.\d{2}\.\d{4})\)', title)
    if match:
        return match.group(1).strip(), match.group(2)
    
    # Match: Wochenschau XXX: Event (DD.MM.YYYY) - already has number
    match = re.match(r'Wochenschau\s+(\d+):\s*(.+?)\s*\((\d{2}\.\d{2}\.\d{4})\)', title)
    if match:
        return None, None  # Already has number
    
    return None, None

def fix_title(title):
    """Add episode number back to title"""
    event, date = extract_event_and_date(title)
    
    if not event:
        return None  # Already has number or can't parse
    
    # Check for special cases with same event name
    if event in DATE_TO_NUMBER and date in DATE_TO_NUMBER[event]:
        nr = DATE_TO_NUMBER[event][date]
    elif event in EVENT_TO_NUMBER:
        nr = EVENT_TO_NUMBER[event]
    else:
        print(f"  ⚠️ Unknown event: {event}")
        return None
    
    # Build corrected title
    # Format: Wochenschau NR: Event (DD.MM.YYYY) | 8K | @remAIke_IT
    new_title = f"Wochenschau {nr}: {event} ({date}) | 8K | @remAIke_IT"
    
    return new_title, nr

def main():
    yt = get_youtube()
    
    print("=" * 70)
    print("🚨 EMERGENCY FIX: Restoring episode numbers to Wochenschau titles")
    print("=" * 70)
    
    # Get all videos from playlist
    response = yt.playlistItems().list(
        part='snippet',
        playlistId='PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg',
        maxResults=50
    ).execute()
    
    videos_to_fix = []
    
    for item in response.get('items', []):
        title = item['snippet']['title']
        video_id = item['snippet']['resourceId']['videoId']
        
        if 'wochenschau' not in title.lower():
            continue
        
        # Check if title is missing number (format: "Wochenschau: Event")
        if title.startswith('Wochenschau:'):
            result = fix_title(title)
            if result:
                new_title, nr = result
                videos_to_fix.append({
                    'id': video_id,
                    'old_title': title,
                    'new_title': new_title,
                    'nr': nr
                })
    
    print(f"\n📹 Found {len(videos_to_fix)} videos to fix:\n")
    
    for v in videos_to_fix:
        print(f"  Nr. {v['nr']:3d}: {v['old_title'][:45]}...")
        print(f"       → {v['new_title'][:45]}...")
        print()
    
    if not videos_to_fix:
        print("✅ No videos need fixing!")
        return
    
    print("=" * 70)
    print("🔧 APPLYING FIXES...")
    print("=" * 70)
    
    success = 0
    failed = 0
    
    for v in videos_to_fix:
        print(f"\n📹 Fixing Wochenschau {v['nr']}...")
        
        try:
            # Get current video details
            current = yt.videos().list(part='snippet', id=v['id']).execute()
            if not current['items']:
                print(f"   ❌ Video not found!")
                failed += 1
                continue
            
            snippet = current['items'][0]['snippet']
            category_id = snippet['categoryId']
            
            # Update with corrected title
            response = yt.videos().update(
                part='snippet',
                body={
                    'id': v['id'],
                    'snippet': {
                        'title': v['new_title'],
                        'description': snippet['description'],
                        'tags': snippet.get('tags', []),
                        'categoryId': category_id
                    }
                }
            ).execute()
            
            print(f"   ✅ Fixed: {v['new_title'][:50]}...")
            success += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {success} ✅ fixed | {failed} ❌ failed")
    print("=" * 70)

if __name__ == '__main__':
    main()
