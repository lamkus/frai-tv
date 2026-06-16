#!/usr/bin/env python3
"""Get LIVE stats for Wochenschau videos via Public API."""
import requests
import os

# Wochenschau Video IDs from cache
VIDEO_IDS = [
    '6K-MuUu6L44',  # Die Deutsche Wochenschau Nr. 720
    'jGz1kC1Z69A',  # Die Deutsche Wochenschau Nr. 746
    '9AgSJyMnxi8',  # Atomic Bomb Newsreel
    'W-UcQleew8Y',  # Die Deutsche Wochenschau Nr. 721
    'w2UvksMOs3c',  # Wochenschau Nr. 750
    'dYBzf5V1TjI',  # Die Deutsche Wochenschau Nr. 654
    'H_n_mS-eKps',  # Wochenschau Nr. 754
    '6YLPpJLgVXk',  # Wochenschau Nr. 751
    'iEEvt-s1XhQ',  # Wochenschau Nr. 753
    'bZkUPQHqyfg',  # Die Deutsche Wochenschau Nr. 722
    '0sO7jVL43yQ',  # Die Deutsche Wochenschau Nr. 652
]

# Try to get API key from environment or config
API_KEY = os.getenv('YOUTUBE_API_KEY')

if not API_KEY:
    # Try to read from a config file
    try:
        import json
        config_paths = [
            'config/api_keys.json',
            'config/youtube_api_key.txt',
            '.env'
        ]
        for path in config_paths:
            if os.path.exists(path):
                print(f"Trying {path}...")
    except:
        pass

if not API_KEY:
    print("❌ YOUTUBE_API_KEY nicht gefunden!")
    print()
    print("Bitte setzen mit:")
    print("  $env:YOUTUBE_API_KEY = 'dein-api-key'")
    print()
    print("Oder prüfe die Cache-Daten nochmal...")
    print()
    
    # Show cached data instead
    import json
    data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))
    
    print("📊 CACHED DATA (von", data.get('fetched_at', '?'), "):")
    print("="*80)
    
    results = []
    for v in data['videos']:
        if v['id'] in VIDEO_IDS:
            stats = v.get('statistics', {})
            views = int(stats.get('viewCount', 0))
            title = v['snippet']['title']
            results.append((views, v['id'], title))
    
    results.sort(reverse=True)
    for views, vid, title in results:
        print(f"{views:5} Views | {vid} | {title}")
else:
    # Use Public API
    print(f"🔑 Using API Key: {API_KEY[:10]}...")
    
    ids_str = ','.join(VIDEO_IDS)
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={ids_str}&key={API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data:
        print("📊 LIVE DATA:")
        print("="*80)
        
        results = []
        for item in data['items']:
            views = int(item['statistics'].get('viewCount', 0))
            title = item['snippet']['title']
            vid = item['id']
            results.append((views, vid, title))
        
        results.sort(reverse=True)
        for views, vid, title in results:
            print(f"{views:5} Views | {vid} | {title}")
    else:
        print("Error:", data)
