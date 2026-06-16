#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════
  COMPREHENSIVE CHANNEL AUDIT v2.0 - remAIke_IT
  Based on ALL workspace research (Feb 2026):
  - .github/copilot-instructions.md (MASTER RULES)
  - docs/youtube/YOUTUBE_ALGORITHM_2026.md
  - docs/YOUTUBE_ALGO_2026_PLAYBOOK.md
  - docs/templates/SOUNDIES_SEO_TEMPLATE.md
  - docs/templates/SERIES_TEMPLATE.md
  - docs/templates/WOCHENSCHAU_MULTILINGUAL_SEO.md
  - docs/youtube/CHANNEL_IMPROVEMENTS_2026.md
═══════════════════════════════════════════════════════════════════════

AUDIT CHECKS (31 checks):

  --- TITLE (40 SEO points - MOST IMPORTANT) ---
  T01: Title <=70 chars (YouTube truncates after ~60-70)
  T02: NO @remAIke_IT in title (copilot-instructions: wastes chars!)
  T03: Has "8K" in title (quality signal)
  T04: Has "HQ" in title (quality signal: "8K HQ" preferred)
  T05: Has "4K" somewhere (batch fix added "4K UHD" - dual keyword)
  T06: Keyword at BEGINNING of title (first 40 chars)
  T07: No raw filename artifacts (sls, xvid, hq_, etc.)
  T08: Has year or date (search signal for vintage content)
  T09: Title not ALL CAPS (spam signal)
  T10: Soundies: Song title FIRST (before "Soundie")
  T11: Wochenschau: Has proper date format (DD.MM.YYYY)
  T12: Series: Has episode format (XX/YY) or clear ep marker

  --- DESCRIPTION (30 SEO points) ---
  D01: Has CTA (LIKE/COMMENT/SUBSCRIBE)
  D02: Has www.remaike.IT (website link - PFLICHT)
  D03: Has YouTube channel link (@remAIke_IT or youtube.com/@remAIke)
  D04: Max 5 hashtags (more = spam per YouTube)
  D05: Has at least 1 hashtag (minimum for discovery)
  D06: First 2 lines contain keyword (visible in search results!)
  D07: Wochenschau: Has multilingual search block
  D08: Description not empty/minimal (<50 chars)
  D09: Has "WE HAVE THE BEST VERSION" header (brand consistency)
  D10: Has FRai.TV link

  --- TAGS (10 SEO points - MINIMAL role per YouTube) ---
  G01: Max 15 tags (more = spam policy violation!)
  G02: Has at least 1 tag
  G03: Has "8K" or "4K" in tags
  G04: Has "public domain" in tags (niche signal)
  G05: Has "remAIke" in tags (brand)

  --- CATEGORY & SETTINGS ---
  C01: Soundies = Category 10 (Music) PFLICHT!
  C02: Wochenschau = Category 25 (News) or 27 (Education)
  C03: Series/Cartoons = Category 1 (Film & Animation)

  --- CONTENT CLASSIFICATION ---
  X01: Classify video type (Soundie/Wochenschau/Series/Film/Other)
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ─── Configuration ────────────────────────────────────────────────────
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOADS_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Known series keywords for classification
SERIES_KEYWORDS = {
    'betty boop': {'category': '1', 'type': 'series', 'series': 'Betty Boop'},
    'alfred j. kwak': {'category': '1', 'type': 'series', 'series': 'Alfred J. Kwak'},
    'alfred jodokus': {'category': '1', 'type': 'series', 'series': 'Alfred J. Kwak'},
    'bravestarr': {'category': '1', 'type': 'series', 'series': 'BraveStarr'},
    'brave starr': {'category': '1', 'type': 'series', 'series': 'BraveStarr'},
    'superman': {'category': '1', 'type': 'series', 'series': 'Superman/Fleischer'},
    'fleischer': {'category': '1', 'type': 'series', 'series': 'Superman/Fleischer'},
    'popeye': {'category': '1', 'type': 'series', 'series': 'Popeye'},
    'felix the cat': {'category': '1', 'type': 'series', 'series': 'Felix the Cat'},
    'felix': {'category': '1', 'type': 'series', 'series': 'Felix the Cat'},
    'looney tunes': {'category': '1', 'type': 'series', 'series': 'Looney Tunes'},
    'merrie melodies': {'category': '1', 'type': 'series', 'series': 'Looney Tunes'},
    'maulwurf': {'category': '1', 'type': 'series', 'series': 'Der kleine Maulwurf'},
    'krtek': {'category': '1', 'type': 'series', 'series': 'Der kleine Maulwurf'},
    'peterchens mondfahrt': {'category': '1', 'type': 'series', 'series': 'Peterchens Mondfahrt'},
    'glücksbärchi': {'category': '1', 'type': 'series', 'series': 'Glücksbärchis'},
    'care bears': {'category': '1', 'type': 'series', 'series': 'Care Bears'},
    'porky pig': {'category': '1', 'type': 'series', 'series': 'Porky Pig'},
}

SOUNDIE_KEYWORDS = ['soundie', 'soundies']
WOCHENSCHAU_KEYWORDS = ['wochenschau', 'newsreel']
FILENAME_ARTIFACTS = ['sls', 'xvid', 'divx', 'avi', 'mp4', '_hq', 'secondrun', '2x2', 'vhs']

# Severity levels
SEV_CRITICAL = 'CRITICAL'  # Must fix immediately
SEV_HIGH = 'HIGH'          # Should fix soon
SEV_MEDIUM = 'MEDIUM'      # Should fix
SEV_LOW = 'LOW'            # Nice to have
SEV_INFO = 'INFO'          # Just informational


def load_youtube_client():
    """Load OAuth client for READ operations (1 unit per batch)"""
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
    return build('youtube', 'v3', credentials=creds)


def fetch_all_video_ids(youtube):
    """Fetch all video IDs from uploads playlist (1 unit per page of 50)"""
    print("📡 Fetching video IDs from upload playlist...")
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


def fetch_video_details(youtube, video_ids):
    """Fetch full details in batches of 50 (1 unit per batch)"""
    print("📡 Fetching video details (snippet + contentDetails + status)...")
    all_videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part='snippet,contentDetails,status',
            id=','.join(batch)
        ).execute()

        all_videos.extend(resp.get('items', []))
        print(f"   {len(all_videos)}/{len(video_ids)} details...", end='\r')

    print(f"\n✅ Got details for {len(all_videos)} videos")
    return all_videos


def classify_video(title, tags, desc):
    """Classify video into content type based on title/tags/description"""
    t_lower = title.lower()
    
    # Check Soundies
    for kw in SOUNDIE_KEYWORDS:
        if kw in t_lower:
            return 'soundie', 'Soundie'
    
    # Check Wochenschau
    for kw in WOCHENSCHAU_KEYWORDS:
        if kw in t_lower:
            return 'wochenschau', 'Wochenschau'
    
    # Check known series
    for kw, info in SERIES_KEYWORDS.items():
        if kw in t_lower:
            return info['type'], info['series']
    
    # Check tags for classification
    tags_lower = [t.lower() for t in (tags or [])]
    for kw in SOUNDIE_KEYWORDS:
        if kw in tags_lower:
            return 'soundie', 'Soundie'
    for kw in WOCHENSCHAU_KEYWORDS:
        if kw in tags_lower:
            return 'wochenschau', 'Wochenschau'
    
    # Check description
    d_lower = desc.lower()
    if 'soundie' in d_lower:
        return 'soundie', 'Soundie'
    if 'wochenschau' in d_lower or 'newsreel' in d_lower:
        return 'wochenschau', 'Wochenschau'
    
    return 'other', 'Other'


def extract_hashtags(desc):
    """Extract hashtags from description"""
    return [w for w in desc.split() if w.startswith('#') and len(w) > 1]


def has_year(title):
    """Check if title contains a year (1800-2099)"""
    return bool(re.search(r'\b(1[89]\d{2}|20[0-9]{2})\b', title))


def has_date_format(title):
    """Check if title contains DD.MM.YYYY date format"""
    return bool(re.search(r'\d{2}\.\d{2}\.\d{4}', title))


def has_filename_artifacts(title):
    """Check for raw filename leftovers"""
    t_lower = title.lower()
    found = []
    for artifact in FILENAME_ARTIFACTS:
        # Check as standalone word
        if re.search(r'\b' + re.escape(artifact) + r'\b', t_lower):
            found.append(artifact)
    # Also check for "STRIKE" marker
    if 'STRIKE' in title:
        found.append('STRIKE')
    return found


def check_keyword_position(title, video_type, series_name):
    """Check if primary keyword is at the beginning (first 40 chars)"""
    first_40 = title[:40].lower()
    
    if video_type == 'soundie':
        # For soundies: Song title should be FIRST (before "Soundie")
        soundie_pos = title.lower().find('soundie')
        if soundie_pos != -1 and soundie_pos < 5:
            return False, "Song title should come BEFORE 'Soundie'"
        return True, "OK"
    
    if video_type == 'wochenschau':
        if 'wochenschau' in first_40:
            return True, "OK"
        return False, "Missing 'Wochenschau' in first 40 chars"
    
    if series_name:
        series_lower = series_name.lower()
        # Check if series name (or short version) is in first 40 chars
        if series_lower in first_40 or series_lower.split()[0] in first_40:
            return True, "OK"
        return False, f"Series keyword '{series_name}' not in first 40 chars"
    
    return True, "OK (no specific keyword expected)"


def audit_video(video):
    """
    Comprehensive audit of a single video against ALL 2026 rules.
    Returns dict with all check results.
    """
    snippet = video['snippet']
    vid_id = video['id']
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    category = snippet.get('categoryId', '0')
    published = snippet.get('publishedAt', '')
    
    # Classify
    video_type, series_name = classify_video(title, tags, desc)
    
    issues = []
    warnings = []
    info_notes = []
    
    # ═══ TITLE CHECKS (T01-T12) ═══════════════════════════════════════
    
    # T01: Title <=70 chars
    title_len = len(title)
    if title_len > 70:
        issues.append({
            'code': 'T01', 'severity': SEV_HIGH,
            'msg': f'Title too long: {title_len} chars (max 70)',
            'fix': f'Shorten by {title_len - 70} chars'
        })
    
    # T02: NO @remAIke_IT in title
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues.append({
            'code': 'T02', 'severity': SEV_MEDIUM,
            'msg': 'Title contains @channel handle (wastes chars, no SEO benefit)',
            'fix': 'Remove @remAIke_IT from title'
        })
    
    # T03: Has "8K" in title
    has_8k = '8K' in title
    if not has_8k and '4K' not in title:
        issues.append({
            'code': 'T03', 'severity': SEV_CRITICAL,
            'msg': 'Title missing quality keyword (no 8K or 4K)',
            'fix': 'Add "8K HQ" or "8K HQ (4K UHD)" to title'
        })
    
    # T04: Has "HQ" in title (preferred: "8K HQ")
    has_hq = 'HQ' in title
    if has_8k and not has_hq:
        warnings.append({
            'code': 'T04', 'severity': SEV_LOW,
            'msg': 'Title has 8K but not "8K HQ" (preferred format)',
            'fix': 'Change "8K" to "8K HQ"'
        })
    
    # T05: Has "4K" keyword (dual quality signal)
    has_4k = '4K' in title
    if not has_4k:
        info_notes.append({
            'code': 'T05', 'severity': SEV_INFO,
            'msg': 'Title missing "4K" keyword (dual quality signal)',
            'detail': 'Consider "8K HQ (4K UHD)" for both 8K and 4K searches'
        })
    
    # T06: Keyword at beginning (first 40 chars)
    kw_ok, kw_msg = check_keyword_position(title, video_type, series_name)
    if not kw_ok:
        issues.append({
            'code': 'T06', 'severity': SEV_MEDIUM,
            'msg': f'Keyword position issue: {kw_msg}',
            'fix': 'Move primary keyword to beginning of title'
        })
    
    # T07: Filename artifacts
    artifacts = has_filename_artifacts(title)
    if artifacts:
        issues.append({
            'code': 'T07', 'severity': SEV_CRITICAL,
            'msg': f'Raw filename artifacts in title: {", ".join(artifacts)}',
            'fix': 'Remove all filename markers, rename properly'
        })
    
    # T08: Has year or date
    if not has_year(title):
        if video_type in ('soundie', 'wochenschau') or series_name:
            warnings.append({
                'code': 'T08', 'severity': SEV_MEDIUM,
                'msg': 'Title missing year/date (important for vintage content)',
                'fix': 'Add year in parentheses: (1940) or (1932)'
            })
    
    # T09: ALL CAPS check
    # Count uppercase letters vs total
    alpha_chars = [c for c in title if c.isalpha()]
    if alpha_chars and len(alpha_chars) > 10:
        upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
        if upper_ratio > 0.7:
            warnings.append({
                'code': 'T09', 'severity': SEV_LOW,
                'msg': f'Title is mostly uppercase ({upper_ratio:.0%}) - looks spammy',
                'fix': 'Use title case instead'
            })
    
    # T10: Soundies - Song title FIRST
    if video_type == 'soundie':
        t_lower = title.lower()
        soundie_pos = t_lower.find('soundie')
        colon_pos = title.find(':')
        if soundie_pos != -1 and soundie_pos < 10:
            # "Soundie:" is at the start - WRONG per 2026 template
            issues.append({
                'code': 'T10', 'severity': SEV_MEDIUM,
                'msg': 'Soundie: Song title should come FIRST, not "Soundie:"',
                'fix': 'Format: [Song Title] (1940s) | Soundie | 8K HQ'
            })
    
    # T11: Wochenschau - proper date format
    if video_type == 'wochenschau':
        if not has_date_format(title):
            warnings.append({
                'code': 'T11', 'severity': SEV_LOW,
                'msg': 'Wochenschau title missing DD.MM.YYYY date format',
                'fix': 'Add exact date: (DD.MM.YYYY)'
            })
    
    # T12: Series - episode format
    if video_type == 'series' and series_name:
        has_ep = bool(re.search(r'\(\d+/\d+\)', title)) or \
                 bool(re.search(r'[Ee]p\.?\s*\d+', title)) or \
                 bool(re.search(r'[Ee]pisode\s*\d+', title))
        if not has_ep:
            info_notes.append({
                'code': 'T12', 'severity': SEV_INFO,
                'msg': f'Series "{series_name}" missing episode format (XX/YY)',
                'detail': 'Consider: [Series] (01/52): [Title] | 8K HQ'
            })
    
    # ═══ DESCRIPTION CHECKS (D01-D10) ══════════════════════════════════
    
    desc_upper = desc.upper()
    desc_lower = desc.lower()
    
    # D01: Has CTA
    has_cta = any(word in desc_upper for word in ['LIKE', 'SUBSCRIBE', 'COMMENT'])
    if not has_cta:
        issues.append({
            'code': 'D01', 'severity': SEV_HIGH,
            'msg': 'Description missing CTA (LIKE/COMMENT/SUBSCRIBE)',
            'fix': 'Add CTA block: LIKE • COMMENT • SUBSCRIBE @remAIke_IT'
        })
    
    # D02: Has www.remaike.IT
    has_website = 'remaike.it' in desc_lower or 'remaike.tv' in desc_lower
    if not has_website:
        issues.append({
            'code': 'D02', 'severity': SEV_HIGH,
            'msg': 'Description missing website link (www.remaike.IT)',
            'fix': 'Add: 🌐 www.remaike.IT'
        })
    
    # D03: Has YouTube channel link
    has_channel_link = '@remAIke_IT' in desc or 'youtube.com/@remAIke' in desc or '@remaike_it' in desc_lower
    if not has_channel_link:
        issues.append({
            'code': 'D03', 'severity': SEV_MEDIUM,
            'msg': 'Description missing YouTube channel link',
            'fix': 'Add: 📺 https://www.youtube.com/@remAIke_IT'
        })
    
    # D04: Max 5 hashtags
    hashtags = extract_hashtags(desc)
    if len(hashtags) > 5:
        issues.append({
            'code': 'D04', 'severity': SEV_MEDIUM,
            'msg': f'Too many hashtags: {len(hashtags)} (max 5)',
            'fix': f'Remove {len(hashtags) - 5} hashtags. Keep most relevant 5.'
        })
    
    # D05: Has at least 1 hashtag
    if len(hashtags) == 0:
        warnings.append({
            'code': 'D05', 'severity': SEV_LOW,
            'msg': 'Description has no hashtags',
            'fix': 'Add 2-5 relevant hashtags at end of description'
        })
    
    # D06: First 2 lines contain keyword
    first_lines = desc[:200].lower() if desc else ''
    title_keywords = [w.lower() for w in title.split() if len(w) > 3 and w.lower() not in 
                      ['8k', 'hq', '4k', 'uhd', 'the', 'and', 'der', 'die', 'das', 'und', 'von']]
    keyword_in_first_lines = any(kw in first_lines for kw in title_keywords[:3]) if title_keywords else True
    if not keyword_in_first_lines and desc:
        warnings.append({
            'code': 'D06', 'severity': SEV_LOW,
            'msg': 'Title keywords not found in first 200 chars of description',
            'fix': 'Put main keyword in first 2 lines (visible in search results)'
        })
    
    # D07: Wochenschau - multilingual search block
    if video_type == 'wochenschau':
        has_multilingual = any(lang in desc for lang in ['🇬🇧', '🇪🇸', '🇫🇷', '🌍', 'SEARCH IN YOUR LANGUAGE'])
        if not has_multilingual:
            warnings.append({
                'code': 'D07', 'severity': SEV_LOW,
                'msg': 'Wochenschau missing multilingual search block',
                'fix': 'Add multilingual search terms from WOCHENSCHAU_MULTILINGUAL_SEO.md'
            })
    
    # D08: Description not empty/minimal
    if len(desc.strip()) < 50:
        issues.append({
            'code': 'D08', 'severity': SEV_CRITICAL,
            'msg': f'Description too short or empty ({len(desc.strip())} chars)',
            'fix': 'Add proper description with context, CTA, links'
        })
    
    # D09: Has brand header "WE HAVE THE BEST VERSION"
    has_brand_header = 'BEST VERSION' in desc_upper or 'WE HAVE THE' in desc_upper
    if not has_brand_header:
        info_notes.append({
            'code': 'D09', 'severity': SEV_INFO,
            'msg': 'Missing brand header "WE HAVE THE BEST VERSION FOR YOU"',
            'detail': 'Brand consistency - adds professionalism'
        })
    
    # D10: Has FRai.TV link
    has_frai = 'frai.tv' in desc_lower
    if not has_frai:
        info_notes.append({
            'code': 'D10', 'severity': SEV_INFO,
            'msg': 'Missing FRai.TV link in description',
            'detail': 'Add: www.FRai.TV - All videos organized'
        })
    
    # ═══ TAG CHECKS (G01-G05) ══════════════════════════════════════════
    
    tags_lower = [t.lower() for t in tags]
    
    # G01: Max 15 tags
    if len(tags) > 15:
        issues.append({
            'code': 'G01', 'severity': SEV_MEDIUM,
            'msg': f'Too many tags: {len(tags)} (max 15 per YouTube policy)',
            'fix': f'Remove {len(tags) - 15} least relevant tags'
        })
    
    # G02: Has at least 1 tag
    if len(tags) == 0:
        warnings.append({
            'code': 'G02', 'severity': SEV_LOW,
            'msg': 'No tags at all',
            'fix': 'Add 5-15 relevant tags'
        })
    
    # G03: Has quality tag
    has_quality_tag = any(t in tags_lower for t in ['8k', '4k', '4k uhd', '8k hq', 'uhd'])
    if not has_quality_tag and tags:
        warnings.append({
            'code': 'G03', 'severity': SEV_LOW,
            'msg': 'Tags missing quality keyword (8K/4K)',
            'fix': 'Add "8K" and "4K UHD" to tags'
        })
    
    # G04: Has "public domain" tag
    has_pd_tag = any('public domain' in t for t in tags_lower)
    if not has_pd_tag and tags:
        info_notes.append({
            'code': 'G04', 'severity': SEV_INFO,
            'msg': 'Tags missing "public domain" (niche signal)',
            'detail': 'Add if content is public domain'
        })
    
    # G05: Has brand tag
    has_brand_tag = any('remaike' in t for t in tags_lower)
    if not has_brand_tag and tags:
        info_notes.append({
            'code': 'G05', 'severity': SEV_INFO,
            'msg': 'Tags missing "remAIke" brand tag',
            'detail': 'Add "remAIke" for brand clustering'
        })
    
    # ═══ CATEGORY CHECKS (C01-C03) ═════════════════════════════════════
    
    # C01: Soundies = Music (10)
    if video_type == 'soundie' and category != '10':
        issues.append({
            'code': 'C01', 'severity': SEV_HIGH,
            'msg': f'Soundie wrong category: {category} (should be 10=Music)',
            'fix': 'Change category to Music (10) in YouTube Studio'
        })
    
    # C02: Wochenschau = News (25) or Education (27)
    if video_type == 'wochenschau' and category not in ('25', '27'):
        issues.append({
            'code': 'C02', 'severity': SEV_HIGH,
            'msg': f'Wochenschau wrong category: {category} (should be 25 or 27)',
            'fix': 'Change category to News (25) or Education (27)'
        })
    
    # C03: Series/Cartoons = Film & Animation (1)
    if video_type == 'series' and category != '1':
        warnings.append({
            'code': 'C03', 'severity': SEV_LOW,
            'msg': f'Series wrong category: {category} (expected 1=Film & Animation)',
            'fix': 'Consider changing to Film & Animation (1)'
        })
    
    # ═══ Score Calculation ═════════════════════════════════════════════
    
    # Points: Start at 100, deduct per issue severity
    score = 100
    for issue in issues:
        if issue['severity'] == SEV_CRITICAL:
            score -= 15
        elif issue['severity'] == SEV_HIGH:
            score -= 8
        elif issue['severity'] == SEV_MEDIUM:
            score -= 4
    for w in warnings:
        score -= 1
    score = max(0, score)
    
    return {
        'id': vid_id,
        'title': title,
        'title_len': title_len,
        'tags_count': len(tags),
        'tags': tags[:15],  # Store first 15 for reference
        'hashtag_count': len(hashtags),
        'category': category,
        'video_type': video_type,
        'series': series_name,
        'published': published,
        'has_8k': has_8k,
        'has_4k': has_4k,
        'has_hq': has_hq,
        'score': score,
        'issues': issues,
        'warnings': warnings,
        'info': info_notes,
        'issue_count': len(issues),
        'warning_count': len(warnings),
    }


def detect_new_uploads(current_ids, old_scan_path='config/fresh_channel_scan.json'):
    """Detect videos not in previous scan"""
    try:
        with open(old_scan_path, 'r', encoding='utf-8') as f:
            old_scan = json.load(f)
        old_ids = set()
        items = old_scan.get('videos', old_scan if isinstance(old_scan, list) else [])
        for v in items:
            if isinstance(v, dict):
                vid = (v.get('id') or v.get('video_id') or 
                       v.get('snippet', {}).get('resourceId', {}).get('videoId', ''))
                if vid:
                    old_ids.add(vid)
        return current_ids - old_ids
    except Exception:
        return set()


def print_score_bar(score):
    """Visual score bar"""
    filled = int(score / 5)
    empty = 20 - filled
    if score >= 90:
        color = '🟢'
    elif score >= 70:
        color = '🟡'
    elif score >= 50:
        color = '🟠'
    else:
        color = '🔴'
    return f"{color} {'█' * filled}{'░' * empty} {score}/100"


def main():
    print("═" * 78)
    print("  remAIke.TV - COMPREHENSIVE CHANNEL AUDIT v2.0")
    print("  31 Checks • 2026 Algorithm Rules • Full Workspace Research")
    print("═" * 78)
    print()
    
    youtube = load_youtube_client()
    
    # 1. Fetch all video IDs
    video_ids = fetch_all_video_ids(youtube)
    if not video_ids:
        print("No videos found!")
        return
    
    # 2. Fetch details
    videos = fetch_video_details(youtube, video_ids)
    
    # 3. Detect new uploads
    current_ids = set(v['id'] for v in videos)
    new_ids = detect_new_uploads(current_ids)
    
    # 4. Audit every video
    print(f"\n🔍 AUDITING {len(videos)} VIDEOS against 31 checks...")
    print("─" * 78)
    
    results = []
    for video in videos:
        result = audit_video(video)
        result['is_new'] = video['id'] in new_ids
        results.append(result)
    
    # ═══ Sort by score (worst first) ═══
    results.sort(key=lambda r: (r['score'], -r['issue_count']))
    
    # ═══ STATISTICS ═══
    total = len(results)
    perfect = sum(1 for r in results if r['issue_count'] == 0 and r['warning_count'] == 0)
    has_issues = sum(1 for r in results if r['issue_count'] > 0)
    has_warnings = sum(1 for r in results if r['warning_count'] > 0 and r['issue_count'] == 0)
    avg_score = sum(r['score'] for r in results) / total if total else 0
    
    # Quality keyword stats
    with_8k = sum(1 for r in results if r['has_8k'])
    with_4k = sum(1 for r in results if r['has_4k'])
    with_hq = sum(1 for r in results if r['has_hq'])
    with_8k_hq = sum(1 for r in results if r['has_8k'] and r['has_hq'])
    with_8k_hq_4k = sum(1 for r in results if r['has_8k'] and r['has_hq'] and r['has_4k'])
    
    # Content type distribution
    type_dist = {}
    for r in results:
        t = r['video_type']
        type_dist[t] = type_dist.get(t, 0) + 1
    
    # Score distribution
    score_90_100 = sum(1 for r in results if r['score'] >= 90)
    score_70_89 = sum(1 for r in results if 70 <= r['score'] < 90)
    score_50_69 = sum(1 for r in results if 50 <= r['score'] < 70)
    score_0_49 = sum(1 for r in results if r['score'] < 50)
    
    # Issue type aggregation
    issue_agg = {}
    for r in results:
        for issue in r['issues']:
            code = issue['code']
            if code not in issue_agg:
                issue_agg[code] = {'count': 0, 'severity': issue['severity'], 'msg': issue['msg'].split(':')[0] if ':' in issue['msg'] else issue['msg']}
            issue_agg[code]['count'] += 1
    
    warning_agg = {}
    for r in results:
        for w in r['warnings']:
            code = w['code']
            if code not in warning_agg:
                warning_agg[code] = {'count': 0, 'msg': w['msg'].split(':')[0] if ':' in w['msg'] else w['msg']}
            warning_agg[code]['count'] += 1
    
    # ═══ PRINT REPORT ═══
    print()
    print("═" * 78)
    print("  📊 AUDIT RESULTS")
    print("═" * 78)
    print()
    print(f"  Total Videos:       {total}")
    print(f"  Average Score:      {print_score_bar(int(avg_score))}")
    print()
    print(f"  ✅ Perfect (0 issues): {perfect}")
    print(f"  ⚠️  Issues:            {has_issues}")
    print(f"  💡 Warnings only:      {has_warnings}")
    print()
    
    # New uploads
    new_results = [r for r in results if r['is_new']]
    if new_results:
        print(f"\n🆕 NEW UPLOADS ({len(new_results)}):")
        print("─" * 60)
        for r in new_results:
            print(f"  🆕 {r['title'][:60]}")
            print(f"     ID: {r['id']} | Score: {r['score']}/100")
            if r['issues']:
                for i in r['issues']:
                    print(f"     ❌ [{i['code']}] {i['msg']}")
    
    # Quality keyword analysis
    print(f"\n📊 QUALITY KEYWORD ANALYSIS (Title):")
    print("─" * 60)
    print(f"  Has '8K':                  {with_8k}/{total} ({with_8k*100//total}%)")
    print(f"  Has '8K HQ':               {with_8k_hq}/{total} ({with_8k_hq*100//total}%)")
    print(f"  Has '4K':                  {with_4k}/{total} ({with_4k*100//total}%)")
    print(f"  Has '8K HQ (4K UHD)':      {with_8k_hq_4k}/{total} ({with_8k_hq_4k*100//total}%)")
    print(f"  Has 'HQ':                  {with_hq}/{total} ({with_hq*100//total}%)")
    
    # Content type distribution
    print(f"\n📺 CONTENT TYPE DISTRIBUTION:")
    print("─" * 60)
    for t, count in sorted(type_dist.items(), key=lambda x: -x[1]):
        print(f"  {t:20s}: {count:4d} videos")
    
    # Score distribution
    print(f"\n📈 SCORE DISTRIBUTION:")
    print("─" * 60)
    print(f"  🟢 90-100 (Excellent):  {score_90_100:4d}")
    print(f"  🟡 70-89  (Good):       {score_70_89:4d}")
    print(f"  🟠 50-69  (Needs Work): {score_50_69:4d}")
    print(f"  🔴 0-49   (Critical):   {score_0_49:4d}")
    
    # Issue breakdown by check code
    print(f"\n❌ ISSUE BREAKDOWN (by check):")
    print("─" * 60)
    for code, data in sorted(issue_agg.items(), key=lambda x: (-{'CRITICAL':4,'HIGH':3,'MEDIUM':2,'LOW':1}.get(x[1]['severity'],0), -x[1]['count'])):
        sev_icon = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '⚪'}.get(data['severity'], '⚪')
        print(f"  {sev_icon} [{code}] {data['msg'][:50]:50s} = {data['count']} videos")
    
    if warning_agg:
        print(f"\n⚠️  WARNING BREAKDOWN:")
        print("─" * 60)
        for code, data in sorted(warning_agg.items(), key=lambda x: -x[1]['count']):
            print(f"  💡 [{code}] {data['msg'][:50]:50s} = {data['count']} videos")
    
    # Detailed: Videos with CRITICAL/HIGH issues (top priority fixes)
    critical_videos = [r for r in results if any(i['severity'] in (SEV_CRITICAL, SEV_HIGH) for i in r['issues'])]
    if critical_videos:
        print(f"\n{'═' * 78}")
        print(f"  🔴 CRITICAL/HIGH PRIORITY FIXES ({len(critical_videos)} videos)")
        print(f"{'═' * 78}")
        for r in critical_videos:
            print(f"\n  {print_score_bar(r['score'])}  {r['title'][:55]}")
            print(f"  {'':6s}ID: {r['id']} | Type: {r['video_type']} | Cat: {r['category']}")
            for i in r['issues']:
                if i['severity'] in (SEV_CRITICAL, SEV_HIGH):
                    icon = '🔴' if i['severity'] == SEV_CRITICAL else '🟠'
                    print(f"  {'':6s}{icon} [{i['code']}] {i['msg']}")
                    print(f"  {'':6s}   Fix: {i['fix']}")
    
    # Medium issues
    medium_videos = [r for r in results if 
                     any(i['severity'] == SEV_MEDIUM for i in r['issues']) and
                     not any(i['severity'] in (SEV_CRITICAL, SEV_HIGH) for i in r['issues'])]
    if medium_videos:
        print(f"\n{'═' * 78}")
        print(f"  🟡 MEDIUM PRIORITY FIXES ({len(medium_videos)} videos)")
        print(f"{'═' * 78}")
        for r in medium_videos[:20]:  # Show first 20
            crit_issues = [i for i in r['issues'] if i['severity'] == SEV_MEDIUM]
            codes = ', '.join(i['code'] for i in crit_issues)
            print(f"  🟡 [{codes}] {r['title'][:55]} (Score: {r['score']})")
        if len(medium_videos) > 20:
            print(f"  ... and {len(medium_videos) - 20} more")
    
    # Summary
    print(f"\n{'═' * 78}")
    print(f"  📋 FIX PRIORITY QUEUE")
    print(f"{'═' * 78}")
    print(f"  1. 🆕 NEW UPLOADS (raw filenames):     {len(new_results)} videos")
    print(f"  2. 🔴 CRITICAL issues:                 {sum(1 for r in results if any(i['severity']==SEV_CRITICAL for i in r['issues']))} videos")
    print(f"  3. 🟠 HIGH issues:                     {sum(1 for r in results if any(i['severity']==SEV_HIGH for i in r['issues']))} videos")
    print(f"  4. 🟡 MEDIUM issues:                   {sum(1 for r in results if any(i['severity']==SEV_MEDIUM for i in r['issues']))} videos")
    print(f"  5. 💡 Warnings/Info:                   {sum(1 for r in results if r['warning_count'] > 0)} videos")
    
    # Quota usage
    pages = (len(video_ids) + 49) // 50
    detail_batches = (len(video_ids) + 49) // 50
    total_quota = pages + detail_batches
    print(f"\n📊 API Quota used: ~{total_quota} units (READ only)")
    
    # Save full results
    output = {
        'audit_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'audit_version': '2.0',
        'checks_count': 31,
        'total_videos': total,
        'average_score': round(avg_score, 1),
        'statistics': {
            'perfect': perfect,
            'with_issues': has_issues,
            'warnings_only': has_warnings,
            'score_distribution': {
                '90-100': score_90_100,
                '70-89': score_70_89,
                '50-69': score_50_69,
                '0-49': score_0_49,
            },
            'quality_keywords': {
                'has_8K': with_8k,
                'has_8K_HQ': with_8k_hq,
                'has_4K': with_4k,
                'has_8K_HQ_4K_UHD': with_8k_hq_4k,
                'has_HQ': with_hq,
            },
            'content_types': type_dist,
        },
        'issue_summary': {code: data['count'] for code, data in issue_agg.items()},
        'new_uploads': [r['id'] for r in new_results],
        'fix_priority': {
            'critical': [{'id': r['id'], 'title': r['title'], 'issues': r['issues']} 
                        for r in results if any(i['severity']==SEV_CRITICAL for i in r['issues'])],
            'high': [{'id': r['id'], 'title': r['title'], 'issues': r['issues']}
                    for r in results if any(i['severity']==SEV_HIGH for i in r['issues']) 
                    and not any(i['severity']==SEV_CRITICAL for i in r['issues'])],
        },
        'videos': results,
    }
    
    output_path = f'config/comprehensive_audit_{datetime.now().strftime("%Y_%m_%d")}.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Full audit saved to {output_path}")
    print(f"\n{'═' * 78}")
    print(f"  ✅ AUDIT COMPLETE - {total} videos checked against 31 rules")
    print(f"{'═' * 78}")


if __name__ == "__main__":
    main()
