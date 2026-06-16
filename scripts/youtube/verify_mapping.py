"""Verify Alfred episode mapping"""
import json
import re

with open('config/live_scan_2026_02_17.json', 'r', encoding='utf-8') as f:
    scan = json.load(f)

alfred = [v for v in scan['all_videos'] if 'ARCHIVE BLURRED' in v['title']]

with open('config/alfred_blur_naming_DE.json', 'r', encoding='utf-8') as f:
    naming = json.load(f)

episodes_by_file = {}
for ep in naming['episodes']:
    if ep.get('file_nr'):
        episodes_by_file[ep['file_nr']] = ep

print('ALFRED RAW TITLE VERIFICATION:')
print('=' * 80)
for v in sorted(alfred, key=lambda x: x['title']):
    vid = v['id']
    raw = v['title']
    match = re.match(r'(\d+)\s+', raw)
    if match:
        file_nr = int(match.group(1))
        ep = episodes_by_file.get(file_nr)
        if ep:
            bnr = ep['broadcast_nr']
            proper = ep['youtube_title']
            print(f"  {vid}: File#{file_nr:02d} -> Broadcast#{bnr:02d}")
            print(f"    RAW:    {raw}")
            print(f"    PROPER: {proper}")
            print()
        else:
            print(f"  {vid}: File#{file_nr:02d} -> NO EPISODE MATCH!")
            print(f"    RAW: {raw}")
            print()

# Also check 7. Sinn
sinn = [v for v in scan['all_videos'] if '7  sinn' in v['title'].lower() or '7. sinn' in v['title'].lower()]
print('\nDER 7. SINN VIDEOS:')
print('=' * 80)
for v in sinn:
    print(f"  {v['id']}: [{v['privacy']}] {v['title']}")
