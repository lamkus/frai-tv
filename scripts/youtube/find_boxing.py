#!/usr/bin/env python3
"""Find Boxing Cats in cache."""
import json

d = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))

print("🐱 Suche nach 'box' oder '1894':")
print("=" * 70)

for v in d['videos']:
    title = v['snippet']['title']
    if 'box' in title.lower() or '1894' in title:
        print(f"{v['id']} | {title}")
