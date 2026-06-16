#!/usr/bin/env python3
"""
Analyze Wochenschau videos SEO status on YouTube.
Check current titles, descriptions, tags and identify issues.
"""

import json
import os
import requests
from datetime import datetime

# Public API für READ-Operationen
API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

def get_wochenschau_videos():
    """Fetch all Wochenschau videos from channel."""
    
    videos = []
    
    # Search for Wochenschau videos
    search_terms = ['wochenschau', 'newsreel', '511', '516', '750', '753']
    
    for term in search_terms:
        url = "https://youtube.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'channelId': CHANNEL_ID,
            'q': term,
            'type': 'video',
            'maxResults': 50,
            'key': API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                if video_id not in [v['video_id'] for v in videos]:
                    videos.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'][:200],
                        'published': item['snippet']['publishedAt']
                    })
    
    return videos

def get_video_details(video_ids):
    """Get detailed info for videos including tags."""
    
    # Batch request (max 50 per call)
    url = "https://youtube.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,statistics,contentDetails',
        'id': ','.join(video_ids[:50]),
        'key': API_KEY
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('items', [])
    return []

def analyze_seo_issues(video):
    """Analyze SEO issues for a video."""
    
    snippet = video['snippet']
    title = snippet.get('title', '')
    description = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    issues = []
    score = 100
    
    # 1. TITLE ANALYSIS (40 points)
    title_lower = title.lower()
    
    # Check for keyword at START
    keywords_at_start = ['wochenschau', 'newsreel', 'die deutsche']
    has_keyword_start = any(title_lower.startswith(kw) for kw in keywords_at_start)
    if not has_keyword_start:
        issues.append("❌ KEYWORD NICHT AM ANFANG - Title muss mit 'Wochenschau' oder 'Newsreel' starten!")
        score -= 15
    
    # Check for 8K marker
    if '8k' not in title_lower and '8K' not in title:
        issues.append("⚠️ Fehlt: 8K im Titel")
        score -= 5
    
    # Check for brand
    if '@remaike' not in title_lower:
        issues.append("⚠️ Fehlt: @remAIke_IT im Titel")
        score -= 5
    
    # Check title length
    if len(title) > 70:
        issues.append(f"⚠️ Titel zu lang: {len(title)} Zeichen (max 70)")
        score -= 5
    elif len(title) < 30:
        issues.append(f"⚠️ Titel zu kurz: {len(title)} Zeichen")
        score -= 5
    
    # 2. DESCRIPTION ANALYSIS (30 points)
    desc_lower = description.lower()
    
    # Check for CTAs
    cta_keywords = ['like', 'subscribe', 'comment', 'abonnieren']
    has_cta = any(kw in desc_lower for kw in cta_keywords)
    if not has_cta:
        issues.append("❌ KEINE CTAs (LIKE/SUBSCRIBE) in Description!")
        score -= 10
    
    # Check for hashtags
    has_hashtags = '#' in description
    if not has_hashtags:
        issues.append("❌ KEINE HASHTAGS in Description!")
        score -= 10
    
    # Check first 2 lines have keyword
    first_lines = description[:150].lower()
    if 'wochenschau' not in first_lines and 'newsreel' not in first_lines:
        issues.append("⚠️ Keyword nicht in ersten 2 Zeilen der Description!")
        score -= 5
    
    # Check for chapters
    if '0:00' not in description:
        issues.append("⚠️ Keine CHAPTERS in Description!")
        score -= 5
    
    # 3. TAGS ANALYSIS (10 points)
    if len(tags) < 5:
        issues.append(f"⚠️ Zu wenig Tags: nur {len(tags)} (min 5 empfohlen)")
        score -= 5
    elif len(tags) > 15:
        issues.append(f"⚠️ Zu viele Tags: {len(tags)} (max 15 empfohlen)")
        score -= 3
    
    # Check for essential tags
    essential_tags = ['wochenschau', 'newsreel', '8k', 'wwii', 'history']
    tag_lower = [t.lower() for t in tags]
    missing_tags = [t for t in essential_tags if not any(t in tl for tl in tag_lower)]
    if missing_tags:
        issues.append(f"⚠️ Fehlende wichtige Tags: {missing_tags}")
        score -= 2
    
    return {
        'score': max(0, score),
        'issues': issues,
        'title_length': len(title),
        'tag_count': len(tags)
    }

def main():
    print("=" * 70)
    print("🎬 WOCHENSCHAU SEO ANALYSE - remAIke_IT")
    print("=" * 70)
    print(f"📅 Datum: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    # Get videos
    print("🔍 Suche Wochenschau-Videos...")
    videos = get_wochenschau_videos()
    print(f"   Gefunden: {len(videos)} Videos")
    
    if not videos:
        print("❌ Keine Videos gefunden!")
        return
    
    # Get details
    video_ids = [v['video_id'] for v in videos]
    print("📊 Hole Video-Details...")
    details = get_video_details(video_ids)
    
    # Analyze
    results = []
    total_score = 0
    critical_issues = []
    
    print()
    print("=" * 70)
    print("📋 ANALYSE ERGEBNISSE")
    print("=" * 70)
    
    for video in details:
        title = video['snippet']['title']
        video_id = video['id']
        
        # Only analyze Wochenschau/Newsreel videos
        title_lower = title.lower()
        if 'wochenschau' not in title_lower and 'newsreel' not in title_lower and '511' not in title:
            continue
        
        analysis = analyze_seo_issues(video)
        total_score += analysis['score']
        
        result = {
            'video_id': video_id,
            'title': title,
            'score': analysis['score'],
            'issues': analysis['issues'],
            'tags': video['snippet'].get('tags', []),
            'view_count': video.get('statistics', {}).get('viewCount', 0)
        }
        results.append(result)
        
        # Print
        score_emoji = "🏆" if analysis['score'] >= 80 else "✅" if analysis['score'] >= 60 else "⚠️" if analysis['score'] >= 40 else "❌"
        print(f"\n{score_emoji} [{analysis['score']}/100] {title[:60]}...")
        print(f"   ID: {video_id}")
        
        if analysis['issues']:
            for issue in analysis['issues']:
                print(f"   {issue}")
                if '❌' in issue:
                    critical_issues.append({
                        'video_id': video_id,
                        'title': title,
                        'issue': issue
                    })
    
    # Summary
    if results:
        avg_score = total_score / len(results)
        print()
        print("=" * 70)
        print("📊 ZUSAMMENFASSUNG")
        print("=" * 70)
        print(f"   Videos analysiert: {len(results)}")
        print(f"   Durchschnittlicher SEO-Score: {avg_score:.1f}/100")
        print(f"   Kritische Issues: {len(critical_issues)}")
        
        if critical_issues:
            print()
            print("🚨 KRITISCHE PROBLEME:")
            for ci in critical_issues[:10]:
                print(f"   • {ci['title'][:50]}...")
                print(f"     → {ci['issue']}")
        
        # Save results
        output = {
            'date': datetime.now().isoformat(),
            'total_videos': len(results),
            'average_score': avg_score,
            'critical_issues_count': len(critical_issues),
            'videos': results
        }
        
        output_file = 'd:/remaike.TV/config/wochenschau_seo_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print()
        print(f"💾 Ergebnisse gespeichert: {output_file}")

if __name__ == '__main__':
    main()
