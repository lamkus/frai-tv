#!/usr/bin/env python3
"""
Full Channel Audit via PUBLIC API (No OAuth Quota!)
Checks every video against 2026 SEO rules from copilot-instructions.md:
  1. Title <=70 chars
  2. NO @remAIke_IT in title
  3. Has "8K" in title
  4. Max 15 tags
  5. Description has CTA (LIKE/SUBSCRIBE)
  6. Description has www.remaike.IT
  7. Description has YouTube channel link
  8. Max 5 hashtags in description
  9. Soundies: Category = Music (10)
 10. Wochenschau: Category = Education (27) or News (25)
"""
import json
import os
import sys
import requests
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load OAuth credentials (used for READ only - 1 unit per batch)
oauth_path = Path('config/youtube_oauth.json')
if not oauth_path.exists():
    print("❌ OAuth config not found!")
    sys.exit(1)

oauth = json.loads(oauth_path.read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth.get('access_token') or oauth.get('token'),
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOADS_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

BASE_URL = 'https://youtube.googleapis.com/youtube/v3'

def fetch_all_video_ids():
    """Fetch all video IDs from uploads playlist (1 unit per page)"""
    print("📡 Fetching video IDs...")
    video_ids = []
    next_page = None
    
    while True:
        resp = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOADS_PLAYLIST,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in resp.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page = resp.get('nextPageToken')
        print(f"   {len(video_ids)} IDs...", end='\r')
        if not next_page:
            break
    
    print(f"\n✅ Found {len(video_ids)} videos")
    return video_ids

def fetch_video_details(video_ids):
    """Fetch full details in batches of 50 (1 unit per batch)"""
    print("📡 Fetching video details...")
    all_videos = []
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part='snippet,contentDetails,status',
            id=','.join(batch)
        ).execute()
        
        all_videos.extend(resp.get('items', []))
        print(f"   {len(all_videos)} details...", end='\r')
    
    print(f"\n✅ Got details for {len(all_videos)} videos")
    return all_videos

def audit_video(video):
    """Audit a single video against all 2026 rules"""
    snippet = video['snippet']
    vid_id = video['id']
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    category = snippet.get('categoryId', '0')
    
    issues = []
    
    # 1. Title length
    if len(title) > 70:
        issues.append(f"TITLE_TOO_LONG ({len(title)} chars)")
    
    # 2. No @remAIke_IT in title (2026 rule: wastes chars, no benefit)
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues.append("TITLE_HAS_@CHANNEL (wastes chars)")
    
    # 3. Has 8K in title
    if '8K' not in title and '4K' not in title:
        issues.append("TITLE_MISSING_QUALITY (no 8K/4K)")
    
    # 4. Max 15 tags
    if len(tags) > 15:
        issues.append(f"TOO_MANY_TAGS ({len(tags)}, max 15)")
    
    # 5. CTA in description
    has_cta = any(word in desc.upper() for word in ['LIKE', 'SUBSCRIBE', 'COMMENT'])
    if not has_cta:
        issues.append("DESC_MISSING_CTA")
    
    # 6. www.remaike.IT in description
    if 'remaike.it' not in desc.lower() and 'remaike.tv' not in desc.lower():
        issues.append("DESC_MISSING_WEBSITE_LINK")
    
    # 7. YouTube channel link in description
    if '@remAIke_IT' not in desc and 'youtube.com/@remAIke' not in desc:
        issues.append("DESC_MISSING_CHANNEL_LINK")
    
    # 8. Max 5 hashtags
    hashtags = [w for w in desc.split() if w.startswith('#') and len(w) > 1]
    if len(hashtags) > 5:
        issues.append(f"TOO_MANY_HASHTAGS ({len(hashtags)}, max 5)")
    
    # 9. Soundies should be Music (10)
    title_lower = title.lower()
    if 'soundie' in title_lower and category != '10':
        issues.append(f"SOUNDIE_WRONG_CATEGORY (is {category}, should be 10)")
    
    # 10. Wochenschau should be Education (27) or News (25)
    if 'wochenschau' in title_lower and category not in ('25', '27'):
        issues.append(f"WOCHENSCHAU_WRONG_CATEGORY (is {category}, should be 25 or 27)")
    
    # 11. Has "8K HQ (4K UHD)" - our new standard
    has_new_format = '8K HQ (4K UHD)' in title or '8K HQ' in title
    if not has_new_format and '8K' in title:
        issues.append("TITLE_OLD_8K_FORMAT (missing 'HQ')")
    
    return {
        'id': vid_id,
        'title': title,
        'title_len': len(title),
        'tags_count': len(tags),
        'category': category,
        'issues': issues,
        'status': snippet.get('liveBroadcastContent', 'none'),
        'published': snippet.get('publishedAt', '')
    }

def main():
    print("=" * 70)
    print("  REMAIKE.TV - FULL CHANNEL AUDIT (PUBLIC API)")
    print("  Rules: copilot-instructions.md + YOUTUBE_ALGORITHM_2026.md")
    print("=" * 70)
    
    # 1. Get all video IDs
    video_ids = fetch_all_video_ids()
    if not video_ids:
        print("No videos found!")
        return
    
    # 2. Get details
    videos = fetch_video_details(video_ids)
    
    # 3. Check for NEW uploads (not in our last scan)
    try:
        with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
            old_scan = json.load(f)
        old_ids = set()
        for v in old_scan.get('videos', old_scan if isinstance(old_scan, list) else []):
            if isinstance(v, dict):
                vid = v.get('id') or v.get('video_id') or v.get('snippet', {}).get('resourceId', {}).get('videoId', '')
                if vid:
                    old_ids.add(vid)
    except:
        old_ids = set()
    
    current_ids = set(v['id'] for v in videos)
    new_ids = current_ids - old_ids if old_ids else set()
    
    if new_ids:
        print(f"\n🆕 NEW UPLOADS DETECTED: {len(new_ids)}")
        for vid in videos:
            if vid['id'] in new_ids:
                print(f"   🆕 {vid['snippet']['title']}")
                print(f"      ID: {vid['id']}")
                print(f"      Published: {vid['snippet'].get('publishedAt', 'N/A')}")
    else:
        print(f"\n✅ No new uploads since last scan.")
    
    # 4. Audit every video
    print(f"\n🔍 AUDITING {len(videos)} VIDEOS...")
    print("-" * 70)
    
    results = []
    perfect = 0
    with_issues = 0
    
    for video in videos:
        result = audit_video(video)
        results.append(result)
        
        if result['issues']:
            with_issues += 1
        else:
            perfect += 1
    
    # 5. Report
    print(f"\n{'=' * 70}")
    print(f"  AUDIT RESULTS")
    print(f"{'=' * 70}")
    print(f"  Total Videos:     {len(results)}")
    print(f"  ✅ Perfect:       {perfect}")
    print(f"  ⚠️  With Issues:  {with_issues}")
    print()
    
    # Group issues by type
    issue_counts = {}
    for r in results:
        for issue in r['issues']:
            issue_type = issue.split('(')[0].strip()
            if issue_type not in issue_counts:
                issue_counts[issue_type] = []
            issue_counts[issue_type].append(r)
    
    print("📊 ISSUE BREAKDOWN:")
    print("-" * 50)
    for issue_type, vids in sorted(issue_counts.items(), key=lambda x: -len(x[1])):
        print(f"  {issue_type}: {len(vids)} videos")
    
    # Show each issue type with affected videos
    print(f"\n{'=' * 70}")
    print("📋 DETAILED ISSUES (Video-by-Video):")
    print(f"{'=' * 70}")
    
    for r in results:
        if r['issues']:
            print(f"\n  🔴 {r['title'][:65]}")
            print(f"     ID: {r['id']} | Len: {r['title_len']} | Tags: {r['tags_count']} | Cat: {r['category']}")
            for issue in r['issues']:
                print(f"     ❌ {issue}")
    
    # Save results
    output = {
        'audit_date': '2026-02-06',
        'total_videos': len(results),
        'perfect': perfect,
        'with_issues': with_issues,
        'new_uploads': list(new_ids),
        'issue_summary': {k: len(v) for k, v in issue_counts.items()},
        'videos': results
    }
    
    with open('config/full_audit_2026_02_06.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full audit saved to config/full_audit_2026_02_06.json")
    
    # Quota usage estimate
    pages = (len(video_ids) + 49) // 50
    detail_batches = (len(video_ids) + 49) // 50
    total_quota = pages + detail_batches
    print(f"\n📊 Quota used: ~{total_quota} units (READ only, minimal!)")

if __name__ == "__main__":
    main()
