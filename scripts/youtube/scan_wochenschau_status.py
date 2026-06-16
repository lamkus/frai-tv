#!/usr/bin/env python3
"""
Scan Wochenschau videos on YouTube - Check status, duplicates, and missing
"""

import json
import os
import re
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
OAUTH_FILE = 'config/youtube_oauth.json'

def get_youtube_client():
    """Get authenticated YouTube client"""
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret']
    )
    
    return build('youtube', 'v3', credentials=creds)

def get_all_channel_videos():
    """Get all videos from channel using playlistItems API (uploads playlist)"""
    youtube = get_youtube_client()
    videos = []
    # Upload playlist ID = UU + channel ID without UC
    upload_playlist = 'UU' + CHANNEL_ID[2:]
    
    next_page = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=upload_playlist,
            maxResults=50,
            pageToken=next_page
        )
        response = request.execute()
        
        for item in response.get('items', []):
            videos.append({
                'id': item['snippet']['resourceId']['videoId'],
                'title': item['snippet']['title']
            })
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    return videos

def main():
    print("Scanning channel for Wochenschau videos...")
    videos = get_all_channel_videos()
    print(f"Total videos on channel: {len(videos)}")
    
    # Find Wochenschau videos and extract numbers
    wochenschau = []
    pattern = r'(?:Nr\.?\s*|#)(\d{3})'
    
    for v in videos:
        title_lower = v['title'].lower()
        if 'wochenschau' in title_lower:
            match = re.search(pattern, v['title'])
            if match:
                nr = int(match.group(1))
                wochenschau.append({'nr': nr, 'id': v['id'], 'title': v['title']})
    
    # Sort by number
    wochenschau.sort(key=lambda x: x['nr'])
    
    print()
    print("=" * 60)
    print("WOCHENSCHAU VIDEOS AUF YOUTUBE")
    print("=" * 60)
    print(f"Total: {len(wochenschau)} Videos")
    print()
    
    for w in wochenschau:
        print(f"Nr. {w['nr']:3d}: {w['title'][:65]}")
    
    # Check for Nr. 516
    print()
    print("=" * 60)
    print("CHECK Nr. 516")
    print("=" * 60)
    nr516 = [w for w in wochenschau if w['nr'] == 516]
    if nr516:
        print(f"GEFUNDEN: {nr516[0]['title']}")
        print(f"ID: {nr516[0]['id']}")
    else:
        print("NICHT GEFUNDEN - Video existiert nicht auf YouTube")
    
    # Check for duplicates
    print()
    print("=" * 60)
    print("DUPLIKATE CHECK")
    print("=" * 60)
    nr_count = defaultdict(list)
    for w in wochenschau:
        nr_count[w['nr']].append(w)
    
    has_duplicates = False
    for nr, items in sorted(nr_count.items()):
        if len(items) > 1:
            has_duplicates = True
            print(f"DUPLIKAT Nr. {nr}:")
            for item in items:
                print(f"  - {item['title']}")
                print(f"    ID: {item['id']}")
    
    if not has_duplicates:
        print("Keine Duplikate gefunden!")
    
    # Summary
    print()
    print("=" * 60)
    print("UPLOAD STATUS")
    print("=" * 60)
    uploaded_nrs = sorted([w['nr'] for w in wochenschau])
    print(f"Hochgeladen: {len(wochenschau)} von 252 Episoden")
    print(f"Fehlend: {252 - len(wochenschau)} Episoden")
    print()
    print(f"Hochgeladene Nummern: {uploaded_nrs}")
    
    # Calculate missing ranges
    print()
    print("=" * 60)
    print("FEHLENDE EPISODEN (459-755)")
    print("=" * 60)
    
    all_nrs = set(range(459, 756))  # 459 to 755
    uploaded_set = set(uploaded_nrs)
    missing = sorted(all_nrs - uploaded_set)
    
    # Group consecutive numbers
    if missing:
        ranges = []
        start = missing[0]
        end = missing[0]
        for nr in missing[1:]:
            if nr == end + 1:
                end = nr
            else:
                if start == end:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{end}")
                start = nr
                end = nr
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")
        
        print(f"Fehlende Bereiche: {', '.join(ranges[:20])}...")
        print(f"(Insgesamt {len(missing)} fehlende Episoden)")

if __name__ == '__main__':
    main()
