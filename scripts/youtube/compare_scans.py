"""Compare today's scan with yesterday's — find new uploads + remaining issues."""
import json

with open('config/live_scan_2026_02_18.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('config/live_scan_2026_02_17.json', 'r', encoding='utf-8') as f:
    old = json.load(f)

old_ids = {v['id'] for v in old['all_videos']}
new_ids = {v['id'] for v in data['all_videos']}

new_uploads = new_ids - old_ids
removed = old_ids - new_ids

print(f"Yesterday: {len(old_ids)} videos")
print(f"Today: {len(new_ids)} videos")
print(f"NEW uploads: {len(new_uploads)}")
print(f"Removed: {len(removed)}")

if new_uploads:
    print("\n=== NEW UPLOADS ===")
    for v in data['all_videos']:
        if v['id'] in new_uploads:
            ntags = len(v.get('tags', []))
            cat = v.get('categoryId', '?')
            print(f"  [{v['privacy']}] {v['id']}: {v['title']}")
            print(f"    Tags: {ntags} | Cat: {cat}")
            desc = v.get('description', '')[:120].replace('\n', ' ')
            print(f"    Desc: {desc}...")
            print()

if removed:
    print("\n=== REMOVED ===")
    for v in old['all_videos']:
        if v['id'] in removed:
            print(f"  {v['id']}: {v['title']}")

# All public videos with issues (excluding R12 localization)
print("\n=== PUBLIC VIDEOS WITH SEO ISSUES (excl R12) ===")
issue_count = 0
for v in data['all_videos']:
    if v.get('issues') and v['privacy'] == 'public':
        issues = [i for i in v['issues'] if 'R12' not in i]
        if issues:
            issue_count += 1
            print(f"  {v['id']}: {v['title'][:65]}")
            for i in issues:
                print(f"    -> {i}")

print(f"\nTotal public videos with issues: {issue_count}")

# Wochenschau stats
print("\n=== WOCHENSCHAU STATS ===")
ws_videos = [v for v in data['all_videos'] if 'Wochenschau' in v.get('title', '') or 'wochenschau' in v.get('title', '').lower()]
ws_public = [v for v in ws_videos if v['privacy'] == 'public']
print(f"Total Wochenschau: {len(ws_videos)}")
print(f"Public: {len(ws_public)}")
for v in ws_public:
    views = v.get('viewCount', 0)
    print(f"  {v['id']}: {v['title'][:60]} | Views: {views}")
