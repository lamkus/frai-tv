#!/usr/bin/env python3
"""
Wochenschau Complete Fix:
1. Fix new upload (Nr. 720) with SEO
2. Add missing videos to playlist
3. Sort playlist chronologically
"""

import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Config
WOCHENSCHAU_PLAYLIST = 'PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg'
NEW_VIDEO_ID = '6K-MuUu6L44'

# SEO Template for Nr. 720
SEO_720 = {
    'title': 'Die Deutsche Wochenschau Nr. 720 (21.06.1944) | 8K HQ | @remAIke_IT',
    'description': '''🇩🇪 Die Deutsche Wochenschau Nr. 720 vom 21. Juni 1944

Originalaufnahmen aus dem Juni 1944 – historisches Zeitdokument in bestmöglicher Qualität restauriert.

⚠️ HISTORISCHES DOKUMENT – Keine Verherrlichung! Dient der historischen Bildung und Forschung.

🇬🇧 German Newsreel No. 720 from June 21, 1944
Original footage from June 1944 – historical document restored in best possible quality.

⚠️ HISTORICAL DOCUMENT – No glorification! For historical education and research purposes only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you appreciate history!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restorations!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at: https://frai.tv | @remAIke_IT

#Wochenschau #WWII #1944 #History #Newsreel #8K #PublicDomain #Historical #remAIke''',
    'tags': [
        'Wochenschau', 'Deutsche Wochenschau', 'Nr. 720', '1944', 'Juni 1944',
        'WWII', 'World War 2', 'Zweiter Weltkrieg', 'Newsreel', 'History',
        'Historical', 'Public Domain', '8K', 'Restored', 'Germany', 'remAIke'
    ]
}

# Expected chronological order (Nr -> VideoID)
WOCHENSCHAU_VIDEOS = {
    # 1940
    511: '3rB80OGKzrg',  # 20.06.1940
    516: 'T-EsdXGhqog',  # 22.07.1940
    # 1943
    652: '0sO7jVL43yQ',  # 03.03.1943
    654: 'dYBzf5V1TjI',  # 17.03.1943
    # 1944
    720: '6K-MuUu6L44',  # 21.06.1944 - NEW!
    721: 'W-UcQleew8Y',  # 28.06.1944
    722: 'bZkUPQHqyfg',  # 06.07.1944
    746: 'jGz1kC1Z69A',  # 21.12.1944
    # 1945
    750: 'w2UvksMOs3c',  # 25.01.1945
    751: '6YLPpJLgVXk',  # 10.02.1945
    753: 'iEEvt-s1XhQ',  # 05.03.1945
    754: 'H_n_mS-eKps',  # 16.03.1945
}

# Non-Wochenschau newsreels (keep at end)
OTHER_NEWSREELS = {
    'eF81rBeXbzk': 'Hindenburg (1937)',
    '9AgSJyMnxi8': 'Atomic Bomb (1946)',
    '4vaim28zk50': 'Nürnberg (1947-49)',
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


def fix_video_720(youtube, apply=False):
    """Fix the new upload with SEO"""
    print("\n" + "="*60)
    print("1. FIXING NEW UPLOAD (Nr. 720)")
    print("="*60)
    
    # Get current state
    response = youtube.videos().list(
        part='snippet,status',
        id=NEW_VIDEO_ID
    ).execute()
    
    if not response['items']:
        print(f"❌ Video {NEW_VIDEO_ID} not found!")
        return False
    
    video = response['items'][0]
    current_title = video['snippet']['title']
    status = video['status']['privacyStatus']
    
    print(f"ID: {NEW_VIDEO_ID}")
    print(f"Status: {status}")
    print(f"Current: {current_title}")
    print(f"New:     {SEO_720['title']}")
    print(f"Tags:    {len(SEO_720['tags'])} tags")
    
    if not apply:
        print("\n⚠️ DRY RUN - use --apply to make changes")
        return True
    
    # Update video
    video['snippet']['title'] = SEO_720['title']
    video['snippet']['description'] = SEO_720['description']
    video['snippet']['tags'] = SEO_720['tags']
    video['snippet']['categoryId'] = '27'  # Education
    video['snippet']['defaultLanguage'] = 'de'
    video['snippet']['defaultAudioLanguage'] = 'de'
    
    youtube.videos().update(
        part='snippet',
        body={'id': NEW_VIDEO_ID, 'snippet': video['snippet']}
    ).execute()
    
    print("✅ Video updated!")
    return True


def get_playlist_items(youtube, playlist_id):
    """Get all items from a playlist"""
    items = []
    next_page = None
    while True:
        response = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        items.extend(response.get('items', []))
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    return items


def check_and_fix_playlist(youtube, apply=False):
    """Check playlist and add missing videos"""
    print("\n" + "="*60)
    print("2. CHECKING PLAYLIST")
    print("="*60)
    
    # Get current playlist items
    items = get_playlist_items(youtube, WOCHENSCHAU_PLAYLIST)
    current_video_ids = {item['contentDetails']['videoId'] for item in items}
    
    print(f"Current items: {len(items)}")
    
    # Find missing Wochenschau videos
    missing = []
    for nr, vid in sorted(WOCHENSCHAU_VIDEOS.items()):
        if vid not in current_video_ids:
            missing.append((nr, vid))
            print(f"  ❌ Missing: Nr. {nr} ({vid})")
        else:
            print(f"  ✅ Present: Nr. {nr}")
    
    # Find missing other newsreels
    for vid, name in OTHER_NEWSREELS.items():
        if vid not in current_video_ids:
            missing.append((9999, vid))  # Put at end
            print(f"  ❌ Missing: {name} ({vid})")
        else:
            print(f"  ✅ Present: {name}")
    
    if not missing:
        print("\n✅ All videos present!")
    else:
        print(f"\n{len(missing)} videos missing from playlist")
        
        if apply:
            for nr, vid in missing:
                print(f"  Adding {vid}...")
                youtube.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'playlistId': WOCHENSCHAU_PLAYLIST,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': vid
                            }
                        }
                    }
                ).execute()
                print(f"  ✅ Added!")
        else:
            print("⚠️ DRY RUN - use --apply to add missing videos")
    
    return len(missing)


def show_playlist_order(youtube):
    """Show current playlist order"""
    print("\n" + "="*60)
    print("3. PLAYLIST ORDER (current)")
    print("="*60)
    
    items = get_playlist_items(youtube, WOCHENSCHAU_PLAYLIST)
    
    for item in items:
        pos = item['snippet']['position']
        vid = item['contentDetails']['videoId']
        title = item['snippet']['title'][:55]
        print(f"{pos:2d}. {title}")
    
    print("\n⚠️ REIHENFOLGE MANUELL IM YOUTUBE STUDIO SORTIEREN!")
    print("   Empfohlen: Chronologisch nach Nr. (511, 516, 652, ...)")
    print("   Studio: https://studio.youtube.com/channel/UCVFv6Egpl0LDvigpFbQXNeQ/playlists")


def main():
    apply = '--apply' in sys.argv
    
    print("="*60)
    print("WOCHENSCHAU COMPLETE FIX")
    print("="*60)
    
    youtube = build('youtube', 'v3', credentials=load_credentials())
    
    # 1. Fix new video
    fix_video_720(youtube, apply)
    
    # 2. Check and fix playlist
    check_and_fix_playlist(youtube, apply)
    
    # 3. Show order
    show_playlist_order(youtube)
    
    if not apply:
        print("\n" + "="*60)
        print("DRY RUN COMPLETE - Run with --apply to make changes")
        print("="*60)


if __name__ == '__main__':
    main()
