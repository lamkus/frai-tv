#!/usr/bin/env python3
"""
Analyze Comic/Cartoon videos SEO status on remAIke_IT channel.
Uses Public API for READ operations (quota-efficient).
"""

import json
import os
import requests
from datetime import datetime

# Load API key from file
API_KEY_FILE = "d:/remaike.TV/config/youtube_api_key.txt"
if os.path.exists(API_KEY_FILE):
    with open(API_KEY_FILE, 'r') as f:
        API_KEY = f.read().strip()
else:
    API_KEY = os.getenv('YOUTUBE_API_KEY', '')

CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"  # Replace first UC with UU

# Comic/Cartoon keywords to search for
COMIC_KEYWORDS = [
    'asterix', 'obelix', 'popeye', 'betty boop', 'felix', 'looney', 
    'superman', 'fleischer', 'cartoon', 'animation', 'animated',
    'tom jerry', 'bugs bunny', 'daffy', 'porky', 'woody woodpecker',
    'casper', 'mighty mouse', 'heckle jeckle', 'terrytoons'
]

def get_all_videos():
    """Get all videos from upload playlist using Public API."""
    
    videos = []
    next_page = None
    
    print("📥 Lade alle Videos vom Channel (Public API)...")
    
    while True:
        url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
        params = {
            'part': 'snippet,contentDetails',
            'playlistId': UPLOAD_PLAYLIST,
            'maxResults': 50,
            'key': API_KEY
        }
        if next_page:
            params['pageToken'] = next_page
        
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            print(response.text)
            break
        
        data = response.json()
        
        for item in data.get('items', []):
            snippet = item.get('snippet', {})
            videos.append({
                'video_id': item['contentDetails']['videoId'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', '')[:300],
                'published': snippet.get('publishedAt', ''),
                'playlist_position': snippet.get('position', 0)
            })
        
        next_page = data.get('nextPageToken')
        if not next_page:
            break
        
        print(f"   ... {len(videos)} Videos geladen")
    
    return videos

def filter_comic_videos(all_videos):
    """Filter videos that are comics/cartoons."""
    
    comic_videos = []
    
    for video in all_videos:
        title_lower = video['title'].lower()
        desc_lower = video['description'].lower()
        
        # Check if any comic keyword matches
        for keyword in COMIC_KEYWORDS:
            if keyword in title_lower or keyword in desc_lower:
                video['matched_keyword'] = keyword
                comic_videos.append(video)
                break
    
    return comic_videos

def get_video_details_batch(video_ids):
    """Get detailed info for videos including tags, views, etc."""
    
    results = []
    
    # Process in batches of 50
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        
        url = "https://youtube.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(batch),
            'key': API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            results.extend(data.get('items', []))
        else:
            print(f"⚠️ Batch error: {response.status_code}")
    
    return results

def analyze_seo_score(video):
    """Calculate SEO score based on 2026 YouTube algorithm factors."""
    
    snippet = video.get('snippet', {})
    stats = video.get('statistics', {})
    
    title = snippet.get('title', '')
    description = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    score = 0
    issues = []
    
    # 1. TITLE ANALYSIS (40 points max)
    title_lower = title.lower()
    
    # Keyword at START (15 points)
    comic_keywords = ['asterix', 'popeye', 'betty boop', 'felix', 'looney', 'superman', 
                      'cartoon', 'animation', 'bugs bunny', 'woody', 'casper']
    keyword_at_start = any(title_lower.startswith(kw) for kw in comic_keywords)
    if keyword_at_start:
        score += 15
    else:
        # Check if keyword is in first 3 words
        first_words = ' '.join(title_lower.split()[:3])
        if any(kw in first_words for kw in comic_keywords):
            score += 10
            issues.append("⚠️ Keyword nicht ganz am Anfang")
        else:
            issues.append("❌ KEYWORD NICHT AM ANFANG des Titels!")
    
    # Title length (10 points)
    if 50 <= len(title) <= 70:
        score += 10
    elif 40 <= len(title) <= 80:
        score += 5
        issues.append(f"⚠️ Titel-Länge: {len(title)} chars (ideal: 50-70)")
    else:
        issues.append(f"❌ Titel-Länge kritisch: {len(title)} chars")
    
    # 8K marker (5 points)
    if '8k' in title_lower:
        score += 5
    else:
        issues.append("⚠️ '8K' fehlt im Titel")
    
    # Brand marker (5 points)
    if '@remaike' in title_lower:
        score += 5
    else:
        issues.append("⚠️ '@remAIke_IT' fehlt im Titel")
    
    # Year in title (5 points) - helps for historical content
    import re
    if re.search(r'\(19\d{2}\)', title) or re.search(r'\(20\d{2}\)', title):
        score += 5
    else:
        issues.append("⚠️ Jahr fehlt im Titel (1932) Format")
    
    # 2. DESCRIPTION ANALYSIS (30 points max)
    desc_lower = description.lower()
    
    # CTAs present (10 points)
    cta_keywords = ['like', 'subscribe', 'comment', 'abonnieren']
    if any(kw in desc_lower for kw in cta_keywords):
        score += 10
    else:
        issues.append("❌ KEINE CTAs in Description!")
    
    # Hashtags (10 points)
    if '#' in description:
        hashtag_count = description.count('#')
        if 2 <= hashtag_count <= 8:
            score += 10
        elif hashtag_count > 0:
            score += 5
            issues.append(f"⚠️ Hashtag-Anzahl: {hashtag_count} (ideal: 3-5)")
    else:
        issues.append("❌ KEINE HASHTAGS!")
    
    # Chapters (10 points)
    if '0:00' in description:
        score += 10
    else:
        issues.append("⚠️ Keine CHAPTERS/Timestamps")
    
    # 3. TAGS ANALYSIS (10 points max)
    if 5 <= len(tags) <= 15:
        score += 10
    elif len(tags) > 0:
        score += 5
        issues.append(f"⚠️ Tags: {len(tags)} (ideal: 5-15)")
    else:
        issues.append("❌ KEINE TAGS!")
    
    # 4. ENGAGEMENT BONUS (20 points max) - indicates if SEO is working
    views = int(stats.get('viewCount', 0))
    likes = int(stats.get('likeCount', 0))
    
    if views > 1000:
        score += 10
    elif views > 100:
        score += 5
    
    if likes > 50:
        score += 10
    elif likes > 10:
        score += 5
    
    return {
        'score': score,
        'issues': issues,
        'views': views,
        'likes': likes,
        'title_length': len(title),
        'tag_count': len(tags)
    }

def categorize_by_series(videos):
    """Group videos by series for better analysis."""
    
    series = {
        'Betty Boop': [],
        'Popeye': [],
        'Superman/Fleischer': [],
        'Looney Tunes': [],
        'Felix the Cat': [],
        'Asterix': [],
        'Other Cartoons': []
    }
    
    for video in videos:
        title_lower = video['snippet']['title'].lower()
        
        if 'betty boop' in title_lower or 'betty' in title_lower:
            series['Betty Boop'].append(video)
        elif 'popeye' in title_lower:
            series['Popeye'].append(video)
        elif 'superman' in title_lower or 'fleischer' in title_lower:
            series['Superman/Fleischer'].append(video)
        elif 'looney' in title_lower or 'bugs' in title_lower or 'daffy' in title_lower or 'porky' in title_lower:
            series['Looney Tunes'].append(video)
        elif 'felix' in title_lower:
            series['Felix the Cat'].append(video)
        elif 'asterix' in title_lower or 'obelix' in title_lower:
            series['Asterix'].append(video)
        else:
            series['Other Cartoons'].append(video)
    
    return series

def main():
    print("=" * 70)
    print("🎬 COMIC/CARTOON SEO ANALYSE - remAIke_IT")
    print("=" * 70)
    print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"🔑 API Key: {API_KEY[:10]}..." if API_KEY else "❌ Kein API Key!")
    print()
    
    if not API_KEY:
        print("Bitte API Key setzen!")
        return
    
    # Get all videos
    all_videos = get_all_videos()
    print(f"\n✅ Total Videos: {len(all_videos)}")
    
    # Filter comics
    comic_videos = filter_comic_videos(all_videos)
    print(f"🎨 Comic/Cartoon Videos: {len(comic_videos)}")
    
    if not comic_videos:
        print("❌ Keine Comic-Videos gefunden!")
        return
    
    # Get detailed info
    video_ids = [v['video_id'] for v in comic_videos]
    print(f"\n📊 Hole Details für {len(video_ids)} Videos...")
    details = get_video_details_batch(video_ids)
    
    # Analyze by series
    series = categorize_by_series(details)
    
    # Results
    all_results = []
    
    print()
    print("=" * 70)
    print("📋 SEO ANALYSE NACH SERIE")
    print("=" * 70)
    
    for series_name, videos in series.items():
        if not videos:
            continue
        
        print(f"\n{'='*50}")
        print(f"📺 {series_name.upper()} ({len(videos)} Videos)")
        print(f"{'='*50}")
        
        series_scores = []
        series_issues = []
        
        for video in videos[:10]:  # Show max 10 per series
            analysis = analyze_seo_score(video)
            series_scores.append(analysis['score'])
            
            title = video['snippet']['title'][:55]
            score_emoji = "🏆" if analysis['score'] >= 80 else "✅" if analysis['score'] >= 60 else "⚠️" if analysis['score'] >= 40 else "❌"
            
            print(f"\n{score_emoji} [{analysis['score']}/100] {title}...")
            print(f"   Views: {analysis['views']:,} | Likes: {analysis['likes']}")
            
            if analysis['issues'][:3]:
                for issue in analysis['issues'][:3]:
                    print(f"   {issue}")
            
            # Store result
            all_results.append({
                'video_id': video['id'],
                'series': series_name,
                'title': video['snippet']['title'],
                'score': analysis['score'],
                'issues': analysis['issues'],
                'views': analysis['views'],
                'tags': video['snippet'].get('tags', [])
            })
        
        if series_scores:
            avg = sum(series_scores) / len(series_scores)
            print(f"\n   📊 Durchschnitt {series_name}: {avg:.1f}/100")
    
    # Summary
    print()
    print("=" * 70)
    print("📊 GESAMTZUSAMMENFASSUNG")
    print("=" * 70)
    
    if all_results:
        total_avg = sum(r['score'] for r in all_results) / len(all_results)
        print(f"   Videos analysiert: {len(all_results)}")
        print(f"   Durchschnittlicher Score: {total_avg:.1f}/100")
        
        # Count issues
        critical = len([r for r in all_results if r['score'] < 40])
        warning = len([r for r in all_results if 40 <= r['score'] < 60])
        good = len([r for r in all_results if 60 <= r['score'] < 80])
        excellent = len([r for r in all_results if r['score'] >= 80])
        
        print(f"\n   🏆 Excellent (80+): {excellent}")
        print(f"   ✅ Good (60-79): {good}")
        print(f"   ⚠️ Warning (40-59): {warning}")
        print(f"   ❌ Critical (<40): {critical}")
        
        # Worst performers
        worst = sorted(all_results, key=lambda x: x['score'])[:5]
        print(f"\n🚨 DRINGENDSTER HANDLUNGSBEDARF:")
        for w in worst:
            print(f"   [{w['score']}] {w['title'][:50]}...")
    
    # Save results
    output = {
        'date': datetime.now().isoformat(),
        'total_analyzed': len(all_results),
        'videos': all_results
    }
    
    output_file = 'd:/remaike.TV/config/comic_seo_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Ergebnisse: {output_file}")

if __name__ == '__main__':
    main()
