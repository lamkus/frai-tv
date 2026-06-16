#!/usr/bin/env python3
"""
Soundies Auto-Analyzer - Extracts artist info from YouTube metadata and cross-references with web
"""
import requests
import os
import json
import re

API_KEY = os.getenv('YOUTUBE_API_KEY')

# Alle Soundie Video IDs
SOUNDIE_IDS = [
    'mReDNz-Exdk', '6XVj6G3qNYY', 'ukmrI7DlXkc', 'oA7XcqVM1Vo', 'OvBqUlzTunI',
    'mDSdzFc572Y', 'hAs6lunYl-E', '1zKpqdriv70', 'Z2SxppvCWvE', 'rprpMDyTWRI',
    'NAk0QvvaT7M', 'w82vzaGBqwE', 'GerP7_evS9o', 'D-LL4VuR5Pg', 'LJp-M01OI-8',
    'HvwtRYp43eU', '2yGX3wy-4SQ', 'hIsTWWP-YkQ', '340C9lsoyYk', 'A8LWgWF5f5k', 'DHogGPBbzRI'
]

def get_youtube_metadata():
    """Fetch full metadata from YouTube API"""
    results = []
    for i in range(0, len(SOUNDIE_IDS), 50):
        batch = SOUNDIE_IDS[i:i+50]
        url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={",".join(batch)}&key={API_KEY}'
        r = requests.get(url).json()
        for item in r.get('items', []):
            results.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'tags': item['snippet'].get('tags', []),
                'thumbnail': item['snippet']['thumbnails'].get('maxres', 
                    item['snippet']['thumbnails'].get('high', {})).get('url', '')
            })
    return results

def extract_artist_from_text(text):
    """Try to extract artist names from description/tags"""
    # Common patterns
    patterns = [
        r'(?:performed by|featuring|artist:|singer:|band:|orchestra:)\s*([A-Z][a-zA-Z\s&]+)',
        r'(?:by|feat\.?)\s+([A-Z][a-zA-Z\s&]+?)(?:\s*[-|,\n])',
        r'^([A-Z][a-zA-Z\s&]+?)\s*[-–]\s*',  # "Artist - Song" format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def analyze_tags_for_artist(tags):
    """Check tags for potential artist names"""
    # Known artist indicators
    artist_keywords = ['orchestra', 'band', 'trio', 'quartet', 'brothers', 'sisters', 
                      'singers', 'players', 'combo', 'ensemble']
    
    for tag in tags:
        tag_lower = tag.lower()
        for keyword in artist_keywords:
            if keyword in tag_lower:
                return tag
    
    # Check for capitalized multi-word names (likely artists)
    for tag in tags:
        words = tag.split()
        if len(words) >= 2 and all(w[0].isupper() for w in words if w):
            # Could be an artist name
            if not any(x in tag.lower() for x in ['soundie', 'vintage', 'music', 'jazz', 'swing', 'public domain', '8k', '4k']):
                return tag
    return None

def main():
    print("🎬 SOUNDIES AUTO-ANALYZER")
    print("=" * 60)
    
    # 1. Get YouTube metadata
    print("\n📥 Fetching YouTube metadata...")
    videos = get_youtube_metadata()
    print(f"   Got {len(videos)} videos")
    
    # Save raw data
    with open('config/soundies_full_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    
    # 2. Analyze each video
    print("\n🔍 Analyzing metadata for artist info...")
    print("-" * 60)
    
    analysis_results = []
    
    for v in videos:
        result = {
            'id': v['id'],
            'title': v['title'],
            'extracted_song': v['title'].split('|')[0].replace('Soundie:', '').strip(),
            'artist_from_desc': None,
            'artist_from_tags': None,
            'thumbnail_url': v['thumbnail'],
            'description_preview': v['description'][:500]
        }
        
        # Try to extract artist from description
        result['artist_from_desc'] = extract_artist_from_text(v['description'])
        
        # Try to find artist in tags
        result['artist_from_tags'] = analyze_tags_for_artist(v['tags'])
        
        # Check if description contains known artist names
        known_artists = [
            'Yvonne De Carlo', 'Johnny Long', 'Tommy Dorsey', 'The Three Suns',
            'The King\'s Men', 'Mills Brothers', 'Duke Ellington', 'Cab Calloway',
            'Louis Armstrong', 'Fats Waller', 'Count Basie', 'Benny Goodman',
            'Glenn Miller', 'Artie Shaw', 'The Ink Spots', 'Andrews Sisters',
            'Doris Day', 'Nat King Cole', 'Louis Jordan', 'Dorothy Dandridge'
        ]
        
        for artist in known_artists:
            if artist.lower() in v['description'].lower() or artist.lower() in ' '.join(v['tags']).lower():
                result['known_artist_found'] = artist
                break
        
        analysis_results.append(result)
        
        # Print findings
        print(f"\n📹 {v['id']}: {result['extracted_song'][:40]}")
        if result.get('known_artist_found'):
            print(f"   ✅ KNOWN ARTIST: {result['known_artist_found']}")
        elif result['artist_from_desc']:
            print(f"   📝 From description: {result['artist_from_desc']}")
        elif result['artist_from_tags']:
            print(f"   🏷️  From tags: {result['artist_from_tags']}")
        else:
            print(f"   ❓ No artist found in metadata")
            print(f"   🖼️  Thumbnail: {v['thumbnail'][:60]}...")
    
    # Save analysis
    with open('config/soundies_auto_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    found = [r for r in analysis_results if r.get('known_artist_found') or r.get('artist_from_desc') or r.get('artist_from_tags')]
    unknown = [r for r in analysis_results if not (r.get('known_artist_found') or r.get('artist_from_desc') or r.get('artist_from_tags'))]
    
    print(f"✅ Artists found: {len(found)}")
    print(f"❓ Unknown: {len(unknown)}")
    
    if unknown:
        print("\n🖼️  THUMBNAILS FOR UNKNOWN VIDEOS (for AI analysis):")
        for r in unknown:
            print(f"   {r['id']}: {r['thumbnail_url']}")
    
    print(f"\n💾 Saved to: config/soundies_auto_analysis.json")
    print(f"💾 Full metadata: config/soundies_full_metadata.json")

if __name__ == '__main__':
    main()
