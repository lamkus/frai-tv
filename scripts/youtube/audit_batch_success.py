#!/usr/bin/env python3
"""
Audit Batch Success
Verifies if the recent batch updates were applied correctly to the live channel.
Checks for Title matches, Quality markers (8K HQ), and Series consistency.
"""
import json
import os
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Configuration
PLAN_FILE = 'config/channel_master_fix_prioritized.json'
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

def get_service():
    """Setup YouTube API service"""
    oauth_path = Path('config/youtube_oauth.json')
    if not oauth_path.exists():
        print(f"❌ OAuth config not found at {oauth_path}")
        sys.exit(1)
        
    oauth = json.loads(oauth_path.read_text(encoding='utf-8'))
    creds = Credentials(
        token=oauth.get('access_token') or oauth.get('token'),
        refresh_token=oauth['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def get_uploads_playlist_id(youtube):
    """Get the Uploads playlist ID for the channel"""
    ch = youtube.channels().list(
        part='contentDetails',
        id=CHANNEL_ID
    ).execute()
    return ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def fetch_all_videos(youtube, uploads_id):
    """Fetch all video snippets from the channel"""
    print(f"🔄 Fetching live channel data...")
    videos = {}
    next_page = None
    
    while True:
        req = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        )
        resp = req.execute()
        
        for item in resp['items']:
            vid_id = item['snippet']['resourceId']['videoId']
            videos[vid_id] = item['snippet']
            
        next_page = resp.get('nextPageToken')
        print(f"   Fetched {len(videos)} videos...", end='\r')
        if not next_page:
            break
    print(f"\n✅ Total live videos fetched: {len(videos)}")
    return videos

def audit_results(plan, live_data):
    """Compare Plan vs Reality"""
    print("\n🔍 AUDITING CHANGES...")
    print("=" * 60)
    
    stats = {
        'total_planned': len(plan),
        'found_live': 0,
        'perfect_match': 0,
        'partial_match': 0,
        'failed': 0,
        'hallucinations': 0,
        'series_errors': 0
    }
    
    series_keywords = {
        'Alfred J. Kwak': ['alfred', 'kwak'],
        'Betty Boop': ['betty', 'boop'],
        'Superman': ['superman'],
        'Popeye': ['popeye'],
        'Felix the Cat': ['felix'],
        'Wochenschau': ['wochenschau']
    }

    # Debug sample list
    samples = []

    for task in plan:
        vid_id = task['id']
        expected_title = task['new_title']
        
        if vid_id not in live_data:
            continue
            
        stats['found_live'] += 1
        live_title = live_data[vid_id]['title']
        
        # Check 1: Exact Match
        if live_title == expected_title:
            stats['perfect_match'] += 1
        # Check 2: Partial Match (The core update logic "8K HQ (4K UHD)" is present)
        elif "8K HQ (4K UHD)" in live_title:
            stats['partial_match'] += 1
        else:
            stats['failed'] += 1
            if len(samples) < 5:
                samples.append(f"❌ FAIL: {live_title} \n     != {expected_title}")

        # Check 3: Series Hallucinations
        # Determine series from expected title
        current_series = None
        for series, keywords in series_keywords.items():
            if series in expected_title:
                current_series = series
                break
        
        # If we know the series, ensure the Live Title DOESN'T contain OTHER series names
        if current_series:
            for other_series, keywords in series_keywords.items():
                if other_series == current_series: 
                    continue
                # If "Betty Boop" appears in an "Alfred J. Kwak" title -> Error
                if other_series in live_title and other_series not in expected_title:
                    stats['series_errors'] += 1
                    print(f"⚠ SERIES ERROR: {live_title} (Expected: {current_series}, Found: {other_series})")

    print(f"\n📊 STATISTICS")
    print("-" * 30)
    print(f"Total Planned Tasks:      {stats['total_planned']}")
    print(f"Videos Found Live:        {stats['found_live']}")
    print("-" * 30)
    print(f"✅ Exact Perfect Matches: {stats['perfect_match']} ({(stats['perfect_match']/stats['found_live'])*100:.1f}%)")
    print(f"⚠️ Partial Matches:       {stats['partial_match']} (Usually manual tweaks)")
    print(f"❌ Not Updated Yet:       {stats['failed']} (Pending execution)")
    print("-" * 30)
    print(f"☠️ Series Hallucinations: {stats['series_errors']}")
    
    if samples:
        print("\n📝 Update Failures (Sample):")
        for s in samples:
            print(s)

def main():
    # 1. Load Plan
    if not os.path.exists(PLAN_FILE):
        print("Plan file not found.")
        return
        
    with open(PLAN_FILE, 'r', encoding='utf-8') as f:
        plan = json.load(f)
        
    print(f"📂 Loaded Plan: {len(plan)} tasks")
    
    # 2. Get Live Data
    yt = get_service()
    uploads = get_uploads_playlist_id(yt)
    live_data = fetch_all_videos(yt, uploads)
    
    # 3. Audit
    audit_results(plan, live_data)

if __name__ == "__main__":
    main()
