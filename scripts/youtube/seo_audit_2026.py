#!/usr/bin/env python3
"""
YouTube 2026 SEO Audit - Basierend auf offiziellen YouTube Ranking-Faktoren:
1. RELEVANCE: Title, Tags, Description, Video Content match search query
2. ENGAGEMENT: Watch time, likes, comments
3. QUALITY: E-E-A-T (Expertise, Experience, Authoritativeness, Trustworthiness)

Official: "Tags play a MINIMAL role" - Title, Thumbnail, Description wichtiger!
"""
import json, sys, io, re
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))
videos = data['public_videos']

print("=" * 70)
print("🎯 YOUTUBE 2026 SEO AUDIT - Official Ranking Factors")
print("=" * 70)
print(f"\nAnalysiere {len(videos)} public Videos...\n")

# Scoring System
scores = []
issues_by_type = defaultdict(list)

for v in videos:
    vid = v['id']
    snippet = v['snippet']
    stats = v.get('statistics', {})
    
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    views = int(stats.get('viewCount', 0))
    likes = int(stats.get('likeCount', 0))
    comments = int(stats.get('commentCount', 0))
    
    score = 0
    issues = []
    
    # === 1. TITLE (40 Punkte) - WICHTIGSTER FAKTOR ===
    title_score = 0
    
    # Keyword am Anfang? (Primary keyword first)
    if title.lower().startswith(('betty', 'soundie', 'alfred', 'bravestarr', 'felix', 'popeye', 'superman', 'wochenschau', 'looney')):
        title_score += 10
    elif ':' in title[:30]:  # Format "Series: Title"
        title_score += 8
    else:
        issues.append("⚠️ Title: Keyword nicht am Anfang")
    
    # 8K Quality-Marker?
    if '8K' in title or '8k' in title:
        title_score += 10
    else:
        issues.append("❌ Title: Kein 8K Marker")
    
    # Brand @remAIke_IT?
    if '@remAIke' in title:
        title_score += 10
    else:
        issues.append("⚠️ Title: Kein @remAIke_IT")
    
    # Länge optimal? (50-70 Zeichen)
    if 50 <= len(title) <= 70:
        title_score += 10
    elif len(title) < 50:
        issues.append(f"⚠️ Title: Zu kurz ({len(title)} chars)")
        title_score += 5
    else:
        title_score += 7  # Zu lang aber ok
    
    score += title_score
    
    # === 2. DESCRIPTION (30 Punkte) ===
    desc_score = 0
    
    # Länge (mind. 200 Zeichen)
    if len(desc) >= 500:
        desc_score += 10
    elif len(desc) >= 200:
        desc_score += 7
    else:
        issues.append(f"❌ Desc: Zu kurz ({len(desc)} chars)")
        desc_score += 3
    
    # CTA vorhanden?
    if 'SUBSCRIBE' in desc.upper() or 'LIKE' in desc.upper():
        desc_score += 5
    else:
        issues.append("⚠️ Desc: Kein CTA (LIKE/SUBSCRIBE)")
    
    # Links vorhanden?
    if 'remAIke' in desc or 'FRai.TV' in desc:
        desc_score += 5
    else:
        issues.append("⚠️ Desc: Keine Links")
    
    # Hashtags am Ende?
    if '#' in desc:
        desc_score += 5
        hashtag_count = desc.count('#')
        if hashtag_count > 15:
            issues.append(f"⚠️ Desc: Zu viele Hashtags ({hashtag_count})")
    else:
        issues.append("⚠️ Desc: Keine Hashtags")
    
    # Chapters?
    if '0:00' in desc:
        desc_score += 5
    
    score += desc_score
    
    # === 3. TAGS (15 Punkte) - "Minimal role" laut YouTube ===
    tags_score = 0
    
    if len(tags) >= 10:
        tags_score += 10
    elif len(tags) >= 5:
        tags_score += 7
    else:
        issues.append(f"⚠️ Tags: Nur {len(tags)} Tags")
        tags_score += 3
    
    # 8K in Tags?
    if any('8k' in t.lower() for t in tags):
        tags_score += 3
    
    # remAIke in Tags?
    if any('remaike' in t.lower() for t in tags):
        tags_score += 2
    
    score += tags_score
    
    # === 4. ENGAGEMENT SIGNALS (15 Punkte) ===
    eng_score = 0
    
    # Views-basiert
    if views >= 1000:
        eng_score += 8
    elif views >= 100:
        eng_score += 5
    elif views >= 10:
        eng_score += 3
    
    # Like-Ratio (wenn views > 100)
    if views > 100 and likes > 0:
        like_ratio = likes / views
        if like_ratio > 0.05:  # >5% like rate
            eng_score += 4
        elif like_ratio > 0.02:
            eng_score += 2
    
    # Comments
    if comments > 0:
        eng_score += 3
    
    score += eng_score
    
    # Kategorisieren
    scores.append({
        'id': vid,
        'title': title,
        'score': score,
        'title_score': title_score,
        'desc_score': desc_score,
        'tags_score': tags_score,
        'eng_score': eng_score,
        'views': views,
        'issues': issues
    })
    
    # Issues sammeln
    for issue in issues:
        issues_by_type[issue].append(title[:40])

# Sortieren nach Score
scores.sort(key=lambda x: x['score'], reverse=True)

# Top & Bottom
print("🏆 TOP 10 (Beste SEO):")
print("-" * 70)
for s in scores[:10]:
    print(f"  {s['score']:3d}/100 | {s['title'][:55]}...")
    
print("\n⚠️ BOTTOM 10 (Brauchen Arbeit):")
print("-" * 70)
for s in scores[-10:]:
    print(f"  {s['score']:3d}/100 | {s['title'][:55]}...")
    if s['issues']:
        print(f"          Issues: {', '.join(s['issues'][:2])}")

# Issue-Statistik
print("\n" + "=" * 70)
print("📊 HÄUFIGSTE PROBLEME:")
print("=" * 70)
for issue, titles in sorted(issues_by_type.items(), key=lambda x: -len(x[1]))[:10]:
    print(f"  {len(titles):3d}x | {issue}")

# Score-Verteilung
excellent = len([s for s in scores if s['score'] >= 80])
good = len([s for s in scores if 60 <= s['score'] < 80])
ok = len([s for s in scores if 40 <= s['score'] < 60])
poor = len([s for s in scores if s['score'] < 40])

print("\n" + "=" * 70)
print("📈 SCORE-VERTEILUNG:")
print("=" * 70)
print(f"  🏆 Excellent (80+):  {excellent:3d} Videos ({excellent/len(scores)*100:.1f}%)")
print(f"  ✅ Good (60-79):     {good:3d} Videos ({good/len(scores)*100:.1f}%)")
print(f"  ⚠️ OK (40-59):       {ok:3d} Videos ({ok/len(scores)*100:.1f}%)")
print(f"  ❌ Poor (<40):       {poor:3d} Videos ({poor/len(scores)*100:.1f}%)")
print(f"\n  📊 Durchschnitt:     {sum(s['score'] for s in scores)/len(scores):.1f}/100")

# Speichern
result = {
    'audit_date': '2026-01-14',
    'total_videos': len(videos),
    'average_score': sum(s['score'] for s in scores)/len(scores),
    'distribution': {
        'excellent': excellent,
        'good': good,
        'ok': ok,
        'poor': poor
    },
    'issues_summary': {k: len(v) for k, v in issues_by_type.items()},
    'all_scores': scores
}
Path('config/seo_audit_2026.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n💾 Gespeichert: config/seo_audit_2026.json")
