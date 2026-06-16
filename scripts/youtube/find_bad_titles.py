"""
find_bad_titles.py – Find ALL videos with bad/missing SEO titles
================================================================
Scans entire channel (including private) for:
- Raw filenames (no SEO applied)
- Default YouTube titles
- Old format titles (pre-SEO)
- Incomplete uploads

Saves results to config/bad_title_videos.json
Quota: search.list = 100 units per page, videos.list = 1 unit per call
"""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TOKEN = r'D:\remaike.TV\token.json'
OUTPUT = r'D:\remaike.TV\config\bad_title_videos.json'

creds = Credentials.from_authorized_user_file(TOKEN)
yt = build('youtube', 'v3', credentials=creds)

# ── Step 1: Get ALL video IDs via search (includes private) ──────────────────
print("Scanning all channel videos (search.list)...")
all_vids = []
page_token = None
for page in range(10):  # max 500 videos
    kwargs = dict(
        part='id',
        forMine=True,
        type='video',
        maxResults=50,
        order='date',
    )
    if page_token:
        kwargs['pageToken'] = page_token
    resp = yt.search().list(**kwargs).execute()
    for item in resp.get('items', []):
        vid_id = item['id'].get('videoId')
        if vid_id:
            all_vids.append(vid_id)
    page_token = resp.get('nextPageToken')
    print(f"  Page {page+1}: {len(all_vids)} videos")
    if not page_token:
        break

print(f"\nTotal videos found: {len(all_vids)}")

# ── Step 2: Get details in batches of 50 ─────────────────────────────────────
print("\nFetching video details (videos.list)...")
bad_videos = []
all_details = []

for i in range(0, len(all_vids), 50):
    batch = all_vids[i:i+50]
    detail = yt.videos().list(
        part='snippet,status',
        id=','.join(batch)
    ).execute()
    
    for v in detail.get('items', []):
        title = v['snippet']['title']
        vid_id = v['id']
        privacy = v['status']['privacyStatus']
        upload_status = v['status'].get('uploadStatus', '?')
        pub = v['snippet'].get('publishedAt', '?')[:10]
        desc = v['snippet'].get('description', '')
        
        all_details.append({
            'id': vid_id,
            'title': title,
            'privacy': privacy,
            'upload_status': upload_status,
            'published': pub,
        })
        
        # ── Detect BAD titles ────────────────────────────────────────────────
        is_bad = False
        reason = ''
        
        # Raw filenames (uploaded without SEO)
        if 'sls' in title.lower() and ('ARCHIVE' in title or 'archive' in title.lower()):
            is_bad = True
            reason = 'RAW FILENAME'
        elif title.lower().startswith('deutsche wochenschau nr'):
            is_bad = True
            reason = 'RAW FILENAME'
        elif title == 'Livestream von remAIke_IT':
            is_bad = True
            reason = 'DEFAULT YOUTUBE TITLE'
        elif title.startswith('History WochenschauTV'):
            is_bad = True
            reason = 'OLD FORMAT (pre-SEO)'
        elif upload_status == 'uploaded' and privacy == 'private':
            is_bad = True
            reason = 'INCOMPLETE UPLOAD'
        elif 'sls' in title.lower() and '8K' not in title:
            is_bad = True
            reason = 'RAW FILENAME (no 8K tag)'
        
        if is_bad:
            bad_videos.append({
                'id': vid_id,
                'title': title,
                'privacy': privacy,
                'upload_status': upload_status,
                'published': pub,
                'reason': reason,
                'description_preview': desc[:100] if desc else '',
            })

# ── Step 3: Report ────────────────────────────────────────────────────────────
print(f"\n{'='*80}")
print(f"BADLY NAMED VIDEOS: {len(bad_videos)} of {len(all_details)}")
print(f"{'='*80}")

for v in bad_videos:
    print(f"  [{v['id']}] {v['privacy']:8s} | {v['upload_status']:10s} | {v['reason']:25s}")
    print(f"    Title: {v['title'][:75]}")
    print()

# Save
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(bad_videos, f, indent=2, ensure_ascii=False)
print(f"Saved to {OUTPUT}")

# Summary
reasons = {}
for v in bad_videos:
    r = v['reason']
    reasons[r] = reasons.get(r, 0) + 1
print(f"\nBy reason:")
for r, c in sorted(reasons.items(), key=lambda x: -x[1]):
    print(f"  {r}: {c}")
