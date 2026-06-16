"""Detailed analysis of Der 7. Sinn videos"""
import json

with open('config/live_scan_2026_02_17.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

sinn = [v for v in scan['all_videos'] if '7' in v['title'] and ('sinn' in v['title'].lower() or 'Sinn' in v['title'])]

for v in sinn:
    print(f"ID: {v['id']}")
    print(f"Title: {v['title']}")
    print(f"Privacy: {v['privacy']}")
    print(f"Category: {v['categoryId']}")
    print(f"Tags: {v['tags']}")
    print(f"Duration: {v['duration']}")
    print(f"Published: {v['publishedAt']}")
    print(f"Desc length: {len(v['description'])}")
    if v['description']:
        print(f"Desc preview: {v['description'][:300]}")
    print('---')
