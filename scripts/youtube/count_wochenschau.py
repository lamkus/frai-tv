#!/usr/bin/env python3
"""Count Wochenschau videos on channel"""

import json

with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
    data = json.load(f)

ws = [v for v in data['videos'] if 'wochenschau' in v['snippet']['title'].lower()]
print(f"Wochenschau Videos auf Channel: {len(ws)}")
print()
for v in ws[:20]:
    print(f"  {v['id']}: {v['snippet']['title'][:70]}")
