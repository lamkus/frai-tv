#!/usr/bin/env python3
"""
comprehensive_seo_geo_audit_2026.py — Full SEO + GEO Audit for @remAIke_IT
==========================================================================

Performs a 2-phase audit:
  Phase 1: Fresh channel scan via Public API (API_KEY, ~8 quota units)
  Phase 2: Deep per-video SEO/GEO scoring against 2026 rules

Scoring: 100 points per video across 6 categories:
  - Title (35 pts)
  - Description (25 pts)
  - Tags (10 pts)
  - Technical (15 pts)
  - GEO/Schema (10 pts)
  - Engagement (5 pts)

Usage:
  python scripts/youtube/comprehensive_seo_geo_audit_2026.py [--scan] [--report]
  
  --scan    Force fresh API scan (uses ~8 quota units)
  --report  Generate markdown report
  
  Default: Uses cached scan if <24h old, otherwise fresh scan.
  
Quota: ~8 units for full scan (playlistItems.list + videos.list batches)
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

# ── YouTube API imports ──
import requests

# ── Constants ──
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'
API_KEY = os.getenv('YOUTUBE_API_KEY')

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SCAN_FILE = BASE_DIR / 'config' / 'channel_full_scan_2026_02_22.json'
AUDIT_FILE = BASE_DIR / 'config' / 'seo_geo_audit_2026_02_22.json'
REPORT_FILE = BASE_DIR / 'reports' / 'SEO_GEO_AUDIT_REPORT.md'

# Category rules
CATEGORY_RULES = {
    'soundies': {'categoryId': '10', 'name': 'Music'},
    'wochenschau': {'categoryId': '27', 'name': 'Education'},
    'betty_boop': {'categoryId': '1', 'name': 'Film & Animation'},
    'alfred': {'categoryId': '1', 'name': 'Film & Animation'},
    'superman': {'categoryId': '1', 'name': 'Film & Animation'},
    'felix': {'categoryId': '1', 'name': 'Film & Animation'},
    'popeye': {'categoryId': '1', 'name': 'Film & Animation'},
    'casper': {'categoryId': '1', 'name': 'Film & Animation'},
    'looney': {'categoryId': '1', 'name': 'Film & Animation'},
    'maulwurf': {'categoryId': '1', 'name': 'Film & Animation'},
    'kenblock': {'categoryId': '2', 'name': 'Autos & Vehicles'},
    'bravestarr': {'categoryId': '1', 'name': 'Film & Animation'},
    'christmas': {'categoryId': '1', 'name': 'Film & Animation'},
    'other': {'categoryId': '1', 'name': 'Film & Animation'},
}

# Mandatory tags per copilot-instructions
MANDATORY_TAGS_ALL = ['remastered', 'restored']
MANDATORY_TAGS_LONG = ['full movie', 'full episode']

# ═══════════════════════════════════════════════════════════
# PHASE 1: FRESH CHANNEL SCAN
# ═══════════════════════════════════════════════════════════

def fetch_all_video_ids():
    """Fetch all video IDs from uploads playlist. ~4 API calls (1 unit each)."""
    video_ids = []
    url = 'https://youtube.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'contentDetails',
        'playlistId': UPLOAD_PLAYLIST,
        'maxResults': 50,
        'key': API_KEY,
    }
    
    page = 0
    while True:
        page += 1
        resp = requests.get(url, params=params).json()
        if 'error' in resp:
            print(f"  ❌ API Error: {resp['error']['message']}")
            return None
        
        items = resp.get('items', [])
        for item in items:
            vid = item['contentDetails']['videoId']
            video_ids.append(vid)
        
        print(f"  Page {page}: {len(items)} items (total: {len(video_ids)})")
        
        next_page = resp.get('nextPageToken')
        if not next_page:
            break
        params['pageToken'] = next_page
    
    return video_ids


def fetch_video_details(video_ids):
    """Fetch full details for all videos in batches of 50. ~8 API calls (1 unit each)."""
    videos = []
    url = 'https://youtube.googleapis.com/youtube/v3/videos'
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            'part': 'snippet,contentDetails,status,statistics',
            'id': ','.join(batch),
            'key': API_KEY,
        }
        resp = requests.get(url, params=params).json()
        if 'error' in resp:
            print(f"  ❌ API Error: {resp['error']['message']}")
            return None
        
        items = resp.get('items', [])
        videos.extend(items)
        print(f"  Batch {i//50 + 1}: {len(items)} videos (total: {len(videos)})")
    
    return videos


def do_fresh_scan():
    """Full channel scan using Public API. ~8 quota units."""
    if not API_KEY:
        print("❌ YOUTUBE_API_KEY not set!")
        return None
    
    print("📡 Phase 1: Fresh Channel Scan")
    print(f"  Channel: {CHANNEL_ID}")
    
    # Step 1: Get all video IDs
    print("\n  Step 1: Fetching video IDs from uploads playlist...")
    video_ids = fetch_all_video_ids()
    if not video_ids:
        return None
    print(f"  ✅ Found {len(video_ids)} videos")
    
    # Step 2: Fetch full details
    print("\n  Step 2: Fetching video details...")
    videos = fetch_video_details(video_ids)
    if not videos:
        return None
    print(f"  ✅ Got details for {len(videos)} videos")
    
    # Separate public/private
    public = [v for v in videos if v['status']['privacyStatus'] == 'public']
    private = [v for v in videos if v['status']['privacyStatus'] == 'private']
    unlisted = [v for v in videos if v['status']['privacyStatus'] == 'unlisted']
    
    scan_data = {
        'scan_date': datetime.now().isoformat(),
        'channel_id': CHANNEL_ID,
        'total_videos': len(videos),
        'public_count': len(public),
        'private_count': len(private),
        'unlisted_count': len(unlisted),
        'public_videos': public,
        'private_videos': private,
    }
    
    # Save
    SCAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(scan_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n  💾 Saved to {SCAN_FILE.name}")
    print(f"  📊 Public: {len(public)} | Private: {len(private)} | Unlisted: {len(unlisted)}")
    
    return scan_data


# ═══════════════════════════════════════════════════════════
# PHASE 2: SEO + GEO AUDIT
# ═══════════════════════════════════════════════════════════

def detect_category(title, tags=None, desc=''):
    """Detect video category from title/tags."""
    t = title.lower()
    if 'soundie' in t or 'soundies' in t:
        return 'soundies'
    if 'wochenschau' in t or 'newsreel' in t:
        return 'wochenschau'
    if 'betty boop' in t or 'betty_boop' in t:
        return 'betty_boop'
    if 'alfred' in t and ('kwak' in t or 'kwack' in t or 'quak' in t or 'quack' in t):
        return 'alfred'
    if 'superman' in t or 'fleischer' in t:
        return 'superman'
    if 'felix' in t and 'cat' in t:
        return 'felix'
    if 'popeye' in t:
        return 'popeye'
    if 'casper' in t:
        return 'casper'
    if 'looney' in t or 'merrie' in t or 'bugs bunny' in t or 'daffy' in t:
        return 'looney'
    if 'maulwurf' in t or 'krtek' in t:
        return 'maulwurf'
    if 'ken block' in t or 'gymkhana' in t:
        return 'kenblock'
    if 'bravestarr' in t or 'brave starr' in t:
        return 'bravestarr'
    if 'christmas' in t or 'xmas' in t or 'weihnacht' in t:
        return 'christmas'
    # Check tags
    if tags:
        joined = ' '.join(tags).lower()
        if 'soundie' in joined:
            return 'soundies'
        if 'betty boop' in joined:
            return 'betty_boop'
        if 'alfred' in joined and 'kwak' in joined:
            return 'alfred'
    return 'other'


def parse_duration_seconds(iso_dur):
    """Parse ISO 8601 duration to seconds. e.g. PT10M30S → 630"""
    if not iso_dur:
        return 0
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_dur)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + s


def count_hashtags(desc):
    """Count hashtags in description."""
    return len(re.findall(r'#\w+', desc))


def audit_video(video):
    """Audit a single video against all SEO/GEO rules. Returns score dict."""
    snippet = video.get('snippet', {})
    content = video.get('contentDetails', {})
    status = video.get('status', {})
    stats = video.get('statistics', {})
    
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    cat_id = snippet.get('categoryId', '0')
    has_thumb = content.get('hasCustomThumbnail', False)
    made_for_kids = status.get('madeForKids', False)
    definition = content.get('definition', 'sd')
    duration_iso = content.get('duration', 'PT0S')
    duration_s = parse_duration_seconds(duration_iso)
    views = int(stats.get('viewCount', 0))
    likes = int(stats.get('likeCount', 0))
    comments = int(stats.get('commentCount', 0))
    
    vid_cat = detect_category(title, tags, desc)
    issues = []
    
    # ── TITLE SCORING (35 pts) ──
    title_score = 0
    
    # 1. Title length 50-70 chars (5 pts)
    tlen = len(title)
    if 50 <= tlen <= 70:
        title_score += 5
    elif 40 <= tlen <= 80:
        title_score += 3
    else:
        issues.append(f"TITLE_LENGTH: {tlen} chars (ideal: 50-70)")
    
    # 2. 8K marker present (5 pts)
    has_8k = bool(re.search(r'8K', title, re.IGNORECASE))
    if has_8k:
        title_score += 5
    else:
        issues.append("TITLE_NO_8K: Missing '8K' in title")
    
    # 3. 4K UHD marker present (5 pts)
    has_4k = bool(re.search(r'4K', title, re.IGNORECASE))
    if has_4k:
        title_score += 5
    else:
        issues.append("TITLE_NO_4K: Missing '4K UHD' in title")
    
    # 4. Both quality markers: "8K HQ (4K UHD)" (5 pts bonus)
    has_full_quality = bool(re.search(r'8K\s*HQ\s*\(4K\s*UHD\)', title, re.IGNORECASE))
    if has_full_quality:
        title_score += 5
    else:
        issues.append("TITLE_FORMAT: Should use '8K HQ (4K UHD)' format")
    
    # 5. No @channel in title (5 pts)
    if '@remAIke' not in title:
        title_score += 5
    else:
        issues.append("TITLE_AT_CHANNEL: Remove @remAIke_IT from title!")
    
    # 6. Keyword at start (5 pts) - series name or key identifier
    keyword_at_start = False
    first_word = title.split(':')[0].strip().lower() if ':' in title else title.split()[0].lower() if title else ''
    known_keywords = ['betty', 'superman', 'felix', 'popeye', 'casper', 'alfred', 
                      'wochenschau', 'soundie', 'bravestarr', 'looney', 'christmas',
                      'ken', 'der', 'the', 'classic', 'vintage']
    if any(kw in first_word for kw in known_keywords):
        title_score += 5
        keyword_at_start = True
    else:
        issues.append(f"TITLE_KEYWORD: No known keyword at title start ('{first_word}')")
    
    # 7. Year present (5 pts)
    has_year = bool(re.search(r'\(?\d{4}\)?', title))
    if has_year or vid_cat in ['kenblock']:  # Ken Block doesn't need year
        title_score += 5
    else:
        issues.append("TITLE_NO_YEAR: Missing year in title")
    
    # ── DESCRIPTION SCORING (25 pts) ──
    desc_score = 0
    
    # 1. Description length (5 pts)
    dlen = len(desc)
    if dlen >= 500:
        desc_score += 5
    elif dlen >= 200:
        desc_score += 3
    elif dlen >= 100:
        desc_score += 1
    else:
        issues.append(f"DESC_SHORT: {dlen} chars (min: 500)")
    
    # 2. CTA block (5 pts)
    has_like = bool(re.search(r'LIKE|👆|👍', desc, re.IGNORECASE))
    has_subscribe = bool(re.search(r'SUBSCRIBE|ABONNIER', desc, re.IGNORECASE))
    has_comment = bool(re.search(r'COMMENT|KOMMENTAR|💬', desc, re.IGNORECASE))
    cta_count = sum([has_like, has_subscribe, has_comment])
    if cta_count >= 2:
        desc_score += 5
    elif cta_count >= 1:
        desc_score += 2
    else:
        issues.append("DESC_NO_CTA: Missing LIKE/SUBSCRIBE/COMMENT CTAs")
    
    # 3. Pflicht-Links (5 pts)
    has_remaike_link = 'www.remaike.IT' in desc or 'remaike.it' in desc.lower()
    has_yt_link = '@remAIke_IT' in desc or 'youtube.com/@remAIke_IT' in desc
    link_pts = 0
    if has_remaike_link:
        link_pts += 2.5
    else:
        issues.append("DESC_NO_WEBSITE: Missing 'www.remaike.IT' link")
    if has_yt_link:
        link_pts += 2.5
    else:
        issues.append("DESC_NO_YTLINK: Missing YouTube channel link")
    desc_score += int(link_pts)
    
    # 4. Hashtags (5 pts) — must have 2-5, not >5
    hashtag_count = count_hashtags(desc)
    if 2 <= hashtag_count <= 5:
        desc_score += 5
    elif hashtag_count == 1:
        desc_score += 2
        issues.append(f"DESC_FEW_HASHTAGS: {hashtag_count} (ideal: 2-5)")
    elif hashtag_count > 5:
        desc_score += 2
        issues.append(f"DESC_TOO_MANY_HASHTAGS: {hashtag_count} (max: 5!)")
    else:
        issues.append("DESC_NO_HASHTAGS: Missing hashtags in description")
    
    # 5. Chapters / timestamps (5 pts)
    has_chapters = bool(re.search(r'\d:\d\d', desc))
    if has_chapters:
        desc_score += 5
    elif duration_s < 120:
        desc_score += 5  # Short videos don't need chapters
    else:
        issues.append("DESC_NO_CHAPTERS: Missing timestamps for chapters")
    
    # ── TAGS SCORING (10 pts) ──
    tags_score = 0
    tags_lower = [t.lower() for t in tags]
    
    # 1. Tag count (3 pts)
    tag_count = len(tags)
    if 5 <= tag_count <= 15:
        tags_score += 3
    elif tag_count > 15:
        tags_score += 1
        issues.append(f"TAGS_TOO_MANY: {tag_count} (max: 15!)")
    elif tag_count > 0:
        tags_score += 1
        issues.append(f"TAGS_TOO_FEW: {tag_count} (ideal: 5-15)")
    else:
        issues.append("TAGS_NONE: No tags set!")
    
    # 2. Has '8K' or '8k' in tags (2 pts)
    if any('8k' in t for t in tags_lower):
        tags_score += 2
    else:
        issues.append("TAGS_NO_8K: Missing '8K' tag")
    
    # 3. Mandatory tags: remastered, restored (3 pts)
    has_remastered = any('remastered' in t for t in tags_lower)
    has_restored = any('restored' in t for t in tags_lower)
    if has_remastered:
        tags_score += 1.5
    else:
        issues.append("TAGS_NO_REMASTERED: Missing 'remastered' tag")
    if has_restored:
        tags_score += 1.5
    else:
        issues.append("TAGS_NO_RESTORED: Missing 'restored' tag")
    tags_score = int(tags_score)
    
    # 4. Public domain tag (2 pts)
    has_pd = any('public domain' in t for t in tags_lower)
    if has_pd:
        tags_score += 2
    else:
        issues.append("TAGS_NO_PD: Missing 'public domain' tag")
    
    # ── TECHNICAL SCORING (15 pts) ──
    tech_score = 0
    
    # 1. Custom thumbnail (4 pts)
    if has_thumb:
        tech_score += 4
    else:
        issues.append("TECH_NO_THUMBNAIL: Missing custom thumbnail!")
    
    # 2. Not made for kids (3 pts)
    if not made_for_kids:
        tech_score += 3
    else:
        issues.append("TECH_KIDS: madeForKids=true — should be false!")
    
    # 3. HD definition (3 pts)
    if definition == 'hd':
        tech_score += 3
    else:
        issues.append(f"TECH_SD: definition='{definition}' — should be 'hd'")
    
    # 4. Correct category (5 pts)
    expected_cat = CATEGORY_RULES.get(vid_cat, {}).get('categoryId', '1')
    if cat_id == expected_cat:
        tech_score += 5
    else:
        expected_name = CATEGORY_RULES.get(vid_cat, {}).get('name', 'Film & Animation')
        issues.append(f"TECH_WRONG_CAT: categoryId={cat_id}, expected={expected_cat} ({expected_name})")
    
    # ── GEO / SCHEMA SCORING (10 pts) ──
    geo_score = 0
    
    # 1. First 2 description lines ≠ title (3 pts) — for AI snippet extraction
    desc_first_line = desc.split('\n')[0].strip() if desc else ''
    if desc_first_line and desc_first_line.lower() != title.lower() and len(desc_first_line) > 20:
        geo_score += 3
    else:
        issues.append("GEO_DESC_FIRST_LINE: First description line should differ from title (for AI snippets)")
    
    # 2. Description contains contextual keywords for AI (3 pts)
    geo_keywords = ['remastered', 'restored', 'AI', '8K', 'classic', 'vintage', 'public domain']
    geo_hits = sum(1 for kw in geo_keywords if kw.lower() in desc.lower())
    if geo_hits >= 4:
        geo_score += 3
    elif geo_hits >= 2:
        geo_score += 2
    elif geo_hits >= 1:
        geo_score += 1
    else:
        issues.append("GEO_NO_CONTEXT: Description lacks GEO keywords (remastered, restored, AI, classic, vintage, public domain)")
    
    # 3. Structured description format (2 pts) — sections, emojis, separators
    has_structure = bool(re.search(r'━|─|═|🎬|📺|🌐|▬', desc))
    if has_structure:
        geo_score += 2
    else:
        issues.append("GEO_NO_STRUCTURE: Description lacks structural formatting for readability")
    
    # 4. Category-specific GEO signals (2 pts)
    if vid_cat == 'wochenschau':
        # Should have location info
        has_location = bool(re.search(r'location|ort|📍', desc, re.IGNORECASE))
        has_date_context = bool(re.search(r'\d{1,2}\.\d{1,2}\.\d{4}', desc))
        if has_location or has_date_context:
            geo_score += 2
        else:
            issues.append("GEO_WS_NO_LOCATION: Wochenschau should have location/date context")
    elif vid_cat == 'soundies':
        has_artist = bool(re.search(r'artist|performer|singer|musician|band', desc, re.IGNORECASE))
        if has_artist or 'jazz' in desc.lower() or 'swing' in desc.lower():
            geo_score += 2
        else:
            issues.append("GEO_SOUNDIE_NO_ARTIST: Soundie should reference genre/artist")
    elif vid_cat in ['alfred', 'betty_boop', 'superman', 'casper', 'felix']:
        has_episode = bool(re.search(r'episode|folge|E\d+|ep\s*\d+', desc, re.IGNORECASE))
        if has_episode or 'series' in desc.lower() or 'serie' in desc.lower():
            geo_score += 2
        else:
            issues.append(f"GEO_SERIES_NO_CONTEXT: {vid_cat} should reference episode/series info")
    else:
        geo_score += 2  # Generic content gets free points
    
    # ── ENGAGEMENT SCORING (5 pts) ──
    eng_score = 0
    
    if views >= 1000:
        eng_score += 2
    elif views >= 100:
        eng_score += 1
    
    like_ratio = (likes / views * 100) if views > 0 else 0
    if like_ratio >= 5:
        eng_score += 1.5
    elif like_ratio >= 2:
        eng_score += 0.5
    
    if comments > 0:
        eng_score += 1.5
    eng_score = int(eng_score)
    
    # ── TOTAL ──
    total = title_score + desc_score + tags_score + tech_score + geo_score + eng_score
    
    # Grade
    if total >= 90:
        grade = 'A+'
    elif total >= 80:
        grade = 'A'
    elif total >= 70:
        grade = 'B'
    elif total >= 60:
        grade = 'C'
    elif total >= 50:
        grade = 'D'
    else:
        grade = 'F'
    
    return {
        'id': video['id'],
        'title': title,
        'category': vid_cat,
        'score': total,
        'grade': grade,
        'title_score': title_score,
        'desc_score': desc_score,
        'tags_score': int(tags_score),
        'tech_score': tech_score,
        'geo_score': geo_score,
        'eng_score': eng_score,
        'views': views,
        'likes': likes,
        'comments': comments,
        'duration_s': duration_s,
        'tag_count': len(tags),
        'hashtag_count': count_hashtags(desc),
        'has_thumbnail': has_thumb,
        'category_id': cat_id,
        'issues': issues,
        'issue_count': len(issues),
    }


def run_audit(videos):
    """Run audit on all public videos."""
    print(f"\n📊 Phase 2: SEO + GEO Audit on {len(videos)} public videos")
    
    results = []
    for v in videos:
        result = audit_video(v)
        results.append(result)
    
    # Sort by score ascending (worst first)
    results.sort(key=lambda r: r['score'])
    
    # Aggregate stats
    scores = [r['score'] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    grade_dist = defaultdict(int)
    for r in results:
        grade_dist[r['grade']] += 1
    
    cat_scores = defaultdict(list)
    for r in results:
        cat_scores[r['category']].append(r['score'])
    cat_averages = {cat: sum(s)/len(s) for cat, s in cat_scores.items()}
    
    # Issue frequency
    issue_freq = defaultdict(int)
    for r in results:
        for iss in r['issues']:
            issue_type = iss.split(':')[0]
            issue_freq[issue_type] += 1
    issue_freq_sorted = sorted(issue_freq.items(), key=lambda x: -x[1])
    
    # Score distribution
    brackets = {'90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0, '50-59': 0, '0-49': 0}
    for s in scores:
        if s >= 90: brackets['90-100'] += 1
        elif s >= 80: brackets['80-89'] += 1
        elif s >= 70: brackets['70-79'] += 1
        elif s >= 60: brackets['60-69'] += 1
        elif s >= 50: brackets['50-59'] += 1
        else: brackets['0-49'] += 1
    
    # Sub-score averages
    sub_avgs = {
        'title': sum(r['title_score'] for r in results) / len(results),
        'description': sum(r['desc_score'] for r in results) / len(results),
        'tags': sum(r['tags_score'] for r in results) / len(results),
        'technical': sum(r['tech_score'] for r in results) / len(results),
        'geo': sum(r['geo_score'] for r in results) / len(results),
        'engagement': sum(r['eng_score'] for r in results) / len(results),
    }
    
    audit = {
        'audit_date': datetime.now().isoformat(),
        'total_videos': len(results),
        'average_score': round(avg_score, 1),
        'grade_distribution': dict(grade_dist),
        'score_distribution': brackets,
        'category_averages': {k: round(v, 1) for k, v in sorted(cat_averages.items(), key=lambda x: -x[1])},
        'sub_score_averages': {k: round(v, 1) for k, v in sub_avgs.items()},
        'top_issues': issue_freq_sorted[:20],
        'videos': results,
    }
    
    return audit


def generate_report(audit):
    """Generate markdown report."""
    lines = [
        f"# SEO + GEO Audit Report — @remAIke_IT",
        f"**Generated:** {audit['audit_date'][:10]}",
        f"**Videos Audited:** {audit['total_videos']}",
        f"**Average Score:** {audit['average_score']}/100",
        "",
        "---",
        "",
        "## Grade Distribution",
        "",
        "| Grade | Count | % |",
        "|-------|-------|---|",
    ]
    
    total = audit['total_videos']
    for grade in ['A+', 'A', 'B', 'C', 'D', 'F']:
        count = audit['grade_distribution'].get(grade, 0)
        pct = round(count / total * 100, 1)
        lines.append(f"| {grade} | {count} | {pct}% |")
    
    lines.extend([
        "",
        "## Score Distribution",
        "",
        "| Range | Count |",
        "|-------|-------|",
    ])
    for bracket, count in audit['score_distribution'].items():
        bar = '█' * count
        lines.append(f"| {bracket} | {count} {bar} |")
    
    lines.extend([
        "",
        "## Sub-Score Averages (max possible)",
        "",
        "| Category | Average | Max |",
        "|----------|---------|-----|",
    ])
    maxes = {'title': 35, 'description': 25, 'tags': 10, 'technical': 15, 'geo': 10, 'engagement': 5}
    for cat, avg in audit['sub_score_averages'].items():
        pct = round(avg / maxes[cat] * 100, 1)
        lines.append(f"| {cat.title()} | {avg}/{maxes[cat]} | {pct}% |")
    
    lines.extend([
        "",
        "## Category Averages",
        "",
        "| Category | Avg Score | Videos |",
        "|----------|-----------|--------|",
    ])
    for cat, avg in audit['category_averages'].items():
        count = sum(1 for r in audit['videos'] if r['category'] == cat)
        lines.append(f"| {cat} | {avg} | {count} |")
    
    lines.extend([
        "",
        "## Top 20 Issues (Most Frequent)",
        "",
        "| # | Issue | Count | % |",
        "|---|-------|-------|---|",
    ])
    for i, (issue, count) in enumerate(audit['top_issues'][:20], 1):
        pct = round(count / total * 100, 1)
        lines.append(f"| {i} | {issue} | {count} | {pct}% |")
    
    lines.extend([
        "",
        "## Worst 20 Videos (Need Attention)",
        "",
        "| Score | Grade | Title | Issues |",
        "|-------|-------|-------|--------|",
    ])
    for r in audit['videos'][:20]:
        short_title = r['title'][:60] + ('...' if len(r['title']) > 60 else '')
        lines.append(f"| {r['score']} | {r['grade']} | {short_title} | {r['issue_count']} |")
    
    lines.extend([
        "",
        "## Best 10 Videos",
        "",
        "| Score | Grade | Title |",
        "|-------|-------|-------|",
    ])
    for r in sorted(audit['videos'], key=lambda x: -x['score'])[:10]:
        short_title = r['title'][:60] + ('...' if len(r['title']) > 60 else '')
        lines.append(f"| {r['score']} | {r['grade']} | {short_title} |")
    
    lines.extend([
        "",
        "---",
        f"*Report generated by comprehensive_seo_geo_audit_2026.py*",
    ])
    
    return '\n'.join(lines)


def main():
    args = sys.argv[1:]
    force_scan = '--scan' in args
    gen_report = '--report' in args
    
    print("=" * 60)
    print("  🔍 COMPREHENSIVE SEO + GEO AUDIT — @remAIke_IT")
    print("=" * 60)
    
    # Check for cached scan
    scan_data = None
    if not force_scan and SCAN_FILE.exists():
        scan_data = json.load(open(SCAN_FILE, 'r', encoding='utf-8'))
        scan_age = datetime.now() - datetime.fromisoformat(scan_data['scan_date'])
        if scan_age < timedelta(hours=24):
            print(f"\n📂 Using cached scan ({scan_data['public_count']} videos, {scan_age.seconds//3600}h old)")
        else:
            print(f"\n⚠️ Cached scan is {scan_age.days}d old — refreshing...")
            scan_data = None
    
    # Do fresh scan if needed
    if scan_data is None:
        scan_data = do_fresh_scan()
        if scan_data is None:
            # Fallback to any existing scan
            for fallback in ['channel_full_scan_2026_02_22.json', 'fresh_channel_scan.json']:
                fp = BASE_DIR / 'config' / fallback
                if fp.exists():
                    print(f"\n📂 Falling back to {fallback}")
                    scan_data = json.load(open(fp, 'r', encoding='utf-8'))
                    break
        if scan_data is None:
            print("❌ No scan data available. Set YOUTUBE_API_KEY and run with --scan")
            sys.exit(1)
    
    # Run audit
    public_videos = scan_data.get('public_videos', [])
    audit = run_audit(public_videos)
    
    # Save audit JSON
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Audit saved to {AUDIT_FILE.name}")
    
    # Print summary
    print(f"\n{'=' * 60}")
    print(f"  📊 AUDIT SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Videos:  {audit['total_videos']}")
    print(f"  Average: {audit['average_score']}/100")
    print(f"  Grades:  {dict(audit['grade_distribution'])}")
    print()
    print(f"  Sub-Scores:")
    maxes = {'title': 35, 'description': 25, 'tags': 10, 'technical': 15, 'geo': 10, 'engagement': 5}
    for cat, avg in audit['sub_score_averages'].items():
        pct = round(avg / maxes[cat] * 100)
        bar = '█' * (pct // 5) + '░' * (20 - pct // 5)
        print(f"    {cat:12s}: {avg:5.1f}/{maxes[cat]:2d}  {bar} {pct}%")
    
    print(f"\n  Top 5 Issues:")
    for i, (issue, count) in enumerate(audit['top_issues'][:5], 1):
        pct = round(count / audit['total_videos'] * 100)
        print(f"    {i}. {issue}: {count} videos ({pct}%)")
    
    print(f"\n  Category Averages:")
    for cat, avg in audit['category_averages'].items():
        count = sum(1 for r in audit['videos'] if r['category'] == cat)
        print(f"    {cat:15s}: {avg:5.1f}/100  ({count} videos)")
    
    # Generate report
    if gen_report or True:  # Always generate
        report = generate_report(audit)
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📝 Report saved to {REPORT_FILE.name}")
    
    print(f"\n{'=' * 60}")
    print(f"  ✅ AUDIT COMPLETE")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
