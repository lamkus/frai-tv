#!/usr/bin/env python3
"""Find specific video."""
import json

data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))

target = 'T-EsdXGhqog'
found = False

for v in data['videos']:
    if v['id'] == target:
        print('GEFUNDEN!')
        print('ID:', v['id'])
        print('Title:', v['snippet']['title'])
        print('Views:', v.get('statistics', {}).get('viewCount', '?'))
        print('Status:', v.get('status', {}).get('privacyStatus', '?'))
        found = True
        break

if not found:
    print(f'Video {target} NICHT im Cache!')
    print(f'Cache hat {len(data["videos"])} Videos')
    print(f'Cache von: {data.get("fetched_at")}')
    
    # Suche nach 516
    print()
    print('Suche nach "516" im Titel:')
    for v in data['videos']:
        if '516' in v['snippet']['title']:
            print(f"  {v['id']} | {v['snippet']['title']}")
