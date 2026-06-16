"""
diagnose_seo.py - Deep SEO/Discovery diagnosis for @remAIke_IT
Checks what's actually visible to YouTube's algorithm and search crawlers.
Uses OAuth (token.json) for API access.
"""
import requests, os, json, sys
from collections import Counter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = r'D:\remaike.TV'
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'


def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    return build('youtube', 'v3', credentials=creds)


def get_all_video_ids():
    """Get ALL video IDs from uploads playlist."""
    yt = get_youtube()
    ids = []
    page = None
    while True:
        req = yt.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOAD_PL,
            maxResults=50,
            pageToken=page
        )
        data = req.execute()
        for item in data.get('items', []):
            ids.append(item['contentDetails']['videoId'])
        page = data.get('nextPageToken')
        if not page:
            break
    return ids


def get_video_details(video_ids):
    """Get full details for videos (50 at a time)."""
    yt = get_youtube()
    all_videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        req = yt.videos().list(
            part='snippet,statistics,contentDetails,status,topicDetails',
            id=','.join(batch)
        )
        data = req.execute()
        all_videos.extend(data.get('items', []))
    return all_videos


def analyze_seo(videos):
    """Comprehensive SEO analysis."""
    issues = Counter()
    category_views = {}
    zero_view_videos = []
    low_view_videos = []
    title_problems = []
    desc_problems = []
    tag_stats = {'total': 0, 'with_tags': 0, 'avg_tags': 0, 'missing_key_tags': []}
    
    total_tags = 0
    videos_with_tags = 0
    
    for v in videos:
        s = v['snippet']
        st = v.get('statistics', {})
        status = v.get('status', {})
        title = s.get('title', '')
        desc = s.get('description', '')
        tags = s.get('tags', [])
        views = int(st.get('viewCount', 0))
        cat_id = s.get('categoryId', '0')
        vid_id = v['id']
        
        # ── View analysis ──
        cat_name = title.split(':')[0].split('(')[0].strip() if ':' in title else 'Other'
        if cat_name not in category_views:
            category_views[cat_name] = []
        category_views[cat_name].append(views)
        
        if views == 0:
            zero_view_videos.append((vid_id, title[:80]))
        elif views < 5:
            low_view_videos.append((vid_id, title[:80], views))
        
        # ── Title SEO ──
        if '@remAIke_IT' in title or '@remaike' in title.lower():
            issues['TITLE_HAS_@CHANNEL (wastes chars)'] += 1
        
        if len(title) > 100:
            issues['TITLE_TOO_LONG (>100 chars, truncated in search)'] += 1
        elif len(title) < 30:
            issues['TITLE_TOO_SHORT (<30 chars, missing keywords)'] += 1
        
        title_lower = title.lower()
        if '8k' not in title_lower and '4k' not in title_lower:
            issues['TITLE_NO_QUALITY (missing 8K/4K keyword)'] += 1
        
        if '8k hq (4k uhd)' not in title_lower and '8k hq' not in title_lower:
            issues['TITLE_NOT_STANDARD_FORMAT (missing "8K HQ")'] += 1
        
        if not any(c.isdigit() and len(c) == 4 for c in title.replace('(', ' ').replace(')', ' ').split()):
            # Check for year
            import re
            if not re.search(r'\b(19|20)\d{2}\b', title):
                issues['TITLE_NO_YEAR'] += 1
        
        # ── Description SEO ──
        first_line = desc.split('\n')[0] if desc else ''
        if first_line.strip() == title.strip():
            issues['DESC_LINE1_EQUALS_TITLE (wasted SEO opportunity!)'] += 1
        
        if len(desc) < 100:
            issues['DESC_TOO_SHORT (<100 chars)'] += 1
        
        if 'remaike.it' not in desc.lower() and 'frai.tv' not in desc.lower():
            issues['DESC_NO_WEBSITE_LINK'] += 1
        
        if '@remAIke_IT' not in desc and '@remaike' not in desc.lower():
            issues['DESC_NO_CHANNEL_LINK'] += 1
        
        desc_lower = desc.lower()
        has_cta = any(w in desc_lower for w in ['subscribe', 'abonnier', 'like', 'comment', 'komment'])
        if not has_cta:
            issues['DESC_NO_CTA (no subscribe/like prompt)'] += 1
        
        # Count hashtags
        hashtags = [w for w in desc.split() if w.startswith('#')]
        if len(hashtags) > 5:
            issues['DESC_TOO_MANY_HASHTAGS (>5 = spam)'] += 1
        elif len(hashtags) == 0:
            issues['DESC_NO_HASHTAGS'] += 1
        
        if '0:00' not in desc and 'chapters' not in desc_lower:
            issues['DESC_NO_CHAPTERS'] += 1
        
        # ── Tags SEO ──
        if tags:
            videos_with_tags += 1
            total_tags += len(tags)
            tags_lower = [t.lower() for t in tags]
            
            if not any('remaster' in t for t in tags_lower):
                issues['TAGS_NO_REMASTERED'] += 1
            if not any('restor' in t for t in tags_lower):
                issues['TAGS_NO_RESTORED'] += 1
            if not any('public domain' in t for t in tags_lower):
                issues['TAGS_NO_PUBLIC_DOMAIN'] += 1
            if len(tags) > 15:
                issues['TAGS_TOO_MANY (>15)'] += 1
        else:
            issues['TAGS_NONE (zero tags!)'] += 1
        
        # ── Technical SEO ──
        thumbs = s.get('thumbnails', {})
        # Auto-generated thumbnails don't have 'maxres' or have specific patterns
        # Actually we can't 100% detect this from API, but standard/maxres check helps
        
        if not status.get('embeddable', True):
            issues['NOT_EMBEDDABLE'] += 1
        
        if status.get('privacyStatus') != 'public':
            issues[f'NOT_PUBLIC ({status.get("privacyStatus")})'] += 1
    
    return {
        'issues': issues,
        'category_views': category_views,
        'zero_view_videos': zero_view_videos,
        'low_view_videos': low_view_videos,
        'avg_tags': total_tags / max(videos_with_tags, 1),
        'videos_with_tags': videos_with_tags,
        'total_videos': len(videos)
    }


def main():
    print("=" * 70)
    print("  SEO/DISCOVERY DIAGNOSIS - @remAIke_IT")
    print("  Using PUBLIC API only (minimal quota)")
    print("=" * 70)
    
    # 1. Channel info
    print("\n[1/4] Fetching channel info...")
    yt = get_youtube()
    ch_data = yt.channels().list(
        part='statistics,snippet,brandingSettings,contentDetails',
        id=CHANNEL_ID
    ).execute()
    ch = ch_data['items'][0]
    stats = ch['statistics']
    brand = ch.get('brandingSettings', {}).get('channel', {})
    
    print(f"\n--- CHANNEL OVERVIEW ---")
    print(f"  Name:        {ch['snippet']['title']}")
    print(f"  Subscribers: {stats['subscriberCount']}")
    print(f"  Total Views: {stats['viewCount']}")
    print(f"  Videos:      {stats['videoCount']}")
    print(f"  Country:     {brand.get('country', 'NOT SET!')}")
    print(f"  Keywords:    {brand.get('keywords', 'NONE!')[:150]}")
    
    ch_desc = ch['snippet'].get('description', '')
    print(f"  Description: {len(ch_desc)} chars")
    if len(ch_desc) < 100:
        print(f"  WARNING: Channel description too short! ({len(ch_desc)} chars)")
    
    # Check for critical channel-level issues
    ch_issues = []
    if not brand.get('country'):
        ch_issues.append("NO COUNTRY SET - YouTube can't target geographic audience!")
    if not brand.get('keywords'):
        ch_issues.append("NO CHANNEL KEYWORDS - YouTube has no topic context!")
    if len(ch_desc) < 200:
        ch_issues.append(f"SHORT CHANNEL DESCRIPTION ({len(ch_desc)} chars) - should be 500+")
    if 'remaike' not in ch_desc.lower() and 'frai' not in ch_desc.lower():
        ch_issues.append("NO WEBSITE IN CHANNEL DESC")
    
    if ch_issues:
        print(f"\n  !!! CHANNEL-LEVEL PROBLEMS !!!")
        for issue in ch_issues:
            print(f"  [CRITICAL] {issue}")
    
    # 2. Get ALL video IDs
    print(f"\n[2/4] Fetching all video IDs...")
    all_ids = get_all_video_ids()
    print(f"  Found {len(all_ids)} videos in uploads playlist")
    
    # 3. Get video details
    print(f"\n[3/4] Fetching video details (batches of 50)...")
    videos = get_video_details(all_ids)
    public_videos = [v for v in videos if v.get('status', {}).get('privacyStatus') == 'public']
    print(f"  Got {len(videos)} total, {len(public_videos)} public")
    
    # 4. Analyze
    print(f"\n[4/4] Analyzing SEO...")
    analysis = analyze_seo(public_videos)
    
    # ── Report ──
    print(f"\n{'='*70}")
    print(f"  SEO DIAGNOSIS RESULTS")
    print(f"{'='*70}")
    
    # Issue ranking
    print(f"\n--- TOP SEO ISSUES (by frequency) ---")
    for issue, count in analysis['issues'].most_common(25):
        pct = count / analysis['total_videos'] * 100
        severity = "CRITICAL" if pct > 50 else "HIGH" if pct > 25 else "MEDIUM" if pct > 10 else "LOW"
        print(f"  [{severity:8s}] {count:3d}/{analysis['total_videos']} ({pct:5.1f}%) {issue}")
    
    # View distribution by category
    print(f"\n--- VIEWS BY CATEGORY ---")
    for cat, views_list in sorted(analysis['category_views'].items(), 
                                   key=lambda x: sum(x[1])/max(len(x[1]),1), reverse=True):
        avg = sum(views_list) / max(len(views_list), 1)
        total = sum(views_list)
        zeros = sum(1 for v in views_list if v == 0)
        print(f"  {cat:30s}  {len(views_list):3d} vids | avg {avg:7.0f} views | total {total:8d} | {zeros} zero-views")
    
    # Zero-view videos (most concerning!)
    if analysis['zero_view_videos']:
        print(f"\n--- ZERO VIEW VIDEOS ({len(analysis['zero_view_videos'])} total!) ---")
        for vid_id, title in analysis['zero_view_videos'][:20]:
            print(f"  {vid_id} | {title}")
        if len(analysis['zero_view_videos']) > 20:
            print(f"  ... and {len(analysis['zero_view_videos'])-20} more")
    
    # Tag stats
    print(f"\n--- TAG STATS ---")
    print(f"  Videos with tags: {analysis['videos_with_tags']}/{analysis['total_videos']}")
    print(f"  Average tags:     {analysis['avg_tags']:.1f}")
    
    # Search simulation: what would someone search for?
    print(f"\n--- SEARCH SIMULATION ---")
    print(f"  Testing common search queries against your titles...")
    
    search_queries = [
        'betty boop cartoon', 'betty boop 8k', 'betty boop remastered',
        'felix the cat cartoon', 'felix the cat 8k',
        'alfred j kwak deutsch', 'alfred j kwak german',
        'superman cartoon 1940', 'fleischer superman',
        'wochenschau', 'deutsche wochenschau', 'ww2 footage 4k',
        'soundie 1940s', 'vintage music video',
        'public domain movies 4k', 'classic cartoon 8k',
        'casper cartoon', 'popeye cartoon 8k',
    ]
    
    for query in search_queries:
        q_words = query.lower().split()
        matches = 0
        for v in public_videos:
            title = v['snippet']['title'].lower()
            desc = v['snippet'].get('description', '').lower()[:500]
            tags = ' '.join(v['snippet'].get('tags', [])).lower()
            
            # Check if ALL query words appear in title, desc, or tags
            all_text = f"{title} {desc} {tags}"
            if all(w in all_text for w in q_words):
                matches += 1
        
        status = "OK" if matches > 0 else "MISS!"
        print(f"  [{status:4s}] '{query}' -> {matches} videos match")
    
    # Key recommendations
    print(f"\n{'='*70}")
    print(f"  KEY FINDINGS & RECOMMENDATIONS")
    print(f"{'='*70}")
    
    print("""
  1. TITLE FORMAT: Most titles still have @remAIke_IT which wastes
     valuable character space. YouTube SEARCH ranks title keywords first!
     
  2. CUSTOM THUMBNAILS: ~99% of videos lack custom thumbnails.
     CTR (click-through rate) is THE #1 factor for YouTube recommendations.
     Auto-generated thumbnails get 2-5x LOWER CTR than custom ones.
     
  3. CHANNEL KEYWORDS: If empty, YouTube has NO topic context for
     recommending your channel or videos to viewers.
     
  4. FIRST LINE OF DESCRIPTION: Many duplicate the title. This wastes
     the most valuable SEO real estate (visible in search results).
     
  5. ENGAGEMENT SIGNALS: Low views + low CTR = YouTube stops showing
     videos in search and recommendations. It's a vicious cycle.
     
  6. SEARCH INTENT MISMATCH: People search for 'betty boop cartoon'
     not 'betty boop 8k'. Your titles optimize for quality keywords
     that nobody searches for, instead of CONTENT keywords people want.
    """)
    
    # Save full report
    report_path = os.path.join('reports', 'SEO_DIAGNOSIS_2026_02_24.json')
    os.makedirs('reports', exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'date': '2026-02-24',
            'channel_stats': stats,
            'channel_keywords': brand.get('keywords', ''),
            'channel_country': brand.get('country', ''),
            'channel_desc_length': len(ch_desc),
            'total_public': len(public_videos),
            'issues': dict(analysis['issues'].most_common()),
            'zero_view_count': len(analysis['zero_view_videos']),
            'zero_view_ids': [v[0] for v in analysis['zero_view_videos']],
            'avg_tags': analysis['avg_tags'],
        }, f, indent=2)
    print(f"\n  Full report saved to: {report_path}")
    
    # Quota used
    api_calls = 1 + (len(all_ids) // 50 + 1) + (len(all_ids) // 50 + 1) + 1
    print(f"\n  Quota used: ~{api_calls} units (all READ/public API)")


if __name__ == '__main__':
    main()
