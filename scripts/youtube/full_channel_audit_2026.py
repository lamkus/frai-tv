#!/usr/bin/env python3
"""
VOLLSTÄNDIGES CHANNEL AUDIT für remAIke_IT
Analysiert ALLE offenen Punkte für YouTube 2026 Algo
"""

import json
import re
from collections import defaultdict
from datetime import datetime

# Lade Channel-Scan
with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

videos = [v for v in scan.get('videos', []) if v.get('status', {}).get('privacyStatus') == 'public']

print("=" * 80)
print("🎬 VOLLSTÄNDIGES CHANNEL AUDIT - remAIke_IT")
print(f"📅 Stand: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 80)

# === 1. TITEL-ANALYSE ===
print("\n" + "=" * 40)
print("📏 1. TITEL-LÄNGEN-ANALYSE")
print("=" * 40)

long_titles = defaultdict(list)
title_lengths = []

for v in videos:
    title = v.get('snippet', {}).get('title', '')
    vid_id = v.get('id', '')
    title_lengths.append(len(title))
    
    if len(title) > 70:
        title_lower = title.lower()
        
        if 'alfred' in title_lower or 'quack' in title_lower or 'kwak' in title_lower:
            series = 'Alfred J. Kwak'
        elif 'soundie' in title_lower:
            series = 'Soundies'
        elif 'wochenschau' in title_lower or ('nr.' in title_lower and '1940' in title_lower):
            series = 'Wochenschau'
        elif 'betty' in title_lower:
            series = 'Betty Boop'
        elif 'superman' in title_lower:
            series = 'Superman'
        elif 'felix' in title_lower:
            series = 'Felix'
        elif 'maulwurf' in title_lower or 'krtek' in title_lower:
            series = 'Maulwurf'
        else:
            series = 'Other'
        
        long_titles[series].append({
            'id': vid_id,
            'title': title,
            'length': len(title)
        })

print(f"Total Videos:     {len(videos)}")
print(f"Titel <70 chars:  {len([l for l in title_lengths if l <= 70])} ✅")
print(f"Titel >70 chars:  {len([l for l in title_lengths if l > 70])} ❌")
print(f"\nNach Serie:")

for series, items in sorted(long_titles.items(), key=lambda x: -len(x[1])):
    print(f"  {series}: {len(items)}")

# === 2. DESCRIPTION-ANALYSE ===
print("\n" + "=" * 40)
print("📝 2. DESCRIPTION-ANALYSE")
print("=" * 40)

missing_cta = []
missing_hashtags = []
short_desc = []

for v in videos:
    title = v.get('snippet', {}).get('title', '')
    desc = v.get('snippet', {}).get('description', '')
    vid_id = v.get('id', '')
    
    # CTA Check
    cta_words = ['subscribe', 'like', 'comment', 'abonnieren', 'kommentier']
    if not any(w in desc.lower() for w in cta_words):
        missing_cta.append({'id': vid_id, 'title': title[:50]})
    
    # Hashtag Check
    if '#' not in desc:
        missing_hashtags.append({'id': vid_id, 'title': title[:50]})
    
    # Length Check
    if len(desc) < 200:
        short_desc.append({'id': vid_id, 'title': title[:50], 'length': len(desc)})

print(f"Missing CTAs:     {len(missing_cta)}")
print(f"Missing Hashtags: {len(missing_hashtags)}")
print(f"Short Desc <200:  {len(short_desc)}")

if missing_hashtags:
    print("\nVideos ohne Hashtags:")
    for item in missing_hashtags[:10]:
        print(f"  - {item['title']}")

# === 3. TAGS-ANALYSE ===
print("\n" + "=" * 40)
print("🏷️ 3. TAGS-ANALYSE")
print("=" * 40)

no_tags = []
few_tags = []
many_tags = []

for v in videos:
    title = v.get('snippet', {}).get('title', '')
    tags = v.get('snippet', {}).get('tags', [])
    vid_id = v.get('id', '')
    
    if len(tags) == 0:
        no_tags.append({'id': vid_id, 'title': title[:50]})
    elif len(tags) < 5:
        few_tags.append({'id': vid_id, 'title': title[:50], 'count': len(tags)})
    elif len(tags) > 15:
        many_tags.append({'id': vid_id, 'title': title[:50], 'count': len(tags)})

print(f"No Tags:          {len(no_tags)}")
print(f"Few Tags (<5):    {len(few_tags)}")
print(f"Many Tags (>15):  {len(many_tags)}")

# === 4. CATEGORY-ANALYSE ===
print("\n" + "=" * 40)
print("📂 4. CATEGORY-ANALYSE")
print("=" * 40)

categories = defaultdict(list)
CATEGORY_NAMES = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '20': 'Gaming',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Tech',
    '29': 'Nonprofits & Activism',
}

for v in videos:
    cat_id = v.get('snippet', {}).get('categoryId', '0')
    title = v.get('snippet', {}).get('title', '')
    categories[cat_id].append(title[:50])

for cat_id, items in sorted(categories.items(), key=lambda x: -len(x[1])):
    cat_name = CATEGORY_NAMES.get(cat_id, f'Unknown ({cat_id})')
    print(f"  {cat_name}: {len(items)}")

# === 5. CONTENT-KATEGORIEN ===
print("\n" + "=" * 40)
print("📺 5. CONTENT-SERIEN ANALYSE")
print("=" * 40)

series_videos = defaultdict(list)

for v in videos:
    title = v.get('snippet', {}).get('title', '').lower()
    vid_id = v.get('id', '')
    full_title = v.get('snippet', {}).get('title', '')
    
    if 'betty boop' in title:
        series_videos['Betty Boop'].append(full_title)
    elif 'soundie' in title:
        series_videos['Soundies'].append(full_title)
    elif 'alfred' in title or 'kwak' in title or 'quack' in title:
        series_videos['Alfred J. Kwak'].append(full_title)
    elif 'superman' in title and 'fleischer' in title.lower():
        series_videos['Superman/Fleischer'].append(full_title)
    elif 'wochenschau' in title or ('nr.' in title and ('1940' in title or '1941' in title or '1942' in title)):
        series_videos['Wochenschau'].append(full_title)
    elif 'felix' in title:
        series_videos['Felix the Cat'].append(full_title)
    elif 'looney' in title or 'merrie' in title:
        series_videos['Looney Tunes'].append(full_title)
    elif 'maulwurf' in title or 'krtek' in title:
        series_videos['Maulwurf'].append(full_title)
    elif 'bravestarr' in title:
        series_videos['BraveStarr'].append(full_title)
    elif 'christmas' in title or 'weihnacht' in title:
        series_videos['Christmas'].append(full_title)
    elif 'documentary' in title or 'doku' in title:
        series_videos['Documentary'].append(full_title)
    else:
        series_videos['Other/Misc'].append(full_title)

for series, items in sorted(series_videos.items(), key=lambda x: -len(x[1])):
    print(f"  {series}: {len(items)}")

# === 6. SHORTS-ANALYSE ===
print("\n" + "=" * 40)
print("📱 6. SHORTS-ANALYSE (<60 Sekunden)")
print("=" * 40)

shorts = []
for v in videos:
    duration = v.get('contentDetails', {}).get('duration', 'PT0S')
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        total = h * 3600 + m * 60 + s
        if total <= 60:
            shorts.append({
                'title': v.get('snippet', {}).get('title', ''),
                'duration': total,
                'id': v.get('id', '')
            })

print(f"Shorts gefunden: {len(shorts)}")
for s in shorts:
    print(f"  [{s['duration']}s] {s['title'][:60]}")

# === 7. RECORDING DETAILS ===
print("\n" + "=" * 40)
print("📍 7. RECORDING DETAILS (Location/Date)")
print("=" * 40)

# Diese Info ist nicht im Scan - muss via API geholt werden
print("⚠️ Recording Details nicht im Scan enthalten")
print("   → Muss via API pro Video geprüft werden")
print("   → Script: set_recording_locations.py vorbereitet")

# === ZUSAMMENFASSUNG ===
print("\n" + "=" * 80)
print("📋 ZUSAMMENFASSUNG - OFFENE PUNKTE")
print("=" * 80)

issues = {
    'Titel >70 chars': sum(len(items) for items in long_titles.values()),
    'Missing Hashtags': len(missing_hashtags),
    'Missing CTAs': len(missing_cta),
    'No Tags': len(no_tags),
    'Recording Locations': '? (API check needed)',
    'Recording Dates': '? (API check needed)',
    'Channel Keywords': 'FEHLT (manuell)',
    'Channel Trailer': 'FEHLT (manuell)',
    'Auto-Chapters': 'Aktivieren (manuell)',
}

for issue, count in issues.items():
    status = '✅' if count == 0 else '❌'
    print(f"  {status} {issue}: {count}")

# Speichere Report
report = {
    'generated': datetime.now().isoformat(),
    'total_videos': len(videos),
    'issues': {
        'long_titles': {series: len(items) for series, items in long_titles.items()},
        'long_titles_total': sum(len(items) for items in long_titles.values()),
        'missing_hashtags': len(missing_hashtags),
        'missing_hashtags_list': missing_hashtags,
        'missing_cta': len(missing_cta),
        'no_tags': len(no_tags),
        'shorts': len(shorts),
    },
    'series_counts': {series: len(items) for series, items in series_videos.items()},
    'category_distribution': {cat_id: len(items) for cat_id, items in categories.items()},
}

# Detaillierte lange Titel für Fixes
report['long_titles_detail'] = {}
for series, items in long_titles.items():
    report['long_titles_detail'][series] = items

with open('config/full_audit_2026_02.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n💾 Report gespeichert: config/full_audit_2026_02.json")
