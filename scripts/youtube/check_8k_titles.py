#!/usr/bin/env python3
"""Check how many titles start with 8K in latest channel scan"""
import json

def main():
    with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
        data = json.load(f)

    vids = [
        v for v in data.get('videos', [])
        if v.get('kind') == 'youtube#video'
        and v.get('status', {}).get('privacyStatus') == 'public'
    ]
    total = len(vids)
    not_start = []

    for v in vids:
        title = v['snippet']['title']
        if not title.strip().lower().startswith('8k '):
            not_start.append((v['id'], title))

    print(f'Public videos: {total}')
    print(f'Not starting with 8K: {len(not_start)}')
    print('Examples:')
    for vid, title in not_start[:15]:
        print(f'[{vid}] {title[:80]}')

if __name__ == '__main__':
    main()
