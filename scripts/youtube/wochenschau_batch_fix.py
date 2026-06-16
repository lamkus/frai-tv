#!/usr/bin/env python3
"""
WOCHENSCHAU BATCH FIX
Korrigiert alle 41 Wochenschau-Videos basierend auf Workspace-Daten:
- Individueller Ort aus config/wochenschau_complete_locations.json
- Hashtags reduzieren: 12 → 5
- Links hinzufügen: www.remaike.IT + YouTube
- @remAIke_IT NICHT im Titel (bleibt so)

Usage:
  python wochenschau_batch_fix.py           # Dry run
  python wochenschau_batch_fix.py --apply   # Live update
"""

import json
import os
import sys
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# === CONFIG ===
OAUTH_FILE = 'config/youtube_oauth.json'
LOCATIONS_FILE = 'config/wochenschau_complete_locations.json'
EVENTS_FILE = 'config/wochenschau_events.json'
CHANNEL_SCAN = 'config/fresh_channel_scan.json'
OUTPUT_FILE = 'config/wochenschau_batch_fix_result.json'

# Pflicht-Hashtags (max 5!)
REQUIRED_HASHTAGS = ['#Wochenschau', '#WWII', '#8K', '#History', '#PublicDomain']

# Pflicht-Links
WEBSITE_LINK = '🌐 www.remaike.IT'
YOUTUBE_LINK = '📺 https://www.youtube.com/@remAIke_IT'

# Multilingual Search Block (kompakt)
MULTILINGUAL_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg
🇬🇧 German Newsreel, World War II, WWII
🇪🇸 Noticiero alemán, Segunda Guerra Mundial
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial
🇫🇷 Actualités allemandes, Seconde Guerre mondiale
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

# CTA Block
CTA_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def load_oauth():
    """Load OAuth credentials"""
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    
    return Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

def extract_number(title):
    """Extract Wochenschau number from title"""
    match = re.search(r'(\d{3})', title)
    return match.group(1) if match else None

def reduce_hashtags(desc):
    """Remove excessive hashtags, keep only 5"""
    # Find all hashtags
    hashtags = re.findall(r'#\w+', desc)
    
    if len(hashtags) <= 5:
        return desc, False
    
    # Remove all hashtags from description
    desc_clean = re.sub(r'#\w+\s*', '', desc).strip()
    
    return desc_clean, True

# Disclaimer Block (CRITICAL for Safety)
DISCLAIMER_BLOCK = """⚠️ HISTORICAL DOCUMENT / HISTORISCHES DOKUMENT
This video outlines the history of the Second World War.
It is for educational purposes only and serves as a historical document.
Die gezeigten Inhalte dienen der historisch-wissenschaftlichen Aufklärung.
Sie spiegeln NICcht die Meinung des Uploaders wider."""

def build_description(old_desc, location_info, event_info):
    """Build optimized description with all required elements"""
    
    # Clean old description (remove excessive hashtags)
    desc_clean, had_excess_hashtags = reduce_hashtags(old_desc)
    
    # Extract first meaningful paragraph (keep intro)
    lines = desc_clean.split('\n')
    intro_lines = []
    for line in lines[:10]:
        if line.strip() and not line.startswith('━'):
            intro_lines.append(line)
        if len(intro_lines) >= 3:
            break
    intro = '\n'.join(intro_lines)
    
    # Build location line
    location_desc = location_info.get('location', {}).get('desc', '')
    historical_note = location_info.get('historical_note', event_info.get('note', ''))
    
    # Build new description
    new_desc = f"""{intro}

📍 Location: {location_desc}
📜 {historical_note}

{DISCLAIMER_BLOCK}

{MULTILINGUAL_BLOCK}

{CTA_BLOCK}

{WEBSITE_LINK}
{YOUTUBE_LINK}

📜 Source: Public Domain (UFA 1940-1945)

{' '.join(REQUIRED_HASHTAGS)}"""
    
    return new_desc

def main():
    apply_mode = '--apply' in sys.argv
    
    print("="*70)
    print("🎬 WOCHENSCHAU BATCH FIX")
    print("="*70)
    print(f"Mode: {'🔴 LIVE UPDATE' if apply_mode else '🟢 DRY RUN'}")
    
    # Load data
    print("\n📂 Loading workspace data...")
    
    with open(LOCATIONS_FILE, 'r', encoding='utf-8') as f:
        locations = json.load(f)
    print(f"   ✅ Locations: {len(locations)} entries")
    
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
    events = events_data.get('events', {})
    print(f"   ✅ Events: {len(events)} entries")
    
    with open(CHANNEL_SCAN, 'r', encoding='utf-8') as f:
        channel = json.load(f)
    print(f"   ✅ Channel scan: {channel['public']} public videos")
    
    # Find Wochenschau videos
    wochenschau_videos = []
    for v in channel['videos']:
        title = v['snippet']['title']
        if 'wochenschau' in title.lower() and v['status']['privacyStatus'] == 'public':
            wochenschau_videos.append(v)
    
    print(f"\n📺 Found {len(wochenschau_videos)} public Wochenschau videos")
    
    # Prepare updates
    updates = []
    
    for v in wochenschau_videos:
        vid = v['id']
        title = v['snippet']['title']
        old_desc = v['snippet'].get('description', '')
        tags = v['snippet'].get('tags', [])
        
        nr = extract_number(title)
        if not nr:
            print(f"   ⚠️ No number found: {title[:50]}")
            continue
        
        location_info = locations.get(nr, {})
        event_info = events.get(nr, {})
        
        # Build new description
        new_desc = build_description(old_desc, location_info, event_info)
        
        # Check if update needed
        needs_update = False
        reasons = []
        
        # Check for required links
        if WEBSITE_LINK not in old_desc:
            needs_update = True
            reasons.append('Missing website link')
        
        if YOUTUBE_LINK not in old_desc:
            needs_update = True
            reasons.append('Missing YouTube link')
        
        # Check hashtag count
        old_hashtags = old_desc.count('#')
        if old_hashtags > 5:
            needs_update = True
            reasons.append(f'Too many hashtags ({old_hashtags} → 5)')
        
        # Check for location
        location_desc = location_info.get('location', {}).get('desc', '')
        if location_desc and location_desc not in old_desc:
            needs_update = True
            reasons.append(f'Missing location: {location_desc}')
        
        if needs_update:
            updates.append({
                'video_id': vid,
                'title': title,
                'number': nr,
                'reasons': reasons,
                'old_desc_preview': old_desc[:200],
                'new_desc': new_desc,
                'location': location_desc,
                'tags': tags[:15] if len(tags) > 15 else tags  # Cap at 15
            })
    
    print(f"\n📋 Updates needed: {len(updates)}/{len(wochenschau_videos)}")
    
    # Show preview
    print("\n" + "="*70)
    print("📝 UPDATE PREVIEW (first 5)")
    print("="*70)
    
    for u in updates[:5]:
        print(f"\n🎬 Nr.{u['number']}: {u['title'][:50]}")
        print(f"   📍 Location: {u['location']}")
        print(f"   🔧 Reasons: {', '.join(u['reasons'])}")
    
    if len(updates) > 5:
        print(f"\n   ... and {len(updates) - 5} more")
    
    # Apply updates if requested
    if apply_mode and updates:
        print("\n" + "="*70)
        print("🔴 APPLYING UPDATES...")
        print("="*70)
        
        creds = load_oauth()
        youtube = build('youtube', 'v3', credentials=creds)
        
        success = 0
        failed = 0
        
        for i, u in enumerate(updates):
            try:
                print(f"\n[{i+1}/{len(updates)}] Updating Nr.{u['number']}...")
                
                youtube.videos().update(
                    part='snippet',
                    body={
                        'id': u['video_id'],
                        'snippet': {
                            'title': u['title'],
                            'description': u['new_desc'],
                            'tags': u['tags'],
                            'categoryId': '27',  # Education (Better for Historical Accuracy/Safety than 25)
                            'defaultLanguage': 'de',
                            'defaultAudioLanguage': 'de'
                        }
                    }
                ).execute()
                
                print(f"   ✅ Updated!")
                success += 1
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed += 1
        
        print(f"\n📊 Results: {success} success, {failed} failed")
    
    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'apply' if apply_mode else 'dry_run',
        'total_wochenschau': len(wochenschau_videos),
        'updates_needed': len(updates),
        'updates': updates
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Report saved: {OUTPUT_FILE}")
    
    if not apply_mode:
        print("\n💡 To apply changes, run:")
        print("   python wochenschau_batch_fix.py --apply")

if __name__ == '__main__':
    main()
