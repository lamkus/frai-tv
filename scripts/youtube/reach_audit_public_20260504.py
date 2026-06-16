#!/usr/bin/env python3
"""
Reach Audit 2026-05-04 (PUBLIC API version).
READ-ONLY scan via API key — no OAuth required.

Checks for ALL public Wochenschau videos:
- 4K + 8K keywords in title
- defaultAudioLanguage / defaultLanguage
- localizations (multi-language metadata)
- description first 2 lines (AEO/snippet quality)
- caption flag (audio/transcript search signal)
- frai.tv + remaike.IT external authority links
- GEO location signals in description
- category 27 (Education)
- tags count

Quota: ~30 read units total.

Setup:
  $env:YOUTUBE_API_KEY='your-api-key'
  python scripts\\youtube\\reach_audit_public_20260504.py
"""
import json
import os
import re
import sys
import requests

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    print("ERROR: YOUTUBE_API_KEY env var not set!")
    print("Set it with: $env:YOUTUBE_API_KEY='your-key-here'")
    sys.exit(1)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
BASE = 'https://youtube.googleapis.com/youtube/v3'
NEWSREEL_RE = re.compile(
    r'^(wochenschau|deutsche\s+wochenschau|german\s+(wwii\s+)?newsreel|newsreel\s+\d+|ufa\s+sound\s+newsreel)',
    re.IGNORECASE,
)

def list_all_uploads():
    """Get all video IDs from upload playlist (PUBLIC videos only via Public API)."""
    ids = []
    token = None
    while True:
        params = {
            'part': 'contentDetails',
            'playlistId': UPLOAD_PL,
            'maxResults': 50,
            'key': API_KEY,
        }
        if token:
            params['pageToken'] = token
        r = requests.get(f'{BASE}/playlistItems', params=params, timeout=30)
        r.raise_for_status()
        d = r.json()
        for it in d.get('items', []):
            ids.append(it['contentDetails']['videoId'])
        token = d.get('nextPageToken')
        if not token:
            break
    return ids

def get_videos_full(ids):
    """Fetch full metadata for video IDs in batches of 50."""
    out = []
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        params = {
            'part': 'snippet,status,localizations,contentDetails,statistics',
            'id': ','.join(batch),
            'key': API_KEY,
        }
        r = requests.get(f'{BASE}/videos', params=params, timeout=30)
        r.raise_for_status()
        out.extend(r.json().get('items', []))
    return out

def main():
    print("=" * 70)
    print("  REACH AUDIT 2026-05-04 (Public API)")
    print("=" * 70)
    print()

    print("Fetching all upload IDs...")
    all_ids = list_all_uploads()
    print(f"  Total public videos: {len(all_ids)}")

    print("Fetching full metadata...")
    all_videos = get_videos_full(all_ids)
    print(f"  Fetched: {len(all_videos)}")

    # Filter Wochenschau/newsreel variants (current channel uses several public title patterns)
    ws_videos = [v for v in all_videos if NEWSREEL_RE.search(v['snippet'].get('title', ''))]
    print(f"  Wochenschau public videos: {len(ws_videos)}")

    # Filter all (we also audit non-Wochenschau for completeness)
    print()

    # Audit
    issues = {
        'missing_4k_keyword': [],
        'missing_8k_keyword': [],
        'no_default_language': [],
        'no_default_audio_language': [],
        'wrong_default_audio_lang_en_for_de_content': [],
        'missing_caption_signal': [],
        'no_localizations': [],
        'only_de_localization': [],
        'missing_en_localization': [],
        'missing_global_market_localizations': [],
        'desc_line1_repeats_title': [],
        'desc_line1_not_aeo_optimized': [],
        'missing_frai_tv_link': [],
        'missing_frai_watch_deeplink': [],
        'missing_remaike_it_link': [],
        'missing_youtube_channel_link': [],
        'missing_geo_location_signal': [],
        'wrong_category': [],
        'too_few_tags': [],
    }

    full_audit = []

    for v in ws_videos:
        sn = v['snippet']
        st = v['status']
        title = sn.get('title', '')
        desc = sn.get('description', '')
        tags = sn.get('tags', [])
        cat = sn.get('categoryId', '')
        default_lang = sn.get('defaultLanguage')
        default_audio_lang = sn.get('defaultAudioLanguage')
        localizations = v.get('localizations', {})
        privacy = st.get('privacyStatus', 'unknown')
        stats = v.get('statistics', {})
        content_details = v.get('contentDetails', {})
        views = int(stats.get('viewCount', 0))

        vid_id = v['id']
        desc_lower = desc.lower()
        has_4k = bool(re.search(r'\b4K\b', title, re.IGNORECASE))
        has_8k = bool(re.search(r'\b8K\b', title, re.IGNORECASE))
        desc_line1 = desc.split('\n')[0].strip()
        desc_line2 = desc.split('\n')[1].strip() if len(desc.split('\n')) > 1 else ''
        first_two = f'{desc_line1} {desc_line2}'.lower()
        # Check if line 1 just repeats title
        title_words_in_line1 = title.lower()[:25] in desc_line1.lower()
        aeo_terms = ['german', 'newsreel', 'wwii', 'world war', 'remastered', 'restored', '8k', '4k', 'historical']
        aeo_hits = sum(1 for term in aeo_terms if term in first_two)
        has_caption_signal = content_details.get('caption') == 'true'
        loc_langs = set(localizations.keys())
        global_markets = {'en', 'es', 'pt', 'hi', 'id'}

        record = {
            'videoId': vid_id,
            'title': title,
            'privacy': privacy,
            'views': views,
            'has_4k_in_title': has_4k,
            'has_8k_in_title': has_8k,
            'category': cat,
            'tags_count': len(tags),
            'default_lang': default_lang,
            'default_audio_lang': default_audio_lang,
            'caption_flag': content_details.get('caption'),
            'has_caption_signal': has_caption_signal,
            'localizations_count': len(localizations),
            'localizations_langs': sorted(localizations.keys()),
            'desc_line1': desc_line1[:120],
            'desc_line1_repeats_title': title_words_in_line1,
            'aeo_hits_first_two_lines': aeo_hits,
            'has_frai_tv_link': 'frai.tv' in desc_lower,
            'has_frai_watch_deeplink': f'frai.tv/watch/{vid_id.lower()}' in desc_lower or f'frai.tv/watch/{vid_id}' in desc,
            'has_remaike_it_link': 'remaike.it' in desc_lower,
            'has_youtube_channel_link': 'youtube.com/@remaike_it' in desc_lower,
            'has_geo_location_signal': any(marker in desc for marker in ['📍', 'Ort:', 'Location:', 'Ubicación:']),
        }
        full_audit.append(record)

        if not has_4k:
            issues['missing_4k_keyword'].append(vid_id)
        if not has_8k:
            issues['missing_8k_keyword'].append(vid_id)
        if not default_lang:
            issues['no_default_language'].append(vid_id)
        if not default_audio_lang:
            issues['no_default_audio_language'].append(vid_id)
        elif default_audio_lang.startswith('en'):
            # All Wochenschau is German narration - if marked 'en', that's wrong
            issues['wrong_default_audio_lang_en_for_de_content'].append(vid_id)
        if not has_caption_signal:
            issues['missing_caption_signal'].append(vid_id)
        if not localizations:
            issues['no_localizations'].append(vid_id)
        elif sorted(localizations.keys()) == ['de']:
            issues['only_de_localization'].append(vid_id)
        if 'en' not in localizations:
            issues['missing_en_localization'].append(vid_id)
        missing_market_locs = sorted(global_markets - loc_langs)
        if missing_market_locs:
            issues['missing_global_market_localizations'].append({'id': vid_id, 'missing': missing_market_locs})
        if title_words_in_line1:
            issues['desc_line1_repeats_title'].append(vid_id)
        if aeo_hits < 4 or 'http' in first_two:
            issues['desc_line1_not_aeo_optimized'].append({'id': vid_id, 'hits': aeo_hits})
        if 'frai.tv' not in desc_lower:
            issues['missing_frai_tv_link'].append(vid_id)
        if not (f'frai.tv/watch/{vid_id.lower()}' in desc_lower or f'frai.tv/watch/{vid_id}' in desc):
            issues['missing_frai_watch_deeplink'].append(vid_id)
        if 'remaike.it' not in desc_lower:
            issues['missing_remaike_it_link'].append(vid_id)
        if 'youtube.com/@remaike_it' not in desc_lower:
            issues['missing_youtube_channel_link'].append(vid_id)
        if not any(marker in desc for marker in ['📍', 'Ort:', 'Location:', 'Ubicación:']):
            issues['missing_geo_location_signal'].append(vid_id)
        if cat != '27':
            issues['wrong_category'].append({'id': vid_id, 'cat': cat})
        if len(tags) < 10:
            issues['too_few_tags'].append({'id': vid_id, 'count': len(tags)})

    print("=" * 70)
    print("  REACH AUDIT RESULTS - Wochenschau (Public Videos)")
    print("=" * 70)
    print(f"\n  Total Wochenschau videos analyzed: {len(ws_videos)}\n")
    for issue_type, items in issues.items():
        count = len(items)
        pct = (count / len(ws_videos) * 100) if ws_videos else 0
        marker = "🚨" if pct > 50 else ("⚠️ " if pct > 20 else "✅")
        print(f"  {marker} {issue_type}: {count} ({pct:.0f}%)")
    print()

    # Top performers vs underperformers
    sorted_by_views = sorted(full_audit, key=lambda x: x['views'], reverse=True)
    print("  TOP 5 by views:")
    for v in sorted_by_views[:5]:
        print(f"    {v['views']:>6} | {v['title'][:60]}")
    print()
    print("  BOTTOM 5 by views (most likely losing reach):")
    for v in sorted_by_views[-5:]:
        print(f"    {v['views']:>6} | {v['title'][:60]}")
    print()

    # Save
    out = {
        'audit_date': '2026-05-04',
        'method': 'public_api',
        'total_channel_videos': len(all_videos),
        'wochenschau_count': len(ws_videos),
        'issues_summary': {k: len(v) for k, v in issues.items()},
        'issues_detail': issues,
        'full_audit': full_audit,
    }
    out_path = 'config/reach_audit_20260504.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"  Saved: {out_path}")
    print(f"  Quota used: ~{len(all_ids)//50 + 10} read units")

if __name__ == '__main__':
    main()
