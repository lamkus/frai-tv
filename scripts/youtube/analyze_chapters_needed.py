#!/usr/bin/env python3
"""Analyze videos needing chapters - prioritize by length"""
import json
import re

with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
    scan = json.load(f)

public = [v for v in scan['videos'] if v.get('status', {}).get('privacyStatus') == 'public']

no_chapters = []
for v in public:
    desc = v['snippet'].get('description', '')
    title = v['snippet'].get('title', '')
    duration = v.get('contentDetails', {}).get('duration', 'PT0S')
    
    # Parse duration
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        h = int(match.group(1) or 0)
        m = int(match.group(2) or 0)
        s = int(match.group(3) or 0)
        total_min = h * 60 + m + s / 60
    else:
        total_min = 0
    
    # Check if no chapters (0:00 format)
    if '0:00' not in desc and total_min > 5:
        no_chapters.append({
            'id': v['id'],
            'title': title,
            'duration_min': round(total_min, 1),
            'views': int(v.get('statistics', {}).get('viewCount', '0'))
        })

# Sort by duration descending
no_chapters.sort(key=lambda x: -x['duration_min'])

print('=' * 70)
print(f'VIDEOS OHNE CHAPTERS (>5min): {len(no_chapters)}')
print('=' * 70)
print()
print('TOP 25 LÄNGSTE (Chapters am wichtigsten):')
print('-' * 70)
for i, v in enumerate(no_chapters[:25], 1):
    print(f"{i:2}. [{v['id']}] {v['duration_min']:6.1f}min | {v['title'][:42]}")

# Save for processing
with open('config/pending_updates/chapters_needed.json', 'w', encoding='utf-8') as f:
    json.dump(no_chapters, f, ensure_ascii=False, indent=2)

print()
print(f"Saved: config/pending_updates/chapters_needed.json")
