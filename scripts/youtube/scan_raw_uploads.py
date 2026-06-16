#!/usr/bin/env python3
"""Scan channel for ALL new/unnamed uploads. Compare against known DB + batch progress."""
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

# Fetch ALL videos
all_vids = []
page_token = None
while True:
    resp = yt.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=page_token
    ).execute()
    for it in resp.get('items', []):
        vid = it['contentDetails']['videoId']
        pub = it['contentDetails'].get('videoPublishedAt', it['snippet'].get('publishedAt', ''))
        title = it['snippet'].get('title', '???')
        desc = it['snippet'].get('description', '')[:200]
        all_vids.append({'id': vid, 'pub': pub, 'title': title, 'desc_preview': desc})
    page_token = resp.get('nextPageToken')
    if not page_token:
        break

print(f"Total videos on channel: {len(all_vids)}")

# Find videos with raw/unnamed titles (contain "sls", "aac", "ARCHIVE", or are very short/lowercase)
raw_uploads = []
for v in all_vids:
    t = v['title']
    is_raw = any([
        ' sls ' in t.lower(),
        ' aac ' in t.lower(),
        'archive blurred' in t.lower(),
        t == 'Deleted video',
        t == 'Private video',
        # Check if title is mostly lowercase (raw upload)
        t == t.lower() and len(t) > 5,
        # Check for raw filename patterns
        'mov ' in t.lower() and 'sls' in t.lower(),
    ])
    if is_raw:
        raw_uploads.append(v)

print(f"\n{'='*70}")
print(f"RAW/UNNAMED UPLOADS: {len(raw_uploads)}")
for v in sorted(raw_uploads, key=lambda x: x['pub'], reverse=True):
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:80]}")
    if v['desc_preview']:
        print(f"           desc: {v['desc_preview'][:80]}")

# Also show newest 20
print(f"\n{'='*70}")
print(f"NEWEST 20:")
for v in sorted(all_vids, key=lambda x: x['pub'], reverse=True)[:20]:
    marker = " ⚠️RAW" if v in raw_uploads else ""
    print(f"  {v['id']} | {v['pub'][:10]} | {v['title'][:65]}{marker}")

# Save for later
with open(os.path.join(ROOT, 'config', 'channel_scan_2026_02_13.json'), 'w', encoding='utf-8') as f:
    json.dump({'total': len(all_vids), 'raw': raw_uploads, 'all': all_vids}, f, indent=2, ensure_ascii=False)
print(f"\nSaved scan to config/channel_scan_2026_02_13.json")
