#!/usr/bin/env python3
"""Find cat-related videos."""
import json

data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))

print("🐱 KATZEN-VIDEOS:")
print("=" * 70)

for v in data['videos']:
    title = v['snippet']['title'].lower()
    desc = v['snippet'].get('description', '').lower()
    if any(x in title or x in desc for x in ['cat', 'katze', 'kitty', 'felix', 'feline', 'gato']):
        print(f"{v['id']} | {v['snippet']['title'][:60]}")
