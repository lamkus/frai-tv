#!/usr/bin/env python3
"""
tactical_seasonal_push.py — Multi-Campaign Seasonal & Tactical Push System
==========================================================================
Handles ALL seasonal campaigns + quick-win title/tag/description fixes.

Campaigns:
  --campaign quick_wins       Underperforming video title/tag/desc fixes (12 videos)
  --campaign retro_day        National Retro Day Feb 27 (hashtag + desc boost)
  --campaign womens_day       International Women's Day Mar 8 (Betty Boop feminist)
  --campaign silent_film      Silent Film Day Apr 15
  --campaign halloween        Halloween Oct 1-31 (BIGGEST opportunity)
  --campaign christmas        Christmas Dec prep
  --campaign new_years        New Year's Eve Dec 31
  --campaign propaganda       Evergreen viral propaganda curiosity
  --campaign all              Run all campaigns

Usage:
  python tactical_seasonal_push.py --campaign quick_wins              # Dry run
  python tactical_seasonal_push.py --campaign quick_wins --apply      # LIVE
  python tactical_seasonal_push.py --campaign retro_day --apply       # LIVE
  python tactical_seasonal_push.py --campaign all                      # Dry run all
"""

import os, sys, json, time, argparse, re
from datetime import datetime, timezone
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "config" / "video_master_db_v3.json"
OAUTH_PATH = BASE_DIR / "config" / "youtube_oauth.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ─── Constants ────────────────────────────────────────────────────────────────
QUOTA_PER_UPDATE = 50
QUOTA_DAILY_LIMIT = 10000
CTA_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

# ─── Auth ─────────────────────────────────────────────────────────────────────
def get_youtube_service():
    """Build authenticated YouTube service (OAuth for writes)."""
    with open(OAUTH_PATH, 'r') as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get('access_token') or token_data.get('token'),
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/youtube'])
    )
    if creds.expired:
        creds.refresh(Request())
        token_data['access_token'] = creds.token
        with open(OAUTH_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
        print("  [AUTH] Token refreshed")
    return build('youtube', 'v3', credentials=creds)


def fetch_live_video(youtube, video_id):
    """Fetch current live state of a video."""
    resp = youtube.videos().list(
        part='snippet,status',
        id=video_id
    ).execute()
    items = resp.get('items', [])
    return items[0] if items else None


def update_video(youtube, video_id, snippet_updates, dry_run=True):
    """Push snippet updates to a video. Returns success bool."""
    if dry_run:
        return True
    
    live = fetch_live_video(youtube, video_id)
    if not live:
        print(f"    ❌ Video {video_id} not found!")
        return False
    
    snippet = live['snippet']
    
    # Merge updates into live snippet
    for key, value in snippet_updates.items():
        if key == 'tags' and value:
            snippet['tags'] = value
        elif key == 'title' and value:
            snippet['title'] = value
        elif key == 'description' and value:
            snippet['description'] = value
        elif key == 'categoryId' and value:
            snippet['categoryId'] = str(value)
    
    body = {
        'id': video_id,
        'snippet': snippet
    }
    
    try:
        youtube.videos().update(part='snippet', body=body).execute()
        return True
    except Exception as e:
        err = str(e)
        if 'quotaExceeded' in err:
            print(f"\n  🛑 QUOTA EXCEEDED! Stopping.")
            sys.exit(1)
        print(f"    ❌ Error: {err[:200]}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN: QUICK WINS — Fix underperforming videos with bad titles/tags
# ═══════════════════════════════════════════════════════════════════════════════
def campaign_quick_wins():
    """Fix titles, tags, descriptions for massively underperforming videos."""
    fixes = [
        {
            'id': 'HGg-g6SwrrQ',
            'label': 'Reefer Madness',
            'new_title': 'Reefer Madness (1938) | Cult Propaganda Classic | 8K HQ',
            'new_tags': ['reefer madness', 'reefer madness full movie', '1938', 'anti-drug propaganda',
                         'cult classic', 'vintage propaganda', 'public domain', '8K', 'marijuana film',
                         'banned film', 'exploitation film', 'so bad its good', 'retro film'],
            'desc_hook': '🎬 Reefer Madness (1938) — The most infamous anti-drug propaganda film ever made!\n\nOriginally financed by a church group, this unintentionally hilarious "educational" film has become one of the greatest cult classics of all time. Watch the full restored version in stunning 8K quality.\n\n',
        },
        {
            'id': 'b4cqLlJ7t4M',
            'label': 'Phantom of the Opera',
            'new_title': 'Phantom of the Opera (1925) | Lon Chaney Horror | 8K HQ',
            'new_tags': ['phantom of the opera', 'lon chaney', '1925', 'silent horror', 'classic horror',
                         'horror movie', 'public domain', '8K', 'vintage horror', 'silent film',
                         'universal horror', 'halloween', 'gothic horror', 'full movie'],
            'desc_hook': '🎬 The Phantom of the Opera (1925) — Lon Chaney\'s legendary horror masterpiece!\n\nThe original silent horror classic that started it all. Lon Chaney\'s iconic unmasking scene remains one of the most shocking moments in cinema history. Now restored in breathtaking 8K quality.\n\n',
        },
        {
            'id': 'exukLdxugy8',
            'label': 'Häxan Witchcraft',
            'new_title': 'Häxan: Witchcraft Through the Ages (1922) | Silent Horror | 8K HQ',
            'new_tags': ['häxan', 'witchcraft through the ages', '1922', 'silent horror', 'witchcraft',
                         'occult', 'documentary horror', 'public domain', '8K', 'swedish horror',
                         'benjamin christensen', 'halloween', 'dark ages', 'witch trials'],
            'desc_hook': '🎬 Häxan: Witchcraft Through the Ages (1922) — The most disturbing silent film ever made!\n\nThis groundbreaking Swedish documentary-drama explores the history of witchcraft, Satanism, and mental illness from the Middle Ages to the 1920s. Banned in multiple countries upon release. Now in stunning 8K.\n\n',
        },
        {
            'id': '8lLtNb11NKU',
            'label': 'Metropolis',
            'new_title': 'Metropolis (1927) | Fritz Lang Sci-Fi Masterpiece | 8K HQ',
            'new_tags': ['metropolis', 'fritz lang', '1927', 'science fiction', 'sci-fi classic',
                         'silent film', 'german expressionism', 'public domain', '8K', 'dystopia',
                         'futuristic', 'classic cinema', 'full movie', 'masterpiece'],
            'desc_hook': '🎬 Metropolis (1927) — Fritz Lang\'s visionary sci-fi masterpiece!\n\nThe most influential science fiction film ever made. This dystopian epic inspired everything from Star Wars to Blade Runner. Every sci-fi film owes something to Metropolis. Now in breathtaking 8K.\n\n',
        },
        {
            'id': 'HCj_w3pBxlc',
            'label': 'Blackmail Hitchcock',
            'new_title': 'Blackmail (1929) | Alfred Hitchcock\'s First Talkie | 8K HQ',
            'new_tags': ['blackmail', 'alfred hitchcock', '1929', 'hitchcock first talkie', 'british cinema',
                         'thriller', 'classic thriller', 'public domain', '8K', 'silent film era',
                         'anny ondra', 'suspense', 'vintage cinema', 'full movie'],
            'desc_hook': '🎬 Blackmail (1929) — Alfred Hitchcock\'s first sound film and first masterpiece!\n\nThe Master of Suspense\'s groundbreaking thriller that marks the transition from silent to sound cinema. Features the iconic British Museum chase sequence. Hitchcock at his early best, now in stunning 8K.\n\n',
        },
        {
            'id': 'bhnnR0WX_X0',
            'label': 'Boxing Cats',
            'new_title': 'Boxing Cats (1894) | World\'s Oldest Cat Video | 8K HQ',
            'new_tags': ['boxing cats', '1894', 'oldest cat video', 'thomas edison', 'vintage film',
                         'cats', 'cat video', 'public domain', '8K', 'film history', 'first films',
                         'black kinetoscope', 'victorian era', 'cats of youtube', 'funny cats'],
            'desc_hook': '🐱 Boxing Cats (1894) — THE WORLD\'S OLDEST CAT VIDEO!\n\nFilmed by Thomas Edison\'s studio in 1894, this is literally the first cat video ever made — 131 years before YouTube! Two cats "boxing" in a miniature ring. The internet was destined for cats from the very beginning. Now in 8K!\n\n',
        },
        {
            'id': '70Ni30lbXRc',
            'label': 'Glücksbärchis',
            'new_title': 'Glücksbärchis: Abenteuer im Wunderland (1987) | Deutsch | 8K HQ',
            'new_tags': ['Glücksbärchis', 'Care Bears', 'Abenteuer im Wunderland', '1987',
                         'Zeichentrickfilm', 'Kinderfilm', '80er Kindheit', 'Nostalgie', '8K',
                         'Deutsch', 'German', 'Kinderserie', 'retro cartoon', 'public domain'],
            'desc_hook': '🎬 Glücksbärchis: Abenteuer im Wunderland (1987) — Der Kult-Kinderfilm der 80er!\n\nDie Glücksbärchis in ihrem magischen Abenteuer — komplett auf Deutsch und in atemberaubender 8K Qualität restauriert. Pure 80er-Nostalgie!\n\n🇩🇪 Care Bears: Adventures in Wonderland — German dub in 8K.\n\n',
        },
        {
            'id': 'Nzi6aRKDoEs',
            'label': 'Nosferatu',
            'new_title': 'Nosferatu (1922) | The First Vampire Film | 8K HQ',
            'new_tags': ['nosferatu', '1922', 'vampire', 'silent horror', 'horror classic',
                         'count orlok', 'f.w. murnau', 'german expressionism', 'public domain', '8K',
                         'dracula', 'gothic horror', 'halloween', 'full movie'],
            'desc_hook': '🧛 Nosferatu (1922) — The ORIGINAL vampire film that started EVERYTHING!\n\nF.W. Murnau\'s unauthorized adaptation of Dracula created cinema\'s most iconic monster. Count Orlok\'s shadow climbing the stairs remains the most terrifying image in film history — over 100 years later. Now fully restored in 8K.\n\n',
        },
        {
            'id': 'V9zhjG_6cHU',
            'label': 'NYE 1950s Supercut',
            'new_title': 'New Year\'s Eve 1950s TV Marathon (74 Min) | Vintage TV | 8K HQ',
            'new_tags': ['new years eve', '1950s', 'vintage tv', 'retro television', 'new year',
                         'silvester', 'tv marathon', 'public domain', '8K', 'classic tv',
                         'times square', 'nostalgia', 'mid century', 'golden age television'],
            'desc_hook': '🎆 New Year\'s Eve 1950s TV Marathon — 74 minutes of pure vintage celebration!\n\nRing in the New Year like it\'s 1959! This supercut features the best New Year\'s Eve TV moments from the golden age of American television. Perfect for your retro NYE party!\n\n',
        },
        {
            'id': 'dpF2uQVgCsM',
            'label': 'Fast and Furious 1954',
            'new_title': 'The Fast and the Furious (1954) | The ORIGINAL Film | 8K HQ',
            'new_tags': ['fast and furious', 'fast and the furious', '1954', 'original fast furious',
                         'car chase', 'roger corman', 'public domain', '8K', 'action movie',
                         'racing film', 'cult classic', 'vintage cars', 'full movie', 'classic film'],
            'desc_hook': '🏎️ The Fast and the Furious (1954) — The ORIGINAL film that inspired a billion-dollar franchise!\n\nDecades before Vin Diesel, THIS was The Fast and the Furious. Roger Corman\'s 1954 racing thriller was the public domain film whose TITLE was licensed to create the modern franchise. Now in 8K!\n\n',
        },
        {
            'id': 'DnwDqCsSqRw',
            'label': 'Berlin Symphony',
            'new_title': 'Berlin: Symphony of a Great City (1927) | Silent Masterpiece | 8K HQ',
            'new_tags': ['berlin', 'symphony of a great city', '1927', 'walter ruttmann', 'weimar republic',
                         'silent film', 'documentary', 'city symphony', 'public domain', '8K',
                         'german cinema', '1920s berlin', 'avant-garde', 'film history'],
            'desc_hook': '🎬 Berlin: Symphony of a Great City (1927) — A day in the life of 1920s Berlin!\n\nWalter Ruttmann\'s groundbreaking "city symphony" captures Berlin during the roaring Weimar Republic. From dawn to midnight, experience a legendary city that would soon be transformed forever. Stunning 8K restoration.\n\n',
        },
        {
            'id': 'hPQN992PMUY',
            'label': 'Frankenstein 1910',
            'new_title': 'Frankenstein (1910) | The FIRST Horror Film | Edison Studios | 8K HQ',
            'new_tags': ['frankenstein', '1910', 'edison studios', 'first horror film', 'silent horror',
                         'horror classic', 'mary shelley', 'public domain', '8K', 'monster movie',
                         'film history', 'halloween', 'gothic horror', 'lost film'],
            'desc_hook': '🧟 Frankenstein (1910) — The FIRST horror film ever made!\n\nThomas Edison\'s studio created cinema\'s first monster movie over 115 years ago. This 12-minute masterpiece was considered LOST for decades until a single print was discovered in the 1970s. Now restored in breathtaking 8K.\n\n',
        },
    ]
    return fixes


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN: RETRO DAY — National Retro Day Feb 27
# ═══════════════════════════════════════════════════════════════════════════════
def campaign_retro_day():
    """Add #NationalRetroDay boost to top 20 performing videos."""
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    vids = db['videos']
    
    # Top 20 videos by views — add retro day hashtags to descriptions
    top = []
    for vid_id, v in vids.items():
        views = v.get('metrics', {}).get('views', 0) or 0
        status = v.get('status', {}).get('privacyStatus', 'public')
        if status == 'public' and views >= 500:
            title = v.get('current', {}).get('title', '')
            top.append({'id': vid_id, 'label': title[:50], 'views': views})
    
    top.sort(key=lambda x: x['views'], reverse=True)
    
    fixes = []
    for item in top[:20]:
        fixes.append({
            'id': item['id'],
            'label': f"[Retro Day] {item['label']}",
            'new_title': None,  # Don't change title
            'new_tags': None,   # Handled via description hashtags
            'desc_hook': None,  # Will add hashtags to end of existing description
            'add_hashtags': ['#NationalRetroDay', '#RetroDay', '#Vintage', '#8K', '#PublicDomain'],
        })
    return fixes


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN: WOMEN'S DAY — Betty Boop as Feminist Icon, Mar 8
# ═══════════════════════════════════════════════════════════════════════════════
def campaign_womens_day():
    """Boost Betty Boop + related videos for International Women's Day."""
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    vids = db['videos']
    
    fixes = []
    for vid_id, v in vids.items():
        series = v.get('series', '')
        title = v.get('current', {}).get('title', '')
        if series == 'betty_boop':
            fixes.append({
                'id': vid_id,
                'label': f"[Women's Day] {title[:50]}",
                'new_title': None,
                'new_tags': None,
                'desc_hook': None,
                'add_hashtags': ['#InternationalWomensDay', '#WomensDay', '#BettyBoop', '#FeministIcon', '#VintageAnimation'],
            })
    
    # Also add Teaserama and Lucy
    for vid_id, v in vids.items():
        title_lower = (v.get('current', {}).get('title', '') or '').lower()
        if 'teaserama' in title_lower or 'lucy' in title_lower:
            fixes.append({
                'id': vid_id,
                'label': f"[Women's Day] {v.get('current',{}).get('title','')[:50]}",
                'new_title': None,
                'new_tags': None,
                'desc_hook': None,
                'add_hashtags': ['#InternationalWomensDay', '#WomensDay', '#VintageWomen'],
            })
    
    return fixes


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN: HALLOWEEN — BIGGEST opportunity (Oct)
# ═══════════════════════════════════════════════════════════════════════════════
def campaign_halloween():
    """Optimize horror/spooky videos for Halloween season."""
    halloween_keywords = ['zombie', 'nosferatu', 'frankenstein', 'skeleton', 'phantom',
                          'häxan', 'caligari', 'casper', 'ghost', 'grim', 'horror',
                          'scarlet street', 'white zombie', 'mummy']
    
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    vids = db['videos']
    
    fixes = []
    for vid_id, v in vids.items():
        title = (v.get('current', {}).get('title', '') or '').lower()
        series = v.get('series', '')
        
        is_halloween = series == 'casper' or any(kw in title for kw in halloween_keywords)
        if not is_halloween:
            continue
        
        full_title = v.get('current', {}).get('title', '')
        fixes.append({
            'id': vid_id,
            'label': f"[Halloween] {full_title[:50]}",
            'new_title': None,
            'new_tags': None,
            'desc_hook': None,
            'add_hashtags': ['#Halloween', '#HorrorClassic', '#Spooky', '#VintageHorror', '#8K'],
        })
    
    return fixes


# ═══════════════════════════════════════════════════════════════════════════════
#  CAMPAIGN: PROPAGANDA VIRAL — Evergreen "they actually showed this?!" 
# ═══════════════════════════════════════════════════════════════════════════════
def campaign_propaganda():
    """Optimize propaganda/curiosity videos for viral discovery."""
    fixes = [
        {
            'id': 'HGg-g6SwrrQ',  # Reefer Madness — already in quick_wins
            'label': '[Propaganda] Reefer Madness',
            'new_title': None,  # Already fixed in quick_wins
            'new_tags': None,
            'desc_hook': None,
            'add_hashtags': ['#ReeferMadness', '#Propaganda', '#CultClassic', '#Banned', '#VintageFilm'],
        },
        {
            'id': 'Ge-mC5q6lXw',
            'label': '[Propaganda] Duck and Cover',
            'new_title': 'Duck and Cover (1951) | Cold War Propaganda | 8K HQ',
            'new_tags': ['duck and cover', '1951', 'cold war', 'nuclear', 'propaganda', 'civil defense',
                         'atomic bomb', 'vintage educational', 'public domain', '8K', 'retro',
                         'school film', 'bert the turtle'],
            'desc_hook': '☢️ Duck and Cover (1951) — The most iconic Cold War propaganda film!\n\n"Bert the Turtle" taught millions of American schoolchildren to hide under their desks in case of nuclear attack. This absurdly optimistic civil defense film became a symbol of Cold War paranoia. Now in 8K.\n\n',
        },
        {
            'id': 'Zu_iBCd5NJc',
            'label': '[Propaganda] Biological Warfare',
            'new_title': 'Biological Warfare: What You Should Know (1952) | Cold War | 8K HQ',
            'new_tags': ['biological warfare', '1952', 'cold war', 'propaganda', 'germ warfare',
                         'military training', 'vintage documentary', 'public domain', '8K',
                         'chemical weapons', 'civil defense', 'retro educational'],
            'desc_hook': '☣️ Biological Warfare: What You Should Know (1952) — Declassified Cold War training film!\n\nThis chilling government film warned Americans about the threat of biological attacks during the height of the Cold War. A fascinating look at 1950s military paranoia. Restored in 8K.\n\n',
        },
        {
            'id': 'M0-tJK4H3lo',
            'label': '[Propaganda] Tokyo Jokio',
            'new_title': None,  # Keep current, already has good views
            'new_tags': None,
            'desc_hook': None,
            'add_hashtags': ['#WWII', '#Propaganda', '#WarCartoon', '#MerrieMelodies', '#VintageAnimation'],
        },
        {
            'id': 'YU9W-d33yYg',
            'label': '[Propaganda] Marihuana short',
            'new_title': 'Marihuana (1936) | Vintage Anti-Drug Propaganda | 8K HQ',
            'new_tags': ['marihuana', 'marijuana', '1936', 'anti-drug', 'propaganda', 'vintage',
                         'reefer', 'exploitation', 'public domain', '8K', 'retro', 'banned'],
            'desc_hook': '🚫 Marihuana (1936) — Vintage anti-drug propaganda at its most dramatic!\n\nOne of many "educational" scare films from the 1930s designed to terrify audiences about marijuana. A fascinating time capsule of drug hysteria. Restored in 8K.\n\n',
        },
    ]
    return fixes


# ═══════════════════════════════════════════════════════════════════════════════
#  EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
def execute_campaign(campaign_name, fixes, apply=False):
    """Execute a campaign — dry run or live."""
    mode = "🔴 LIVE" if apply else "🟢 DRY RUN"
    print(f"\n{'='*70}")
    print(f"  CAMPAIGN: {campaign_name.upper()} | {mode} | {len(fixes)} videos")
    print(f"  Quota cost: {len(fixes) * QUOTA_PER_UPDATE} units")
    print(f"{'='*70}\n")
    
    youtube = None
    if apply:
        youtube = get_youtube_service()
    
    results = {'success': [], 'failed': [], 'skipped': []}
    quota_used = 0
    
    for i, fix in enumerate(fixes):
        vid_id = fix['id']
        label = fix.get('label', vid_id)
        
        print(f"\n  [{i+1}/{len(fixes)}] {label}")
        print(f"    Video: https://youtu.be/{vid_id}")
        
        changes = {}
        
        # IDEMPOTENCY: In live mode, fetch current state and skip if already done
        if apply:
            live = fetch_live_video(youtube, vid_id)
            if not live:
                print(f"    ❌ Could not fetch video!")
                results['failed'].append(vid_id)
                continue
            live_title = live['snippet'].get('title', '')
            live_desc = live['snippet'].get('description', '')
            live_tags = live['snippet'].get('tags', [])
            
            # Check if title already matches
            if fix.get('new_title') and live_title == fix['new_title']:
                already_done = True
                # Also check tags
                if fix.get('new_tags'):
                    already_done = set(fix['new_tags']) == set(live_tags)
                if already_done:
                    print(f"    ⏭️  Already up-to-date, skipping")
                    results['skipped'].append(vid_id)
                    continue
        
        if fix.get('new_title'):
            print(f"    📝 Title → {fix['new_title'][:65]}")
            changes['title'] = fix['new_title']
        if fix.get('new_tags'):
            print(f"    🏷️  Tags → {len(fix['new_tags'])} tags: {', '.join(fix['new_tags'][:5])}...")
            changes['tags'] = fix['new_tags']
        
        # Build description
        if fix.get('desc_hook') or fix.get('add_hashtags'):
            if apply:
                current_desc = live_desc
            else:
                current_desc = "[CURRENT DESCRIPTION - will fetch live]"
            
            if fix.get('desc_hook'):
                # Check if hook already applied
                hook_start = fix['desc_hook'][:50]
                if apply and hook_start in current_desc:
                    print(f"    ⏭️  Description hook already present")
                    # Still apply title/tags if changed
                else:
                    new_desc = fix['desc_hook'] + CTA_BLOCK
                    if fix.get('add_hashtags'):
                        new_desc += '\n\n' + ' '.join(fix['add_hashtags'])
                    changes['description'] = new_desc
                    print(f"    📄 Description → new hook + CTA ({len(new_desc)} chars)")
            elif fix.get('add_hashtags'):
                # Just append hashtags if not already present
                hashtags_str = ' '.join(fix['add_hashtags'])
                if apply:
                    if hashtags_str not in current_desc:
                        new_desc = current_desc.rstrip() + '\n\n' + hashtags_str
                        changes['description'] = new_desc
                        print(f"    #️⃣  Hashtags → {hashtags_str}")
                    else:
                        print(f"    ⏭️  Hashtags already present, skipping")
                        results['skipped'].append(vid_id)
                        continue
                else:
                    print(f"    #️⃣  Hashtags → {hashtags_str}")
        
        if not changes:
            print(f"    ⏭️  No changes needed")
            results['skipped'].append(vid_id)
            continue
        
        if apply:
            success = update_video(youtube, vid_id, changes, dry_run=False)
            if success:
                print(f"    ✅ Updated!")
                results['success'].append(vid_id)
                quota_used += QUOTA_PER_UPDATE
                time.sleep(0.5)  # Rate limiting
            else:
                print(f"    ❌ Failed!")
                results['failed'].append(vid_id)
        else:
            print(f"    ✅ Would update (dry run)")
            results['success'].append(vid_id)
            quota_used += QUOTA_PER_UPDATE
    
    # Summary
    print(f"\n{'='*70}")
    print(f"  CAMPAIGN SUMMARY: {campaign_name.upper()}")
    print(f"{'='*70}")
    print(f"  ✅ Success: {len(results['success'])}")
    print(f"  ❌ Failed:  {len(results['failed'])}")
    print(f"  ⏭️  Skipped: {len(results['skipped'])}")
    print(f"  📊 Quota used: {quota_used} / {QUOTA_DAILY_LIMIT}")
    
    # Log results
    log_path = LOG_DIR / f"tactical_{campaign_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_data = {
        'campaign': campaign_name,
        'mode': 'live' if apply else 'dry_run',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'total': len(fixes),
        'success': len(results['success']),
        'failed': len(results['failed']),
        'skipped': len(results['skipped']),
        'quota_used': quota_used,
        'details': results,
    }
    with open(log_path, 'w') as f:
        json.dump(log_data, f, indent=2)
    print(f"  📁 Log: {log_path}")
    
    return results


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
CAMPAIGNS = {
    'quick_wins': campaign_quick_wins,
    'retro_day': campaign_retro_day,
    'womens_day': campaign_womens_day,
    'halloween': campaign_halloween,
    'propaganda': campaign_propaganda,
}

def main():
    parser = argparse.ArgumentParser(description='Tactical Seasonal Push System for remAIke_IT')
    parser.add_argument('--campaign', required=True, 
                        choices=list(CAMPAIGNS.keys()) + ['all'],
                        help='Campaign to run')
    parser.add_argument('--apply', action='store_true', help='Apply changes (default: dry run)')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of videos to process')
    args = parser.parse_args()
    
    print(f"\n{'='*70}")
    print(f"  TACTICAL SEASONAL PUSH SYSTEM — remAIke_IT")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Mode: {'🔴 LIVE' if args.apply else '🟢 DRY RUN'}")
    print(f"{'='*70}")
    
    if args.campaign == 'all':
        campaigns_to_run = list(CAMPAIGNS.keys())
    else:
        campaigns_to_run = [args.campaign]
    
    total_quota = 0
    for campaign_name in campaigns_to_run:
        fixes = CAMPAIGNS[campaign_name]()
        if args.limit > 0:
            fixes = fixes[:args.limit]
        results = execute_campaign(campaign_name, fixes, apply=args.apply)
        total_quota += len([x for x in results['success']]) * QUOTA_PER_UPDATE
    
    print(f"\n{'='*70}")
    print(f"  ALL CAMPAIGNS COMPLETE")
    print(f"  Total quota: {total_quota}")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()
