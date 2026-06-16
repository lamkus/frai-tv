#!/usr/bin/env python3
"""
COMPLETE Wochenschau Status Report
- Uses Search API to find ALL videos (not just uploads playlist)
- Identifies format inconsistencies
- Prepares update list
"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

def get_youtube():
    with open(OAUTH_FILE,'r') as f:
        td = json.load(f)
    c = Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    )
    return build('youtube','v3',credentials=c)

def extract_nr(title):
    for pattern in [r'Nr\.?\s*(\d+)', r'#(\d+)']:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def main():
    yt = get_youtube()
    
    print("=" * 70)
    print("COMPLETE WOCHENSCHAU STATUS REPORT")
    print("=" * 70)
    
    # Use search API to find ALL Wochenschau videos
    all_wochenschau = []
    next_page = None
    
    print("\nSearching via Search API...")
    while True:
        r = yt.search().list(
            part='snippet',
            channelId=CHANNEL_ID,
            q='Wochenschau',
            type='video',
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in r.get('items', []):
            title = item['snippet']['title']
            if 'wochenschau' in title.lower():
                nr = extract_nr(title)
                if nr:
                    all_wochenschau.append({
                        'id': item['id']['videoId'],
                        'title': title,
                        'nr': nr
                    })
        
        next_page = r.get('nextPageToken')
        if not next_page:
            break
    
    # Sort by number
    all_wochenschau.sort(key=lambda x: x['nr'])
    
    # Analyze title formats
    old_format = []  # "Wochenschau Nr. XXX"
    new_format = []  # "Event – Wochenschau Nr. XXX"
    
    print(f"\nFound {len(all_wochenschau)} Wochenschau videos:")
    print("-" * 70)
    
    for v in all_wochenschau:
        if '–' in v['title'] and 'Wochenschau Nr' in v['title']:
            fmt = "NEW"
            new_format.append(v)
        elif v['title'].startswith('Wochenschau'):
            fmt = "OLD"
            old_format.append(v)
        else:
            fmt = "???"
        
        marker = " ⚠️ NEEDS UPDATE" if fmt == "OLD" else ""
        print(f"Nr. {v['nr']:3d} [{fmt}] {v['title'][:50]}{marker}")
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Wochenschau: {len(all_wochenschau)}")
    print(f"  - New Format (Event – Wochenschau): {len(new_format)}")
    print(f"  - Old Format (Wochenschau Nr.):     {len(old_format)}")
    
    if old_format:
        print()
        print("⚠️ VIDEOS THAT NEED TITLE UPDATE:")
        for v in old_format:
            print(f"   Nr. {v['nr']}: {v['id']}")
            print(f"      Current: {v['title']}")
    
    # Save for update script
    if old_format:
        with open('config/wochenschau_to_update.json', 'w', encoding='utf-8') as f:
            json.dump(old_format, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(old_format)} videos to config/wochenschau_to_update.json")

if __name__ == '__main__':
    main()
