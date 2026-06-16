#!/usr/bin/env python3
"""
Batch fix remaining 32 videos with Score < 90.
Groups:
  1. CRITICAL: Raw filenames + empty descriptions (3 videos)
  2. Wochenschau DUPEs: Add www.remaike.IT, trim hashtags (8 videos)
  3. Title too long: Shorten to <=70 chars (various)
  4. Minor fixes: @channel removal, hashtag trim, missing links

Cost: 32 × 50 = 1600 quota (+ 1 READ batch = ~1601 total)
"""
import json
import sys
import re
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ─── OAuth ────────────────────────────────────────────────────────────
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth.get('access_token') or oauth.get('token'),
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# ─── Standard description blocks ──────────────────────────────────────

BRAND_HEADER = """WE HAVE THE BEST VERSION FOR YOU!
SHARE AND PUSH US TO GET THE WHOLE INTERNET UPGRADED :)

@remAIke_IT | www.remAIke.IT
www.FRai.TV - All videos organized...."""

CTA_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more 8K classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

QUALITY_BLOCK = """8K HQ Edition by remAIke:
• AI-upscaled from archival source
• Enhanced clarity for modern displays
• Original audio preserved"""

# ─── Helper functions ──────────────────────────────────────────────────

def trim_hashtags(desc, keep=5):
    """Keep only the first `keep` hashtags, remove the rest."""
    lines = desc.split('\n')
    new_lines = []
    hashtag_count = 0
    for line in lines:
        words = line.split()
        new_words = []
        for word in words:
            if word.startswith('#') and len(word) > 1:
                hashtag_count += 1
                if hashtag_count <= keep:
                    new_words.append(word)
                # else skip it
            else:
                new_words.append(word)
        new_lines.append(' '.join(new_words))
    return '\n'.join(new_lines)

def inject_website_link(desc):
    """Add www.remaike.IT link if missing. Inject before hashtags or at end."""
    if 'remaike.it' in desc.lower() or 'remaike.tv' in desc.lower():
        return desc  # Already has it
    
    # Try to inject before the hashtag line
    lines = desc.split('\n')
    insert_idx = len(lines)
    for i, line in enumerate(lines):
        if line.strip().startswith('#') and len(line.strip()) > 2:
            insert_idx = i
            break
    
    inject = "\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT\n"
    lines.insert(insert_idx, inject)
    return '\n'.join(lines)

def inject_channel_link(desc):
    """Add @remAIke_IT channel link if missing."""
    if '@remAIke_IT' in desc or 'youtube.com/@remAIke' in desc:
        return desc
    # Already handled by inject_website_link which adds both
    return desc

# ─── Fix definitions ──────────────────────────────────────────────────

def build_fixes():
    """Build the list of all fixes to apply."""
    fixes = []
    
    # ═══ GROUP 1: CRITICAL — Raw filenames + empty descriptions ═══════
    
    # 1a. "what this country needs sls 8K HQ" → private, raw filename
    fixes.append({
        'id': 'aKcgVrL3wvQ',
        'group': 'CRITICAL',
        'changes': {
            'title': 'What This Country Needs (1930s) | Cartoon | 8K HQ (4K UHD)',
            'categoryId': '1',
            'tags': [
                'What This Country Needs', 'cartoon', '1930s', 'vintage animation',
                '8K', '4K UHD', 'remAIke', 'public domain', 'classic cartoon',
                'political cartoon', 'depression era', 'short film'
            ],
            'description': f"""🎬 What This Country Needs (1930s) | Vintage Cartoon

{BRAND_HEADER}

🇬🇧 English:
A vintage animated short from the 1930s — a humorous take on what the country really needs.
Classic political satire from the Depression era, restored in stunning 8K quality.

🇩🇪 Deutsch:
Ein klassischer Zeichentrickfilm aus den 1930er Jahren — ein humorvoller Blick auf das, was das Land wirklich braucht.
Politische Satire aus der Ära der Großen Depression, restauriert in atemberaubender 8K-Qualität.

{QUALITY_BLOCK}

{CTA_BLOCK}

#VintageCartoon #1930s #8K #PublicDomain #ClassicAnimation""",
        }
    })
    
    # 1b. "Glücksbärchis Abenteuer Im Wunderland" → private, empty desc
    fixes.append({
        'id': '70Ni30lbXRc',
        'group': 'CRITICAL',
        'changes': {
            'title': 'Glücksbärchis: Abenteuer im Wunderland | 8K HQ (4K UHD)',
            'categoryId': '1',
            'tags': [
                'Glücksbärchis', 'Care Bears', 'Abenteuer im Wunderland',
                'Adventures in Wonderland', 'Zeichentrick', '8K', '4K UHD',
                'remAIke', 'Kinderserie', '90er', 'deutsch', 'classic cartoon',
                'animation', 'public domain'
            ],
            'description': f"""🎬 Glücksbärchis: Abenteuer im Wunderland

{BRAND_HEADER}

🇩🇪 Deutsch:
Die Glücksbärchis erleben ein magisches Abenteuer im Wunderland!
Ein Klassiker der Kinderanimation, restauriert in brillanter 8K-Qualität.

🇬🇧 English:
The Care Bears embark on a magical adventure in Wonderland!
A classic of children's animation, restored in brilliant 8K quality.

{QUALITY_BLOCK}

{CTA_BLOCK}

#Glücksbärchis #CareBears #8K #Zeichentrick #remAIke""",
        }
    })
    
    # ═══ GROUP 2: Skeleton Dance — too long + missing links ═══════════
    
    fixes.append({
        'id': 'TLdsnAi8bWg',
        'group': 'TITLE_FIX',
        'changes': {
            'title': 'Silly Symphony: The Skeleton Dance (1929) | 8K HQ (4K UHD)',
            # Keep existing tags but trim to 15
            # Description: will inject links
        },
        'desc_action': 'inject_links_trim_hashtags',
    })
    
    # ═══ GROUP 3: Porky Pig titles too long ═══════════════════════════
    
    fixes.append({
        'id': 'u5poUF6KQfA',
        'group': 'TITLE_FIX',
        'changes': {
            'title': "Porky Pig (45/159): Porky's Cafe (1942) | 8K HQ (4K UHD)",
        },
        'desc_action': 'inject_links_trim_hashtags',
    })
    
    fixes.append({
        'id': 'U6CAhg95Izk',
        'group': 'TITLE_FIX',
        'changes': {
            'title': "Porky Pig (40/159): Porky's Bear Facts (1941) | 8K HQ (4K UHD)",
        },
        'desc_action': 'inject_links_trim_hashtags',
    })
    
    # ═══ GROUP 4: Blackmail — too long + extra tags/hashtags ══════════
    
    fixes.append({
        'id': 'HCj_w3pBxlc',
        'group': 'TITLE_FIX',
        'changes': {
            'title': 'Blackmail (1929) | Alfred Hitchcock | 8K HQ (4K UHD)',
        },
        'desc_action': 'trim_hashtags',
    })
    
    # ═══ GROUP 5: Vimeo Clip — missing website link ═══════════════════
    
    fixes.append({
        'id': 'CKLYjy30fIw',
        'group': 'MINOR_FIX',
        'changes': {
            'title': 'Vimeo 8K Clip Derives (4m56 / 9m10)',
        },
        'desc_action': 'inject_links',
    })
    
    # ═══ GROUP 6: Porky Pig Bear Facts duplicate — missing links ══════
    
    fixes.append({
        'id': '5_Rx2lmeRfw',
        'group': 'MINOR_FIX',
        'changes': {
            'title': "Porky Pig: Porky's Bear Facts (1941) | 8K HQ (4K UHD)",
        },
        'desc_action': 'inject_links',
    })
    
    # ═══ GROUP 7: 8 Wochenschau DUPEs — inject links + trim hashtags ═
    
    wochenschau_dupes = [
        ('SV7o2XaYZyc', None),  # Keep title as-is
        ('LCa6Klpi8ts', None),
        ('ULzsDOb2x3U', None),
        ('iFSHNS7kVgQ', None),
        ('sGZg6lIHFh8', None),
        ('LjGFowS8qHI', None),
        ('1O8sVLS-zfI', None),
        ('D_kLmNFlbZI', None),
    ]
    
    for vid_id, new_title in wochenschau_dupes:
        fix = {
            'id': vid_id,
            'group': 'WOCHENSCHAU_FIX',
            'changes': {},
            'desc_action': 'inject_links_trim_hashtags',
        }
        if new_title:
            fix['changes']['title'] = new_title
        fixes.append(fix)
    
    # ═══ GROUP 8: Atomic Bomb Newsreel — wrong category ═══════════════
    
    fixes.append({
        'id': '9AgSJyMnxi8',
        'group': 'CATEGORY_FIX',
        'changes': {
            'categoryId': '27',  # Education
        },
    })
    
    # ═══ GROUP 9: Title too long — various public videos ══════════════
    
    title_fixes = [
        ('xzZ9yB5lJ9s', 'Ferdy: Die abenteuerliche Rettung Bambini | 8K HQ (4K UHD)'),  # 58 ✅
        ('3gzbxznJ_PM', 'Popeye Movie Marathon | Fleischer Studios | 8K HQ (4K UHD)'),  # 57 ✅
        ('Ucub3igzk2U', "Dick Whittington's Cat (1935) | 8K HQ (4K UHD)"),  # 49 ✅
        ('1mVWh_B6_00', 'Little Lambkins (1940) | Fleischer Color Classic | 8K HQ (4K UHD)'),  # 62 ✅
        ('fVp_aVBZhak', 'Gabby: King for a Day (1940) | Fleischer | 8K HQ (4K UHD)'),  # 56 ✅
        ('4VO2weDCfi0', 'The Little Stranger (1936) | Fleischer | 8K HQ (4K UHD)'),  # 55 ✅
        ('PzbAE96bG1Q', 'Hawaiian Birds (1936) | Fleischer Color Classic | 8K HQ (4K UHD)'),  # 61 ✅
        ('hvdNZy8AciI', 'Casper (15/55): True Boo (1952) | 8K HQ (4K UHD)'),  # 50 ✅
        ('EpzJcD6zkvs', 'Suzy Snowflake (1953) | Christmas Short | 8K HQ (4K UHD)'),  # 55 ✅
        ('U-WD47NSgAE', 'Coca‑Cola Christmas Trucks (1995) | 8K HQ (4K UHD)'),  # 51 ✅
        ('WSjkAZkPbKs', 'Coca‑Cola Christmas Trucks – EPIC Edit (1995) | 8K HQ (4K UHD)'),  # 62 ✅
        ('yIQCHpjp4NE', 'Batman & Robin Meet Santa Claus (1966) | 8K HQ (4K UHD)'),  # 55 ✅
        ('Zu_iBCd5NJc', 'Biological Warfare Documentary (1952) | 8K HQ (4K UHD)'),  # 55 ✅
        ('YbC2JynVCRA', 'A Bill of Divorcement (1932) | Hepburn | 8K HQ (4K UHD)'),  # 56 ✅
        ('dGD2CeoZX68', 'A Christmas Carol (1984) | George C. Scott | 8K HQ (4K UHD)'),  # 59 ✅
    ]
    
    for vid_id, new_title in title_fixes:
        fixes.append({
            'id': vid_id,
            'group': 'TITLE_SHORTEN',
            'changes': {
                'title': new_title,
            },
        })
    
    return fixes


def apply_fix(youtube, fix, live_data):
    """Apply a single fix. Returns True on success."""
    vid_id = fix['id']
    snippet = live_data['snippet']
    changes = fix.get('changes', {})
    desc_action = fix.get('desc_action', None)
    
    # Start with current values
    new_title = changes.get('title', snippet['title'])
    new_desc = snippet.get('description', '')
    new_tags = changes.get('tags', snippet.get('tags', []))
    new_category = changes.get('categoryId', snippet.get('categoryId', '1'))
    
    # Apply description actions
    if desc_action:
        if 'inject_links' in desc_action:
            new_desc = inject_website_link(new_desc)
            new_desc = inject_channel_link(new_desc)
        if 'trim_hashtags' in desc_action:
            new_desc = trim_hashtags(new_desc, keep=5)
    
    # If full description override in changes
    if 'description' in changes:
        new_desc = changes['description']
    
    # Trim tags to 15
    if len(new_tags) > 15:
        new_tags = new_tags[:15]
    
    # Remove @remAIke_IT from title if present
    if '@remAIke_IT' in new_title or '@remaike' in new_title.lower():
        new_title = re.sub(r'\s*\|\s*@remAIke_IT', '', new_title)
        new_title = re.sub(r'\s*@remAIke_IT', '', new_title)
        new_title = re.sub(r'\s*@remaike\s*it', '', new_title, flags=re.IGNORECASE)
        new_title = new_title.strip()
    
    # Validate
    assert len(new_title) <= 70, f"Title still too long: {len(new_title)} chars: {new_title}"
    assert len(new_tags) <= 15, f"Still too many tags: {len(new_tags)}"
    
    body = {
        'id': vid_id,
        'snippet': {
            'title': new_title,
            'description': new_desc,
            'tags': new_tags,
            'categoryId': new_category,
        }
    }
    
    resp = youtube.videos().update(part='snippet', body=body).execute()
    return resp


def main():
    fixes = build_fixes()
    
    print("═" * 78)
    print(f"  BATCH FIX — {len(fixes)} Videos")
    print(f"  Quota Cost: {len(fixes)} × 50 = {len(fixes) * 50} units + READ")
    print("═" * 78)
    
    # Group summary
    groups = {}
    for f in fixes:
        g = f['group']
        groups[g] = groups.get(g, 0) + 1
    for g, c in sorted(groups.items()):
        print(f"  {g}: {c} videos")
    
    # Preview titles
    print(f"\n📋 TITLE CHANGES:")
    print("─" * 78)
    for f in fixes:
        new_title = f['changes'].get('title', '(keep current)')
        chars = len(new_title) if new_title != '(keep current)' else '-'
        print(f"  {f['id']} [{f['group']}]")
        print(f"    → {new_title[:65]} ({chars})")
    
    if '--apply' not in sys.argv:
        print(f"\n⚠️  DRY RUN — Add --apply to execute")
        print(f"    python scripts/youtube/fix_batch_remaining.py --apply")
        return
    
    # Fetch live data for all videos
    all_ids = [f['id'] for f in fixes]
    print(f"\n📡 Fetching live data for {len(all_ids)} videos...")
    live_map = {}
    for i in range(0, len(all_ids), 50):
        batch = all_ids[i:i+50]
        resp = youtube.videos().list(part='snippet,status', id=','.join(batch)).execute()
        for v in resp.get('items', []):
            live_map[v['id']] = v
    
    print(f"✅ Got live data for {len(live_map)} videos")
    
    # Apply fixes
    print(f"\n🚀 APPLYING {len(fixes)} FIXES...")
    print("─" * 78)
    success = 0
    failed = 0
    
    for fix in fixes:
        vid_id = fix['id']
        if vid_id not in live_map:
            print(f"  ⚠️ {vid_id}: Not found in live data, skipping")
            failed += 1
            continue
        
        try:
            resp = apply_fix(youtube, fix, live_map[vid_id])
            new_title = resp['snippet']['title']
            print(f"  ✅ {new_title[:65]}")
            success += 1
        except Exception as e:
            print(f"  ❌ {vid_id}: {e}")
            failed += 1
            # On quota error, stop immediately
            if 'quotaExceeded' in str(e) or 'quota' in str(e).lower():
                print(f"\n🛑 QUOTA EXCEEDED! Stopping.")
                break
    
    print(f"\n{'═' * 78}")
    print(f"  Results: {success} updated, {failed} failed")
    print(f"  Quota used: ~{success * 50 + 1} units")
    print(f"{'═' * 78}")


if __name__ == "__main__":
    main()
