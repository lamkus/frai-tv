"""
remAIke Global Fix v2 — Complete channel cleanup
1. Fix 8 naming issues (handle, raw filename, too long)
2. Resume old plan (38 remaining videos)
3. SEO-fix ~20 new videos not in plan
"""
import os, sys, json, time, re
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import googleapiclient.discovery

os.chdir(r'D:\remaike.TV')

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
QUOTA_LIMIT = 9500  # Safety margin

def get_yt():
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return googleapiclient.discovery.build('youtube', 'v3', credentials=creds)

youtube = get_yt()
quota_used = 0
updated = 0
skipped = 0
errors = []

def quota_check(cost=50):
    global quota_used
    if quota_used + cost > QUOTA_LIMIT:
        print(f"\n🛑 QUOTA SAFETY STOP at {quota_used} units!")
        return False
    return True

def read_video(vid_id):
    """Read current video snippet (1 unit)."""
    global quota_used
    res = youtube.videos().list(part="snippet", id=vid_id).execute()
    quota_used += 1
    if not res['items']:
        return None
    return res['items'][0]['snippet']

def update_video(vid_id, snippet):
    """Update video snippet (50 units)."""
    global quota_used, updated
    youtube.videos().update(
        part="snippet",
        body={"id": vid_id, "snippet": snippet}
    ).execute()
    quota_used += 50
    updated += 1

# ═══════════════════════════════════════════════════════════
# STEP 1: Fix 8 naming issues (dynamic — read first, then fix)
# ═══════════════════════════════════════════════════════════

# Only hardcode titles for RAW FILENAMES that need complete replacement
raw_filename_overrides = {
    '3GM123aC4bE': 'Maulwurf: Das Hühnerei (1975) | 8K HQ (4K UHD)',
}

# IDs with issues (handle, too_long, no_8k)
naming_issue_ids = [
    '3GM123aC4bE',  # raw_filename, no_8k
    '4_2qWUEje-c',  # has_handle, too_long
    'h6rDmu7FBzo',  # has_handle
    'gVsamT781zU',  # has_handle, too_long
    'ZglrHGrG_oY',  # has_handle
    '-W05bAEhFvM',  # has_handle, too_long
    'RmfemqBK3tw',  # has_handle
    'ehjlG5IEZGg',  # has_handle
]

def fix_title(title, vid_id):
    """Dynamically fix a title: remove handle, add 8K, truncate."""
    original = title
    
    # Complete override for raw filenames
    if vid_id in raw_filename_overrides:
        return raw_filename_overrides[vid_id]
    
    # Remove @handle variations
    title = re.sub(r'\s*\|\s*@remAIke_IT\s*', '', title)
    title = re.sub(r'\s*@remAIke_IT\s*', '', title)
    title = re.sub(r'\s*@remAIke_\s*', '', title)
    title = re.sub(r'\s*@remAIke\s*', '', title)
    title = title.rstrip(' |')
    title = title.strip()
    
    # Ensure 8K in title
    if '8K' not in title:
        title = title + ' | 8K HQ'
    
    # Truncate if >70 chars
    if len(title) > 70:
        # Try to keep the quality suffix
        parts = title.rsplit('|', 1)
        if len(parts) > 1:
            suffix = parts[-1].strip()
            base = parts[0].strip()
            max_base = 70 - len(suffix) - 3  # " | " 
            if max_base > 20:
                title = f"{base[:max_base].rstrip()} | {suffix}"
            else:
                title = title[:67] + '...'
        else:
            title = title[:67] + '...'
    
    return title

print("═" * 60)
print("  STEP 1: Fix 8 naming issues")
print("═" * 60)

for vid_id in naming_issue_ids:
    if not quota_check():
        break
    try:
        snippet = read_video(vid_id)
        if not snippet:
            print(f"  ⏩ {vid_id} — not found (deleted?)")
            skipped += 1
            continue
        
        old_title = snippet['title']
        new_title = fix_title(old_title, vid_id)
        
        # Check if fix actually changed anything
        if old_title == new_title:
            print(f"  ⏩ Already OK: {new_title[:50]}")
            skipped += 1
            continue
        
        snippet['title'] = new_title
        
        # Fix tags if >15
        tags = snippet.get('tags', [])
        if len(tags) > 15:
            snippet['tags'] = tags[:15]
        
        update_video(vid_id, snippet)
        print(f"  ✅ [{quota_used}q] {old_title[:35]} → {new_title[:35]}")
        time.sleep(0.5)
        
    except Exception as e:
        if 'quotaExceeded' in str(e):
            print(f"\n🛑 QUOTA EXCEEDED at {quota_used} units!")
            break
        errors.append({'id': vid_id, 'error': str(e)})
        print(f"  ❌ {vid_id}: {e}")

print(f"\n  Step 1 done: {updated} updated, {skipped} skipped, {len(errors)} errors")
print(f"  Quota: {quota_used} units\n")

# ═══════════════════════════════════════════════════════════
# STEP 2: Resume old plan (38 remaining)
# ═══════════════════════════════════════════════════════════

print("═" * 60)
print("  STEP 2: Resume old fix plan (38 remaining)")
print("═" * 60)

with open('config/channel_master_fix_prioritized.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

step2_updated = 0
step2_skipped = 0

for item in plan:
    if not quota_check():
        break
    vid_id = item['id']
    try:
        snippet = read_video(vid_id)
        if not snippet:
            step2_skipped += 1
            continue
        
        # Idempotency check
        if snippet['title'] == item['new_title']:
            step2_skipped += 1
            continue
        
        # Apply changes
        snippet['title'] = item['new_title']
        snippet['tags'] = item['new_tags']
        
        if item.get('new_description') and item['new_description'] != snippet['description']:
            snippet['description'] = item['new_description']
        
        update_video(vid_id, snippet)
        print(f"  ✅ [{quota_used}q] {item['new_title'][:55]}")
        time.sleep(0.5)
        step2_updated += 1
        
    except Exception as e:
        if 'quotaExceeded' in str(e):
            print(f"\n🛑 QUOTA EXCEEDED at {quota_used} units!")
            break
        errors.append({'id': vid_id, 'error': str(e)})
        print(f"  ❌ {vid_id}: {e}")

print(f"\n  Step 2 done: {step2_updated} updated, {step2_skipped} skipped")
print(f"  Quota: {quota_used} units\n")

# ═══════════════════════════════════════════════════════════
# STEP 3: Fix new videos not in plan — SEO compliance
# ═══════════════════════════════════════════════════════════

print("═" * 60)
print("  STEP 3: Fix new videos not in plan")
print("═" * 60)

# New videos that need SEO check (exclude deleted, dupes, already-ok)
new_video_ids = [
    # Maulwurf new uploads (raw filenames!)
    'j4aBiGJcEY8',  # e21 der maulwurf als fotograf
    'UsppP3mPwHM',  # e18 der maulwurf als uhrmacher
    'wjpCNxf5SsY',  # e16 der maulwurf und die streichhölzer
    'ts5qtXqneq8',  # e13 der maulwurf als maler
    # NASA / Skylab
    'sp1AzW-_rV0',  # Skylab 3
    'ndAzCIUxo-c',  # Skylab Gyroscopes
    # Newer uploads since plan
    'hvJsq7z3sjg',  # Die drei Mäuse-Musketiere
    'HGg-g6SwrrQ',  # Reefer Madness
    'aKcgVrL3wvQ',  # What This Country Needs
    'CKLYjy30fIw',  # Vimeo 8K Clip
    'TWodj8k8-zU',  # Alfred J. Kwak 29
    'Q_hgdk3UaJs',  # Alfred J. Kwak 31
    '_9GLuLakxgw',  # Burlesque Short
    's_0yOzCKDa8',  # December 7th Pearl Harbor
    '70Ni30lbXRc',  # Glücksbärchis
    'HCj_w3pBxlc',  # Blackmail Hitchcock
    'A8LWgWF5f5k',  # Hut-Sut Song Soundie
    'eX5cbYwNvnI',  # Betty Boop 19 Limited
    'eF81rBeXbzk',  # Hindenburg
    'tk3DHvp9CFs',  # Astronomer's Dream
    'TLdsnAi8bWg',  # Silly Symphony Skeleton Dance
    'u5poUF6KQfA',  # Porky's Cafe
    '5_Rx2lmeRfw',  # Porky's Bear Facts
    'U6CAhg95Izk',  # Porky's Bear Facts (dupe?)
]

# Better titles for raw filenames
title_overrides = {
    'j4aBiGJcEY8': 'Maulwurf: Als Fotograf (1975) | 8K HQ (4K UHD)',
    'UsppP3mPwHM': 'Maulwurf: Als Uhrmacher (1974) | 8K HQ (4K UHD)',
    'wjpCNxf5SsY': 'Maulwurf: Die Streichhölzer (1974) | 8K HQ (4K UHD)',
    'ts5qtXqneq8': 'Maulwurf: Als Maler (1972) | 8K HQ (4K UHD)',
}

# SEO description template
CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT
"""

step3_updated = 0
step3_skipped = 0

for vid_id in new_video_ids:
    if not quota_check():
        break
    try:
        snippet = read_video(vid_id)
        if not snippet:
            step3_skipped += 1
            continue
        
        changed = False
        old_title = snippet['title']
        
        # Title override?
        if vid_id in title_overrides:
            new_title = title_overrides[vid_id]
            if snippet['title'] != new_title:
                snippet['title'] = new_title
                changed = True
        
        # Remove @handle from title
        if '@remAIke_IT' in snippet['title'] or '@remAIke' in snippet['title']:
            snippet['title'] = re.sub(r'\s*\|\s*@remAIke_IT\s*', '', snippet['title'])
            snippet['title'] = re.sub(r'\s*@remAIke_IT\s*', '', snippet['title'])
            snippet['title'] = re.sub(r'\s*@remAIke\s*', '', snippet['title'])
            changed = True
        
        # Ensure 8K in title
        if '8K' not in snippet['title']:
            snippet['title'] = snippet['title'].rstrip() + ' | 8K HQ'
            changed = True
        
        # Truncate if too long
        if len(snippet['title']) > 70:
            # Smart truncation: keep before last |, add 8K
            parts = snippet['title'].rsplit('|', 1)
            if len(parts) > 1:
                base = parts[0].strip()[:60]
                snippet['title'] = f"{base} | 8K HQ"
            else:
                snippet['title'] = snippet['title'][:67] + '...'
            changed = True
        
        desc = snippet.get('description', '')
        
        # Add CTA if missing
        if 'www.remaike.IT' not in desc:
            desc = desc.rstrip() + '\n' + CTA_BLOCK
            snippet['description'] = desc
            changed = True
        
        # Add hashtags if missing (check last 200 chars)
        tail = desc[-200:] if len(desc) > 200 else desc
        if '#' not in tail:
            # Detect series for hashtags
            title_lower = snippet['title'].lower()
            if 'maulwurf' in title_lower or 'krtek' in title_lower:
                hashtags = '\n\n#DerKleineMaulwurf #Krtek #8K #PublicDomain #VintageAnimation'
            elif 'soundie' in title_lower:
                hashtags = '\n\n#Soundie #VintageMusic #1940s #Jazz #8K'
            elif 'wochenschau' in title_lower:
                hashtags = '\n\n#Wochenschau #WWII #8K #History #PublicDomain'
            elif 'betty boop' in title_lower:
                hashtags = '\n\n#BettyBoop #8K #VintageCartoon #PublicDomain #1930s'
            elif 'alfred' in title_lower or 'kwak' in title_lower:
                hashtags = '\n\n#AlfredJKwak #8K #Kinderserie #Animation #Classic'
            elif 'superman' in title_lower:
                hashtags = '\n\n#Superman #Fleischer #8K #PublicDomain #Animation'
            elif 'porky' in title_lower or 'looney' in title_lower:
                hashtags = '\n\n#LooneyTunes #PorkyPig #8K #PublicDomain #VintageCartoon'
            elif 'skylab' in title_lower or 'nasa' in title_lower:
                hashtags = '\n\n#NASA #Skylab #8K #SpaceHistory #Documentary'
            else:
                hashtags = '\n\n#8K #PublicDomain #VintageFilm #ClassicCinema #Restored'
            
            snippet['description'] = desc + hashtags
            changed = True
        
        # Fix tags >15
        tags = snippet.get('tags', [])
        if len(tags) > 15:
            snippet['tags'] = tags[:15]
            changed = True
        
        if not changed:
            print(f"  ⏩ Already compliant: {snippet['title'][:50]}")
            step3_skipped += 1
            continue
        
        update_video(vid_id, snippet)
        print(f"  ✅ [{quota_used}q] {old_title[:30]} → {snippet['title'][:30]}")
        time.sleep(0.5)
        step3_updated += 1
        
    except Exception as e:
        if 'quotaExceeded' in str(e):
            print(f"\n🛑 QUOTA EXCEEDED at {quota_used} units!")
            break
        errors.append({'id': vid_id, 'error': str(e)})
        print(f"  ❌ {vid_id}: {e}")

print(f"\n  Step 3 done: {step3_updated} updated, {step3_skipped} skipped")

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print(f"  TOTAL SUMMARY")
print(f"═" * 60)
print(f"  Total updated:   {updated}")
print(f"  Total skipped:   {skipped + step2_skipped + step3_skipped}")
print(f"  Total errors:    {len(errors)}")
print(f"  Quota used:      {quota_used} / 10,000")
print(f"  Quota remaining: {10000 - quota_used}")

if errors:
    print(f"\n  Errors:")
    for e in errors:
        print(f"    {e['id']}: {e['error'][:80]}")

# Save report
report = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'total_updated': updated,
    'total_skipped': skipped + step2_skipped + step3_skipped,
    'total_errors': len(errors),
    'quota_used': quota_used,
    'errors': errors,
}
with open('config/global_fix_v2_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n  Report saved to config/global_fix_v2_report.json")
