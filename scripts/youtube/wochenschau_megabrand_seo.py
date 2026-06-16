#!/usr/bin/env python3
"""
wochenschau_megabrand_seo.py — Mega-Brand SEO Update for ALL Wochenschau Videos

Adds to EVERY Wochenschau description:
1. frai.tv watch link (cross-promotion)
2. remAIke.IT brand link
3. Location-specific data from wochenschau_complete_locations.json
4. Multilingual search keywords (EN/DE/ES/PT/HI/ID)
5. Proper YouTube channel link

Also generates a JSON file for descriptions of ALL channel videos (not just Wochenschau)
that need frai.tv / remaike.IT cross-promotion added.

Usage:
    python wochenschau_megabrand_seo.py --dry-run      # Preview changes
    python wochenschau_megabrand_seo.py --apply         # Apply changes (uses quota!)
    python wochenschau_megabrand_seo.py --generate-all  # Generate JSON for all videos

Quota: 1 unit per videos.list + 50 units per videos.update
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime

API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'
UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# ── Load location data ──
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR))

LOCATIONS_FILE = os.path.join(ROOT_DIR, 'config', 'wochenschau_complete_locations.json')
EVENTS_FILE = os.path.join(ROOT_DIR, 'config', 'wochenschau_events.json')
SCAN_FILE = os.path.join(ROOT_DIR, 'config', 'channel_scan_2026_02_13.json')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

locations = load_json(LOCATIONS_FILE)
events = load_json(EVENTS_FILE)
scan_data = load_json(SCAN_FILE)

# ── Extract wNum from title ──
import re
def extract_wnum(title):
    m = re.search(r'Wochenschau\s+(\d{3})', title, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r'wochenschau\s*nr\.?\s*(\d{3})', title, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None

# ── Mega-Brand Footer (added to every description) ──
MEGA_BRAND_FOOTER = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT — AI Video Restoration
📺 https://frai.tv — FREE AI Enhanced TV (All Videos Organized)
▶️ https://www.youtube.com/@remAIke_IT
"""

# ── Wochenschau Multilingual SEO Block ──
def wochenschau_seo_block(wnum, title_en, title_de, location, date_str):
    return f"""
🔍 SEARCH / SUCHE / BÚSQUEDA / PESQUISA:
🇬🇧 German WWII Newsreel Nr. {wnum} | {title_en} | {location} | {date_str}
🇩🇪 Deutsche Wochenschau Nr. {wnum} | {title_de} | {location} | {date_str}
🇪🇸 Noticiario alemán WWII Nr. {wnum} | Segunda Guerra Mundial | {location}
🇧🇷 Cinejornal alemão WWII Nr. {wnum} | Segunda Guerra Mundial | {location}
🇮🇳 जर्मन WWII न्यूज़रील Nr. {wnum} | द्वितीय विश्व युद्ध | {location}
🇮🇩 Berita Jerman WWII Nr. {wnum} | Perang Dunia II | {location}

📍 Location: {location}
📅 Date: {date_str}
"""

def wochenschau_frai_link(video_id):
    return f"🎬 Watch organized on frai.tv: https://frai.tv/watch/{video_id}\n"

# ── Build updated description ──
def build_wochenschau_description(video_id, current_desc, wnum):
    """Build enhanced Wochenschau description with mega-brand + geo + multilingual SEO."""
    
    # Get location/event data
    wnum_str = str(wnum)
    loc_data = locations.get(wnum_str, {})
    evt_data = events.get(wnum_str, {}) if isinstance(events, dict) else {}
    
    # For list-based events file
    if isinstance(events, list):
        for e in events:
            if e.get('nr') == wnum or e.get('wNum') == wnum:
                evt_data = e
                break
    
    location = loc_data.get('loc', loc_data.get('location', 'Europe'))
    date_str = loc_data.get('date', evt_data.get('date', ''))
    title_en = loc_data.get('en', evt_data.get('en', ''))
    title_de = loc_data.get('de', evt_data.get('de', ''))
    
    # Check if mega-brand links already present
    has_frai = 'frai.tv' in current_desc
    has_remaike = 'remaike.IT' in current_desc.lower() or 'remaike.it' in current_desc
    has_multilingual = 'BÚSQUEDA' in current_desc or 'PESQUISA' in current_desc
    has_location_tag = f'📍 Location: {location}' in current_desc
    
    # Start with current description
    desc = current_desc.rstrip()
    
    additions = []
    
    # Add frai.tv link if missing
    if not has_frai:
        additions.append(wochenschau_frai_link(video_id))
    
    # Add multilingual SEO block if missing
    if not has_multilingual and title_en and title_de:
        additions.append(wochenschau_seo_block(wnum, title_en, title_de, location, date_str))
    
    # Add mega-brand footer if missing
    if not has_frai or not has_remaike:
        additions.append(MEGA_BRAND_FOOTER)
    
    # Add hashtags if missing
    if '#Wochenschau' not in desc:
        additions.append('\n#Wochenschau #WWII #8K #History #PublicDomain')
    
    if additions:
        desc = desc + '\n' + '\n'.join(additions)
    
    # Trim to YouTube's 5000 char limit
    if len(desc) > 5000:
        desc = desc[:4990] + '...'
    
    return desc


def build_generic_brand_footer(video_id, current_desc, cat='other'):
    """Add mega-brand footer to any non-Wochenschau video description."""
    desc = current_desc.rstrip()
    
    additions = []
    
    if 'frai.tv' not in desc:
        additions.append(f'\n🎬 Watch organized on frai.tv: https://frai.tv/watch/{video_id}')
    
    if 'remaike.IT' not in desc.lower() and 'remaike.it' not in desc:
        additions.append(MEGA_BRAND_FOOTER)
    
    if additions:
        desc = desc + '\n'.join(additions)
    
    if len(desc) > 5000:
        desc = desc[:4990] + '...'
    
    return desc


# ── YouTube API Functions ──
def get_video_details(video_ids):
    """Fetch video details using Public API (1 unit per 50 videos)."""
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = requests.get(
            'https://youtube.googleapis.com/youtube/v3/videos',
            params={
                'part': 'snippet',
                'id': ','.join(batch),
                'key': API_KEY,
            }
        )
        if resp.status_code != 200:
            print(f"❌ API Error {resp.status_code}: {resp.text[:200]}")
            break
        data = resp.json()
        results.extend(data.get('items', []))
    return results


def update_video_description(video_id, new_description, credentials):
    """Update video description via OAuth (50 units per call)."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # First get current snippet
    resp = youtube.videos().list(part='snippet', id=video_id).execute()
    if not resp.get('items'):
        return False
    
    snippet = resp['items'][0]['snippet']
    snippet['description'] = new_description
    
    youtube.videos().update(
        part='snippet',
        body={'id': video_id, 'snippet': snippet}
    ).execute()
    return True


def load_oauth_credentials():
    """Load OAuth credentials from token.json."""
    token_path = os.path.join(ROOT_DIR, 'token.json')
    if not os.path.exists(token_path):
        print(f"❌ OAuth token not found: {token_path}")
        sys.exit(1)
    
    from google.oauth2.credentials import Credentials
    creds = Credentials.from_authorized_user_file(token_path)
    return creds


# ── Main ──
def main():
    parser = argparse.ArgumentParser(description='Wochenschau Mega-Brand SEO Update')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without applying')
    parser.add_argument('--apply', action='store_true', help='Apply changes (uses YouTube API quota)')
    parser.add_argument('--generate-all', action='store_true', help='Generate JSON for ALL videos needing brand updates')
    parser.add_argument('--limit', type=int, default=59, help='Max videos to process')
    args = parser.parse_args()
    
    if not API_KEY:
        print("❌ YOUTUBE_API_KEY not set!")
        sys.exit(1)
    
    # Load channel scan data
    videos = scan_data.get('videos', scan_data) if isinstance(scan_data, dict) else scan_data
    if isinstance(videos, dict) and 'items' in videos:
        videos = videos['items']
    
    # Find Wochenschau videos
    wochenschau_videos = []
    all_videos = []
    
    for v in videos:
        vid = v if isinstance(v, dict) else {}
        title = vid.get('title', '')
        video_id = vid.get('id', '')
        
        if not video_id:
            continue
        
        all_videos.append(vid)
        
        wnum = extract_wnum(title)
        if wnum:
            wochenschau_videos.append({
                'id': video_id,
                'title': title,
                'wnum': wnum,
                'desc_preview': vid.get('desc_preview', ''),
            })
    
    print(f"\n📊 Channel: {len(all_videos)} videos total")
    print(f"📺 Wochenschau: {len(wochenschau_videos)} videos found")
    
    # Check which need updates
    needs_update = []
    for wv in wochenschau_videos[:args.limit]:
        desc = wv['desc_preview']
        missing = []
        if 'frai.tv' not in desc:
            missing.append('frai.tv link')
        if 'remaike.IT' not in desc.lower() and 'remaike.it' not in desc:
            missing.append('remaike.IT link')
        if 'BÚSQUEDA' not in desc and 'PESQUISA' not in desc:
            missing.append('multilingual SEO')
        
        if missing:
            wv['missing'] = missing
            needs_update.append(wv)
    
    print(f"\n🔧 Need updates: {len(needs_update)} Wochenschau videos")
    
    if args.dry_run or (not args.apply and not args.generate_all):
        print("\n── DRY RUN (Preview) ──")
        
        # Fetch full descriptions for first 5
        if needs_update:
            sample_ids = [v['id'] for v in needs_update[:5]]
            details = get_video_details(sample_ids)
            
            for detail in details:
                vid = detail['id']
                current_desc = detail['snippet']['description']
                
                wv = next((w for w in needs_update if w['id'] == vid), None)
                if not wv:
                    continue
                
                new_desc = build_wochenschau_description(vid, current_desc, wv['wnum'])
                
                print(f"\n{'='*60}")
                print(f"📺 {wv['title']}")
                print(f"🆔 {vid} | wNum: {wv['wnum']}")
                print(f"❌ Missing: {', '.join(wv.get('missing', []))}")
                print(f"📏 Current: {len(current_desc)} chars → New: {len(new_desc)} chars")
                print(f"\n── NEW ADDITIONS ──")
                # Show only the new parts
                added = new_desc[len(current_desc):]
                print(added[:500])
                if len(added) > 500:
                    print(f"  ... (+{len(added)-500} more chars)")
        
        print(f"\n{'='*60}")
        print(f"\n📊 QUOTA ESTIMATE:")
        print(f"   READ:  {(len(needs_update) + 49) // 50} units (videos.list)")
        print(f"   WRITE: {len(needs_update) * 50} units (videos.update)")
        print(f"   TOTAL: {(len(needs_update) + 49) // 50 + len(needs_update) * 50} units")
        print(f"\n   Run with --apply to execute changes.")
    
    if args.apply:
        print("\n── APPLYING CHANGES ──")
        creds = load_oauth_credentials()
        
        # Process in batches
        quota_used = 0
        updated = 0
        failed = 0
        
        # First fetch all descriptions
        all_ids = [v['id'] for v in needs_update]
        all_details = get_video_details(all_ids)
        quota_used += (len(all_ids) + 49) // 50
        
        detail_map = {d['id']: d['snippet']['description'] for d in all_details}
        
        for wv in needs_update:
            vid = wv['id']
            current_desc = detail_map.get(vid)
            if not current_desc:
                print(f"  ⚠️ {vid} — no description found, skipping")
                failed += 1
                continue
            
            new_desc = build_wochenschau_description(vid, current_desc, wv['wnum'])
            
            if new_desc == current_desc:
                print(f"  ⏭️ {vid} — already up to date")
                continue
            
            try:
                success = update_video_description(vid, new_desc, creds)
                if success:
                    print(f"  ✅ {wv['title']}")
                    updated += 1
                    quota_used += 51  # 1 read + 50 write
                else:
                    print(f"  ❌ {wv['title']} — update failed")
                    failed += 1
            except Exception as e:
                print(f"  ❌ {wv['title']} — {e}")
                failed += 1
                if '403' in str(e) or 'quota' in str(e).lower():
                    print("\n🛑 QUOTA EXHAUSTED — Stopping!")
                    break
        
        print(f"\n📊 RESULTS:")
        print(f"   Updated: {updated}")
        print(f"   Failed:  {failed}")
        print(f"   Quota:   ~{quota_used} units used")
    
    if args.generate_all:
        print("\n── GENERATING ALL-VIDEOS BRAND UPDATE JSON ──")
        
        # Find ALL videos missing frai.tv link
        all_need_brand = []
        for v in all_videos:
            desc = v.get('desc_preview', '')
            missing = []
            if 'frai.tv' not in desc:
                missing.append('frai.tv')
            if 'remaike.IT' not in desc.lower() and 'remaike.it' not in desc:
                missing.append('remaike.IT')
            if missing:
                all_need_brand.append({
                    'id': v.get('id'),
                    'title': v.get('title'),
                    'missing': missing,
                })
        
        out_path = os.path.join(ROOT_DIR, 'config', 'pending_brand_updates.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated': datetime.now().isoformat(),
                'total_videos': len(all_videos),
                'need_update': len(all_need_brand),
                'wochenschau_need_update': len(needs_update),
                'videos': all_need_brand,
            }, f, ensure_ascii=False, indent=2)
        
        print(f"   📄 {out_path}")
        print(f"   📊 {len(all_need_brand)}/{len(all_videos)} videos need brand links")
        print(f"   📺 {len(needs_update)} Wochenschau need full SEO update")


if __name__ == '__main__':
    main()
