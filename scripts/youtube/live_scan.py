"""
Live Channel Scanner - Uses OAuth token to scan ALL videos
and identify SEO issues based on copilot-instructions.md rules.

Quota cost: ~8 units (1 per page of 50 videos = ~8 pages for 390 videos)
Uses playlistItems.list (1 unit per call) + videos.list (1 unit per call)
"""
import json
import os
import sys
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

def get_youtube_service():
    """Build YouTube service from token.json"""
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
    token_path = os.path.abspath(token_path)
    
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    )
    
    if creds.expired or not creds.valid:
        print("Refreshing OAuth token...")
        creds.refresh(Request())
        # Save refreshed token
        token_data['token'] = creds.token
        token_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("Token refreshed and saved.")
    
    return build('youtube', 'v3', credentials=creds)

def get_all_video_ids(youtube):
    """Get all video IDs from upload playlist. Cost: 1 unit per page."""
    video_ids = []
    next_page = None
    
    while True:
        req = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOAD_PLAYLIST,
            maxResults=50,
            pageToken=next_page
        )
        resp = req.execute()
        
        for item in resp.get('items', []):
            vid = item['contentDetails']['videoId']
            video_ids.append(vid)
        
        next_page = resp.get('nextPageToken')
        if not next_page:
            break
        print(f"  Got {len(video_ids)} video IDs...")
    
    print(f"Total video IDs: {len(video_ids)}")
    return video_ids

def get_video_details(youtube, video_ids):
    """Get full details for videos. Cost: 1 unit per batch of 50."""
    videos = []
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        req = youtube.videos().list(
            part='snippet,status,contentDetails,localizations',
            id=','.join(batch)
        )
        resp = req.execute()
        
        for item in resp.get('items', []):
            vid = {
                'id': item['id'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'tags': item['snippet'].get('tags', []),
                'categoryId': item['snippet']['categoryId'],
                'publishedAt': item['snippet']['publishedAt'],
                'privacy': item['status']['privacyStatus'],
                'duration': item['contentDetails']['duration'],
                'localizations': list(item.get('localizations', {}).keys()),
                'channelTitle': item['snippet'].get('channelTitle', ''),
            }
            videos.append(vid)
        
        print(f"  Got details for {len(videos)} videos...")
    
    return videos

def audit_video(video):
    """Check a video against SEO rules. Returns list of issues."""
    issues = []
    title = video['title']
    desc = video['description']
    tags = video['tags']
    cat = video['categoryId']
    privacy = video['privacy']
    locs = video['localizations']
    
    # R1: Must have 8K or 4K in title
    if '8K' not in title and '4K' not in title:
        issues.append('R1: No 8K/4K in title')
    
    # R1b: Should have both "8K HQ" and "(4K UHD)"
    if '8K HQ' in title and '(4K UHD)' not in title:
        issues.append('R1b: Missing (4K UHD) after 8K HQ')
    
    # R2: No @remAIke_IT in title
    if '@remAIke_IT' in title or '@remAIke' in title:
        issues.append('R2: @remAIke_IT in title')
    
    # R3: Title too long (max 70 chars, soft limit 80)
    if len(title) > 80:
        issues.append(f'R3: Title too long ({len(title)} chars)')
    
    # R4: CTA in description
    cta_words = ['LIKE', 'SUBSCRIBE', 'COMMENT']
    has_cta = any(w in desc.upper() for w in cta_words)
    if not has_cta and privacy == 'public':
        issues.append('R4: No CTA in description')
    
    # R5: www.remaike.IT in description
    if 'www.remaike.it' not in desc.lower() and 'remaike.it' not in desc.lower():
        if privacy == 'public':
            issues.append('R5: Missing www.remaike.IT')
    
    # R6: YouTube channel link
    if 'youtube.com/@remAIke_IT' not in desc and '@remAIke_IT' not in desc:
        if privacy == 'public':
            issues.append('R6: Missing YouTube channel link')
    
    # R7: Too many hashtags in description
    hashtag_count = desc.count('#')
    if hashtag_count > 5:
        issues.append(f'R7: Too many hashtags ({hashtag_count})')
    
    # R8: Too many tags
    if len(tags) > 15:
        issues.append(f'R8: Too many tags ({len(tags)})')
    
    # R9: Category check
    is_wochenschau = 'wochenschau' in title.lower() or 'newsreel' in title.lower()
    is_soundie = 'soundie' in title.lower()
    if is_wochenschau and cat != '27':
        issues.append(f'R9: Wochenschau should be Education(27), is {cat}')
    if is_soundie and cat != '10':
        issues.append(f'R9: Soundie should be Music(10), is {cat}')
    
    # R10: Raw filename artifacts
    raw_indicators = ['sls', 'ARCHIVE PROTECTED', 'aac sls', 'CINEMA', 'xvid']
    for ind in raw_indicators:
        if ind.lower() in title.lower():
            issues.append(f'R10: Raw artifact "{ind}" in title')
            break
    
    # R11: Description too short
    if len(desc) < 50 and privacy == 'public':
        issues.append(f'R11: Description too short ({len(desc)} chars)')
    
    # R12: Localizations
    if len(locs) < 2:
        issues.append(f'R12: Too few localizations ({len(locs)})')
    
    return issues

def main():
    print(f"=== Live Channel Scanner ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ===\n")
    
    youtube = get_youtube_service()
    
    # Step 1: Get all video IDs
    print("Step 1: Getting video IDs...")
    video_ids = get_all_video_ids(youtube)
    
    # Step 2: Get full details
    print("\nStep 2: Getting video details...")
    videos = get_video_details(youtube, video_ids)
    
    # Step 3: Audit each video
    print("\nStep 3: Auditing videos...")
    results = {
        'scan_date': datetime.now().isoformat(),
        'total': len(videos),
        'public': 0,
        'private': 0,
        'unlisted': 0,
        'issues_found': 0,
        'critical_issues': [],  # Need title fix
        'minor_issues': [],     # Need desc/tag/loc fix
        'compliant': [],        # All good
        'all_videos': []
    }
    
    critical_rules = {'R1', 'R2', 'R3', 'R9', 'R10'}
    
    for v in videos:
        if v['privacy'] == 'public':
            results['public'] += 1
        elif v['privacy'] == 'private':
            results['private'] += 1
        else:
            results['unlisted'] += 1
        
        issues = audit_video(v)
        v['issues'] = issues
        results['all_videos'].append(v)
        
        if issues:
            results['issues_found'] += 1
            has_critical = any(any(i.startswith(r) for r in critical_rules) for i in issues)
            if has_critical:
                results['critical_issues'].append({
                    'id': v['id'],
                    'title': v['title'],
                    'privacy': v['privacy'],
                    'issues': issues
                })
            else:
                results['minor_issues'].append({
                    'id': v['id'],
                    'title': v['title'],
                    'privacy': v['privacy'],
                    'issues': issues
                })
        else:
            results['compliant'].append(v['id'])
    
    # Save full results
    output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 
                               f'live_scan_{datetime.now().strftime("%Y_%m_%d")}.json')
    output_path = os.path.abspath(output_path)
    
    # Save without all_videos for summary
    summary = {k: v for k, v in results.items() if k != 'all_videos'}
    summary['compliant_count'] = len(results['compliant'])
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"SCAN RESULTS")
    print(f"{'='*60}")
    print(f"Total Videos:    {results['total']}")
    print(f"  Public:        {results['public']}")
    print(f"  Private:       {results['private']}")
    print(f"  Unlisted:      {results['unlisted']}")
    print(f"")
    print(f"Compliant:       {len(results['compliant'])}")
    print(f"Issues Found:    {results['issues_found']}")
    print(f"  CRITICAL:      {len(results['critical_issues'])}")
    print(f"  Minor:         {len(results['minor_issues'])}")
    
    if results['critical_issues']:
        print(f"\n{'='*60}")
        print("CRITICAL ISSUES (need title/category fix):")
        print(f"{'='*60}")
        for v in results['critical_issues']:
            print(f"\n  [{v['privacy']}] {v['id']}: {v['title'][:70]}")
            for i in v['issues']:
                print(f"    - {i}")
    
    if results['minor_issues'][:20]:  # Show first 20
        print(f"\n{'='*60}")
        print(f"MINOR ISSUES (first 20 of {len(results['minor_issues'])}):")
        print(f"{'='*60}")
        for v in results['minor_issues'][:20]:
            print(f"\n  [{v['privacy']}] {v['id']}: {v['title'][:70]}")
            for i in v['issues']:
                print(f"    - {i}")
    
    print(f"\nSaved to: {output_path}")
    print(f"Estimated quota used: ~{len(video_ids)//50 + 1 + len(video_ids)//50 + 1} units")

if __name__ == '__main__':
    main()
