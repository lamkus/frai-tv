#!/usr/bin/env python3
"""Scan channel for new uploads, Maulwurf status, and playlist gaps. Uses OAuth."""
import os, json, sqlite3
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT = r'D:\remaike.TV'
TOKEN = os.path.join(ROOT, 'token.json')
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

def get_yt():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

yt = get_yt()

# Fetch ALL videos from upload playlist
all_vids = []
page_token = None
pages = 0
while True:
    pages += 1
    req = yt.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=page_token
    )
    resp = req.execute()
    for it in resp.get('items', []):
        vid = it['contentDetails']['videoId']
        pub = it['contentDetails'].get('videoPublishedAt', it['snippet'].get('publishedAt', ''))
        title = it['snippet'].get('title', '???')
        all_vids.append({'id': vid, 'pub': pub, 'title': title})
    page_token = resp.get('nextPageToken')
    if not page_token:
        break

print(f"Total videos on channel: {len(all_vids)} ({pages} pages)")

# Load known IDs from DB
db_path = os.path.join(ROOT, 'tools', 'channel_manager', 'channel_manager.db')
known_ids = set()
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id FROM videos").fetchall()
    known_ids = {r[0] for r in rows}
    conn.close()
print(f"Known in DB: {len(known_ids)}")

# Load batch progress
bp_path = os.path.join(ROOT, 'config', 'pending_updates', 'batch_progress_2026_02_11.json')
batch_ids = set()
if os.path.exists(bp_path):
    with open(bp_path) as f:
        bp = json.load(f)
    batch_ids = set(bp.get('completed', []))
print(f"Batch-fixed: {len(batch_ids)}")

combined_known = known_ids | batch_ids

# Find NEW videos
new_vids = [v for v in all_vids if v['id'] not in combined_known]
print(f"\n{'='*70}")
print(f"NEW/UNKNOWN videos: {len(new_vids)}")
for v in sorted(new_vids, key=lambda x: x['pub'], reverse=True):
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:70]}")

# Maulwurf videos
maulwurf = [v for v in all_vids if any(k in v['title'].lower() for k in ['maulwurf', 'krtek', 'mole'])]
print(f"\n{'='*70}")
print(f"MAULWURF VIDEOS: {len(maulwurf)}")
for v in sorted(maulwurf, key=lambda x: x['title']):
    is_new = " [NEW!]" if v['id'] not in combined_known else ""
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:70]}{is_new}")

# Newest 15
print(f"\n{'='*70}")
print(f"NEWEST 15 VIDEOS:")
sorted_all = sorted(all_vids, key=lambda x: x['pub'], reverse=True)
for v in sorted_all[:15]:
    marker = " [NEW!]" if v['id'] not in combined_known else ""
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:65]}{marker}")

# Series breakdown
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
    elif 'bravestarr' in t: s = 'BraveStarr'
    else: s = 'Other'
    series[s] = series.get(s, 0) + 1
for s, c in sorted(series.items(), key=lambda x: -x[1]):
    print(f"  {c:3d} | {s}")

# Save scan
output = os.path.join(ROOT, 'config', 'channel_scan_2026_02_12.json')
with open(output, 'w', encoding='utf-8') as f:
    json.dump({
        'scan_date': '2026-02-12',
        'total': len(all_vids),
        'new_count': len(new_vids),
        'new': new_vids,
        'maulwurf': maulwurf,
        'all': all_vids
    }, f, indent=2, ensure_ascii=False)
print(f"\nSaved to {output}")
