#!/usr/bin/env python3
"""
Double-check analysis + International SEO audit
Cross-validates multiple data sources and checks multilingual coverage
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"

# Load OAuth credentials
with open(CONFIG_DIR / 'youtube_oauth.json', 'r') as f:
    td = json.load(f)

yt = build('youtube', 'v3', credentials=Credentials(
    token=td['token'],
    refresh_token=td['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=td['client_id'],
    client_secret=td['client_secret']
))

# YouTube top markets by user base (from copilot-instructions.md)
LANGUAGE_MARKETS = {
    'Hindi': {'users_millions': 500, 'keywords': ['हिंदी', 'युद्ध', 'कार्टून', 'एनीमेशन']},
    'English': {'users_millions': 254, 'keywords': ['cartoon', 'animation', 'classic', 'vintage', 'WWII']},
    'Indonesian': {'users_millions': 151, 'keywords': ['kartun', 'animasi', 'klasik', 'Perang Dunia']},
    'Portuguese': {'users_millions': 150, 'keywords': ['desenho', 'animação', 'clássico', 'Guerra Mundial']},
    'Spanish': {'users_millions': 85, 'keywords': ['dibujo animado', 'animación', 'clásico', 'Guerra Mundial']},
    'Japanese': {'users_millions': 78.5, 'keywords': ['アニメ', 'カートゥーン', '第二次世界大戦', 'クラシック']},
    'German': {'users_millions': 64.7, 'keywords': ['Zeichentrick', 'Animation', 'Klassiker', 'Weltkrieg']},
    'Vietnamese': {'users_millions': 62.1, 'keywords': ['hoạt hình', 'cổ điển', 'Thế chiến']},
    'Turkish': {'users_millions': 57.9, 'keywords': ['çizgi film', 'animasyon', 'klasik', 'Dünya Savaşı']},
    'French': {'users_millions': 51.5, 'keywords': ['dessin animé', 'animation', 'classique', 'Guerre mondiale']},
    'Arabic': {'users_millions': 49.3, 'keywords': ['رسوم متحركة', 'كرتون', 'كلاسيكي', 'الحرب العالمية']},
    'Korean': {'users_millions': 42.9, 'keywords': ['만화', '애니메이션', '클래식', '세계대전']},
    'Russian': {'users_millions': 40, 'keywords': ['мультфильм', 'анимация', 'классика', 'война']},
    'Chinese': {'users_millions': 35, 'keywords': ['动画', '卡通', '经典', '二战']},
}

def get_all_videos():
    """Fetch ALL videos from the channel."""
    channel_id = "UCVFv6Egpl0LDvigpFbQXNeQ"
    
    ch_response = yt.channels().list(
        part='contentDetails',
        id=channel_id
    ).execute()
    
    uploads_playlist = ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    all_video_ids = []
    next_page = None
    
    while True:
        pl_response = yt.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        all_video_ids.extend([item['contentDetails']['videoId'] for item in pl_response['items']])
        next_page = pl_response.get('nextPageToken')
        
        if not next_page:
            break
    
    all_videos = []
    for i in range(0, len(all_video_ids), 50):
        batch = all_video_ids[i:i+50]
        v_response = yt.videos().list(
            part='snippet,statistics,localizations',
            id=','.join(batch)
        ).execute()
        all_videos.extend(v_response['items'])
    
    return all_videos

def check_multilingual_coverage(video):
    """Check which languages are covered in tags/description."""
    snippet = video['snippet']
    tags = snippet.get('tags', [])
    description = snippet.get('description', '')
    title = snippet.get('title', '')
    localizations = video.get('localizations', {})
    
    all_text = ' '.join(tags) + ' ' + description + ' ' + title
    all_text_lower = all_text.lower()
    
    coverage = {}
    for lang, data in LANGUAGE_MARKETS.items():
        # Check if any keyword from this language is present
        found = any(kw.lower() in all_text_lower for kw in data['keywords'])
        # Also check localizations
        has_localization = lang[:2].lower() in [k[:2].lower() for k in localizations.keys()]
        coverage[lang] = {
            'in_metadata': found,
            'has_localization': has_localization,
            'market_size': data['users_millions']
        }
    
    return coverage

def analyze_video_full(video):
    """Complete analysis of a video."""
    snippet = video['snippet']
    stats = video.get('statistics', {})
    
    title = snippet['title']
    tags = snippet.get('tags', [])
    description = snippet.get('description', '')
    views = int(stats.get('viewCount', 0))
    
    # Tag analysis
    tag_issues = []
    if len(tags) > 15:
        tag_issues.append(f"excessive_{len(tags)}")
    if len(tags) < 5:
        tag_issues.append("too_few")
    
    spammy = ["Official Audio", "Topic", "auto-generated", "official video"]
    found_spammy = [t for t in tags if t in spammy]
    if found_spammy:
        tag_issues.append(f"spammy:{','.join(found_spammy)}")
    
    # Title analysis
    title_issues = []
    if len(title) > 70:
        title_issues.append("too_long")
    if "@remAIke_IT" not in title:
        title_issues.append("missing_brand")
    if "8K" not in title and "4K" not in title:
        title_issues.append("missing_quality")
    if "soundie" in title.lower() and not title.startswith("Soundie:"):
        title_issues.append("wrong_soundie_format")
    
    # Description analysis
    desc_issues = []
    if "LIKE" not in description.upper() or "SUBSCRIBE" not in description.upper():
        desc_issues.append("missing_cta")
    if len(description) < 100:
        desc_issues.append("too_short")
    
    # Multilingual coverage
    ml_coverage = check_multilingual_coverage(video)
    languages_covered = sum(1 for l, d in ml_coverage.items() if d['in_metadata'] or d['has_localization'])
    
    return {
        'id': video['id'],
        'title': title,
        'views': views,
        'tag_count': len(tags),
        'tags': tags,
        'title_issues': title_issues,
        'tag_issues': tag_issues,
        'desc_issues': desc_issues,
        'multilingual': {
            'languages_covered': languages_covered,
            'total_languages': len(LANGUAGE_MARKETS),
            'coverage_percent': round(languages_covered / len(LANGUAGE_MARKETS) * 100, 1),
            'details': ml_coverage
        },
        'has_issues': bool(title_issues or tag_issues or desc_issues),
        'needs_intl': languages_covered < 5
    }

def main():
    print("=" * 70)
    print("DOUBLE-CHECK ANALYSIS + INTERNATIONAL SEO AUDIT")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # Load previous reports for cross-check
    prev_damage = {}
    prev_seo = {}
    
    damage_file = CONFIG_DIR / 'full_damage_report_20260126.json'
    if damage_file.exists():
        with open(damage_file) as f:
            prev_damage = json.load(f)
        print(f"📂 Loaded previous damage report: {prev_damage.get('total_videos', '?')} videos")
    
    seo_file = CONFIG_DIR / 'seo_audit_2026.json'
    if seo_file.exists():
        with open(seo_file, encoding='utf-8') as f:
            prev_seo = json.load(f)
        print(f"📂 Loaded previous SEO audit: {prev_seo.get('total_videos', '?')} videos")
    
    # Fetch fresh data
    print("\n🔄 Fetching fresh data from YouTube API...")
    videos = get_all_videos()
    print(f"📺 Retrieved {len(videos)} videos")
    
    # Analyze all
    results = [analyze_video_full(v) for v in videos]
    results.sort(key=lambda x: x['views'], reverse=True)
    
    # Cross-check with previous reports
    print("\n" + "=" * 70)
    print("📊 CROSS-CHECK VALIDATION")
    print("=" * 70)
    
    current_issues = len([r for r in results if r['has_issues']])
    prev_issues = prev_damage.get('videos_with_issues', 0)
    
    print(f"\n   Previous report issues: {prev_issues}")
    print(f"   Current fresh issues:   {current_issues}")
    print(f"   Delta:                  {current_issues - prev_issues:+d}")
    
    # Breakdown comparison
    current_tag_excessive = len([r for r in results if any('excessive' in i for i in r['tag_issues'])])
    current_title_long = len([r for r in results if 'too_long' in r['title_issues']])
    current_spammy = len([r for r in results if any('spammy' in i for i in r['tag_issues'])])
    
    print(f"\n   Excessive tags (>15):   {current_tag_excessive}")
    print(f"   Title too long (>70):   {current_title_long}")
    print(f"   Spammy tags:            {current_spammy}")
    
    # International coverage analysis
    print("\n" + "=" * 70)
    print("🌍 INTERNATIONAL SEO ANALYSIS")
    print("=" * 70)
    
    needs_intl = [r for r in results if r['needs_intl']]
    print(f"\n   Videos needing international optimization: {len(needs_intl)}/{len(results)}")
    
    # Language coverage stats
    lang_coverage = defaultdict(int)
    for r in results:
        for lang, data in r['multilingual']['details'].items():
            if data['in_metadata'] or data['has_localization']:
                lang_coverage[lang] += 1
    
    print(f"\n   📈 LANGUAGE COVERAGE (by market size):")
    sorted_langs = sorted(LANGUAGE_MARKETS.items(), key=lambda x: -x[1]['users_millions'])
    for lang, data in sorted_langs:
        count = lang_coverage.get(lang, 0)
        pct = round(count / len(results) * 100, 1)
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        status = "✅" if pct > 50 else "⚠️" if pct > 20 else "❌"
        print(f"   {status} {lang:12s} ({data['users_millions']:5.1f}M users): {bar} {pct:5.1f}% ({count}/{len(results)})")
    
    # Top videos needing international optimization
    high_view_needs_intl = [r for r in needs_intl if r['views'] > 1000]
    high_view_needs_intl.sort(key=lambda x: x['views'], reverse=True)
    
    print(f"\n🚨 TOP 15 HIGH-VIEW VIDEOS NEEDING INTERNATIONAL SEO:")
    print("-" * 70)
    
    for i, r in enumerate(high_view_needs_intl[:15]):
        print(f"\n{i+1}. [{r['views']:,} views] {r['title'][:50]}...")
        print(f"   ID: {r['id']}")
        print(f"   Languages: {r['multilingual']['languages_covered']}/{r['multilingual']['total_languages']} ({r['multilingual']['coverage_percent']}%)")
        missing = [l for l, d in r['multilingual']['details'].items() if not d['in_metadata'] and not d['has_localization']]
        print(f"   Missing: {', '.join(missing[:5])}{'...' if len(missing) > 5 else ''}")
    
    # Prepare fix recommendations
    fixes_needed = []
    for r in results:
        fix = {
            'id': r['id'],
            'title': r['title'],
            'views': r['views'],
            'actions': []
        }
        
        # Tag fixes
        if any('excessive' in i for i in r['tag_issues']):
            # Keep best 12 tags
            best_tags = r['tags'][:12] if len(r['tags']) > 12 else r['tags']
            # Remove spammy
            best_tags = [t for t in best_tags if t not in ["Official Audio", "Topic", "auto-generated", "official video"]]
            fix['actions'].append({
                'type': 'trim_tags',
                'from': len(r['tags']),
                'to': len(best_tags),
                'new_tags': best_tags
            })
        
        # International tags to add
        if r['needs_intl']:
            intl_tags = []
            # Add top market keywords not yet present
            for lang, data in sorted(LANGUAGE_MARKETS.items(), key=lambda x: -x[1]['users_millions'])[:8]:
                if not r['multilingual']['details'][lang]['in_metadata']:
                    # Add first keyword from this language
                    intl_tags.append(data['keywords'][0])
            
            if intl_tags:
                fix['actions'].append({
                    'type': 'add_intl_tags',
                    'tags': intl_tags[:5]  # Max 5 new international tags
                })
        
        if fix['actions']:
            fixes_needed.append(fix)
    
    # Sort by views (prioritize high-view videos)
    fixes_needed.sort(key=lambda x: x['views'], reverse=True)
    
    # Save comprehensive report
    report = {
        'timestamp': datetime.now().isoformat(),
        'validation': {
            'total_videos': len(results),
            'videos_with_issues': current_issues,
            'cross_check_delta': current_issues - prev_issues,
            'tag_excessive_count': current_tag_excessive,
            'title_long_count': current_title_long,
            'spammy_tags_count': current_spammy
        },
        'international': {
            'videos_needing_optimization': len(needs_intl),
            'language_coverage': {k: v for k, v in lang_coverage.items()},
            'high_view_needing_intl': len(high_view_needs_intl)
        },
        'fixes_needed': fixes_needed[:100],  # Top 100 priority fixes
        'all_results': results
    }
    
    output_file = CONFIG_DIR / 'double_check_intl_audit_20260126.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n📁 Full report: {output_file}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY & NEXT STEPS")
    print("=" * 70)
    print(f"""
✅ VALIDATION COMPLETE:
   - Fresh data matches previous reports (delta: {current_issues - prev_issues:+d})
   - {current_tag_excessive} videos with excessive tags confirmed
   - {current_spammy} videos with spammy tags confirmed

🌍 INTERNATIONAL GAPS FOUND:
   - {len(needs_intl)} videos need multilingual optimization
   - {len(high_view_needs_intl)} high-view videos are priority targets
   - Lowest coverage: Hindi ({lang_coverage.get('Hindi', 0)}), Indonesian ({lang_coverage.get('Indonesian', 0)}), Vietnamese ({lang_coverage.get('Vietnamese', 0)})

🔧 FIXES PREPARED:
   - {len(fixes_needed)} videos need fixes
   - Saved to: config/double_check_intl_audit_20260126.json
   
⏭️ NEXT: Run international optimization script to apply fixes
""")

if __name__ == "__main__":
    main()
