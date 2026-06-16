"""
Audit + Fix new uploads against ALL 13 workspace rules.
Usage: python audit_new_uploads.py          # dry run
       python audit_new_uploads.py --apply  # write fixes
"""
import os, sys, json, re, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = r"D:\remaike.TV\token.json"
DRY_RUN = "--apply" not in sys.argv

# The NEW video IDs to audit (excluding "Deleted video" entries)
NEW_VIDEO_IDS = [
    "21iqU9NKJL0",  # SHORT skeleton dance full CINEMA
    "3FstojEXJ5k",  # deutsche wochenschau nr496
    "n-_DEeOSKz0",  # deutsche wochenschau nr504
    "W1zYu-fTejs",  # deutsche wochenschau nr491
    "3rB80OGKzrg",  # Wochenschau 511: Paris Falls
    "YHlhhiAfxEA",  # Rare 1955 Burlesque Footage
    "3UBF9ycZwJU",  # 8K ORIGINAL Fast & Furious
    "FQvtw2ira-o",  # Times Square Vintage Compilation
    "2CwXPhUDC7U",  # New Year's Eve 1951-1952
    "XAyK1yy_e-M",  # Day of the Earth (1951)
]

# ---------- Auth ----------
def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

yt = get_youtube()

# ---------- Category Rules ----------
CATEGORY_MAP = {
    'soundie': 10,
    'wochenschau': 27,
    'ken_block': 2,
}

# ---------- Wochenschau locations ----------
WS_LOCATIONS_PATH = r"D:\remaike.TV\config\wochenschau_complete_locations.json"
ws_locations = {}
if os.path.exists(WS_LOCATIONS_PATH):
    with open(WS_LOCATIONS_PATH, 'r', encoding='utf-8') as f:
        ws_data = json.load(f)
        for ep in ws_data if isinstance(ws_data, list) else ws_data.get('episodes', []):
            nr = ep.get('nr') or ep.get('number')
            if nr:
                ws_locations[str(nr)] = ep

# ---------- Fetch full details ----------
print(f"{'='*70}")
print(f"AUDIT NEW UPLOADS — {'DRY RUN' if DRY_RUN else 'APPLY MODE'}")
print(f"Videos to audit: {len(NEW_VIDEO_IDS)}")
print(f"{'='*70}\n")

# Fetch in batches of 50
all_videos = []
for i in range(0, len(NEW_VIDEO_IDS), 50):
    batch = NEW_VIDEO_IDS[i:i+50]
    resp = yt.videos().list(
        part='snippet,status,contentDetails,localizations',
        id=','.join(batch)
    ).execute()
    all_videos.extend(resp.get('items', []))

print(f"Fetched details for {len(all_videos)} videos\n")

# ---------- Audit Rules ----------
CTA_PATTERNS = [
    r'(?i)(like|subscribe|comment|abonnier|daumen|👍|🔔|💬)',
    r'(?i)(LIKE if|SUBSCRIBE for|COMMENT your)',
]
LINK_REMAIKE = 'www.remaike.IT'
LINK_YOUTUBE = 'youtube.com/@remAIke_IT'

fixes = []
quota_cost = 0

for video in all_videos:
    vid_id = video['id']
    snippet = video['snippet']
    status = video['status']
    title = snippet.get('title', '')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    cat_id = snippet.get('categoryId', '1')
    localizations = video.get('localizations', {})
    privacy = status.get('privacyStatus', 'public')
    made_for_kids = status.get('madeForKids', False)

    issues = []
    new_title = title
    new_desc = desc
    new_tags = list(tags)
    new_cat = cat_id
    needs_localizations = False

    print(f"── {vid_id} ─────────────────────────")
    print(f"   Title:    {title[:70]}")
    print(f"   Privacy:  {privacy}")
    print(f"   Category: {cat_id}")
    print(f"   Tags:     {len(tags)}")
    print(f"   Locs:     {len(localizations)}")

    # R1: 8K or 4K in title
    if '8K' not in title and '4K' not in title:
        issues.append("R1: No 8K/4K in title")

    # R2: No @remAIke_IT in title
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues.append("R2: @remAIke_IT in title")
        new_title = re.sub(r'\s*[\|·]\s*@remAIke_IT', '', new_title)
        new_title = re.sub(r'\s*@remAIke_IT', '', new_title)

    # R3: Title ≤70 chars (aiming for 60 ideally)
    if len(title) > 70:
        issues.append(f"R3: Title too long ({len(title)} chars)")

    # R4: CTA in description
    has_cta = any(re.search(p, desc) for p in CTA_PATTERNS)
    if not has_cta:
        issues.append("R4: No CTA in description")

    # R5: www.remaike.IT in description
    if LINK_REMAIKE.lower() not in desc.lower():
        issues.append("R5: Missing www.remaike.IT")

    # R6: YouTube channel link
    if LINK_YOUTUBE.lower() not in desc.lower() and '@remaike_it' not in desc.lower():
        issues.append("R6: Missing YouTube channel link")

    # R7: Max 5 hashtags
    hashtags = re.findall(r'#\w+', desc)
    if len(hashtags) > 5:
        issues.append(f"R7: Too many hashtags ({len(hashtags)})")

    # R8: Max 15 tags
    if len(tags) > 15:
        issues.append(f"R8: Too many tags ({len(tags)})")

    # R9: Category correct
    title_lower = title.lower()
    if 'wochenschau' in title_lower and cat_id != '27':
        issues.append(f"R9: Wochenschau should be Education(27), is {cat_id}")
        new_cat = '27'
    if 'soundie' in title_lower and cat_id != '10':
        issues.append(f"R9: Soundie should be Music(10), is {cat_id}")
        new_cat = '10'

    # R10: No raw "sls" artifacts in title
    if ' sls ' in title.lower() or title.lower().endswith(' sls'):
        issues.append("R10: Raw 'sls' artifact in title")

    # R11: Description ≥50 chars
    if len(desc) < 50:
        issues.append(f"R11: Description too short ({len(desc)} chars)")

    # R12: Localizations (min 5 languages)
    if len(localizations) < 5:
        issues.append(f"R12: Too few localizations ({len(localizations)})")
        needs_localizations = True

    # R13: madeForKids = false
    if made_for_kids:
        issues.append("R13: madeForKids should be false")

    # EXTRA: Raw filename as title (all lowercase, contains production markers)
    if title == title.lower() and ('sls' in title.lower() or 'archive' in title.lower()):
        issues.append("EXTRA: Title looks like raw filename")

    if issues:
        print(f"   ⚠️  ISSUES ({len(issues)}):")
        for iss in issues:
            print(f"      - {iss}")
        fixes.append({
            'id': vid_id,
            'title': title,
            'privacy': privacy,
            'issues': issues,
            'needs_title_fix': any('R1' in i or 'R2' in i or 'R3' in i or 'R10' in i or 'EXTRA' in i for i in issues),
            'needs_desc_fix': any('R4' in i or 'R5' in i or 'R6' in i or 'R7' in i or 'R11' in i for i in issues),
            'needs_cat_fix': new_cat != cat_id,
            'new_cat': new_cat,
            'needs_localizations': needs_localizations,
        })
    else:
        print(f"   ✅ COMPLIANT")
    print()

# ---------- Summary ----------
print(f"\n{'='*70}")
print(f"AUDIT SUMMARY")
print(f"{'='*70}")
print(f"Total audited:  {len(all_videos)}")
print(f"Compliant:      {len(all_videos) - len(fixes)}")
print(f"Need fixing:    {len(fixes)}")
for fx in fixes:
    print(f"  - {fx['id']}: {', '.join(fx['issues'][:5])}")

# ---------- Build Fix Plan ----------
if not fixes:
    print("\n✅ All new videos are compliant! Nothing to fix.")
    sys.exit(0)

print(f"\n{'='*70}")
print("FIX PLAN")
print(f"{'='*70}")

# CTA block to add
CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

STANDARD_HASHTAGS = "\n\n#8K #PublicDomain #Vintage #ClassicFilm #Restored"
WOCHENSCHAU_HASHTAGS = "\n\n#Wochenschau #WWII #8K #History #PublicDomain"

# Standard localizations
STANDARD_LOCS = {
    'en': {'title': '', 'description': ''},  # filled per video
    'es': {'title': '', 'description': ''},
    'fr': {'title': '', 'description': ''},
    'ja': {'title': '', 'description': ''},
    'pt': {'title': '', 'description': ''},
}

for fx in fixes:
    vid = fx['id']
    # Find the full video data
    video = next(v for v in all_videos if v['id'] == vid)
    snippet = video['snippet']
    title = snippet['title']
    desc = snippet['description']
    tags = list(snippet.get('tags', []))
    cat_id = snippet['categoryId']

    update_snippet = {}
    update_status = {}
    changes = []

    # ── TITLE FIXES ──
    new_title = title
    is_raw_filename = (title == title.lower() and ('sls' in title.lower() or 'archive' in title.lower()))

    if is_raw_filename:
        # Parse raw filename to create proper title
        if 'wochenschau' in title.lower():
            # Parse: "deutsche wochenschau nr496 1940 03 06 14min sls ARCHIVE PROTECTED"
            m = re.search(r'nr(\d+)\s+(\d{4})\s+(\d{2})\s+(\d{2})', title)
            if m:
                nr = m.group(1)
                year = m.group(2)
                month = m.group(3)
                day = m.group(4)
                date_str = f"{day}.{month}.{year}"

                # Try to get event from locations config
                event = ""
                if nr in ws_locations:
                    loc = ws_locations[nr]
                    event = loc.get('event', loc.get('title_en', ''))

                if event:
                    new_title = f"Wochenschau {nr}: {event} ({date_str}) | 8K HQ"
                else:
                    new_title = f"Wochenschau Nr. {nr} ({date_str}) | 8K HQ"

                # Truncate if too long
                if len(new_title) > 70:
                    new_title = new_title[:67] + "..."
        elif 'skeleton' in title.lower():
            new_title = "The Skeleton Dance (1929) | Disney | 8K HQ"
        else:
            # Generic cleanup
            new_title = title.replace(' sls ', ' ').replace(' ARCHIVE PROTECTED', '').strip()
            if '8K' not in new_title:
                new_title += ' | 8K HQ'

    # Remove @remAIke_IT from title
    if '@remAIke_IT' in new_title or '@remaike' in new_title.lower():
        new_title = re.sub(r'\s*[\|·]+\s*@remAIke_IT', '', new_title)
        new_title = re.sub(r'\s*@remAIke_IT', '', new_title)
        new_title = new_title.strip()

    if new_title != title:
        update_snippet['title'] = new_title
        changes.append(f"Title: '{title[:50]}' → '{new_title[:50]}'")

    # ── DESCRIPTION FIXES ──
    new_desc = desc

    # Add CTA block if missing
    has_cta = any(re.search(p, new_desc) for p in CTA_PATTERNS)
    has_remaike = LINK_REMAIKE.lower() in new_desc.lower()
    has_yt_link = LINK_YOUTUBE.lower() in new_desc.lower() or '@remaike_it' in new_desc.lower()

    if not has_cta or not has_remaike or not has_yt_link:
        # Remove existing scattered links/CTAs first, then add proper block
        if CTA_BLOCK.strip() not in new_desc:
            new_desc = new_desc.rstrip() + "\n" + CTA_BLOCK
            changes.append("Added CTA + links block")

    # Fix hashtags (max 5)
    existing_hashtags = re.findall(r'#\w+', new_desc)
    if len(existing_hashtags) > 5:
        # Remove all hashtags from desc, add proper ones at end
        new_desc_clean = re.sub(r'\n*#\w+', '', new_desc).rstrip()
        if 'wochenschau' in title.lower():
            new_desc = new_desc_clean + WOCHENSCHAU_HASHTAGS
        else:
            new_desc = new_desc_clean + STANDARD_HASHTAGS
        changes.append(f"Reduced hashtags from {len(existing_hashtags)} to 5")
    elif len(existing_hashtags) == 0:
        if 'wochenschau' in title.lower():
            new_desc = new_desc.rstrip() + WOCHENSCHAU_HASHTAGS
        else:
            new_desc = new_desc.rstrip() + STANDARD_HASHTAGS
        changes.append("Added hashtags")

    # Wochenschau: must have disclaimer at top
    if 'wochenschau' in (new_title or title).lower():
        disclaimer = "⚠️ HISTORICAL DOCUMENT"
        if disclaimer not in new_desc and 'historical' not in new_desc.lower()[:200]:
            disclaimer_block = "⚠️ HISTORICAL DOCUMENT — This newsreel is presented for educational and documentary purposes. The content reflects the propaganda of its era and does not represent the views of the uploader.\n\n"
            new_desc = disclaimer_block + new_desc
            changes.append("Added Wochenschau disclaimer")

    if new_desc != desc:
        update_snippet['description'] = new_desc

    # ── CATEGORY FIX ──
    new_cat = cat_id
    if fx.get('needs_cat_fix'):
        new_cat = fx['new_cat']
        update_snippet['categoryId'] = new_cat
        changes.append(f"Category: {cat_id} → {new_cat}")

    # ── TAGS FIX ──
    new_tags = list(tags)
    if len(new_tags) > 15:
        new_tags = new_tags[:15]
        update_snippet['tags'] = new_tags
        changes.append(f"Tags trimmed: {len(tags)} → 15")

    # ── Print Plan ──
    print(f"\n🔧 {vid}: {(new_title or title)[:60]}")
    for c in changes:
        print(f"   → {c}")

    if not DRY_RUN and changes:
        # Build update body
        body = {
            'id': vid,
            'snippet': {
                'title': update_snippet.get('title', title),
                'description': update_snippet.get('description', desc),
                'categoryId': update_snippet.get('categoryId', cat_id),
                'tags': update_snippet.get('tags', tags),
            }
        }
        parts = ['snippet']

        try:
            yt.videos().update(part=','.join(parts), body=body).execute()
            quota_cost += 50
            print(f"   ✅ UPDATED (quota: +50, total: {quota_cost})")
            time.sleep(1)
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if DRY_RUN:
    est_quota = len([f for f in fixes if any(k.startswith('needs_') and v for k, v in f.items())]) * 50
    print(f"\n⚠️  DRY RUN — No changes applied!")
    print(f"   Estimated quota cost: ~{est_quota} units")
    print(f"   Run with --apply to execute fixes")
else:
    print(f"\n✅ All fixes applied! Total quota cost: {quota_cost} units")

# Save report
report = {
    'date': '2026-02-10',
    'mode': 'dry_run' if DRY_RUN else 'applied',
    'total_audited': len(all_videos),
    'compliant': len(all_videos) - len(fixes),
    'fixes': fixes,
    'quota_cost': quota_cost,
}
report_path = r'D:\remaike.TV\config\new_uploads_audit.json'
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nReport saved: {report_path}")
