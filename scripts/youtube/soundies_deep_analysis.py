#!/usr/bin/env python3
"""
Soundies Deep Analysis - YouTube Music Optimization Check
"""
import json, sys, io
from pathlib import Path
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))

print('=' * 70)
print('🎵 SOUNDIES DEEP ANALYSIS - YouTube Music Optimization')
print('=' * 70)

soundies = [v for v in data['public_videos'] if 'soundie' in v['snippet'].get('title','').lower()]
print(f'\n📊 Total Soundies: {len(soundies)}')

# Category Check
categories = Counter([s['snippet'].get('categoryId', '?') for s in soundies])
print(f'\n📁 Categories:')
for cat, count in categories.items():
    cat_name = {
        '1': 'Film & Animation',
        '10': 'Music ✅',
        '22': 'People & Blogs',
        '24': 'Entertainment'
    }.get(cat, f'Unknown ({cat})')
    status = '✅' if cat == '10' else '❌'
    print(f'   {status} {cat_name}: {count}')

# SEO Scoring
print('\n' + '=' * 70)
print('🎯 SEO SCORE BREAKDOWN:')
print('=' * 70)

scores = []
issues_count = Counter()

for s in soundies:
    title = s['snippet'].get('title', '')
    desc = s['snippet'].get('description', '')
    tags = s['snippet'].get('tags', [])
    cat = s['snippet'].get('categoryId', '')
    
    score = 0
    issues = []
    
    # Category = Music (10)?
    if cat == '10':
        score += 25
    else:
        issues.append('Wrong Category')
    
    # Title SEO
    if '8K' in title or '8k' in title:
        score += 10
    else:
        issues.append('No 8K in title')
    
    if '@remAIke' in title:
        score += 10
    else:
        issues.append('No @remAIke_IT')
    
    # Song name in title?
    if ':' in title or '|' in title:
        score += 5
    
    # Description
    if len(desc) >= 200:
        score += 10
    elif len(desc) >= 100:
        score += 5
    else:
        issues.append('Short description')
    
    # CTA
    if 'SUBSCRIBE' in desc.upper() or 'LIKE' in desc.upper():
        score += 10
    else:
        issues.append('No CTA')
    
    # Hashtags
    if '#' in desc:
        score += 5
        hashtag_count = desc.count('#')
        if hashtag_count >= 3:
            score += 5
    else:
        issues.append('No hashtags')
    
    # Tags
    if len(tags) >= 10:
        score += 10
    elif len(tags) >= 5:
        score += 5
    else:
        issues.append(f'Few tags ({len(tags)})')
    
    # Music-specific tags
    music_tags = ['soundie', 'soundies', 'jazz', 'swing', '1940s', 'vintage music', 'jukebox']
    if any(mt in ' '.join(tags).lower() for mt in music_tags):
        score += 10
    else:
        issues.append('Missing music tags')
    
    scores.append({
        'id': s['id'],
        'title': title,
        'score': score,
        'issues': issues
    })
    
    for issue in issues:
        issues_count[issue] += 1

# Score distribution
excellent = len([s for s in scores if s['score'] >= 80])
good = len([s for s in scores if 60 <= s['score'] < 80])
needs_work = len([s for s in scores if s['score'] < 60])

print(f'\n🏆 Excellent (80+): {excellent}')
print(f'✅ Good (60-79):   {good}')
print(f'⚠️ Needs Work (<60): {needs_work}')
print(f'\n📊 Average Score: {sum(s["score"] for s in scores)/len(scores):.1f}/100')

# Most common issues
print('\n' + '=' * 70)
print('⚠️ MOST COMMON ISSUES:')
print('=' * 70)
for issue, count in issues_count.most_common(10):
    print(f'   {count:2d}x | {issue}')

# Show worst 5
print('\n' + '=' * 70)
print('🔧 WORST 5 (Need Most Work):')
print('=' * 70)
scores.sort(key=lambda x: x['score'])
for s in scores[:5]:
    print(f"\n📹 {s['title'][:55]}...")
    print(f"   Score: {s['score']}/100")
    print(f"   Issues: {', '.join(s['issues'])}")
    print(f"   Studio: https://studio.youtube.com/video/{s['id']}/edit")

# Show best 3
print('\n' + '=' * 70)
print('🏆 BEST 3:')
print('=' * 70)
scores.sort(key=lambda x: x['score'], reverse=True)
for s in scores[:3]:
    print(f"\n📹 {s['title'][:55]}...")
    print(f"   Score: {s['score']}/100")

# Save results
result = {
    'total': len(soundies),
    'category_10_count': categories.get('10', 0),
    'average_score': sum(s['score'] for s in scores)/len(scores),
    'issues_summary': dict(issues_count),
    'all_scores': scores
}
Path('config/soundies_deep_analysis.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)
print(f'\n💾 Saved: config/soundies_deep_analysis.json')
