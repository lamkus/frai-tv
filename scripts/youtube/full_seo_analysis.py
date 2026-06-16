#!/usr/bin/env python3
"""
Analyze ALL videos from fresh_channel_scan.json for SEO issues.
No API calls needed - uses cached data.
"""

import json
from datetime import datetime
from collections import defaultdict
import re

# Load channel scan data
with open('d:/remaike.TV/config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

videos = data.get('videos', [])
print(f"=" * 70)
print(f"🎬 FULL CHANNEL SEO ANALYSE - remAIke_IT")
print(f"=" * 70)
print(f"📅 Scan-Datum: {data.get('fetched_at', 'Unknown')}")
print(f"📺 Total Videos: {data.get('total_videos', len(videos))}")
print()

# Category mapping
CATEGORIES = {
    'Betty Boop': ['betty boop', 'betty'],
    'Popeye': ['popeye', 'sailor'],
    'Superman/Fleischer': ['superman', 'fleischer'],
    'Looney Tunes': ['looney', 'bugs bunny', 'daffy', 'porky', 'tweety', 'sylvester', 'merrie melodies'],
    'Felix the Cat': ['felix the cat', 'felix'],
    'Asterix': ['asterix', 'obelix', 'gallier'],
    'Wochenschau': ['wochenschau', 'newsreel'],
    'Soundies': ['soundie'],
    'Alfred J. Kwak': ['alfred', 'kwak', 'quack'],
    'BraveStarr': ['bravestarr', 'brave star'],
    'Christmas': ['christmas', 'weihnacht', 'santa', 'xmas'],
    'Dokumentation': ['documentary', 'dokument', 'history'],
    'Public Domain Films': ['public domain', 'film', 'movie', '1930', '1940', '1950'],
}

def analyze_seo(video):
    """Analyze SEO score based on 2026 YouTube algorithm."""
    snippet = video.get('snippet', {})
    stats = video.get('statistics', {})
    
    title = snippet.get('title', '')
    description = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    score = 0
    issues = []
    
    title_lower = title.lower()
    
    # 1. TITLE ANALYSIS (40 points)
    
    # Keyword position - first 3 words (15 pts)
    first_words = ' '.join(title_lower.split()[:3])
    keywords = ['betty boop', 'popeye', 'superman', 'looney', 'felix', 'asterix', 
                'soundie', 'alfred', 'wochenschau', 'bravestarr', 'bugs bunny']
    
    has_keyword_start = any(kw in first_words for kw in keywords)
    if has_keyword_start:
        score += 15
    elif any(kw in title_lower for kw in keywords):
        score += 8
        issues.append("⚠️ Keyword nicht am ANFANG")
    else:
        issues.append("❌ KEIN erkennbares Keyword im Titel")
    
    # Title length (10 pts)
    if 50 <= len(title) <= 70:
        score += 10
    elif 40 <= len(title) <= 80:
        score += 5
        issues.append(f"⚠️ Titel: {len(title)} chars (ideal: 50-70)")
    else:
        issues.append(f"❌ Titel: {len(title)} chars (kritisch!)")
    
    # 8K marker (5 pts)
    if '8k' in title_lower:
        score += 5
    else:
        issues.append("⚠️ '8K' fehlt im Titel")
    
    # @remAIke brand (5 pts)
    if '@remaike' in title_lower:
        score += 5
    else:
        issues.append("⚠️ '@remAIke_IT' fehlt")
    
    # Year in parentheses (5 pts)
    if re.search(r'\(19\d{2}\)', title) or re.search(r'\(20\d{2}\)', title):
        score += 5
    else:
        issues.append("⚠️ Jahr fehlt (1932) Format")
    
    # 2. DESCRIPTION ANALYSIS (30 points)
    desc_lower = description.lower()
    
    # CTAs (10 pts)
    cta_words = ['like', 'subscribe', 'comment', 'abonnieren', 'kommentier']
    if any(w in desc_lower for w in cta_words):
        score += 10
    else:
        issues.append("❌ KEINE CTAs!")
    
    # Hashtags (10 pts)
    hashtag_count = description.count('#')
    if 3 <= hashtag_count <= 8:
        score += 10
    elif hashtag_count > 0:
        score += 5
        issues.append(f"⚠️ Hashtags: {hashtag_count} (ideal: 3-8)")
    else:
        issues.append("❌ KEINE Hashtags!")
    
    # Chapters/Timestamps (10 pts)
    if '0:00' in description:
        score += 10
    else:
        issues.append("⚠️ Keine Chapters")
    
    # 3. TAGS (10 points)
    if 5 <= len(tags) <= 15:
        score += 10
    elif len(tags) > 0:
        score += 5
        issues.append(f"⚠️ Tags: {len(tags)} (ideal: 5-15)")
    else:
        issues.append("❌ KEINE Tags!")
    
    # 4. ENGAGEMENT INDICATORS (20 points)
    views = int(stats.get('viewCount', 0))
    likes = int(stats.get('likeCount', 0))
    
    if views > 500:
        score += 10
    elif views > 100:
        score += 7
    elif views > 20:
        score += 3
    
    if likes > 20:
        score += 10
    elif likes > 5:
        score += 5
    elif likes > 0:
        score += 2
    
    return {
        'score': score,
        'issues': issues,
        'views': views,
        'likes': likes,
        'title_length': len(title),
        'tag_count': len(tags),
        'has_chapters': '0:00' in description
    }

def categorize_video(video):
    """Determine video category."""
    title = video.get('snippet', {}).get('title', '').lower()
    desc = video.get('snippet', {}).get('description', '').lower()
    
    for cat_name, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in title or kw in desc:
                return cat_name
    
    return 'Other'

# Analyze all videos
results_by_category = defaultdict(list)
all_results = []

for video in videos:
    status = video.get('status', {}).get('privacyStatus', 'unknown')
    if status != 'public':
        continue
    
    analysis = analyze_seo(video)
    category = categorize_video(video)
    
    result = {
        'video_id': video['id'],
        'title': video['snippet']['title'],
        'category': category,
        'score': analysis['score'],
        'issues': analysis['issues'],
        'views': analysis['views'],
        'likes': analysis['likes'],
        'tags': video['snippet'].get('tags', [])
    }
    
    results_by_category[category].append(result)
    all_results.append(result)

# Print results by category
print("=" * 70)
print("📊 ERGEBNISSE NACH KATEGORIE")
print("=" * 70)

for category in sorted(results_by_category.keys()):
    videos_in_cat = results_by_category[category]
    if not videos_in_cat:
        continue
    
    avg_score = sum(v['score'] for v in videos_in_cat) / len(videos_in_cat)
    avg_views = sum(v['views'] for v in videos_in_cat) / len(videos_in_cat)
    
    status = "🏆" if avg_score >= 70 else "✅" if avg_score >= 50 else "⚠️" if avg_score >= 30 else "❌"
    
    print(f"\n{status} {category.upper()} ({len(videos_in_cat)} Videos)")
    print(f"   Ø Score: {avg_score:.1f}/100 | Ø Views: {avg_views:.0f}")
    
    # Show worst 3 in each category
    worst = sorted(videos_in_cat, key=lambda x: x['score'])[:3]
    if worst:
        print(f"   🚨 Dringend:")
        for w in worst:
            print(f"      [{w['score']}] {w['title'][:45]}...")
            if w['issues'][:2]:
                for issue in w['issues'][:2]:
                    print(f"          {issue}")

# Overall summary
print()
print("=" * 70)
print("📊 GESAMTÜBERSICHT")
print("=" * 70)

total_avg = sum(r['score'] for r in all_results) / len(all_results) if all_results else 0
excellent = len([r for r in all_results if r['score'] >= 70])
good = len([r for r in all_results if 50 <= r['score'] < 70])
warning = len([r for r in all_results if 30 <= r['score'] < 50])
critical = len([r for r in all_results if r['score'] < 30])

print(f"   Analysierte Videos: {len(all_results)}")
print(f"   Durchschnittlicher Score: {total_avg:.1f}/100")
print()
print(f"   🏆 Excellent (70+): {excellent} ({excellent*100/len(all_results):.1f}%)")
print(f"   ✅ Good (50-69):    {good} ({good*100/len(all_results):.1f}%)")
print(f"   ⚠️ Warning (30-49): {warning} ({warning*100/len(all_results):.1f}%)")
print(f"   ❌ Critical (<30):  {critical} ({critical*100/len(all_results):.1f}%)")

# Most common issues
print()
print("=" * 70)
print("🔧 HÄUFIGSTE PROBLEME")
print("=" * 70)

issue_counts = defaultdict(int)
for r in all_results:
    for issue in r['issues']:
        # Simplify issue text
        if 'Keyword nicht am ANFANG' in issue:
            issue_counts['Keyword nicht am Anfang'] += 1
        elif 'KEIN erkennbares Keyword' in issue:
            issue_counts['Kein Keyword im Titel'] += 1
        elif 'KEINE CTAs' in issue:
            issue_counts['Keine CTAs'] += 1
        elif 'KEINE Hashtags' in issue:
            issue_counts['Keine Hashtags'] += 1
        elif 'Keine Chapters' in issue:
            issue_counts['Keine Chapters'] += 1
        elif '8K' in issue:
            issue_counts['8K fehlt'] += 1
        elif '@remAIke' in issue:
            issue_counts['@remAIke fehlt'] += 1
        elif 'Jahr fehlt' in issue:
            issue_counts['Jahr fehlt'] += 1
        elif 'Tags' in issue or 'KEINE Tags' in issue:
            issue_counts['Tag-Probleme'] += 1
        elif 'Titel:' in issue:
            issue_counts['Titel-Länge'] += 1

for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
    pct = count * 100 / len(all_results)
    print(f"   {count:3d} ({pct:5.1f}%) - {issue}")

# Worst performers overall
print()
print("=" * 70)
print("🚨 TOP 15 DRINGENDSTER HANDLUNGSBEDARF")
print("=" * 70)

worst_overall = sorted(all_results, key=lambda x: (x['score'], -x['views']))[:15]
for i, w in enumerate(worst_overall, 1):
    print(f"\n{i}. [{w['score']}/100] {w['title'][:55]}...")
    print(f"   Views: {w['views']} | Category: {w['category']}")
    for issue in w['issues'][:3]:
        print(f"   {issue}")

# Save results
output = {
    'date': datetime.now().isoformat(),
    'summary': {
        'total_analyzed': len(all_results),
        'average_score': total_avg,
        'excellent': excellent,
        'good': good,
        'warning': warning,
        'critical': critical
    },
    'by_category': {k: len(v) for k, v in results_by_category.items()},
    'worst_performers': worst_overall[:20],
    'all_videos': all_results
}

with open('d:/remaike.TV/config/full_seo_analysis_2026.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n💾 Ergebnisse: config/full_seo_analysis_2026.json")
