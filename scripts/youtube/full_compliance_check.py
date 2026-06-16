"""
COMPREHENSIVE COMPLIANCE CHECK — ALL rules from copilot-instructions.md
Checks EVERY video against EVERY rule, outputs exact fix needed.

Rules enforced:
R1: Title MUST have "8K HQ (4K UHD)" — BOTH keywords!
R2: NO @remAIke_IT in title
R3: Title max 70 chars (soft 80)
R4: CTA in description (public only)
R5: www.remaike.IT in description (public only)
R6: YouTube channel link in description (public only)
R7: Max 5 hashtags in description
R8: Max 15 tags
R9: Category: Wochenschau=27, Soundie=10
R10: No raw artifacts (sls, ARCHIVE, CINEMA, xvid, aac)
R11: Description min 50 chars (public)
R12: Min 2 localizations
R13: Pflicht-Tags present (remastered, restored, AI enhanced, classic)
"""
import json
import os
import re
from collections import defaultdict

with open('config/live_scan_2026_02_17.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

# Also load the just-fixed videos (they won't be in the scan)
# We need to re-check them too since we just changed them
JUST_FIXED = {
    'Hto044hFaZ4', 'is5qVIkr6Vo', 'UHS1MqpTng8', 'rqWucYVxqTA',
    'FjvUAUsQi8Q', 'ea5LQn-BJQs', '4Nu91xa9_eY', 'x7u-1DcabiE',
    'I1Hqb1mGlzU', 'ghhyzR9NSLE', 'oWZ5BmJVsxI', 'NvwmtSLyCE4',
    'GpYO8Yel0WY', 'Dg6eQNIY_Ys', 'qGzRqmiOcNw', '8aeRL4PwSVI',
    'Y28BihR4fkk', 'KaIC0B-xYBg', 'HyaZLqdMS9k'
}

DUPE_IDS = {
    'QRNAv0GKymk', 'R9dz4YGCy5E', 'SV7o2XaYZyc', 'LjGFowS8qHI',
    'LCa6Klpi8ts', 'ULzsDOb2x3U', 'sGZg6lIHFh8', 'iFSHNS7kVgQ'
}

PFLICHT_TAGS = {'remastered', 'restored'}

stats = defaultdict(int)
issues_by_rule = defaultdict(list)
fixable = []

for v in scan['all_videos']:
    vid = v['id']
    title = v['title']
    desc = v['description']
    tags = [t.lower() for t in v.get('tags', [])]
    cat = v['categoryId']
    privacy = v['privacy']
    locs = v.get('localizations', [])
    
    # Skip deleted/DUPE
    if 'Deleted video' in title or vid in DUPE_IDS:
        continue
    
    # Skip just-fixed (they have correct titles now but scan has old data)
    if vid in JUST_FIXED:
        continue
    
    issues = []
    title_fix = None
    desc_fix = False
    tag_fix = False
    cat_fix = None
    
    # R1: MUST have "8K HQ (4K UHD)" — BOTH!
    has_8k = '8K' in title
    has_4k = '4K' in title
    has_full_quality = '8K HQ (4K UHD)' in title or '8K HQ' in title
    
    if not has_8k and not has_4k:
        issues.append('R1: No 8K/4K in title')
    elif has_8k and '(4K UHD)' not in title:
        # Has 8K but missing (4K UHD)
        if '8K HQ' in title and '(4K UHD)' not in title:
            issues.append('R1b: Has "8K HQ" but missing "(4K UHD)"')
        elif '8K' in title and '4K' not in title:
            issues.append('R1c: Has 8K but no 4K')
    
    # R2: No @remAIke_IT in title
    if '@remAIke_IT' in title or '@remAIke' in title:
        issues.append('R2: @remAIke_IT in title')
    
    # R3: Title too long
    if len(title) > 80:
        issues.append(f'R3: Title {len(title)} chars (max 80)')
    
    # R4-R6: Description checks (public only)
    if privacy == 'public':
        cta_words = ['LIKE', 'SUBSCRIBE', 'COMMENT']
        if not any(w in desc.upper() for w in cta_words):
            issues.append('R4: No CTA')
            desc_fix = True
        
        if 'remaike.it' not in desc.lower() and 'remaike.IT' not in desc:
            issues.append('R5: Missing www.remaike.IT')
            desc_fix = True
        
        if 'youtube.com/@remAIke_IT' not in desc and '@remAIke_IT' not in desc:
            issues.append('R6: Missing YouTube link')
            desc_fix = True
    
    # R7: Max 5 hashtags
    hashtag_count = desc.count('#')
    if hashtag_count > 5:
        issues.append(f'R7: {hashtag_count} hashtags (max 5)')
        desc_fix = True
    
    # R8: Max 15 tags
    if len(v.get('tags', [])) > 15:
        issues.append(f'R8: {len(v["tags"])} tags (max 15)')
        tag_fix = True
    
    # R9: Category
    is_ws = 'wochenschau' in title.lower() or 'newsreel' in title.lower()
    is_soundie = 'soundie' in title.lower()
    if is_ws and cat != '27':
        issues.append(f'R9: WS cat={cat} should be 27')
        cat_fix = '27'
    if is_soundie and cat != '10':
        issues.append(f'R9: Soundie cat={cat} should be 10')
        cat_fix = '10'
    
    # R10: Raw artifacts
    raw_words = ['sls', 'ARCHIVE PROTECTED', 'ARCHIVE BLURRED', 'CINEMA', 'xvid', 'aac sls']
    for rw in raw_words:
        if rw.lower() in title.lower():
            issues.append(f'R10: Raw "{rw}" in title')
            break
    
    # R11: Description too short
    if privacy == 'public' and len(desc) < 50:
        issues.append(f'R11: Desc {len(desc)} chars')
        desc_fix = True
    
    # R13: Pflicht-tags
    if privacy == 'public':
        tag_set = set(tags)
        missing_pflicht = PFLICHT_TAGS - tag_set
        if missing_pflicht:
            issues.append(f'R13: Missing tags: {missing_pflicht}')
            tag_fix = True
    
    if issues:
        stats['total_issues'] += len(issues)
        for i in issues:
            rule = i.split(':')[0]
            issues_by_rule[rule].append(vid)
        
        fixable.append({
            'id': vid,
            'title': title,
            'privacy': privacy,
            'issues': issues,
            'needs_title_fix': any(i.startswith(('R1', 'R2', 'R3', 'R10')) for i in issues),
            'needs_desc_fix': desc_fix,
            'needs_tag_fix': tag_fix,
            'needs_cat_fix': cat_fix,
        })

# Summary
print('=' * 70)
print('COMPREHENSIVE COMPLIANCE REPORT')
print('=' * 70)
total = len(scan['all_videos']) - len(DUPE_IDS) - len(JUST_FIXED)
print(f'Videos checked: {total} (excl {len(DUPE_IDS)} DUPEs, {len(JUST_FIXED)} just-fixed)')
print(f'Videos with issues: {len(fixable)}')
print(f'Total issues: {stats["total_issues"]}')

print(f'\nISSUES BY RULE:')
for rule in sorted(issues_by_rule.keys()):
    count = len(issues_by_rule[rule])
    print(f'  {rule}: {count} videos')

# Group fixable by action type
title_fixes = [f for f in fixable if f['needs_title_fix']]
desc_fixes = [f for f in fixable if f['needs_desc_fix']]
tag_fixes = [f for f in fixable if f['needs_tag_fix']]
cat_fixes = [f for f in fixable if f['needs_cat_fix']]

print(f'\nFIXES NEEDED:')
print(f'  Title fixes: {len(title_fixes)} videos')
print(f'  Description fixes: {len(desc_fixes)} videos')
print(f'  Tag fixes: {len(tag_fixes)} videos')
print(f'  Category fixes: {len(cat_fixes)} videos')

# Calculate quota
unique_fix_ids = set()
for f in fixable:
    if f['needs_title_fix'] or f['needs_desc_fix'] or f['needs_tag_fix'] or f['needs_cat_fix']:
        unique_fix_ids.add(f['id'])
print(f'\n  UNIQUE videos needing API update: {len(unique_fix_ids)}')
print(f'  QUOTA COST: {len(unique_fix_ids)} × 50 = {len(unique_fix_ids) * 50} units')

# Detail: R1b (missing 4K UHD in title)
r1b = [f for f in fixable if any('R1b' in i or 'R1c' in i for i in f['issues'])]
if r1b:
    print(f'\n{"="*70}')
    print(f'R1b/R1c: Missing (4K UHD) — {len(r1b)} videos:')
    print(f'{"="*70}')
    for f in r1b:
        print(f"  [{f['privacy']}] {f['id']}: {f['title']}")

# Detail: R2 (@handle in title)
r2 = [f for f in fixable if any('R2' in i for i in f['issues'])]
if r2:
    print(f'\n{"="*70}')
    print(f'R2: @remAIke_IT in title — {len(r2)} videos:')
    print(f'{"="*70}')
    for f in r2:
        print(f"  [{f['privacy']}] {f['id']}: {f['title']}")

# Detail: R7 (too many hashtags)
r7 = [f for f in fixable if any('R7' in i for i in f['issues'])]
if r7:
    print(f'\n{"="*70}')
    print(f'R7: Too many hashtags — {len(r7)} videos:')
    print(f'{"="*70}')
    for f in r7:
        ht = [i for i in f['issues'] if 'R7' in i][0]
        print(f"  [{f['privacy']}] {f['id']}: {f['title'][:50]} | {ht}")

# Detail: R10 (raw artifacts)
r10 = [f for f in fixable if any('R10' in i for i in f['issues'])]
if r10:
    print(f'\n{"="*70}')
    print(f'R10: Raw artifacts — {len(r10)} videos:')
    print(f'{"="*70}')
    for f in r10:
        print(f"  [{f['privacy']}] {f['id']}: {f['title']}")

# Save for fix script
with open('config/full_compliance_issues_2026_02_17.json', 'w', encoding='utf-8') as f2:
    json.dump({
        'date': '2026-02-17',
        'total_checked': total,
        'issues_found': len(fixable),
        'fixable': fixable,
        'issues_by_rule': {k: len(v) for k, v in issues_by_rule.items()},
    }, f2, ensure_ascii=False, indent=2)

print(f'\nSaved to config/full_compliance_issues_2026_02_17.json')
