#!/usr/bin/env python3
"""Check current channel status from cached scan"""

import json

with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('='*60)
print('CHANNEL STATUS aus fresh_channel_scan.json')
print('='*60)
print(f"Scan Datum: {data['fetched_at']}")
print(f"Total Videos: {data['total_videos']}")
print(f"  Public: {data['public']}")
print(f"  Private: {data['private']}")
print()

# Kategorien zaehlen
categories = {
    'Betty Boop': 0,
    'Wochenschau': 0,
    'Alfred': 0,
    'Felix': 0,
    'Soundie': 0,
    'Looney/Porky': 0,
    'Superman': 0,
    'Other': 0
}

long_titles = []
no_hashtags = []

for v in data['videos']:
    title = v['snippet']['title']
    desc = v['snippet'].get('description', '')
    
    # Kategorisieren
    tl = title.lower()
    if 'betty boop' in tl or 'teaserama' in tl:
        categories['Betty Boop'] += 1
    elif 'wochenschau' in tl:
        categories['Wochenschau'] += 1
    elif 'alfred' in tl or 'kwak' in tl:
        categories['Alfred'] += 1
    elif 'felix' in tl:
        categories['Felix'] += 1
    elif 'soundie' in tl:
        categories['Soundie'] += 1
    elif 'looney' in tl or 'porky' in tl:
        categories['Looney/Porky'] += 1
    elif 'superman' in tl or 'fleischer' in tl:
        categories['Superman'] += 1
    else:
        categories['Other'] += 1
    
    # Titel-Laenge pruefen
    if len(title) > 70:
        long_titles.append((v['id'], len(title), title[:60]))
    
    # Hashtags pruefen
    if '#' not in desc:
        no_hashtags.append((v['id'], title[:50]))

print('KATEGORIEN:')
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f'  {cat}: {count}')

print()
print(f'TITEL >70 Zeichen: {len(long_titles)}')
if long_titles:
    for vid, length, title in long_titles[:10]:
        print(f'  [{length}] {title}...')
    if len(long_titles) > 10:
        print(f'  ... und {len(long_titles)-10} weitere')

print()
print(f'OHNE Hashtags: {len(no_hashtags)}')
if no_hashtags:
    for vid, title in no_hashtags[:5]:
        print(f'  {vid}: {title}...')

print()
print('='*60)
