"""
═══════════════════════════════════════════════════════════════════
CHANNEL PERFECTION ENGINE — Full Live Audit + Auto-Fix
═══════════════════════════════════════════════════════════════════

Phase 1: Live-Scan aller Videos von YouTube (READ = ~7 units)
Phase 2: Audit gegen ALLE Workspace-Regeln
Phase 3: Auto-Fix Plan erstellen
Phase 4: Fixes anwenden (WRITE = 50 units pro Video)

Rules enforced:
  R1  8K/4K in title
  R2  NO @remAIke_IT in title (new 2026 rule)
  R3  Title ≤70 chars
  R4  CTA in description (LIKE/SUBSCRIBE/COMMENT)
  R5  www.remaike.IT in description
  R6  youtube.com/@remAIke_IT in description
  R7  Max 5 hashtags in description
  R8  Max 15 tags
  R9  Category correct per series
  R10 No raw "sls" artifacts in title
  R11 Description ≥50 chars
  R12 Localizations (min 5 languages)
  R13 madeForKids = false
"""

import os, sys, json, re, time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ──────────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────────
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"
TOKEN_PATH = r"D:\remaike.TV\token.json"
CLIENT_SECRET = r"D:\remaike.TV\config\client_secret.json"
REPORT_PATH = r"D:\remaike.TV\config\channel_perfection_report.json"

DRY_RUN = "--apply" not in sys.argv  # Default: dry run!

# Category rules
CATEGORY_MAP = {
    'soundies': 10,       # Music
    'wochenschau': 27,    # Education
    'ken_block': 2,       # Autos & Vehicles
    'nasa': 27,           # Education (space docs)
    'nuremberg': 27,      # Education (historical)
}
# Special overrides by video content (not series)
CATEGORY_OVERRIDES = {
    'NcfUWqlfSm0': 2,   # Getaway Stockholm = Autos
    'DO8dSN4aAB4': 27,  # Nuremberg Nazi Camps = Education
    '4vaim28zk50': 27,  # Nürnberger Nachfolgeprozesse = Education
    'sp1AzW-_rV0': 27,  # Skylab = Education (NASA doc)
    'ndAzCIUxo-c': 27,  # Skylab Gyroscopes = Education (NASA doc)
    'eF81rBeXbzk': 27,  # Hindenburg = Education
    'bhnnR0WX_X0': 1,   # Boxing Cats = Film & Animation
    'wAkUnHRxwT8': 24,  # Livestream = Entertainment
}

# ── MANUAL TITLE OVERRIDES (verified ≤70 chars) ──
TITLE_OVERRIDES = {
    'dCCl4JxrlF8': 'Betty Boop: Minnie the Moocher (1932) | 8K HQ',             # was 87 — drop (11/105) + junk
    'zouf8VMUeCo': 'Betty Boop: Out of the Inkwell (1938) | 8K HQ',              # was 87
    'xoCvBUIaqwg': 'Betty Boop: Pudgy the Watchman (1938) | 8K HQ',              # was 87
    'hvdNZy8AciI': 'Casper: True Boo (1952) | 8K HQ',                            # was 78
    'U-WD47NSgAE': 'Coca-Cola Christmas Trucks (1995) | 8K HQ',                  # was 83
    'WSjkAZkPbKs': 'Coca-Cola Christmas Trucks (1995) | EPIC | 8K HQ',           # was 83 — different version
    'dGD2CeoZX68': 'A Christmas Carol (1984) | George C. Scott | 8K HQ',         # was 82
    'yIQCHpjp4NE': 'Batman & Robin Meet Santa Claus (1966) | 8K HQ',             # was 83
    'EpzJcD6zkvs': 'Suzy Snowflake (1953) | Christmas Classic | 8K HQ',          # was 83
    'lxrwknLmRl4': 'Deleted Porky Pig Episode Restored to 8K | 8K HQ',           # was 71
    'YbC2JynVCRA': 'A Bill of Divorcement (1932) | Hepburn | 8K HQ',             # was 83
    'Ucub3igzk2U': "Dick Whittington's Cat (1935) | ComiColor | 8K HQ",          # was 83
    'MXE3TqsT2oE': 'Old Mother Hubbard (1935) | ComiColor | 8K HQ',             # was 83
    'Zu_iBCd5NJc': 'Biological Warfare: What You Should Know (1952) | 8K HQ',    # was 83
    '1yiNR69g0qA': 'My Girl Loves a Sailor | Soundie | 8K HQ',                   # was 71 — drop "Johnny Long Orchestr:"
    'fVp_aVBZhak': 'Gabby: King for a Day (1940) | Fleischer | 8K HQ',           # was 83
    'PzbAE96bG1Q': 'Hawaiian Birds (1936) | Fleischer Color Classic | 8K HQ',     # was 83
    '1mVWh_B6_00': 'Little Lambkins (1940) | Fleischer Color Classic | 8K HQ',   # was 83
    '3gzbxznJ_PM': 'Popeye Movie Marathon | 4K Fleischer Studios | 8K HQ',       # was 84
    '4VO2weDCfi0': 'The Little Stranger (1936) | Fleischer Classic | 8K HQ',     # was 80
}
DEFAULT_CAT = 1  # Film & Animation

# CTA Block
CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT
"""

# ──────────────────────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────────────────────
def get_youtube_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

# ──────────────────────────────────────────────────────────────
# PHASE 1: Live Scan
# ──────────────────────────────────────────────────────────────
def fetch_all_videos(youtube):
    """Fetch all video IDs from upload playlist, then get full details."""
    print("📡 Phase 1: Fetching ALL videos from YouTube...")
    
    # Step 1: Get all video IDs from upload playlist
    video_ids = []
    page_token = None
    while True:
        resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=UPLOAD_PLAYLIST,
            maxResults=50,
            pageToken=page_token
        ).execute()
        
        for item in resp.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    
    print(f"   Found {len(video_ids)} video IDs")
    
    # Step 2: Fetch full details in batches of 50
    all_videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part="snippet,status,contentDetails,localizations,statistics",
            id=",".join(batch)
        ).execute()
        all_videos.extend(resp.get('items', []))
        print(f"   Fetched {len(all_videos)}/{len(video_ids)} details...")
    
    print(f"   ✅ {len(all_videos)} videos fetched (READ cost: ~{len(video_ids)//50 + len(video_ids)//50 + 2} units)")
    return all_videos

# ──────────────────────────────────────────────────────────────
# SERIES DETECTION
# ──────────────────────────────────────────────────────────────
def detect_series(title, desc, tags_str):
    """Detect which series a video belongs to."""
    t = (title or '').lower()
    d = (desc or '').lower()
    tags = (tags_str or '').lower()
    
    if 'betty boop' in t or 'betty boop' in tags: return 'betty_boop'
    if 'alfred' in t and ('kwak' in t or 'quack' in t): return 'alfred_kwak'
    if 'wochenschau' in t or 'newsreel' in tags: return 'wochenschau'
    if 'soundie' in t or 'soundie' in tags: return 'soundies'
    if 'superman' in t and ('fleischer' in d or '194' in t): return 'superman'
    if 'felix' in t and 'cat' in t: return 'felix'
    if 'popeye' in t: return 'popeye'
    if 'casper' in t: return 'casper'
    if 'maulwurf' in t or 'krtek' in t or 'mole' in t: return 'maulwurf'
    if 'looney' in t or 'porky' in t or 'bugs bunny' in t or 'daffy' in t: return 'looney_tunes'
    if 'bravestarr' in t: return 'bravestarr'
    if 'ken block' in t or 'gymkhana' in t: return 'ken_block'
    if 'skylab' in t or 'nasa' in t: return 'nasa'
    if 'astro boy' in t: return 'astro_boy'
    if 'chaplin' in t or 'charlie chaplin' in d: return 'chaplin'
    if 'buster keaton' in t: return 'keaton'
    if 'teaserama' in t or 'bettie page' in t: return 'teaserama'
    if 'christmas' in t or 'xmas' in t or 'santa' in t or 'snowflake' in t: return 'christmas'
    if 'nürnberg' in t or 'nuremberg' in t: return 'nuremberg'
    if 'getaway' in t and 'stockholm' in t: return 'getaway'
    if 'hindenburg' in t: return 'wochenschau'
    if 'atomic bomb' in t or 'nuclear' in t: return 'wochenschau'
    return 'other'

# ──────────────────────────────────────────────────────────────
# PHASE 2: Audit
# ──────────────────────────────────────────────────────────────
def audit_video(video):
    """Audit a single video against ALL rules. Returns list of issues + fixes."""
    snippet = video['snippet']
    status = video['status']
    vid_id = video['id']
    
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    cat_id = snippet.get('categoryId', '1')
    localizations = video.get('localizations', {})
    made_for_kids = status.get('madeForKids', False)
    privacy = status.get('privacyStatus', 'private')
    
    if privacy != 'public':
        return [], {}
    
    series = detect_series(title, desc, ','.join(tags))
    issues = []
    fixes = {}  # What to change
    
    # R1: 8K or 4K in title
    if '8K' not in title and '4K' not in title:
        issues.append('R1_no_quality_marker')
        # Don't auto-fix title without more context
    
    # R2: No @remAIke_IT in title
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues.append('R2_handle_in_title')
        new_title = title.replace(' | @remAIke_IT', '').replace(' | @remAI...', '')
        new_title = re.sub(r'\s*\|\s*@remAIk?e?_?I?T?\s*\.{0,3}', '', new_title)
        new_title = re.sub(r'\s*@remAIke_IT\s*', ' ', new_title).strip()
        fixes['title'] = new_title
    
    # R3: Title ≤70 chars — use manual override if available
    current_title = fixes.get('title', title)
    if vid_id in TITLE_OVERRIDES:
        fixes['title'] = TITLE_OVERRIDES[vid_id]
        if len(current_title) > 70:
            issues.append(f'R3_title_too_long_{len(current_title)}')
    elif len(current_title) > 70:
        issues.append(f'R3_title_too_long_{len(current_title)}')
        shortened = shorten_title(current_title)
        if shortened != current_title:
            fixes['title'] = shortened
    
    # R4: CTA in description
    desc_lower = desc.lower()
    has_cta = any(w in desc_lower for w in ['subscribe', 'abonnieren', '👆', '💬', '🔔'])
    if not has_cta:
        issues.append('R4_no_cta')
        fixes['add_cta'] = True
    
    # R5: www.remaike.IT in description
    if 'remaike.it' not in desc_lower:
        issues.append('R5_no_website')
        fixes['add_links'] = True
    
    # R6: youtube.com/@remAIke_IT in description
    if '@remaike_it' not in desc_lower and 'youtube.com/@remaike' not in desc_lower:
        issues.append('R6_no_channel_link')
        fixes['add_links'] = True
    
    # R7: Max 5 hashtags
    hashtags = re.findall(r'#\w+', desc)
    if len(hashtags) > 5:
        issues.append(f'R7_too_many_hashtags_{len(hashtags)}')
        fixes['trim_hashtags'] = True
    
    # R8: Max 15 tags
    if len(tags) > 15:
        issues.append(f'R8_too_many_tags_{len(tags)}')
        fixes['trim_tags'] = True
    
    # R9: Category
    expected_cat = str(CATEGORY_OVERRIDES.get(vid_id, CATEGORY_MAP.get(series, DEFAULT_CAT)))
    if str(cat_id) != expected_cat:
        issues.append(f'R9_wrong_category_{cat_id}_should_be_{expected_cat}')
        fixes['categoryId'] = expected_cat
    
    # R10: sls artifacts
    if ' sls ' in title.lower() or '_sls_' in title.lower():
        issues.append('R10_sls_artifact')
    
    # R11: Description min length
    if len(desc.strip()) < 50:
        issues.append('R11_short_description')
    
    # R12: Localizations (min 5 languages)
    if len(localizations) < 5:
        issues.append(f'R12_low_i18n_{len(localizations)}_langs')
        # Don't auto-fix i18n here — needs per-video research
    
    # R13: madeForKids
    if made_for_kids:
        issues.append('R13_madeForKids_true')
        fixes['madeForKids'] = False
    
    return issues, fixes, series, {
        'title': title,
        'description': desc,
        'tags': tags,
        'categoryId': cat_id,
        'localizations': localizations,
        'privacy': privacy,
        'views': int(video.get('statistics', {}).get('viewCount', 0)),
    }


def shorten_title(title):
    """Intelligently shorten a title to ≤70 chars."""
    if len(title) <= 70:
        return title
    
    result = title
    
    # Remove common long suffixes (order matters — most specific first)
    cleanup_patterns = [
        r'\s*\|\s*8K HQ \(4K UHD\)\s*$',        # | 8K HQ (4K UHD)
        r'\s*\(4K UHD\)\s*$',                     # (4K UHD)
        r'\s*\|\s*Best Online Versio\.{3}\s*',     # | Best Online Versio...
        r'\s*\|\s*@remAIk?e?[^\|]{0,10}',          # | @remAI... (any variant)
        r'\s*\|\s*\.{3}\s*\|',                     # | ... |
        r'\s*\|\s*\.{3}\s*$',                      # | ... at end
        r'\s+\|\s+\|\s*',                          # || double pipes
    ]
    
    for pattern in cleanup_patterns:
        result = re.sub(pattern, '', result).strip()
    
    # Clean double spaces
    result = re.sub(r'\s{2,}', ' ', result).strip()
    result = result.rstrip(' |')
    
    # Ensure 8K HQ is at the end
    has_8k = '8K' in result or '4K' in result
    if not has_8k:
        if len(result) <= 62:
            result += ' | 8K HQ'
        elif len(result) <= 66:
            result += ' | 8K'
    
    # If already has 8K HQ somewhere in middle, move to end
    if '| 8K HQ' not in result and '| 8K' not in result and ('8K' in result or '4K' in result):
        pass  # Quality marker already present in content
    
    # If STILL too long, truncate content smartly
    if len(result) > 70:
        # Try removing everything after last |
        parts = result.rsplit('|', 1)
        if len(parts) > 1:
            core = parts[0].strip()
            if len(core) <= 62:
                result = core + ' | 8K HQ'
            elif len(core) <= 66:
                result = core + ' | 8K'
            else:
                result = core[:64] + '... | 8K'
        else:
            result = result[:64] + '... | 8K'
    
    return result


def trim_hashtags(desc, max_hashtags=5):
    """Keep only the best 5 hashtags in description."""
    # Find all hashtags
    all_hashtags = re.findall(r'#\w+', desc)
    if len(all_hashtags) <= max_hashtags:
        return desc
    
    # Priority hashtags to KEEP
    priority = ['#8K', '#PublicDomain', '#WWII', '#History', '#Wochenschau',
                '#BettyBoop', '#Superman', '#VintageAnimation', '#ClassicFilm',
                '#Soundie', '#Jazz', '#Swing', '#Popeye', '#FelixTheCat',
                '#AlfredJKwak', '#Krtek', '#Maulwurf', '#Casper', '#Animation',
                '#SilentFilm', '#VintageMusic', '#Newsreel', '#Education',
                '#KenBlock', '#Gymkhana', '#Christmas', '#NASA']
    
    # Score each hashtag
    keep = []
    for h in all_hashtags:
        if h in priority:
            keep.append(h)
    
    # Fill remaining from original order (non-priority)
    for h in all_hashtags:
        if h not in keep and len(keep) < max_hashtags:
            keep.append(h)
    
    keep = keep[:max_hashtags]
    
    # Remove ALL hashtags from desc
    clean_desc = desc
    for h in all_hashtags:
        clean_desc = clean_desc.replace(h, '')
    
    # Clean up multiple spaces/newlines left behind
    clean_desc = re.sub(r'\n\s*\n\s*\n', '\n\n', clean_desc).strip()
    
    # Add back the kept hashtags at the end
    clean_desc += '\n\n' + ' '.join(keep)
    
    return clean_desc


def ensure_links(desc):
    """Ensure www.remaike.IT and YouTube channel link are in description."""
    additions = []
    desc_lower = desc.lower()
    
    if 'remaike.it' not in desc_lower:
        additions.append('🌐 www.remaike.IT')
    if '@remaike_it' not in desc_lower and 'youtube.com/@remaike' not in desc_lower:
        additions.append('📺 https://www.youtube.com/@remAIke_IT')
    
    if additions:
        desc = desc.rstrip() + '\n\n' + '\n'.join(additions)
    
    return desc


def ensure_cta(desc):
    """Add CTA block if missing."""
    desc_lower = desc.lower()
    if any(w in desc_lower for w in ['subscribe', '👆', '🔔']):
        return desc
    
    # Insert CTA before hashtags if present, else at end
    hashtag_match = re.search(r'\n\s*#\w+', desc)
    if hashtag_match:
        pos = hashtag_match.start()
        desc = desc[:pos] + CTA_BLOCK + desc[pos:]
    else:
        desc = desc.rstrip() + CTA_BLOCK
    
    return desc


# ──────────────────────────────────────────────────────────────
# PHASE 3: Build Fix Plan
# ──────────────────────────────────────────────────────────────
def build_fix_plan(all_videos):
    """Audit every video and build the fix plan."""
    print("\n🔍 Phase 2: Auditing ALL videos against workspace rules...")
    
    results = {
        'clean': [],
        'needs_fix': [],
        'private': [],
        'issue_counts': {},
    }
    
    for video in all_videos:
        if video['status']['privacyStatus'] != 'public':
            results['private'].append(video['id'])
            continue
        
        issues, fixes, series, data = audit_video(video)
        
        if not issues:
            results['clean'].append(video['id'])
        else:
            results['needs_fix'].append({
                'id': video['id'],
                'title': data['title'],
                'series': series,
                'views': data['views'],
                'issues': issues,
                'fixes': fixes,
                'current_data': data,
            })
            for iss in issues:
                key = iss.split('_')[0] + '_' + iss.split('_')[1]
                results['issue_counts'][key] = results['issue_counts'].get(key, 0) + 1
    
    # Sort by issue severity (more issues first), then by views (high views first)
    results['needs_fix'].sort(key=lambda x: (-len(x['issues']), -x['views']))
    
    print(f"\n{'='*70}")
    print(f"📋 AUDIT RESULTS")
    print(f"{'='*70}")
    print(f"✅ Clean:     {len(results['clean'])}")
    print(f"⚠️  Needs fix: {len(results['needs_fix'])}")
    print(f"🔒 Private:   {len(results['private'])}")
    print(f"\nIssue breakdown:")
    for key, count in sorted(results['issue_counts'].items(), key=lambda x: -x[1]):
        print(f"   {key}: {count} videos")
    
    return results


# ──────────────────────────────────────────────────────────────
# PHASE 4: Apply Fixes  
# ──────────────────────────────────────────────────────────────
def apply_fixes(youtube, results):
    """Apply all fixes via YouTube API."""
    to_fix = results['needs_fix']
    
    # Filter to auto-fixable only (have actual fixes, not just warnings)
    fixable = [v for v in to_fix if v['fixes']]
    
    print(f"\n{'='*70}")
    print(f"🔧 Phase {'3 (DRY RUN)' if DRY_RUN else '4 (APPLYING FIXES)'}")
    print(f"{'='*70}")
    print(f"Fixable videos: {len(fixable)}")
    
    # Estimate quota
    quota = len(fixable) * 50
    print(f"Estimated quota: {quota} units ({len(fixable)} × 50)")
    
    if quota > 8000:
        print(f"⚠️  Would exceed safe quota limit! Processing first 150 videos.")
        fixable = fixable[:150]
    
    applied = []
    failed = []
    skipped = []
    
    for i, entry in enumerate(fixable):
        vid_id = entry['id']
        fixes = entry['fixes']
        current = entry['current_data']
        
        print(f"\n[{i+1}/{len(fixable)}] {vid_id}: {current['title'][:60]}")
        print(f"   Issues: {', '.join(entry['issues'])}")
        
        # Build the update body
        snippet = {'categoryId': fixes.get('categoryId', current['categoryId'])}
        status_body = {}
        
        # Title fix
        if 'title' in fixes:
            snippet['title'] = fixes['title']
            print(f"   📝 Title: {current['title'][:50]} → {fixes['title'][:50]}")
        else:
            snippet['title'] = current['title']
        
        # Description fixes
        new_desc = current['description']
        if fixes.get('trim_hashtags'):
            new_desc = trim_hashtags(new_desc, 5)
            print(f"   #️⃣  Trimmed hashtags to 5")
        if fixes.get('add_cta'):
            new_desc = ensure_cta(new_desc)
            print(f"   📢 Added CTA block")
        if fixes.get('add_links'):
            new_desc = ensure_links(new_desc)
            print(f"   🔗 Added missing links")
        
        snippet['description'] = new_desc
        
        # Tags fix
        if fixes.get('trim_tags'):
            snippet['tags'] = current['tags'][:15]
            print(f"   🏷️  Trimmed tags to 15")
        else:
            snippet['tags'] = current['tags']
        
        # Category fix
        if 'categoryId' in fixes:
            cat_from = current['categoryId']
            cat_to = fixes['categoryId']
            print(f"   📂 Category: {cat_from} → {cat_to}")
        
        # madeForKids fix
        if 'madeForKids' in fixes:
            status_body['madeForKids'] = fixes['madeForKids']
            print(f"   👶 madeForKids → false")
        
        if DRY_RUN:
            applied.append({
                'id': vid_id,
                'title': snippet.get('title', current['title']),
                'issues': entry['issues'],
                'fixes_applied': list(fixes.keys()),
            })
            continue
        
        # APPLY!
        try:
            body = {
                'id': vid_id,
                'snippet': snippet,
            }
            if status_body:
                body['status'] = status_body
            
            parts = ['snippet']
            if status_body:
                parts.append('status')
            
            youtube.videos().update(
                part=','.join(parts),
                body=body
            ).execute()
            
            applied.append({
                'id': vid_id,
                'title': snippet.get('title', current['title']),
                'issues': entry['issues'],
                'fixes_applied': list(fixes.keys()),
            })
            print(f"   ✅ Fixed!")
            time.sleep(1.2)  # Rate limiting
            
        except Exception as e:
            err_msg = str(e)
            print(f"   ❌ Error: {err_msg[:100]}")
            failed.append({'id': vid_id, 'error': err_msg[:200]})
            
            if 'quota' in err_msg.lower():
                print("\n🛑 QUOTA EXCEEDED — Stopping immediately!")
                for remaining in fixable[i+1:]:
                    skipped.append(remaining['id'])
                break
    
    return applied, failed, skipped


# ──────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────
def main():
    print("═" * 70)
    print("🎯 CHANNEL PERFECTION ENGINE v1.0")
    print(f"   Mode: {'DRY RUN (preview only)' if DRY_RUN else '🔴 LIVE — APPLYING FIXES!'}")
    print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("═" * 70)
    
    youtube = get_youtube_service()
    
    # Phase 1: Fetch
    all_videos = fetch_all_videos(youtube)
    
    # Phase 2+3: Audit + Plan
    results = build_fix_plan(all_videos)
    
    # Phase 4: Apply
    applied, failed, skipped = apply_fixes(youtube, results)
    
    # Final Report
    print(f"\n{'═'*70}")
    print(f"📊 FINAL REPORT")
    print(f"{'═'*70}")
    print(f"{'DRY RUN — No changes made!' if DRY_RUN else 'CHANGES APPLIED!'}")
    print(f"✅ Fixed:   {len(applied)}")
    print(f"❌ Failed:  {len(failed)}")
    print(f"⏭️  Skipped: {len(skipped)}")
    print(f"Quota used: {'~0 (dry run)' if DRY_RUN else f'~{len(applied) * 50} units'}")
    
    # Issues still needing manual attention
    manual = [v for v in results['needs_fix'] if not v['fixes']]
    if manual:
        print(f"\n⚠️  {len(manual)} videos need MANUAL review (no auto-fix possible):")
        for v in manual[:10]:
            print(f"   - {v['title'][:60]}")
            print(f"     Issues: {', '.join(v['issues'])}")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'dry_run' if DRY_RUN else 'applied',
        'total_videos': len(all_videos),
        'clean': len(results['clean']),
        'needs_fix': len(results['needs_fix']),
        'private': len(results['private']),
        'issue_breakdown': results['issue_counts'],
        'fixed': applied,
        'failed': failed,
        'skipped': skipped,
        'manual_review': [{'id': v['id'], 'title': v['title'], 'issues': v['issues']} 
                          for v in manual],
    }
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Report: {REPORT_PATH}")
    
    if DRY_RUN and applied:
        print(f"\n💡 To apply fixes, run: python channel_perfection.py --apply")


if __name__ == '__main__':
    main()
