#!/usr/bin/env python3
"""Critical audit of the channel - unbiased review"""
import json
import re
from collections import Counter

with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
    scan = json.load(f)

public = [v for v in scan['videos'] if v.get('status', {}).get('privacyStatus') == 'public']
drafts = [v for v in scan['videos'] if v.get('status', {}).get('privacyStatus') == 'private']

print('=' * 70)
print('🔍 KRITISCHER AUDIT - UNVOREINGENOMMEN')
print('=' * 70)
print(f'Public: {len(public)} | Drafts: {len(drafts)}')
print()

issues = []

# 1. HASHTAGS IM TITEL
print('1️⃣ HASHTAGS IM TITEL (YouTube sagt: gehören in Description!)')
print('-' * 50)
hashtag_titles = []
for v in public:
    title = v['snippet'].get('title', '')
    if '#' in title:
        hashtag_titles.append((v['id'], title))
if hashtag_titles:
    print(f'   ❌ {len(hashtag_titles)} Videos mit Hashtags im Titel')
    for vid, title in hashtag_titles:
        print(f'      [{vid}] {title[:60]}')
    issues.append(('Hashtags im Titel', len(hashtag_titles)))
else:
    print('   ✅ Keine Hashtags im Titel')
print()

# 2. EMOJIS IM TITEL
print('2️⃣ EMOJIS IM TITEL')
print('-' * 50)
emoji_pattern = re.compile('[\U0001F300-\U0001F9FF\U0001FA00-\U0001FAFF\U00002600-\U000027BF]')
emoji_titles = []
for v in public:
    title = v['snippet'].get('title', '')
    if emoji_pattern.search(title):
        emoji_titles.append((v['id'], title))
print(f'   ⚠️ {len(emoji_titles)} Videos mit Emojis im Titel')
if emoji_titles:
    for vid, title in emoji_titles[:5]:
        print(f'      [{vid}] {title[:55]}')
    print('   INFO: Emojis können CTR helfen, wirken aber teils clickbaity')
print()

# 3. TITEL LÄNGE
print('3️⃣ TITEL-LÄNGE (optimal: 50-70 Zeichen)')
print('-' * 50)
too_short = []
too_long = []
for v in public:
    title = v['snippet'].get('title', '')
    if len(title) < 40:
        too_short.append((v['id'], title, len(title)))
    if len(title) > 80:
        too_long.append((v['id'], title, len(title)))
print(f'   Zu kurz (<40): {len(too_short)}')
print(f'   Zu lang (>80): {len(too_long)}')
if too_long:
    issues.append(('Titel zu lang', len(too_long)))
    for vid, title, length in too_long[:3]:
        print(f'      [{vid}] ({length}): {title[:50]}...')
print()

# 4. DESCRIPTION OHNE CHAPTERS
print('4️⃣ VIDEOS OHNE CHAPTERS (bei Länge >3min)')
print('-' * 50)
no_chapters = []
for v in public:
    desc = v['snippet'].get('description', '')
    title = v['snippet'].get('title', '')
    # Check if likely long video (has substantial description)
    if len(desc) > 300 and '0:00' not in desc and ':00' not in desc:
        no_chapters.append((v['id'], title[:50]))
print(f'   ⚠️ {len(no_chapters)} Videos ohne Chapters')
if no_chapters:
    issues.append(('Keine Chapters', len(no_chapters)))
print()

# 5. INKONSISTENTE 8K SCHREIBWEISE
print('5️⃣ INKONSISTENTE 8K SCHREIBWEISE')
print('-' * 50)
variants = {'8K': 0, '8k': 0, '8KHQ': 0, 'HQ8K': 0, '8K HQ': 0}
other_8k = []
for v in public:
    title = v['snippet'].get('title', '')
    if '8K HQ' in title:
        variants['8K HQ'] += 1
    elif '8KHQ' in title:
        variants['8KHQ'] += 1
    elif 'HQ8K' in title:
        variants['HQ8K'] += 1
    elif '8K' in title:
        variants['8K'] += 1
    elif '8k' in title:
        variants['8k'] += 1
for var, count in variants.items():
    if count > 0:
        print(f'   "{var}": {count} Videos')
inconsistent = variants['8KHQ'] + variants['HQ8K'] + variants['8k']
if inconsistent > 0:
    issues.append(('Inkonsistente 8K-Schreibweise', inconsistent))
print()

# 6. DUPLIKATE
print('6️⃣ MÖGLICHE DUPLIKATE')
print('-' * 50)
title_map = {}
for v in public:
    title = v['snippet'].get('title', '')
    # Normalize: remove year, quality markers, branding
    norm = title.lower()
    norm = re.sub(r'\(\d{4}\)', '', norm)
    norm = re.sub(r'8k|hq|4k|\|.*', '', norm)
    norm = norm.strip()[:30]
    if norm in title_map:
        title_map[norm].append((v['id'], title[:50]))
    else:
        title_map[norm] = [(v['id'], title[:50])]

dupes = {k: v for k, v in title_map.items() if len(v) > 1}
if dupes:
    print(f'   ⚠️ {len(dupes)} Gruppen mit ähnlichen Titeln')
    for norm, vids in list(dupes.items())[:3]:
        print(f'   Gruppe "{norm[:25]}":')
        for vid, title in vids:
            print(f'      [{vid}] {title}')
    issues.append(('Mögliche Duplikate', len(dupes)))
print()

# 7. SERIEN OHNE EPISODEN-NUMMER
print('7️⃣ SERIEN-EPISODEN FORMAT')
print('-' * 50)
series_keywords = ['betty boop', 'felix', 'popeye', 'looney', 'superman', 'alfred', 'kwak', 'bravestarr']
no_episode = []
for v in public:
    title = v['snippet'].get('title', '').lower()
    for kw in series_keywords:
        if kw in title:
            # Check for episode number pattern
            if not re.search(r'\d+/\d+|\(\d+\)|e\d+|ep\d+|episode|folge', title):
                no_episode.append((v['id'], v['snippet']['title'][:50]))
            break
print(f'   Serien-Videos ohne Episoden-Nr: {len(no_episode)}')
if no_episode and len(no_episode) < 20:
    for vid, title in no_episode[:5]:
        print(f'      [{vid}] {title}')
print()

# 8. BEST PRACTICE TITEL-FORMAT CHECK
print('8️⃣ BEST PRACTICE TITEL-FORMAT')
print('-' * 50)
# Format: [Keyword]: [Title] (Year) | 8K HQ | @remAIke_IT
good_format = 0
bad_format = []
for v in public:
    title = v['snippet'].get('title', '')
    # Check: has year in (), has 8K, has @remAIke, uses | separator
    has_year = bool(re.search(r'\(\d{4}\)', title))
    has_8k = '8K' in title or '8k' in title
    has_brand = '@remAIke' in title or '@remaike' in title.lower()
    has_pipe = ' | ' in title
    
    if has_year and has_8k and has_brand and has_pipe:
        good_format += 1
    else:
        missing = []
        if not has_year: missing.append('Jahr')
        if not has_8k: missing.append('8K')
        if not has_brand: missing.append('Branding')
        if not has_pipe: missing.append('Pipe')
        bad_format.append((v['id'], title[:45], missing))

print(f'   ✅ Best Practice Format: {good_format}/{len(public)} ({100*good_format//len(public)}%)')
print(f'   ⚠️ Nicht optimal: {len(bad_format)}')
if bad_format:
    issues.append(('Nicht-optimales Titel-Format', len(bad_format)))
    print('   Häufigste Probleme:')
    missing_counts = Counter()
    for _, _, missing in bad_format:
        for m in missing:
            missing_counts[m] += 1
    for prob, count in missing_counts.most_common():
        print(f'      - {prob}: {count}x')
print()

# SUMMARY
print('=' * 70)
print('📊 ZUSAMMENFASSUNG - OFFENE PROBLEME')
print('=' * 70)
if issues:
    total_issues = sum(count for _, count in issues)
    for issue, count in sorted(issues, key=lambda x: -x[1]):
        print(f'   ❌ {issue}: {count}')
    print()
    print(f'   TOTAL: {total_issues} Video-Probleme zu fixen')
    print(f'   Quota-Kosten: {total_issues} x 50 = {total_issues * 50} Units')
else:
    print('   ✅ Keine kritischen Probleme gefunden!')
