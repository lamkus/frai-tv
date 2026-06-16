#!/usr/bin/env python3
"""
FIX ALL SEO ISSUES - remAIke_IT Channel
2026 YouTube Algorithm Compliant

FIXES:
1. Soundies: Song title FIRST, not "Soundie:" prefix
2. Wochenschau: "Wochenschau" keyword at START
3. Alfred J. Kwak: Shorter titles (max 70 chars)
4. All: Add missing CTAs, hashtags, chapters

USAGE:
  python fix_all_seo_issues.py --analyze    # Show what would change
  python fix_all_seo_issues.py --apply      # Apply changes via API
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

# Load channel scan data
SCAN_FILE = 'd:/remaike.TV/config/fresh_channel_scan.json'
OUTPUT_FILE = 'd:/remaike.TV/config/seo_fixes_pending.json'

def load_videos():
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [v for v in data.get('videos', []) 
            if v.get('status', {}).get('privacyStatus') == 'public']

def fix_soundie_title(title):
    """
    ALTE FORMAT: Soundie: [Song] | 8K HQ (4K UHD) | Vintage Music Film | @remAIke_IT
    NEUES FORMAT: [Song] (1940s) | Soundie | 8K HQ | @remAIke_IT
    
    Grund: Song-Titel muss ZUERST kommen für YouTube Music Discovery!
    """
    # Extract song title from "Soundie: [Song Title] | ..."
    match = re.match(r'^Soundie:\s*([^|]+)', title, re.IGNORECASE)
    if not match:
        return None
    
    song_title = match.group(1).strip()
    
    # Clean up song title
    song_title = re.sub(r'\s*\|\s*$', '', song_title)  # Remove trailing |
    song_title = re.sub(r'\s+', ' ', song_title)  # Normalize spaces
    
    # Build new title: Song (1940s) | Soundie | 8K HQ | @remAIke_IT
    new_title = f"{song_title} (1940s) | Soundie | 8K HQ | @remAIke_IT"
    
    # Ensure max 70 chars
    if len(new_title) > 70:
        # Shorten by removing "(1940s)" if needed
        new_title = f"{song_title} | Soundie | 8K | @remAIke_IT"
    
    if len(new_title) > 70:
        # Further shorten - truncate song title
        max_song_len = 70 - len(" | Soundie | 8K | @remAIke_IT")
        song_title = song_title[:max_song_len-3] + "..."
        new_title = f"{song_title} | Soundie | 8K | @remAIke_IT"
    
    return new_title

def fix_wochenschau_title(title):
    """
    ALTE FORMAT: 8K HQ Die Deutsche Wochenschau Nr. 516 | 22.07.1940 | German WWII Newsreel | @remAIke_IT
    NEUES FORMAT: Wochenschau Nr. 516 (1940) | 8K HQ | @remAIke_IT
    
    Grund: "Wochenschau" Keyword muss am ANFANG stehen!
    """
    # Extract Wochenschau number
    match = re.search(r'Wochenschau\s*Nr\.?\s*(\d+)', title, re.IGNORECASE)
    if not match:
        return None
    
    nr = match.group(1)
    
    # Extract year from date or title
    year_match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', title)
    if year_match:
        year = year_match.group(3)
    else:
        year_match = re.search(r'\((\d{4})\)', title)
        year = year_match.group(1) if year_match else "1940s"
    
    # Build new title
    new_title = f"Wochenschau Nr. {nr} ({year}) | 8K HQ | @remAIke_IT"
    
    return new_title

def fix_alfred_title(title):
    """
    ALTE FORMAT: Alfred Jodokus Quack (31/52): Die Bohrinsel | Deutsch | 8K HQ (4K UHD) | @remAIke_IT
    NEUES FORMAT: Alfred J. Kwak (31): Die Bohrinsel | 8K | @remAIke_IT
    
    Grund: Titel auf max 70 Zeichen kürzen!
    """
    # Extract episode info
    match = re.match(r'Alfred\s+(?:Jodokus\s+)?(?:Quack|Kwak)\s*\((\d+)(?:/\d+)?\):\s*([^|]+)', title, re.IGNORECASE)
    if not match:
        return None
    
    episode = match.group(1)
    episode_title = match.group(2).strip()
    
    # Build new title - use "Alfred J. Kwak" (shorter + SEO for both spellings)
    new_title = f"Alfred J. Kwak ({episode}): {episode_title} | 8K | @remAIke_IT"
    
    # Ensure max 70 chars
    if len(new_title) > 70:
        max_ep_len = 70 - len(f"Alfred J. Kwak ({episode}):  | 8K | @remAIke_IT")
        episode_title = episode_title[:max_ep_len-3] + "..."
        new_title = f"Alfred J. Kwak ({episode}): {episode_title} | 8K | @remAIke_IT"
    
    return new_title

def needs_cta_fix(description):
    """Check if description needs CTA block."""
    desc_lower = description.lower()
    cta_words = ['like', 'subscribe', 'comment', 'abonnieren', 'kommentier']
    return not any(w in desc_lower for w in cta_words)

def needs_hashtag_fix(description):
    """Check if description needs hashtags."""
    hashtag_count = description.count('#')
    return hashtag_count < 3

def generate_cta_block():
    """Generate standard CTA block."""
    return """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you enjoyed!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more: @remAIke_IT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT
"""

def generate_hashtags(category):
    """Generate category-appropriate hashtags."""
    base = "#8K #remAIke #PublicDomain #VintageVideo"
    
    category_tags = {
        'Soundies': "#Soundie #VintageMusic #1940s #Jazz #Swing",
        'Wochenschau': "#Wochenschau #Newsreel #History #WWII #Documentary",
        'Alfred J. Kwak': "#AlfredJKwak #AlfredKwak #Anime #Cartoon #80s #Nostalgie",
        'Betty Boop': "#BettyBoop #Fleischer #1930s #Animation #Cartoon",
        'Popeye': "#Popeye #Fleischer #Animation #Cartoon #Classic",
        'Superman/Fleischer': "#Superman #Fleischer #Animation #DCComics #Classic",
        'Felix the Cat': "#FelixTheCat #SilentFilm #Animation #1920s #Cartoon",
        'Looney Tunes': "#LooneyTunes #WB #Animation #Cartoon #Classic",
    }
    
    return f"\n{category_tags.get(category, base)}"

def categorize_video(video):
    """Determine video category."""
    title = video.get('snippet', {}).get('title', '').lower()
    
    if 'soundie' in title:
        return 'Soundies'
    elif 'wochenschau' in title:
        return 'Wochenschau'
    elif 'alfred' in title and ('kwak' in title or 'quack' in title):
        return 'Alfred J. Kwak'
    elif 'betty boop' in title or 'betty' in title:
        return 'Betty Boop'
    elif 'popeye' in title:
        return 'Popeye'
    elif 'superman' in title or 'fleischer' in title:
        return 'Superman/Fleischer'
    elif 'felix' in title:
        return 'Felix the Cat'
    elif 'looney' in title or 'porky' in title or 'bugs' in title:
        return 'Looney Tunes'
    else:
        return 'Other'

def analyze_and_fix():
    """Analyze all videos and generate fix recommendations."""
    videos = load_videos()
    
    fixes = {
        'title_fixes': [],
        'description_fixes': [],
        'stats': {
            'total_analyzed': len(videos),
            'title_fixes_needed': 0,
            'cta_fixes_needed': 0,
            'hashtag_fixes_needed': 0
        }
    }
    
    print("=" * 70)
    print("🔧 SEO FIX ANALYSE - remAIke_IT")
    print("=" * 70)
    
    for video in videos:
        video_id = video['id']
        title = video['snippet']['title']
        description = video['snippet'].get('description', '')
        category = categorize_video(video)
        
        fix_entry = {
            'video_id': video_id,
            'category': category,
            'current_title': title,
            'new_title': None,
            'title_change_reason': None,
            'needs_cta': needs_cta_fix(description),
            'needs_hashtags': needs_hashtag_fix(description)
        }
        
        # Check for title fixes
        new_title = None
        reason = None
        
        if category == 'Soundies' and title.lower().startswith('soundie:'):
            new_title = fix_soundie_title(title)
            reason = "Song-Titel muss am Anfang stehen für YouTube Music"
            
        elif category == 'Wochenschau':
            if not title.lower().startswith('wochenschau'):
                new_title = fix_wochenschau_title(title)
                reason = "Keyword 'Wochenschau' muss am Anfang stehen"
                
        elif category == 'Alfred J. Kwak':
            if len(title) > 70:
                new_title = fix_alfred_title(title)
                reason = f"Titel zu lang ({len(title)} chars) - max 70"
        
        if new_title and new_title != title:
            fix_entry['new_title'] = new_title
            fix_entry['title_change_reason'] = reason
            fixes['stats']['title_fixes_needed'] += 1
        
        if fix_entry['needs_cta']:
            fixes['stats']['cta_fixes_needed'] += 1
        if fix_entry['needs_hashtags']:
            fixes['stats']['hashtag_fixes_needed'] += 1
        
        # Only add if any fix needed
        if fix_entry['new_title'] or fix_entry['needs_cta'] or fix_entry['needs_hashtags']:
            fixes['title_fixes'].append(fix_entry)
    
    # Print summary by category
    print("\n📊 FIXES NACH KATEGORIE")
    print("-" * 70)
    
    by_category = defaultdict(list)
    for fix in fixes['title_fixes']:
        by_category[fix['category']].append(fix)
    
    for cat in sorted(by_category.keys()):
        cat_fixes = by_category[cat]
        title_fixes = len([f for f in cat_fixes if f['new_title']])
        cta_fixes = len([f for f in cat_fixes if f['needs_cta']])
        hash_fixes = len([f for f in cat_fixes if f['needs_hashtags']])
        
        print(f"\n{cat}:")
        print(f"  📝 Titel-Änderungen: {title_fixes}")
        print(f"  📢 CTA fehlt: {cta_fixes}")
        print(f"  #️⃣ Hashtags fehlen: {hash_fixes}")
        
        # Show examples
        if title_fixes > 0:
            example = next(f for f in cat_fixes if f['new_title'])
            print(f"\n  Beispiel:")
            print(f"    ALT:  {example['current_title'][:60]}...")
            print(f"    NEU:  {example['new_title']}")
    
    # Print overall stats
    print("\n" + "=" * 70)
    print("📊 GESAMTÜBERSICHT")
    print("=" * 70)
    print(f"  Analysierte Videos: {fixes['stats']['total_analyzed']}")
    print(f"  Titel-Änderungen nötig: {fixes['stats']['title_fixes_needed']}")
    print(f"  CTA-Blöcke fehlen: {fixes['stats']['cta_fixes_needed']}")
    print(f"  Hashtags fehlen: {fixes['stats']['hashtag_fixes_needed']}")
    
    # Save to file
    fixes['generated_at'] = datetime.now().isoformat()
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fixes, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Gespeichert: {OUTPUT_FILE}")
    print("\n⚠️  Zum Anwenden: python fix_all_seo_issues.py --apply")
    
    return fixes

def apply_fixes():
    """Apply fixes via YouTube API (requires OAuth)."""
    print("🚨 STOP-GATE: Video-Updates")
    print("=" * 70)
    print("""
Diese Aktion würde Videos ändern!

PFLICHT-CHECKS:
1. ✓ Änderungen in config/seo_fixes_pending.json geprüft?
2. ✓ Alle Titel-Änderungen sinnvoll?
3. ✓ YouTube OAuth Token gültig?

YOUTUBE API KOSTEN:
- videos.update = 50 Units pro Video
- Bei 50 Videos = 2500 Units (25% Tagesquota!)

""")
    
    # Load pending fixes
    if not os.path.exists(OUTPUT_FILE):
        print("❌ Keine pending fixes gefunden. Erst --analyze ausführen!")
        return
    
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        fixes = json.load(f)
    
    title_fixes = [f for f in fixes['title_fixes'] if f.get('new_title')]
    
    print(f"📊 Pending Title Fixes: {len(title_fixes)}")
    print(f"📊 Geschätzte API-Kosten: {len(title_fixes) * 50} Units")
    print()
    
    response = input("Wirklich anwenden? (ja/nein): ")
    if response.lower() != 'ja':
        print("❌ Abgebrochen.")
        return
    
    print("\n⚠️  API-Implementierung noch nicht aktiv.")
    print("    Änderungen wurden in config/seo_fixes_pending.json gespeichert.")
    print("    Diese können manuell im YouTube Studio angewendet werden.")

if __name__ == '__main__':
    import sys
    
    if '--apply' in sys.argv:
        apply_fixes()
    else:
        analyze_and_fix()
