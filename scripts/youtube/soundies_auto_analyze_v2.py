#!/usr/bin/env python3
"""
Soundies Auto-Analyzer V2 - Uses OAuth + Downloads Thumbnails for AI Analysis
"""
import requests
import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Alle Soundie Video IDs
SOUNDIE_IDS = [
    'mReDNz-Exdk', '6XVj6G3qNYY', 'ukmrI7DlXkc', 'oA7XcqVM1Vo', 'OvBqUlzTunI',
    'mDSdzFc572Y', 'hAs6lunYl-E', '1zKpqdriv70', 'Z2SxppvCWvE', 'rprpMDyTWRI',
    'NAk0QvvaT7M', 'w82vzaGBqwE', 'GerP7_evS9o', 'D-LL4VuR5Pg', 'LJp-M01OI-8',
    'HvwtRYp43eU', '2yGX3wy-4SQ', 'hIsTWWP-YkQ', '340C9lsoyYk', 'A8LWgWF5f5k', 'DHogGPBbzRI'
]

def get_youtube_client():
    """Get authenticated YouTube client"""
    with open('config/youtube_oauth.json', 'r') as f:
        token_data = json.load(f)
    
    credentials = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    return build('youtube', 'v3', credentials=credentials)

def download_thumbnail(url, video_id, output_dir='config/soundie_thumbnails'):
    """Download thumbnail for AI analysis"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f'{video_id}.jpg')
    
    if os.path.exists(filepath):
        return filepath
    
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            return filepath
    except Exception as e:
        print(f"   ⚠️ Could not download thumbnail: {e}")
    return None

def main():
    print("🎬 SOUNDIES AUTO-ANALYZER V2 (OAuth + Thumbnails)")
    print("=" * 70)
    
    # 1. Get YouTube client
    print("\n📥 Connecting to YouTube API...")
    youtube = get_youtube_client()
    
    # 2. Fetch all video metadata
    print("📥 Fetching video metadata...")
    
    all_videos = []
    for i in range(0, len(SOUNDIE_IDS), 50):
        batch = SOUNDIE_IDS[i:i+50]
        request = youtube.videos().list(
            part='snippet,contentDetails',
            id=','.join(batch)
        )
        response = request.execute()
        all_videos.extend(response.get('items', []))
    
    print(f"   ✅ Got {len(all_videos)} videos")
    
    # 3. Analyze and extract info
    print("\n🔍 Analyzing metadata and downloading thumbnails...")
    print("-" * 70)
    
    results = []
    
    # Known Soundies artists from my research
    known_soundie_artists = {
        'yvonne de carlo': 'Yvonne De Carlo',
        'johnny long': 'Johnny Long Orchestra', 
        'tommy dorsey': 'Tommy Dorsey Orchestra',
        'three suns': 'The Three Suns',
        'king\'s men': 'The King\'s Men',
        'mills brothers': 'The Mills Brothers',
        'duke ellington': 'Duke Ellington Orchestra',
        'cab calloway': 'Cab Calloway',
        'louis armstrong': 'Louis Armstrong',
        'fats waller': 'Fats Waller',
        'count basie': 'Count Basie Orchestra',
        'benny goodman': 'Benny Goodman',
        'glenn miller': 'Glenn Miller Orchestra',
        'artie shaw': 'Artie Shaw',
        'ink spots': 'The Ink Spots',
        'andrews sisters': 'The Andrews Sisters',
        'doris day': 'Doris Day',
        'nat king cole': 'Nat King Cole',
        'louis jordan': 'Louis Jordan',
        'dorothy dandridge': 'Dorothy Dandridge',
        'horace heidt': 'Horace Heidt',
        'freddy martin': 'Freddy Martin Orchestra',
        'spike jones': 'Spike Jones',
        'teddy powell': 'Teddy Powell Orchestra',
        'ray mckinley': 'Ray McKinley',
        'stan kenton': 'Stan Kenton Orchestra',
        'gene krupa': 'Gene Krupa Orchestra',
        'charlie barnet': 'Charlie Barnet Orchestra',
        'shep fields': 'Shep Fields Orchestra',
        'hal mcintyre': 'Hal McIntyre Orchestra',
    }
    
    for v in all_videos:
        snippet = v['snippet']
        video_id = v['id']
        title = snippet['title']
        desc = snippet.get('description', '')
        tags = snippet.get('tags', [])
        
        # Extract song name
        song = title.split('|')[0].replace('Soundie:', '').strip()
        
        # Get best thumbnail
        thumbs = snippet.get('thumbnails', {})
        thumb_url = (thumbs.get('maxres') or thumbs.get('high') or thumbs.get('medium') or thumbs.get('default', {})).get('url', '')
        
        result = {
            'id': video_id,
            'title': title,
            'song': song,
            'description': desc,
            'tags': tags,
            'thumbnail_url': thumb_url,
            'artist': None,
            'artist_source': None,
            'confidence': None
        }
        
        # Search for artist in description and tags
        search_text = (desc + ' ' + ' '.join(tags)).lower()
        
        for key, artist_name in known_soundie_artists.items():
            if key in search_text:
                result['artist'] = artist_name
                result['artist_source'] = 'metadata'
                result['confidence'] = 'HIGH'
                break
        
        # Download thumbnail for unknown videos
        if thumb_url:
            thumb_path = download_thumbnail(thumb_url, video_id)
            result['thumbnail_local'] = thumb_path
        
        results.append(result)
        
        # Print status
        artist_info = f"✅ {result['artist']}" if result['artist'] else "❓ Unknown"
        print(f"{video_id}: {song[:35]:<35} | {artist_info}")
    
    # 4. Save results
    with open('config/soundies_auto_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # 5. Summary
    found = [r for r in results if r['artist']]
    unknown = [r for r in results if not r['artist']]
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"✅ Artists identified: {len(found)}")
    print(f"❓ Need AI analysis: {len(unknown)}")
    
    if found:
        print("\n🎵 IDENTIFIED ARTISTS:")
        for r in found:
            print(f"   {r['id']}: {r['artist']} - {r['song'][:40]}")
    
    if unknown:
        print("\n🖼️ THUMBNAILS DOWNLOADED FOR AI ANALYSIS:")
        print("   Location: config/soundie_thumbnails/")
        for r in unknown:
            print(f"   {r['id']}.jpg: {r['song'][:40]}")
    
    print(f"\n💾 Results saved to: config/soundies_auto_analysis.json")
    
    return results, unknown

if __name__ == '__main__':
    main()
