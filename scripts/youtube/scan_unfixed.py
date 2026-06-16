"""Scan channel data for unfixed videos"""
import json

with open('config/channel_scan_2026_02_13.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

raw_indicators = ['sls', 'ARCHIVE PROTECTED', 'aac sls', 'CINEMA']
all_vids = scan.get('all', [])
print(f'Total videos in scan: {len(all_vids)}')

# Already fixed on Feb 13
fixed_ids = {'pFCidUe6JV4', 'Ima7UohPE4Y', 'SYY31eEbYiQ'}

unfixed = []
for v in all_vids:
    title = v.get('title', '')
    vid = v.get('id', '')
    
    if vid in fixed_ids:
        continue
    if 'Deleted video' in title:
        continue
    
    is_raw = any(ind.lower() in title.lower() for ind in raw_indicators)
    has_handle = '@remAIke_IT' in title or '@remAIke' in title
    missing_quality = '8K' not in title and '4K' not in title
    too_many_hash = title.count('#') > 2
    
    if is_raw or has_handle or too_many_hash:
        flags = []
        if is_raw: flags.append('RAW')
        if has_handle: flags.append('@HANDLE')
        if too_many_hash: flags.append('HASHTAGS')
        unfixed.append({'id': vid, 'title': title, 'flags': flags})

print(f'\nUnfixed videos: {len(unfixed)}')
for u in unfixed:
    flag_str = ','.join(u['flags'])
    print(f"  [{flag_str}] {u['id']}: {u['title'][:75]}")

# Also check fix plan - which were applied?
print("\n\n--- Fix Plan Status ---")
with open('config/new_uploads_fix_plan.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

scan_titles = {v['id']: v['title'] for v in all_vids}

for fix in plan.get('fixes', []):
    vid = fix['video_id']
    current = fix.get('current_title', '?')
    new = fix.get('new_title', 'N/A')
    scan_title = scan_titles.get(vid, 'NOT IN SCAN')
    
    if vid in fixed_ids:
        status = 'FIXED-FEB13'
    elif scan_title == 'NOT IN SCAN':
        status = 'MISSING'
    elif scan_title != current:
        status = 'CHANGED'
    else:
        status = 'UNFIXED'
    
    print(f"  [{status}] {vid}: {current[:50]}")
    if status == 'CHANGED':
        print(f"           NOW: {scan_title[:50]}")
