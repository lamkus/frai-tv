#!/usr/bin/env python3
"""Scan channel for new uploads, Maulwurf status, and playlist gaps."""
import requests, os, json, sqlite3

API_KEY = os.getenv('YOUTUBE_API_KEY')
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
ROOT = r'D:\remaike.TV'

# Step 1: Fetch ALL videos from upload playlist (Public API)
all_vids = []
page_token = None
pages = 0
while True:
    pages += 1
    params = {
        'part': 'contentDetails,snippet',
        'playlistId': UPLOAD_PL,
        'maxResults': 50,
        'key': API_KEY
    }
    if page_token:
        params['pageToken'] = page_token
    r = requests.get('https://youtube.googleapis.com/youtube/v3/playlistItems', params=params)
    data = r.json()
    if 'error' in data:
        print(f"ERROR: {data['error']['message']}")
        break
    for it in data.get('items', []):
        vid = it['contentDetails']['videoId']
        pub = it['contentDetails'].get('videoPublishedAt', it['snippet'].get('publishedAt', ''))
        title = it['snippet'].get('title', '???')
        all_vids.append({'id': vid, 'pub': pub, 'title': title})
    page_token = data.get('nextPageToken')
    if not page_token:
        break

print(f"Total videos on channel: {len(all_vids)} ({pages} pages, ~{pages} quota)")

# Step 2: Load known IDs from DB
db_path = os.path.join(ROOT, 'tools', 'channel_manager', 'channel_manager.db')
known_ids = set()
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id FROM videos").fetchall()
    known_ids = {r[0] for r in rows}
    conn.close()
print(f"Known in DB: {len(known_ids)}")

# Step 3: Load batch progress
bp_path = os.path.join(ROOT, 'config', 'pending_updates', 'batch_progress_2026_02_11.json')
batch_ids = set()
if os.path.exists(bp_path):
    with open(bp_path) as f:
        bp = json.load(f)
    batch_ids = set(bp.get('completed', []))
print(f"Batch-fixed: {len(batch_ids)}")

combined_known = known_ids | batch_ids

# Step 4: Find NEW videos
new_vids = [v for v in all_vids if v['id'] not in combined_known]
print(f"\n{'='*70}")
print(f"NEW/UNKNOWN videos (not in DB or batch): {len(new_vids)}")
for v in sorted(new_vids, key=lambda x: x['pub'], reverse=True):
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:70]}")

# Step 5: Maulwurf videos
maulwurf = [v for v in all_vids if 'maulwurf' in v['title'].lower() or 'krtek' in v['title'].lower() or 'mole' in v['title'].lower()]
print(f"\n{'='*70}")
print(f"MAULWURF VIDEOS: {len(maulwurf)}")
for v in sorted(maulwurf, key=lambda x: x['pub']):
    is_new = " [NEW!]" if v['id'] not in combined_known else ""
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:70]}{is_new}")

# Step 6: Newest 15
print(f"\n{'='*70}")
print(f"NEWEST 15 VIDEOS:")
sorted_all = sorted(all_vids, key=lambda x: x['pub'], reverse=True)
for v in sorted_all[:15]:
    marker = " [NEW!]" if v['id'] not in combined_known else ""
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:65]}{marker}")

# Step 7: Series breakdown
print(f"\n{'='*70}")
print("SERIES COUNTS:")
series = {}
for v in all_vids:
    t = v['title'].lower()
    if 'betty boop' in t: s = 'Betty Boop'
    elif 'alfred' in t or 'kwak' in t: s = 'Alfred J. Kwak'
    elif 'wochenschau' in t or 'newsreel' in t: s = 'Wochenschau'
    elif 'soundie' in t: s = 'Soundies'
    elif 'superman' in t: s = 'Superman'
    elif 'maulwurf' in t or 'krtek' in t: s = 'Maulwurf'
    elif 'casper' in t: s = 'Casper'
    elif 'felix' in t: s = 'Felix the Cat'
    elif 'porky' in t: s = 'Porky Pig'
    elif 'ken block' in t or 'gymkhana' in t: s = 'Ken Block'
    elif 'looney' in t: s = 'Looney Tunes'
    elif 'astro boy' in t: s = 'Astro Boy'
    else: s = 'Other'
    series[s] = series.get(s, 0) + 1

for s, c in sorted(series.items(), key=lambda x: -x[1]):
    print(f"  {c:3d} | {s}")

# Save full list for later use
output_path = os.path.join(ROOT, 'config', 'channel_scan_2026_02_12.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump({'total': len(all_vids), 'new': [v for v in new_vids], 'maulwurf': maulwurf, 'all': all_vids}, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output_path}")
