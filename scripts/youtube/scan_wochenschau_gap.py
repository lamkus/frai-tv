#!/usr/bin/env python3
"""Verified YouTube Wochenschau gap analysis via OAuth."""
import json, os, re, sys

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, '..', '..')

# OAuth
token_path = os.path.join(ROOT, 'token.json')
creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, 'w') as f:
            f.write(creds.to_json())
        print('Token refreshed')
    else:
        print('ERROR: No valid OAuth token')
        sys.exit(1)

yt = build('youtube', 'v3', credentials=creds)
print('OAuth OK')

# 1) Get ALL upload video IDs
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
all_ids = []
page_token = None
while True:
    req = yt.playlistItems().list(
        part='contentDetails', playlistId=UPLOAD_PL,
        maxResults=50, pageToken=page_token
    )
    resp = req.execute()
    for item in resp['items']:
        all_ids.append(item['contentDetails']['videoId'])
    page_token = resp.get('nextPageToken')
    if not page_token:
        break
print(f'Total channel videos: {len(all_ids)}')

# 2) Get snippet+status for ALL in 50-item batches
wochenschau = []
for i in range(0, len(all_ids), 50):
    batch = all_ids[i:i+50]
    req = yt.videos().list(part='snippet,status', id=','.join(batch))
    resp = req.execute()
    for item in resp.get('items', []):
        tl = item['snippet']['title'].lower()
        if any(kw in tl for kw in ['wochenschau', 'newsreel', 'pre-war', 'phoney war']):
            wochenschau.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'privacy': item['status']['privacyStatus']
            })

print(f'Wochenschau videos found: {len(wochenschau)}')

# 3) Load events.json for date-based matching
events_path = os.path.join(ROOT, 'config', 'wochenschau_events.json')
with open(events_path, 'r', encoding='utf-8') as f:
    events = json.load(f)

date_to_ep = {}
for ep_str, info in events.items():
    d = info.get('date', '')
    if d:
        date_to_ep[d] = int(ep_str)

# 4) Extract episode numbers - multiple patterns
for v in wochenschau:
    t = v['title']
    nr = None

    # Pattern 1: 'Nr. 459' or 'Nr.459' or 'Nr 459'
    m = re.search(r'Nr\.?\s*(\d{3})', t)
    if m:
        nr = int(m.group(1))

    # Pattern 2: German date DD.MM.YYYY in title -> match via events.json
    if nr is None:
        m = re.search(r'(\d{2}\.\d{2}\.\d{4})', t)
        if m:
            nr = date_to_ep.get(m.group(1))

    v['nr'] = nr

wochenschau.sort(key=lambda x: (x['nr'] or 9999, x['title']))

# 5) Print all found
print()
print('=' * 80)
print('ALL WOCHENSCHAU VIDEOS ON YOUTUBE (VERIFIED via OAuth)')
print('=' * 80)
for v in wochenschau:
    nr_s = 'Nr' + str(v['nr']) if v['nr'] else 'Nr???'
    p = v['privacy'][:3].upper()
    print(f'  [{p}] {nr_s:>6} | {v["title"]}')

# 6) Gap analysis vs 60 targets
TARGET = [
    459,468,470,471,473,477,480,482,483,488,
    491,492,493,496,502,504,505,506,508,509,
    512,513,514,515,518,519,520,522,523,542,
    543,544,545,547,548,550,552,553,554,555,
    556,565,567,569,573,605,606,607,652,654,
    720,721,722,746,749,750,751,752,753,754
]

yt_eps = {}
for v in wochenschau:
    if v['nr'] and v['nr'] not in yt_eps:
        yt_eps[v['nr']] = v

pub, prv, miss = [], [], []
for ep in sorted(TARGET):
    if ep in yt_eps:
        if yt_eps[ep]['privacy'] == 'public':
            pub.append(ep)
        else:
            prv.append(ep)
    else:
        miss.append(ep)

extra = [nr for nr in sorted(yt_eps.keys()) if nr not in TARGET]
unmatched = [v for v in wochenschau if v['nr'] is None]

print()
print('=' * 80)
print('GAP REPORT: 60 TARGET EPISODES vs YOUTUBE')
print('=' * 80)
print(f'  PUBLIC on YT:  {len(pub):3d} episodes')
for ep in pub:
    v = yt_eps[ep]
    print(f'    {ep}: {v["title"][:72]}')

print(f'\n  PRIVATE on YT: {len(prv):3d} episodes')
for ep in prv:
    v = yt_eps[ep]
    print(f'    {ep}: {v["title"][:72]}')

print(f'\n  MISSING (not on YT): {len(miss):3d} episodes  *** NEED UPLOAD ***')
for ep in miss:
    ev = events.get(str(ep), {})
    d = ev.get('date', '?')
    e = ev.get('event', '?')[:50]
    print(f'    {ep}: {d} - {e}')

if extra:
    print(f'\n  On YT but NOT in 60-list: {len(extra)}')
    for nr in extra:
        v = yt_eps[nr]
        print(f'    {nr}: {v["title"][:72]}')

if unmatched:
    print(f'\n  UNMATCHED (no episode nr found): {len(unmatched)}')
    for v in unmatched:
        p = v['privacy'][:3].upper()
        print(f'    [{p}] {v["title"][:65]}')
        print(f'         https://youtube.com/watch?v={v["id"]}')

# 7) Save report
report = {
    'scan_date': '2026-02-22',
    'total_channel_videos': len(all_ids),
    'wochenschau_found': len(wochenschau),
    'target_60': TARGET,
    'public': pub,
    'private': prv,
    'missing': miss,
    'extra_on_yt': extra,
    'unmatched': [{'id': v['id'], 'title': v['title'], 'privacy': v['privacy']} for v in unmatched],
    'all_wochenschau': wochenschau
}
out_path = os.path.join(ROOT, 'config', 'wochenschau_yt_gap_2026_02_22.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f'\nReport saved: {out_path}')
