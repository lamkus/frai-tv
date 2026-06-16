"""Scan channel for videos missing localizations (<2 languages).

Reads all public videos and identifies those without English localizations.
Generates a fix plan with proper EN/DE titles and descriptions.
"""
import os, json, sys, re

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_FILE = 'token.json'
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

youtube = get_youtube()
quota_used = 0

# ── 1. Fetch all video IDs ──
print("Step 1: Fetching all channel videos...")
all_video_ids = []
next_token = None
while True:
    resp = youtube.playlistItems().list(
        part='contentDetails', playlistId=UPLOAD_PL,
        maxResults=50, pageToken=next_token
    ).execute()
    quota_used += 1
    for item in resp.get('items', []):
        all_video_ids.append(item['contentDetails']['videoId'])
    next_token = resp.get('nextPageToken')
    if not next_token:
        break
print(f"  Total videos: {len(all_video_ids)}")

# ── 2. Fetch video details with localizations ──
print("\nStep 2: Checking localizations...")
missing_locs = []
has_locs = 0

for i in range(0, len(all_video_ids), 50):
    batch = all_video_ids[i:i+50]
    resp = youtube.videos().list(
        part='snippet,localizations,status', id=','.join(batch)
    ).execute()
    quota_used += 1
    
    for v in resp.get('items', []):
        if v['status']['privacyStatus'] != 'public':
            continue
        
        vid = v['id']
        snip = v['snippet']
        title = snip.get('title', '')
        desc = snip.get('description', '')
        default_lang = snip.get('defaultLanguage', '')
        default_audio = snip.get('defaultAudioLanguage', '')
        locs = v.get('localizations', {})
        loc_langs = list(locs.keys())
        
        if len(loc_langs) >= 2:
            has_locs += 1
            continue
        
        # Determine what's missing
        has_de = 'de' in loc_langs
        has_en = 'en' in loc_langs
        
        missing_locs.append({
            'id': vid,
            'title': title,
            'desc_preview': desc[:100].replace('\n', ' '),
            'default_lang': default_lang,
            'default_audio': default_audio,
            'current_locs': loc_langs,
            'has_de': has_de,
            'has_en': has_en,
        })

print(f"  Videos with 2+ localizations: {has_locs}")
print(f"  Videos missing localizations: {len(missing_locs)}")
print(f"  Quota used: {quota_used}")

# ── 3. Categorize ──
print(f"\nStep 3: Categorizing {len(missing_locs)} videos...")

# Show sample
for v in missing_locs[:10]:
    locs_str = ', '.join(v['current_locs']) if v['current_locs'] else 'NONE'
    print(f"  {v['id']} | {v['title'][:55]} | locs: [{locs_str}]")
if len(missing_locs) > 10:
    print(f"  ... and {len(missing_locs) - 10} more")

# ── 4. Save report ──
report = {
    'scan_date': '2026-02-19',
    'total_scanned': len(all_video_ids),
    'with_locs': has_locs,
    'missing_locs': len(missing_locs),
    'quota_used': quota_used,
    'videos': missing_locs,
}

output_file = 'config/localizations_scan_2026_02_19.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {output_file}")
print(f"Total quota: {quota_used} Units")
