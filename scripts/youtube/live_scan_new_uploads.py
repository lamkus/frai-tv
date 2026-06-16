#!/usr/bin/env python3
"""
Live-Scan: Find all videos that need renaming (drafts, new uploads, bad titles).
Scans the full upload playlist via OAuth to include private/draft videos.
"""
import json
import os
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def main():
    yt = get_youtube()
    
    # Get upload playlist
    UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
    
    # Fetch ALL video IDs from upload playlist
    all_ids = []
    token = None
    while True:
        req = yt.playlistItems().list(
            part='contentDetails,snippet',
            playlistId=UPLOAD_PL,
            maxResults=50,
            pageToken=token
        )
        resp = req.execute()
        for item in resp['items']:
            vid_id = item['contentDetails']['videoId']
            title = item['snippet']['title']
            all_ids.append((vid_id, title))
        token = resp.get('nextPageToken')
        if not token:
            break
    
    print(f"Total videos in channel: {len(all_ids)}")
    
    # Patterns that indicate a video needs renaming
    BAD_PATTERNS = [
        r'^Nr\d+\s+strike',           # "Nr459 strike 8k"
        r'^\d{4}\s+\d{2}\s+\d{2}\s+wochenschau',  # "1945 01 25 wochenschau nr 750"
        r'\bsls\b',                    # Contains "sls" (raw upload marker)
        r'^wochenschau\s+nr\s+\d+',    # "wochenschau nr 750 sls 8K HQ"
        r'_sls_',                       # underscore sls underscore
        r'^[a-z0-9_\-]+\.(mp4|mkv)',   # Looks like a filename
        r'^\d+\s*[-_]\s*\d+',          # Just numbers
        r'^(?:Private|Deleted)\s+video', # Private/Deleted
    ]
    
    # Also detect any that lack proper format
    PROPER_PATTERN = re.compile(
        r'^(Wochenschau:|Betty Boop:|Superman:|Felix|Alfred|Soundie:|Looney Tunes|'
        r'Popeye|Casper|Der kleine Maulwurf|BraveStarr|Ken Block|Christmas|'
        r'Der 7\. Sinn|NASA|Apollo|Skylab|Krtek|The Mole|Clever & Smart|'
        r'Asterix|Porky Pig|Bugs Bunny|Daffy Duck|Tom and Jerry|'
        r'Wochenschau LIVE|Dr\. Jekyll|Nosferatu|Phantom of the Opera|'
        r'The Man Who Laughs|The Cabinet)'
    )
    
    needs_fix = []
    drafts = []
    bad_titles = []
    
    # Get full snippet for ALL videos (batch of 50)
    print("\nFetching full video details...")
    quota_reads = 0
    all_video_data = []
    
    for i in range(0, len(all_ids), 50):
        batch_ids = [vid_id for vid_id, _ in all_ids[i:i+50]]
        resp = yt.videos().list(
            part='snippet,status',
            id=','.join(batch_ids)
        ).execute()
        quota_reads += 1
        all_video_data.extend(resp.get('items', []))
    
    print(f"Fetched {len(all_video_data)} videos ({quota_reads} API reads)")
    
    for item in all_video_data:
        vid_id = item['id']
        snippet = item['snippet']
        status = item['status']
        title = snippet['title']
        privacy = status.get('privacyStatus', 'unknown')
        category = snippet.get('categoryId', '?')
        tags = snippet.get('tags', [])
        desc_line1 = snippet.get('description', '').split('\n')[0][:80]
        
        is_bad = False
        reasons = []
        
        # Check bad patterns
        for pat in BAD_PATTERNS:
            if re.search(pat, title, re.IGNORECASE):
                is_bad = True
                reasons.append(f'bad_pattern: {pat}')
                break
        
        # Check if draft/private (might be new upload)
        if privacy in ('private', 'unlisted'):
            is_bad = True
            reasons.append(f'status: {privacy}')
        
        # Check if title doesn't match proper format
        if not PROPER_PATTERN.match(title) and not is_bad:
            # Could be a known format we missed, check more
            if 'strike' in title.lower() or 'sls' in title.lower():
                is_bad = True
                reasons.append('contains_raw_marker')
        
        if is_bad:
            needs_fix.append({
                'videoId': vid_id,
                'title': title,
                'privacy': privacy,
                'category': category,
                'tags_count': len(tags),
                'desc_preview': desc_line1,
                'reasons': reasons,
                'studio_link': f'https://studio.youtube.com/video/{vid_id}/edit'
            })
    
    # Sort: drafts first, then by title
    needs_fix.sort(key=lambda x: (0 if x['privacy'] != 'public' else 1, x['title']))
    
    print(f"\n{'='*70}")
    print(f"  VIDEOS NEEDING ATTENTION: {len(needs_fix)}")
    print(f"{'='*70}\n")
    
    for i, v in enumerate(needs_fix, 1):
        privacy_tag = f"[{v['privacy'].upper()}]" if v['privacy'] != 'public' else '[PUBLIC]'
        print(f"  {i:3d}. {privacy_tag:10s} {v['videoId']} | {v['title'][:60]}")
        print(f"       Cat:{v['category']} Tags:{v['tags_count']} | {', '.join(v['reasons'])}")
        if v['desc_preview']:
            print(f"       Desc: {v['desc_preview']}")
        print()
    
    # Save full results
    out_path = 'config/live_scan_needs_fix_20260228.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'scan_date': '2026-02-28',
            'total_channel_videos': len(all_ids),
            'total_fetched': len(all_video_data),
            'needs_fix_count': len(needs_fix),
            'quota_reads': quota_reads,
            'videos': needs_fix
        }, f, indent=2, ensure_ascii=False)
    
    print(f"Saved: {out_path}")
    print(f"Quota used: ~{quota_reads} read units")

if __name__ == '__main__':
    main()
