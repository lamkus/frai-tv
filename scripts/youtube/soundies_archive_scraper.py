#!/usr/bin/env python3
"""
Soundies Archive.org Scraper - Gets artist info from Internet Archive
"""
import requests
import json
import re
import time

# Song titles to search for
SOUNDIE_SONGS = [
    ("mReDNz-Exdk", "Lamp of Memory"),
    ("6XVj6G3qNYY", "Jiveroo"),
    ("ukmrI7DlXkc", "In a Shanty in Old Shanty Town"),
    ("oA7XcqVM1Vo", "I Can't Give You Anything But Love"),
    ("OvBqUlzTunI", "Hollywood Boogie"),
    ("mDSdzFc572Y", "What This Country Needs"),
    ("hAs6lunYl-E", "A Jazz Etude"),
    ("1zKpqdriv70", "Ten Pretty Girls"),
    ("Z2SxppvCWvE", "Hawaiian Hula Song"),
    ("rprpMDyTWRI", "Zig Me Baby with a Gentle Zag"),
    ("NAk0QvvaT7M", "Who's Yehudi"),
    ("w82vzaGBqwE", "A Little Robin Told Me So"),
    ("GerP7_evS9o", "Beyond the Blue Horizon"),
    ("D-LL4VuR5Pg", "Lullaby of Broadway"),
    ("LJp-M01OI-8", "Chime Bells"),
    ("HvwtRYp43eU", "Got to Be This or That"),
    ("2yGX3wy-4SQ", "Havana Madrid Show"),
    ("hIsTWWP-YkQ", "Once in a While"),
    ("340C9lsoyYk", "Tica Ti Tica Ta"),
    ("A8LWgWF5f5k", "The Hut-Sut Song"),
    ("DHogGPBbzRI", "Sweet Sue"),
]

def search_archive_org(song_title):
    """Search Archive.org for Soundie with this title"""
    # Clean title for search
    clean_title = re.sub(r'[^\w\s]', '', song_title).strip()
    
    # Search Archive.org
    search_url = f"https://archive.org/advancedsearch.php?q=soundie+{clean_title.replace(' ', '+')}&fl[]=identifier,description,title,subject&rows=10&output=json"
    
    try:
        r = requests.get(search_url, timeout=10)
        data = r.json()
        
        results = data.get('response', {}).get('docs', [])
        
        for doc in results:
            title = doc.get('title', '').lower()
            if any(word.lower() in title for word in clean_title.split()[:2]):
                return {
                    'identifier': doc.get('identifier'),
                    'title': doc.get('title'),
                    'description': doc.get('description', ''),
                    'subject': doc.get('subject', [])
                }
    except Exception as e:
        print(f"   Error searching: {e}")
    
    return None

def get_archive_metadata(identifier):
    """Get detailed metadata from Archive.org item"""
    url = f"https://archive.org/metadata/{identifier}"
    
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        
        metadata = data.get('metadata', {})
        return {
            'identifier': identifier,
            'title': metadata.get('title'),
            'description': metadata.get('description'),
            'date': metadata.get('date') or metadata.get('proddate'),
            'creator': metadata.get('creator'),
            'subject': metadata.get('subject'),
            'notes': metadata.get('notes'),
        }
    except Exception as e:
        print(f"   Error getting metadata: {e}")
    
    return None

def extract_performer(metadata):
    """Extract performer info from Archive.org metadata"""
    if not metadata:
        return None, None
    
    # Check description for common patterns
    desc = str(metadata.get('description', '') or '')
    
    # Patterns: "with Artist Name", "featuring Artist", "performed by Artist"
    patterns = [
        r'with\s+([A-Z][a-zA-Z\s,&]+?)(?:\s+and\s+|$|\n)',
        r'featuring\s+([A-Z][a-zA-Z\s,&]+)',
        r'performed by\s+([A-Z][a-zA-Z\s,&]+)',
        r'danced by\s+([A-Z][a-zA-Z\s,&]+)',
        r'sung by\s+([A-Z][a-zA-Z\s,&]+)',
        r'^([A-Z][a-zA-Z\s]+(?:Orchestra|Band|Trio|Quartet|Sisters|Brothers))',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, desc, re.IGNORECASE | re.MULTILINE)
        if match:
            performer = match.group(1).strip()
            return performer, 'archive.org'
    
    # Check creator field
    creator = metadata.get('creator')
    if creator:
        return creator, 'archive.org creator'
    
    return None, None

def main():
    print("🎬 SOUNDIES ARCHIVE.ORG RESEARCHER")
    print("=" * 70)
    
    results = []
    
    for video_id, song_title in SOUNDIE_SONGS:
        print(f"\n🔍 Searching: {song_title}")
        
        result = {
            'video_id': video_id,
            'song': song_title,
            'archive_found': False,
            'performer': None,
            'source': None,
            'archive_id': None,
            'year': None
        }
        
        # Search Archive.org
        search_result = search_archive_org(song_title)
        
        if search_result:
            result['archive_found'] = True
            result['archive_id'] = search_result['identifier']
            print(f"   ✅ Found: {search_result['identifier']}")
            
            # Get detailed metadata
            metadata = get_archive_metadata(search_result['identifier'])
            
            if metadata:
                performer, source = extract_performer(metadata)
                if performer:
                    result['performer'] = performer
                    result['source'] = source
                    result['year'] = metadata.get('date')
                    print(f"   🎤 Performer: {performer}")
                else:
                    # Print raw description for manual analysis
                    desc = metadata.get('description', '')
                    if desc:
                        print(f"   📝 Description: {desc[:100]}")
        else:
            print(f"   ❌ Not found on Archive.org")
        
        results.append(result)
        time.sleep(0.5)  # Be nice to Archive.org
    
    # Save results
    with open('config/soundies_archive_research.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ARCHIVE.ORG RESEARCH SUMMARY")
    print("=" * 70)
    
    found_performers = [r for r in results if r['performer']]
    found_archive = [r for r in results if r['archive_found']]
    
    print(f"✅ Found on Archive.org: {len(found_archive)}/21")
    print(f"🎤 Performers identified: {len(found_performers)}/21")
    
    if found_performers:
        print("\n🎵 IDENTIFIED PERFORMERS:")
        for r in found_performers:
            print(f"   {r['video_id']}: {r['performer']} - {r['song']}")
    
    print(f"\n💾 Saved to: config/soundies_archive_research.json")

if __name__ == '__main__':
    main()
