#!/usr/bin/env python3
"""
Channel Organization Tool
========================
1. Fix ALL playlist (add missing videos)
2. Create FEATURED playlist for homepage
3. Analyze playlist coverage
4. Suggest optimal homepage layout
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

# Config
ALL_PLAYLIST = 'PL3d2Tsr13ihPiIyGzDm0xRRxtbTD7Lpre'
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Category keywords for auto-detection
CATEGORIES = {
    'Betty Boop': ['betty boop', 'betty'],
    'Alfred J. Kwak': ['alfred', 'quack', 'kwak', 'jodokus'],
    'Soundies': ['soundie'],
    'Wochenschau': ['wochenschau'],
    'Superman': ['superman', 'fleischer'],
    'Popeye': ['popeye'],
    'Looney Tunes': ['looney', 'merrie melodies', 'porky', 'daffy', 'bugs bunny'],
    'Felix': ['felix the cat', 'felix'],
    'Casper': ['casper'],
    'BraveStarr': ['bravestarr'],
    'Silent Film': ['chaplin', 'keaton', 'buster', 'harold lloyd'],
    'Christmas': ['christmas', 'xmas', 'weihnacht'],
    'Documentary': ['documentary', 'nuremberg', 'nürnberg', 'atomic', 'pearl harbor'],
}


def load_credentials():
    with open('config/youtube_oauth.json', 'r') as f:
        token_data = json.load(f)
    return Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret']
    )


def get_all_public_videos(youtube):
    """Get all public videos from channel"""
    all_videos = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOAD_PLAYLIST,
            maxResults=50,
            pageToken=next_page
        ).execute()
        all_videos.extend(response.get('items', []))
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    # Get status of all videos
    video_ids = [item['contentDetails']['videoId'] for item in all_videos]
    public_videos = []
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        vids = youtube.videos().list(
            part='status,snippet,statistics',
            id=','.join(batch)
        ).execute()
        for v in vids.get('items', []):
            if v['status']['privacyStatus'] == 'public':
                public_videos.append(v)
    
    return public_videos


def get_playlist_videos(youtube, playlist_id):
    """Get all video IDs from a playlist"""
    video_ids = set()
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        for item in response.get('items', []):
            video_ids.add(item['contentDetails']['videoId'])
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    return video_ids


def categorize_video(title):
    """Auto-detect category from title"""
    title_lower = title.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in title_lower:
                return cat
    return 'Other'


def analyze_channel(youtube):
    """Full channel analysis"""
    print("=" * 60)
    print("CHANNEL ANALYSE")
    print("=" * 60)
    
    # Get all public videos
    public_videos = get_all_public_videos(youtube)
    print(f"\nTotal Public Videos: {len(public_videos)}")
    
    # Get ALL playlist
    all_pl_videos = get_playlist_videos(youtube, ALL_PLAYLIST)
    print(f"Videos in ALL Playlist: {len(all_pl_videos)}")
    
    # Find missing
    missing = []
    for v in public_videos:
        if v['id'] not in all_pl_videos:
            missing.append(v)
    
    print(f"❌ MISSING from ALL Playlist: {len(missing)}")
    
    # Categorize all videos
    print("\n" + "=" * 60)
    print("KATEGORIEN-VERTEILUNG")
    print("=" * 60)
    
    categories = defaultdict(list)
    for v in public_videos:
        cat = categorize_video(v['snippet']['title'])
        categories[cat].append(v)
    
    for cat, vids in sorted(categories.items(), key=lambda x: -len(x[1])):
        print(f"{len(vids):3d} | {cat}")
    
    # Get all playlists
    print("\n" + "=" * 60)
    print("PLAYLIST COVERAGE")
    print("=" * 60)
    
    playlists = []
    next_page = None
    while True:
        response = youtube.playlists().list(
            part='snippet,contentDetails',
            mine=True,
            maxResults=50,
            pageToken=next_page
        ).execute()
        playlists.extend(response.get('items', []))
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    # Check coverage
    covered_videos = set()
    for pl in playlists:
        if pl['snippet']['title'] in ['ALL @reAImastered', 'Jasmine Geburtstag', 'test']:
            continue
        pl_videos = get_playlist_videos(youtube, pl['id'])
        covered_videos.update(pl_videos)
        count = pl['contentDetails']['itemCount']
        title = pl['snippet']['title'][:40]
        print(f"{count:3d} | {title}")
    
    uncovered = []
    for v in public_videos:
        if v['id'] not in covered_videos:
            uncovered.append(v)
    
    print(f"\n⚠️ Videos OHNE Kategorie-Playlist: {len(uncovered)}")
    if uncovered:
        for v in uncovered[:10]:
            print(f"   - {v['snippet']['title'][:50]}")
        if len(uncovered) > 10:
            print(f"   ... und {len(uncovered) - 10} weitere")
    
    return missing, categories, uncovered


def add_missing_to_all_playlist(youtube, missing, apply=False):
    """Add missing videos to ALL playlist"""
    print("\n" + "=" * 60)
    print(f"ADD {len(missing)} VIDEOS TO ALL PLAYLIST")
    print("=" * 60)
    
    if not missing:
        print("✅ All videos already in ALL playlist!")
        return
    
    if not apply:
        print("⚠️ DRY RUN - use --apply to add videos")
        for v in missing[:20]:
            print(f"   Would add: {v['snippet']['title'][:50]}")
        if len(missing) > 20:
            print(f"   ... and {len(missing) - 20} more")
        return
    
    # Add videos to ALL playlist
    added = 0
    for v in missing:
        try:
            youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': ALL_PLAYLIST,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': v['id']
                        }
                    }
                }
            ).execute()
            added += 1
            print(f"✅ Added: {v['snippet']['title'][:50]}")
        except Exception as e:
            print(f"❌ Failed: {v['id']} - {str(e)[:50]}")
    
    print(f"\n✅ Added {added}/{len(missing)} videos to ALL playlist")


def suggest_homepage_layout(categories):
    """Suggest optimal homepage playlist layout"""
    print("\n" + "=" * 60)
    print("EMPFOHLENE HOMEPAGE LAYOUT")
    print("=" * 60)
    print("""
YouTube Channel Homepage zeigt diese Sections:

┌─────────────────────────────────────────────────────────────┐
│  🎬 CHANNEL TRAILER (1 Video für neue Besucher)             │
│     → Erstelle: "Welcome to remAIke_IT" Trailer             │
├─────────────────────────────────────────────────────────────┤
│  🔥 FEATURED / BEST OF (8-12 Videos)                         │
│     → Neue Playlist: "⭐ Best of remAIke_IT | 8K Restored"   │
│     → Mix aus allen Kategorien (Betty, Alfred, Soundies...) │
├─────────────────────────────────────────────────────────────┤
│  📺 SERIEN (Horizontal Scrolls)                              │
│                                                             │
│  🦆 Alfred J. Kwak (41 Videos)                               │
│  💋 Betty Boop (59 Videos)                                   │
│  🎵 Soundies (19 Videos)                                     │
│  📰 Deutsche Wochenschau (15 Videos)                         │
│  🦸 Superman (10 Videos)                                     │
│  ⚓ Popeye (4 Videos)                                        │
├─────────────────────────────────────────────────────────────┤
│  🎨 SAMMLUNGEN                                               │
│                                                             │
│  🎭 Classic Cartoons (110 Videos)                            │
│  🎭 Silent Film Era (18 Videos)                              │
│  🎭 Looney Tunes (16 Videos)                                 │
└─────────────────────────────────────────────────────────────┘

AKTIONEN:
1. Erstelle "⭐ Best of remAIke_IT" Playlist (10-12 Videos)
2. Rename "ALL @reAImastered" → "📚 Complete Archive | All Videos"
3. Lösche "test" Playlist (0 Videos)
4. Merge "Soundies" (3) in "Soundies - Vintage..." (19)
5. Homepage Layout in YouTube Studio konfigurieren
""")


def main():
    apply = '--apply' in sys.argv
    
    youtube = build('youtube', 'v3', credentials=load_credentials())
    
    # Analyze
    missing, categories, uncovered = analyze_channel(youtube)
    
    # Add missing to ALL
    add_missing_to_all_playlist(youtube, missing, apply)
    
    # Suggest layout
    suggest_homepage_layout(categories)
    
    if not apply and missing:
        print("\n" + "=" * 60)
        print(f"Run with --apply to add {len(missing)} missing videos to ALL playlist")
        print("=" * 60)


if __name__ == '__main__':
    main()
