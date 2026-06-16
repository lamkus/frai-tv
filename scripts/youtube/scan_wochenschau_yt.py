#!/usr/bin/env python3
"""Scan ALL Wochenschau videos on YouTube channel - verified via Public API."""
import json, os, re, requests

API_KEY = os.getenv('YOUTUBE_API_KEY')
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# 1) Get ALL video IDs from uploads playlist
all_vids = []
token = None
while True:
    params = {'part': 'contentDetails', 'playlistId': UPLOAD_PL, 'maxResults': 50, 'key': API_KEY}
    if token:
        params['pageToken'] = token
    r = requests.get('https://youtube.googleapis.com/youtube/v3/playlistItems', params=params)
    data = r.json()
    if 'items' not in data:
        print(f'ERROR: {data}')
        break
    for item in data['items']:
        all_vids.append(item['contentDetails']['videoId'])
    token = data.get('nextPageToken')
    if not token:
        break

print(f"Total videos on channel: {len(all_vids)}")

# 2) Get snippet+status for ALL videos in 50-item batches
all_details = []
for i in range(0, len(all_vids), 50):
    batch = all_vids[i:i+50]
    params = {'part': 'snippet,status', 'id': ','.join(batch), 'key': API_KEY}
    r = requests.get('https://youtube.googleapis.com/youtube/v3/videos', params=params)
    data = r.json()
    for item in data.get('items', []):
        all_details.append(item)

# 3) Filter Wochenschau videos
wochenschau = []
for item in all_details:
    title = item['snippet']['title']
    vid_id = item['id']
    privacy = item['status']['privacyStatus']
    tl = title.lower()
    if 'wochenschau' in tl or 'newsreel' in tl or 'pre-war' in tl or 'phoney war' in tl:
        wochenschau.append({'id': vid_id, 'title': title, 'privacy': privacy})

print(f"Wochenschau videos found: {len(wochenschau)}")

# 4) Load events.json for date-based matching
events_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'wochenschau_events.json')
with open(events_path, 'r', encoding='utf-8') as f:
    events = json.load(f)

# Build date->episode lookup
date_to_ep = {}
for ep_str, info in events.items():
    date_val = info.get('date', '')
    if date_val:
        date_to_ep[date_val] = int(ep_str)

# 5) Extract episode numbers - multiple patterns
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
            date_str = m.group(1)
            nr = date_to_ep.get(date_str)
    
    # Pattern 3: ISO date YYYY-MM-DD
    if nr is None:
        m = re.search(r'(\d{4}-\d{2}-\d{2})', t)
        if m:
            # Convert to DD.MM.YYYY
            parts = m.group(1).split('-')
            date_str = f"{parts[2]}.{parts[1]}.{parts[0]}"
            nr = date_to_ep.get(date_str)
    
    v['nr'] = nr

# Sort by episode number
wochenschau.sort(key=lambda x: (x['nr'] or 9999, x['title']))

# 6) Print results
print("\n" + "="*80)
print("WOCHENSCHAU VIDEOS ON YOUTUBE (VERIFIED)")
print("="*80)
for v in wochenschau:
    nr_str = f"Nr{v['nr']}" if v['nr'] else "Nr???"
    priv = v['privacy'].upper()[:3]
    print(f"  [{priv}] {nr_str:>6} | {v['title']}")

# 7) Our target 60 episodes
TARGET_60 = [459,468,470,471,473,477,480,482,483,488,491,492,493,496,502,504,505,506,
             508,509,512,513,514,515,518,519,520,522,523,542,543,544,545,547,548,550,
             552,553,554,555,556,565,567,569,573,605,606,607,652,654,720,721,722,746,
             749,750,751,752,753,754]

yt_episodes = {}
for v in wochenschau:
    if v['nr']:
        if v['nr'] not in yt_episodes:
            yt_episodes[v['nr']] = []
        yt_episodes[v['nr']].append(v)

# 8) Analysis
print("\n" + "="*80)
print("GAP ANALYSIS: 60 TARGET EPISODES vs YOUTUBE")
print("="*80)

on_yt_public = []
on_yt_private = []
on_yt_unlisted = []
not_on_yt = []
unmatched_on_yt = []

for ep in sorted(TARGET_60):
    if ep in yt_episodes:
        vids = yt_episodes[ep]
        for v in vids:
            if v['privacy'] == 'public':
                on_yt_public.append(ep)
            elif v['privacy'] == 'private':
                on_yt_private.append(ep)
            else:
                on_yt_unlisted.append(ep)
    else:
        not_on_yt.append(ep)

# Check for YT episodes NOT in our 60 list
for nr in sorted(yt_episodes.keys()):
    if nr not in TARGET_60:
        unmatched_on_yt.append(nr)

# Unmatched videos (no episode number)
unmatched_vids = [v for v in wochenschau if v['nr'] is None]

print(f"\n  PUBLIC on YT:     {len(on_yt_public)} episodes")
for ep in on_yt_public:
    vid = yt_episodes[ep][0]
    print(f"    Nr{ep}: {vid['title'][:70]}")

print(f"\n  PRIVATE on YT:    {len(on_yt_private)} episodes")
for ep in on_yt_private:
    vid = yt_episodes[ep][0]
    print(f"    Nr{ep}: {vid['title'][:70]}")

print(f"\n  NOT on YouTube:   {len(not_on_yt)} episodes - NEED UPLOAD")
for ep in not_on_yt:
    # Check if event data exists
    ev = events.get(str(ep), {})
    date = ev.get('date', '?')
    event = ev.get('event', '?')[:50]
    print(f"    Nr{ep}: {date} - {event}")

print(f"\n  On YT but NOT in 60-list: {len(unmatched_on_yt)}")
for nr in unmatched_on_yt:
    vid = yt_episodes[nr][0]
    print(f"    Nr{nr}: {vid['title'][:70]}")

if unmatched_vids:
    print(f"\n  UNMATCHED (no episode nr): {len(unmatched_vids)}")
    for v in unmatched_vids:
        print(f"    [{v['privacy'][:3].upper()}] {v['title'][:70]}")
        print(f"         ID: {v['id']}")

# 9) Save full report
report = {
    'scan_date': '2026-02-22',
    'total_channel_videos': len(all_vids),
    'wochenschau_found': len(wochenschau),
    'target_60': TARGET_60,
    'public': on_yt_public,
    'private': on_yt_private,
    'not_on_youtube': not_on_yt,
    'on_yt_not_in_60': unmatched_on_yt,
    'unmatched_videos': [{'id': v['id'], 'title': v['title'], 'privacy': v['privacy']} for v in unmatched_vids],
    'all_wochenschau': wochenschau
}
out = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'wochenschau_yt_gap_2026_02_22.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nFull report: config/wochenschau_yt_gap_2026_02_22.json")
