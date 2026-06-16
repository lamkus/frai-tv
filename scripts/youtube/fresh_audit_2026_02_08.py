"""
Fresh Channel Audit - 2026-02-08
Scans ALL videos live, finds unoptimized ones, checks 2026 algo compliance.
"""
import json, os, sys, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def get_all_upload_ids(youtube):
    """Get all video IDs from uploads playlist (1 unit per page)"""
    UPLOADS_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
    ids = []
    next_page = None
    while True:
        res = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOADS_PL,
            maxResults=50,
            pageToken=next_page
        ).execute()
        for item in res['items']:
            ids.append(item['contentDetails']['videoId'])
        next_page = res.get('nextPageToken')
        if not next_page:
            break
    return ids

def get_video_details(youtube, video_ids):
    """Batch get video details (50 per call, 1 unit each)"""
    all_details = []
    for i in range(0, len(video_ids), 50):
        batch = ','.join(video_ids[i:i+50])
        res = youtube.videos().list(
            part='snippet,status,contentDetails,statistics',
            id=batch
        ).execute()
        all_details.extend(res.get('items', []))
    return all_details

def audit_video(video):
    """Full 2026 Algorithm Compliance Check"""
    snippet = video['snippet']
    status = video['status']
    stats = video.get('statistics', {})
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    cat = snippet.get('categoryId', '0')
    
    issues = []
    warnings = []
    score = 100
    
    # === TITLE CHECKS (40 points) ===
    # T1: 8K in title
    if '8K' not in title:
        issues.append('T1-CRITICAL: Missing 8K in title')
        score -= 15
    
    # T2: Full format 8K HQ (4K UHD)
    if '8K HQ (4K UHD)' not in title and '8K' in title:
        if '4K' not in title:
            warnings.append('T2: Missing (4K UHD) - old format')
            score -= 5
    
    # T3: Title length
    if len(title) > 70:
        warnings.append(f'T3: Title too long ({len(title)} chars, max 70)')
        score -= 3
    if len(title) < 20:
        warnings.append(f'T3: Title too short ({len(title)} chars)')
        score -= 5
    
    # T4: @remAIke_IT in title (waste!)
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues.append('T4: @remAIke_IT in title wastes chars!')
        score -= 5
    
    # T5: Keyword at start
    # (Can't easily check, skip)
    
    # === DESCRIPTION CHECKS (30 points) ===
    # D1: CTA present
    has_cta = any(w in desc.upper() for w in ['SUBSCRIBE', 'LIKE', 'COMMENT', 'ABONNIEREN'])
    if not has_cta:
        issues.append('D1: Missing CTA (LIKE/SUBSCRIBE)')
        score -= 8
    
    # D2: Website link
    if 'remaike.it' not in desc.lower() and 'remaike.tv' not in desc.lower():
        warnings.append('D2: Missing www.remaike.IT link')
        score -= 3
    
    # D3: YouTube channel link
    if '@remAIke_IT' not in desc and 'youtube.com/@remAIke' not in desc:
        warnings.append('D3: Missing YouTube channel link in desc')
        score -= 2
    
    # D4: Hashtags (2-5 optimal, >5 = spam)
    hashtags = [w for w in desc.split() if w.startswith('#') and len(w) > 1]
    if len(hashtags) == 0:
        warnings.append('D4: No hashtags in description')
        score -= 3
    elif len(hashtags) > 5:
        warnings.append(f'D4: Too many hashtags ({len(hashtags)}, max 5)')
        score -= 2
    
    # D5: Description too short
    if len(desc) < 100:
        issues.append(f'D5: Description too short ({len(desc)} chars)')
        score -= 5
    
    # === TAGS CHECKS (10 points) ===
    if len(tags) == 0:
        warnings.append('TG1: No tags')
        score -= 3
    elif len(tags) > 15:
        warnings.append(f'TG1: Too many tags ({len(tags)}, max 15)')
        score -= 2
    
    # === CATEGORY CHECK ===
    # Soundies should be Music (10)
    is_soundie = 'soundie' in title.lower() or 'soundie' in desc.lower()
    if is_soundie and cat != '10':
        issues.append(f'CAT: Soundie should be Music (10), is {cat}')
        score -= 5
    
    # Wochenschau should be Education (27)
    is_wochenschau = 'wochenschau' in title.lower()
    if is_wochenschau and cat != '27':
        issues.append(f'CAT: Wochenschau should be Education (27), is {cat}')
        score -= 5
    
    # === STATUS ===
    privacy = status.get('privacyStatus', 'unknown')
    
    return {
        'id': video['id'],
        'title': title,
        'privacy': privacy,
        'category': cat,
        'tags_count': len(tags),
        'desc_length': len(desc),
        'views': int(stats.get('viewCount', 0)),
        'likes': int(stats.get('likeCount', 0)),
        'score': max(0, score),
        'issues': issues,
        'warnings': warnings,
        'has_8k': '8K' in title,
        'has_4k_uhd': '4K UHD' in title or '4K' in title,
        'has_full_format': '8K HQ (4K UHD)' in title,
        'has_cta': has_cta,
        'has_website': 'remaike.it' in desc.lower() or 'remaike.tv' in desc.lower(),
        'has_channel_link': '@remAIke_IT' in desc or 'youtube.com/@remAIke' in desc,
        'hashtag_count': len([w for w in desc.split() if w.startswith('#')]),
        'published': snippet.get('publishedAt', '')[:10],
    }

def main():
    print("🔍 Fresh Channel Audit - 2026-02-08")
    print("=" * 60)
    
    youtube = get_youtube()
    
    # Step 1: Get all video IDs
    print("📋 Fetching all video IDs from uploads playlist...")
    video_ids = get_all_upload_ids(youtube)
    print(f"   Found {len(video_ids)} videos")
    
    # Step 2: Get full details
    print("📊 Fetching full video details...")
    videos = get_video_details(youtube, video_ids)
    print(f"   Got details for {len(videos)} videos")
    
    # Step 3: Audit each video
    print("🔎 Auditing each video...")
    results = []
    for v in videos:
        r = audit_video(v)
        results.append(r)
    
    # Step 4: Load fix plan to find NEW uploads
    fix_ids = set()
    if os.path.exists('config/channel_master_fix_prioritized.json'):
        with open('config/channel_master_fix_prioritized.json', 'r', encoding='utf-8') as f:
            fixes = json.load(f)
        fix_ids = set(x['id'] for x in fixes)
    
    new_uploads = [r for r in results if r['id'] not in fix_ids]
    
    # === REPORT ===
    public = [r for r in results if r['privacy'] == 'public']
    private = [r for r in results if r['privacy'] == 'private']
    
    print(f"\n{'='*60}")
    print(f"📊 CHANNEL OVERVIEW")
    print(f"{'='*60}")
    print(f"  Total videos:    {len(results)}")
    print(f"  Public:          {len(public)}")
    print(f"  Private:         {len(private)}")
    print(f"  Avg SEO Score:   {sum(r['score'] for r in public)/max(1,len(public)):.1f}/100")
    
    print(f"\n{'='*60}")
    print(f"📈 TITLE FORMAT COMPLIANCE")
    print(f"{'='*60}")
    print(f"  Has '8K':              {sum(1 for r in public if r['has_8k'])}/{len(public)}")
    print(f"  Has '4K':              {sum(1 for r in public if r['has_4k_uhd'])}/{len(public)}")
    print(f"  Full '8K HQ (4K UHD)': {sum(1 for r in public if r['has_full_format'])}/{len(public)}")
    print(f"  Has @channel in title: {sum(1 for r in public if '@remAIke' in r['title'].lower())}/{len(public)}")
    
    print(f"\n{'='*60}")
    print(f"📝 DESCRIPTION COMPLIANCE")
    print(f"{'='*60}")
    print(f"  Has CTA:          {sum(1 for r in public if r['has_cta'])}/{len(public)}")
    print(f"  Has website link:  {sum(1 for r in public if r['has_website'])}/{len(public)}")
    print(f"  Has channel link:  {sum(1 for r in public if r['has_channel_link'])}/{len(public)}")
    print(f"  Has hashtags:      {sum(1 for r in public if r['hashtag_count'] > 0)}/{len(public)}")
    print(f"  Too many hashtags: {sum(1 for r in public if r['hashtag_count'] > 5)}/{len(public)}")
    
    print(f"\n{'='*60}")
    print(f"🆕 NEW UPLOADS (not in fix plan): {len(new_uploads)}")
    print(f"{'='*60}")
    for v in new_uploads:
        flag = '✅' if v['score'] >= 90 else '⚠️' if v['score'] >= 70 else '❌'
        print(f"  {flag} [{v['score']:3d}] {v['title'][:65]}")
        for iss in v['issues']:
            print(f"        ❌ {iss}")
        for warn in v['warnings']:
            print(f"        ⚠️ {warn}")
    
    # Videos with ISSUES (score < 90)
    problem_videos = [r for r in public if r['score'] < 90]
    problem_videos.sort(key=lambda x: x['score'])
    
    print(f"\n{'='*60}")
    print(f"🔴 PROBLEM VIDEOS (score < 90): {len(problem_videos)}")
    print(f"{'='*60}")
    for v in problem_videos[:30]:
        print(f"  [{v['score']:3d}] {v['id']} | {v['title'][:55]}")
        for iss in v['issues']:
            print(f"        ❌ {iss}")
        for warn in v['warnings'][:2]:
            print(f"        ⚠️ {warn}")
    
    # Save full results
    output = {
        'scan_date': '2026-02-08',
        'total': len(results),
        'public': len(public),
        'private': len(private),
        'avg_score': round(sum(r['score'] for r in public)/max(1,len(public)), 1),
        'new_uploads': new_uploads,
        'problem_videos': problem_videos,
        'all_videos': results
    }
    
    with open('config/fresh_audit_2026_02_08.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to config/fresh_audit_2026_02_08.json")
    
    return output

if __name__ == '__main__':
    main()
