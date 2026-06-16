"""Get details of videos needing fixes"""
import json

with open('config/fresh_audit_2026_02_08.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

new = data['new_uploads']
problems = [v for v in new if v['score'] < 95]
print('=== VIDEOS NEEDING FIXES ===')
for v in problems:
    print(f"ID: {v['id']}")
    print(f"  Title:    {v['title']}")
    print(f"  Score:    {v['score']}")
    print(f"  Privacy:  {v['privacy']}")
    print(f"  Category: {v['category']}")
    print(f"  Issues:   {v['issues']}")
    print(f"  Warnings: {v['warnings']}")
    print()

# Wochenschau with wrong category
all_v = data['all_videos']
wc = [v for v in all_v if 'wochenschau' in v['title'].lower() and v['category'] != '27' and v['privacy'] == 'public']
print(f'=== WOCHENSCHAU WRONG CATEGORY ({len(wc)}) ===')
for v in wc:
    print(f"  {v['id']}: cat={v['category']} | {v['title'][:65]}")

# Videos with too many hashtags (>5)
hh = [v for v in all_v if v['hashtag_count'] > 5 and v['privacy'] == 'public']
print(f'\n=== TOO MANY HASHTAGS ({len(hh)}) ===')
for v in hh:
    print(f"  {v['id']}: {v['hashtag_count']} hashtags | {v['title'][:55]}")
