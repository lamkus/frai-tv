#!/usr/bin/env python3
"""
COMPLETE CHANNEL AUDIT - remAIke_IT
Check ALL videos against 2026 YouTube SEO best practices

Rules:
1. Keyword at START of title (first 3 words)
2. Title max 60-70 chars
3. 8K marker in title
4. @remAIke_IT branding
5. Year in title (1932) format
6. CTAs in description (LIKE/SUBSCRIBE)
7. Hashtags 3-8 (not excessive)
8. Chapters (0:00 format)
9. Tags 5-15 (not too many, not too few)
"""

import json
import re
from datetime import datetime
from collections import defaultdict

# Load fresh channel scan
SCAN_FILE = 'd:/remaike.TV/config/fresh_channel_scan.json'
OUTPUT_FILE = 'd:/remaike.TV/config/complete_audit_2026.json'

# Category detection keywords
CATEGORIES = {
    'Soundies': ['soundie'],
    'Wochenschau': ['wochenschau', 'newsreel'],
    'Alfred J. Kwak': ['alfred', 'kwak', 'quack'],
    'Betty Boop': ['betty boop', 'betty'],
    'Popeye': ['popeye'],
    'Superman/Fleischer': ['superman', 'fleischer'],
    'Felix the Cat': ['felix the cat', 'felix'],
    'Looney Tunes': ['looney', 'bugs bunny', 'porky', 'daffy', 'tweety', 'merrie melodies'],
    'BraveStarr': ['bravestarr', 'brave star'],
    'Christmas': ['christmas', 'weihnacht', 'santa', 'xmas'],
    'Asterix': ['asterix', 'obelix', 'gallier'],
    'Dokumentation': ['documentary', 'dokument'],
}

# Expected keywords per category (should be at START of title)
CATEGORY_KEYWORDS = {
    'Soundies': ['song title first'],  # Special: Song title should be first, "Soundie" second
    'Wochenschau': ['wochenschau'],
    'Alfred J. Kwak': ['alfred'],
    'Betty Boop': ['betty boop'],
    'Popeye': ['popeye'],
    'Superman/Fleischer': ['superman', 'fleischer'],
    'Felix the Cat': ['felix'],
    'Looney Tunes': ['looney', 'bugs', 'porky', 'daffy'],
    'BraveStarr': ['bravestarr'],
    'Christmas': ['christmas', 'weihnacht'],
    'Asterix': ['asterix'],
}

def categorize_video(title, description=''):
    """Detect video category."""
    text = (title + ' ' + description).lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            return cat
    return 'Other'

def audit_video(video):
    """
    Audit a single video against 2026 SEO rules.
    Returns score (0-100) and list of issues.
    """
    snippet = video.get('snippet', {})
    stats = video.get('statistics', {})
    
    title = snippet.get('title', '')
    description = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    title_lower = title.lower()
    desc_lower = description.lower()
    
    score = 0
    issues = []
    recommendations = []
    
    category = categorize_video(title, description)
    
    # =========================================
    # TITLE ANALYSIS (50 points total)
    # =========================================
    
    # 1. Title length (15 pts)
    title_len = len(title)
    if 50 <= title_len <= 70:
        score += 15
    elif 40 <= title_len <= 80:
        score += 8
        if title_len > 70:
            issues.append(f"⚠️ Titel zu lang: {title_len} chars (max 70)")
            recommendations.append(f"Titel auf max 70 Zeichen kürzen")
        else:
            issues.append(f"⚠️ Titel kurz: {title_len} chars (ideal 50-70)")
    else:
        if title_len > 80:
            issues.append(f"❌ Titel VIEL zu lang: {title_len} chars!")
            recommendations.append(f"DRINGEND: Titel auf max 70 Zeichen kürzen")
        else:
            issues.append(f"❌ Titel zu kurz: {title_len} chars")
    
    # 2. Keyword at START - first 3 words (15 pts)
    first_words = ' '.join(title_lower.split()[:3])
    
    # Special handling per category
    keyword_at_start = False
    
    if category == 'Soundies':
        # For Soundies: Should NOT start with "Soundie:" anymore
        # Song title should be first
        if title_lower.startswith('soundie:'):
            issues.append("❌ 'Soundie:' am Anfang - Song-Titel sollte zuerst!")
            recommendations.append("Format: [Song] (1940s) | Soundie | 8K HQ | @remAIke_IT")
        elif '| soundie |' in title_lower or 'soundie' in first_words:
            keyword_at_start = True
            score += 15
        else:
            # Check if it looks like a song title format
            if '(1940s)' in title or '(194' in title:
                keyword_at_start = True
                score += 15
    
    elif category == 'Wochenschau':
        if 'wochenschau' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("❌ 'Wochenschau' nicht am Anfang!")
            recommendations.append("Format: Wochenschau Nr. XXX (Jahr) | 8K HQ | @remAIke_IT")
    
    elif category == 'Alfred J. Kwak':
        if 'alfred' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("❌ 'Alfred' nicht am Anfang!")
            recommendations.append("Format: Alfred J. Kwak (XX): [Titel] | 8K | @remAIke_IT")
    
    elif category == 'Betty Boop':
        if 'betty' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'Betty Boop' nicht am Anfang")
            recommendations.append("'Betty Boop' an den Anfang des Titels")
    
    elif category == 'Popeye':
        if 'popeye' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'Popeye' nicht am Anfang")
    
    elif category == 'Felix the Cat':
        if 'felix' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'Felix' nicht am Anfang")
    
    elif category == 'Superman/Fleischer':
        if 'superman' in first_words or 'fleischer' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'Superman/Fleischer' nicht am Anfang")
    
    elif category == 'Looney Tunes':
        if any(kw in first_words for kw in ['looney', 'bugs', 'porky', 'daffy', 'tweety']):
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ Looney Tunes Keyword nicht am Anfang")
    
    elif category == 'BraveStarr':
        if 'bravestarr' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'BraveStarr' nicht am Anfang")
    
    elif category == 'Asterix':
        if 'asterix' in first_words:
            keyword_at_start = True
            score += 15
        else:
            issues.append("⚠️ 'Asterix' nicht am Anfang")
    
    else:
        # Generic check - any recognizable keyword
        generic_keywords = ['betty', 'popeye', 'superman', 'felix', 'looney', 'soundie', 
                          'wochenschau', 'alfred', 'asterix', 'bravestarr', 'christmas']
        if any(kw in first_words for kw in generic_keywords):
            keyword_at_start = True
            score += 15
        elif any(kw in title_lower for kw in generic_keywords):
            score += 8
            issues.append("⚠️ Keyword im Titel, aber nicht am Anfang")
        else:
            issues.append("⚠️ Kein erkennbares Keyword im Titel")
    
    # 3. 8K marker (10 pts)
    if '8k' in title_lower:
        score += 10
    else:
        issues.append("⚠️ '8K' fehlt im Titel")
        recommendations.append("'8K' oder '8K HQ' in Titel einfügen")
    
    # 4. @remAIke_IT branding (5 pts)
    if '@remaike' in title_lower:
        score += 5
    else:
        issues.append("⚠️ '@remAIke_IT' fehlt")
        recommendations.append("'@remAIke_IT' am Ende des Titels")
    
    # 5. Year in title (5 pts)
    if re.search(r'\(19\d{2}\)', title) or re.search(r'\(20\d{2}\)', title) or '(1940s)' in title:
        score += 5
    else:
        issues.append("⚠️ Jahr fehlt - Format (1932)")
    
    # =========================================
    # DESCRIPTION ANALYSIS (30 points total)
    # =========================================
    
    # 6. CTAs (15 pts)
    cta_words = ['like', 'subscribe', 'comment', 'abonnieren', 'kommentier', '👍', '🔔', '💬']
    has_cta = any(w in desc_lower for w in cta_words)
    if has_cta:
        score += 15
    else:
        issues.append("❌ KEINE CTAs in Description!")
        recommendations.append("CTAs hinzufügen: 👍 LIKE | 💬 COMMENT | 🔔 SUBSCRIBE")
    
    # 7. Hashtags (10 pts)
    hashtag_count = description.count('#')
    if 3 <= hashtag_count <= 8:
        score += 10
    elif hashtag_count > 0:
        if hashtag_count > 8:
            score += 5
            issues.append(f"⚠️ Zu viele Hashtags: {hashtag_count} (ideal 3-8)")
            recommendations.append(f"Hashtags auf 3-8 reduzieren")
        else:
            score += 5
            issues.append(f"⚠️ Wenige Hashtags: {hashtag_count} (ideal 3-8)")
    else:
        issues.append("❌ KEINE Hashtags!")
        recommendations.append("Hashtags hinzufügen: #8K #remAIke #PublicDomain etc.")
    
    # 8. Chapters (5 pts)
    if '0:00' in description:
        score += 5
    else:
        issues.append("⚠️ Keine Chapters (0:00 Format)")
        recommendations.append("Chapters hinzufügen für bessere Navigation")
    
    # =========================================
    # TAGS ANALYSIS (20 points total)
    # =========================================
    
    # 9. Tags count (10 pts)
    tag_count = len(tags)
    if 5 <= tag_count <= 15:
        score += 10
    elif tag_count > 0:
        if tag_count > 15:
            score += 5
            issues.append(f"⚠️ Zu viele Tags: {tag_count} (ideal 5-15)")
        else:
            score += 5
            issues.append(f"⚠️ Wenige Tags: {tag_count} (ideal 5-15)")
    else:
        issues.append("❌ KEINE Tags!")
        recommendations.append("5-15 relevante Tags hinzufügen")
    
    # 10. Tag quality (10 pts)
    if tags:
        essential_tags = ['8k', 'remaike', 'public domain', 'remastered', 'restored']
        has_essential = sum(1 for t in tags if any(e in t.lower() for e in essential_tags))
        if has_essential >= 3:
            score += 10
        elif has_essential >= 1:
            score += 5
        else:
            issues.append("⚠️ Wichtige Tags fehlen (8K, remAIke, public domain)")
    
    return {
        'score': score,
        'issues': issues,
        'recommendations': recommendations,
        'category': category,
        'title_length': title_len,
        'hashtag_count': hashtag_count,
        'tag_count': tag_count,
        'has_cta': has_cta,
        'has_chapters': '0:00' in description,
        'keyword_at_start': keyword_at_start
    }

def main():
    print("=" * 70)
    print("🔍 COMPLETE CHANNEL AUDIT - remAIke_IT")
    print("=" * 70)
    
    # Load videos
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = [v for v in data.get('videos', []) 
              if v.get('status', {}).get('privacyStatus') == 'public']
    
    print(f"📺 Analysiere {len(videos)} öffentliche Videos...")
    print()
    
    # Audit all videos
    results = []
    category_stats = defaultdict(lambda: {'count': 0, 'total_score': 0, 'issues': []})
    
    for video in videos:
        video_id = video['id']
        title = video['snippet']['title']
        
        audit = audit_video(video)
        
        result = {
            'video_id': video_id,
            'title': title,
            **audit
        }
        results.append(result)
        
        cat = audit['category']
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_score'] += audit['score']
        if audit['issues']:
            category_stats[cat]['issues'].extend(audit['issues'])
    
    # Sort by score (worst first)
    results.sort(key=lambda x: x['score'])
    
    # Print category summary
    print("=" * 70)
    print("📊 ERGEBNISSE NACH KATEGORIE")
    print("=" * 70)
    
    for cat in sorted(category_stats.keys()):
        stats = category_stats[cat]
        avg_score = stats['total_score'] / stats['count'] if stats['count'] > 0 else 0
        
        if avg_score >= 80:
            status = "🏆"
        elif avg_score >= 60:
            status = "✅"
        elif avg_score >= 40:
            status = "⚠️"
        else:
            status = "❌"
        
        print(f"\n{status} {cat}: {stats['count']} Videos | Ø Score: {avg_score:.1f}/100")
    
    # Overall stats
    total_score = sum(r['score'] for r in results)
    avg_score = total_score / len(results) if results else 0
    
    excellent = len([r for r in results if r['score'] >= 80])
    good = len([r for r in results if 60 <= r['score'] < 80])
    warning = len([r for r in results if 40 <= r['score'] < 60])
    critical = len([r for r in results if r['score'] < 40])
    
    print()
    print("=" * 70)
    print("📊 GESAMTÜBERSICHT")
    print("=" * 70)
    print(f"   Analysierte Videos: {len(results)}")
    print(f"   Durchschnittlicher Score: {avg_score:.1f}/100")
    print()
    print(f"   🏆 Excellent (80+): {excellent} ({excellent*100/len(results):.1f}%)")
    print(f"   ✅ Good (60-79):    {good} ({good*100/len(results):.1f}%)")
    print(f"   ⚠️ Warning (40-59): {warning} ({warning*100/len(results):.1f}%)")
    print(f"   ❌ Critical (<40):  {critical} ({critical*100/len(results):.1f}%)")
    
    # Issue frequency
    print()
    print("=" * 70)
    print("🔧 HÄUFIGSTE PROBLEME")
    print("=" * 70)
    
    issue_counts = defaultdict(int)
    for r in results:
        for issue in r['issues']:
            # Simplify issue
            if 'Titel zu lang' in issue or 'VIEL zu lang' in issue:
                issue_counts['Titel zu lang (>70 chars)'] += 1
            elif 'Titel kurz' in issue or 'zu kurz' in issue:
                issue_counts['Titel zu kurz (<50 chars)'] += 1
            elif 'nicht am Anfang' in issue:
                issue_counts['Keyword nicht am Anfang'] += 1
            elif '8K' in issue:
                issue_counts['8K fehlt im Titel'] += 1
            elif '@remAIke' in issue:
                issue_counts['@remAIke_IT fehlt'] += 1
            elif 'Jahr fehlt' in issue:
                issue_counts['Jahr fehlt im Titel'] += 1
            elif 'KEINE CTAs' in issue:
                issue_counts['Keine CTAs'] += 1
            elif 'Hashtags' in issue:
                issue_counts['Hashtag-Probleme'] += 1
            elif 'Chapters' in issue:
                issue_counts['Keine Chapters'] += 1
            elif 'Tags' in issue or 'KEINE Tags' in issue:
                issue_counts['Tag-Probleme'] += 1
    
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
        pct = count * 100 / len(results)
        bar = "█" * int(pct / 5)
        print(f"   {count:3d} ({pct:5.1f}%) {bar} {issue}")
    
    # Critical videos needing fixes
    critical_videos = [r for r in results if r['score'] < 60]
    
    print()
    print("=" * 70)
    print(f"🚨 VIDEOS MIT DRINGENDEM HANDLUNGSBEDARF ({len(critical_videos)})")
    print("=" * 70)
    
    for i, v in enumerate(critical_videos[:30], 1):
        print(f"\n{i}. [{v['score']}/100] {v['category']}")
        print(f"   {v['title'][:60]}...")
        print(f"   ID: {v['video_id']}")
        for issue in v['issues'][:3]:
            print(f"   {issue}")
        if v['recommendations']:
            print(f"   💡 {v['recommendations'][0]}")
    
    if len(critical_videos) > 30:
        print(f"\n   ... und {len(critical_videos) - 30} weitere")
    
    # Save full results
    output = {
        'audit_date': datetime.now().isoformat(),
        'summary': {
            'total_videos': len(results),
            'average_score': avg_score,
            'excellent': excellent,
            'good': good,
            'warning': warning,
            'critical': critical
        },
        'category_stats': {k: {'count': v['count'], 'avg_score': v['total_score']/v['count'] if v['count'] else 0} 
                          for k, v in category_stats.items()},
        'issue_frequency': dict(issue_counts),
        'all_videos': results,
        'needs_fix': [r for r in results if r['score'] < 70]
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Vollständiger Report: {OUTPUT_FILE}")
    
    return output

if __name__ == '__main__':
    main()
