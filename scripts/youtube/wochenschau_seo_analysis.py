#!/usr/bin/env python3
"""
Comprehensive Wochenschau SEO Analysis
- Find ALL Wochenschau videos (any title format)
- Check SEO scores
- Analyze keyword positioning for YouTube search
"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from collections import defaultdict

OAUTH_FILE = 'config/youtube_oauth.json'
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

def get_youtube_client():
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

def extract_nr(title):
    """Extract Wochenschau number from various title formats"""
    patterns = [
        r'Wochenschau\s+Nr\.?\s*(\d+)',   # Wochenschau Nr. 516 or Wochenschau Nr 516
        r'Wochenschau\s+#(\d+)',           # Wochenschau #516
        r'Nr\.?\s*(\d+)',                  # Any Nr. followed by digits
        r'–\s*Wochenschau\s+Nr\.?\s*(\d+)', # – Wochenschau Nr. 516
    ]
    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None

def get_all_channel_videos(youtube):
    """Get all videos from channel"""
    videos = []
    upload_playlist = 'UU' + CHANNEL_ID[2:]
    
    next_page = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=upload_playlist,
            maxResults=50,
            pageToken=next_page
        )
        response = request.execute()
        
        for item in response.get('items', []):
            video_id = item['contentDetails']['videoId']
            videos.append(video_id)
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    return videos

def get_video_details(youtube, video_ids):
    """Get detailed info for videos"""
    all_details = []
    
    # Process in batches of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(batch)
        ).execute()
        
        for item in response.get('items', []):
            all_details.append(item)
    
    return all_details

def analyze_seo(video):
    """Analyze SEO score for a video"""
    snippet = video['snippet']
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    score = 0
    issues = []
    
    # Title analysis (40 points max)
    title_lower = title.lower()
    if 'wochenschau' in title_lower:
        score += 15
        # Keyword position
        wochenschau_pos = title_lower.find('wochenschau')
        if wochenschau_pos < 20:
            score += 10  # Keyword near beginning
        elif wochenschau_pos < 40:
            score += 5
        else:
            issues.append("Keyword 'Wochenschau' not near title start")
    else:
        issues.append("CRITICAL: 'Wochenschau' not in title!")
    
    if '8k' in title_lower or '4k' in title_lower:
        score += 5
    
    if '@remaike' in title_lower:
        score += 5
    
    if len(title) > 70:
        issues.append(f"Title too long ({len(title)} chars)")
    elif len(title) >= 50:
        score += 5
    
    # Description analysis (30 points max)
    desc_lower = desc.lower()
    if 'wochenschau' in desc_lower:
        score += 10
    else:
        issues.append("'Wochenschau' not in description")
    
    if 'subscribe' in desc_lower or 'like' in desc_lower:
        score += 5
    else:
        issues.append("No CTA in description")
    
    if '#' in desc:
        score += 5
    else:
        issues.append("No hashtags")
    
    if len(desc) > 200:
        score += 5
    
    if any(lang in desc_lower for lang in ['educational', 'bildungszweck', 'historical']):
        score += 5
    
    # Tags analysis (20 points max)
    if tags:
        score += 5
        tags_lower = [t.lower() for t in tags]
        if any('wochenschau' in t for t in tags_lower):
            score += 5
        if any('wwii' in t or 'ww2' in t or 'world war' in t for t in tags_lower):
            score += 5
        if len(tags) >= 10:
            score += 5
    else:
        issues.append("No tags!")
    
    # Views bonus (10 points max)
    stats = video.get('statistics', {})
    views = int(stats.get('viewCount', 0))
    if views > 1000:
        score += 10
    elif views > 500:
        score += 7
    elif views > 100:
        score += 5
    elif views > 50:
        score += 3
    
    return {
        'score': score,
        'max_score': 100,
        'issues': issues,
        'views': views
    }

def check_title_format(title):
    """Check which title format is used"""
    if re.match(r'^[A-Za-z].*–\s*Wochenschau', title):
        return "NEW (Event – Wochenschau Nr.)"
    elif re.match(r'^Wochenschau\s+Nr\.', title, re.IGNORECASE):
        return "OLD (Wochenschau Nr. ...)"
    elif re.match(r'^Die\s+Deutsche\s+Wochenschau', title, re.IGNORECASE):
        return "LEGACY (Die Deutsche Wochenschau)"
    else:
        return "OTHER"

def main():
    print("🔍 COMPREHENSIVE WOCHENSCHAU SEO ANALYSIS")
    print("=" * 70)
    
    youtube = get_youtube_client()
    
    # Get all videos
    print("\n📺 Fetching all channel videos...")
    video_ids = get_all_channel_videos(youtube)
    print(f"   Total videos on channel: {len(video_ids)}")
    
    # Get details
    print("📋 Fetching video details...")
    all_videos = get_video_details(youtube, video_ids)
    
    # Find Wochenschau videos
    wochenschau_videos = []
    for video in all_videos:
        title = video['snippet']['title']
        nr = extract_nr(title)
        if nr or 'wochenschau' in title.lower():
            wochenschau_videos.append({
                'video': video,
                'nr': nr,
                'title': title,
                'format': check_title_format(title)
            })
    
    # Sort by number
    wochenschau_videos.sort(key=lambda x: x['nr'] or 999)
    
    print(f"\n📺 WOCHENSCHAU VIDEOS FOUND: {len(wochenschau_videos)}")
    print("=" * 70)
    
    # Title format analysis
    format_counts = defaultdict(list)
    for v in wochenschau_videos:
        format_counts[v['format']].append(v)
    
    print("\n📊 TITLE FORMAT ANALYSIS:")
    print("-" * 40)
    for fmt, videos in format_counts.items():
        print(f"   {fmt}: {len(videos)} videos")
        for v in videos[:3]:
            print(f"      Nr. {v['nr']}: {v['title'][:50]}...")
        if len(videos) > 3:
            print(f"      ... and {len(videos)-3} more")
    
    # SEO Analysis
    print("\n📈 SEO SCORES:")
    print("-" * 70)
    
    total_score = 0
    issues_count = defaultdict(int)
    
    for v in wochenschau_videos:
        seo = analyze_seo(v['video'])
        total_score += seo['score']
        
        status = "✅" if seo['score'] >= 70 else "⚠️" if seo['score'] >= 50 else "❌"
        print(f"Nr. {v['nr']:3d} | {status} {seo['score']:2d}/100 | {seo['views']:5d} views | {v['format'][:20]}")
        
        for issue in seo['issues']:
            issues_count[issue] += 1
    
    avg_score = total_score / len(wochenschau_videos) if wochenschau_videos else 0
    print(f"\n📊 AVERAGE SEO SCORE: {avg_score:.1f}/100")
    
    # Common issues
    print("\n⚠️ COMMON SEO ISSUES:")
    print("-" * 40)
    for issue, count in sorted(issues_count.items(), key=lambda x: -x[1]):
        print(f"   {count}x: {issue}")
    
    # Keyword positioning analysis
    print("\n🔑 KEYWORD 'WOCHENSCHAU' POSITION IN TITLES:")
    print("-" * 40)
    positions = []
    for v in wochenschau_videos:
        title = v['title'].lower()
        pos = title.find('wochenschau')
        if pos >= 0:
            positions.append(pos)
            category = "FRONT (0-15)" if pos < 15 else "MIDDLE (15-40)" if pos < 40 else "BACK (40+)"
            print(f"   Nr. {v['nr']}: Position {pos:2d} [{category}]")
    
    if positions:
        avg_pos = sum(positions) / len(positions)
        print(f"\n   Average position: {avg_pos:.1f}")
        print(f"   Best: {min(positions)}, Worst: {max(positions)}")
    
    # YouTube SEO Recommendations
    print("\n" + "=" * 70)
    print("🎯 YOUTUBE SEO RECOMMENDATIONS FOR 'WOCHENSCHAU' RANKING")
    print("=" * 70)
    print("""
1. TITLE KEYWORD POSITION (CRITICAL!)
   YouTube heavily weights the FIRST 60 characters of titles.
   Current issue: New format puts event BEFORE 'Wochenschau'
   
   OLD:  "Wochenschau Nr. 516 (1940) | 8K HQ"          ← Keyword at pos 0
   NEW:  "Poland Occupied – Wochenschau Nr. 477"      ← Keyword at pos 18
   
   RECOMMENDATION: Consider "Wochenschau Nr. XXX: [Event]" format
   
2. DESCRIPTION FIRST 2 LINES
   Only first ~160 chars show in search results!
   Always start with: "Die Deutsche Wochenschau Nr. XXX..."
   
3. TAGS PRIORITY ORDER
   First 3 tags matter most:
   - "Wochenschau" (exact match)
   - "Deutsche Wochenschau"  
   - "Die Deutsche Wochenschau Nr. [NUMBER]"
   
4. LOCAL SEO OPPORTUNITY
   Add locations mentioned in each episode:
   - City names (Berlin, Paris, Warschau, Stalingrad)
   - Country names (Deutschland, Frankreich, Polen)
   - Battle locations (Normandie, Kursk, El Alamein)
   
   This helps people searching for "Wochenschau Berlin" or "WWII Paris footage"

5. ENGAGEMENT SIGNALS
   - Ask questions in description to encourage comments
   - Add timestamps/chapters for longer videos
   - Pin a comment with historical context
""")
    
    # Format inconsistency warning
    if len(format_counts) > 1:
        print("\n⚠️ TITLE FORMAT INCONSISTENCY DETECTED!")
        print("-" * 40)
        print("   You have multiple title formats. This can confuse both")
        print("   YouTube algorithm and viewers. Consider standardizing.")
        print()
        print("   OPTIONS:")
        print("   A) 'Wochenschau Nr. XXX: [Event] (YYYY) | 8K'  ← Keyword first")
        print("   B) '[Event] – Wochenschau Nr. XXX (YYYY) | 8K' ← Event first")
        print()
        print("   For SEARCH ranking: Option A is better")
        print("   For CLICK-THROUGH: Option B might be more engaging")

if __name__ == '__main__':
    main()
