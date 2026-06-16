#!/usr/bin/env python3
"""
Fix new uploads + correct Maulwurf episode numbers + build playlist.
2026-02-12

Tasks:
  A) 4 NEW Maulwurf: Full metadata build (title, desc, tags, category, locs)
  B) 6 EXISTING Maulwurf: Fix wrong episode numbers (previous fix was wrong)
  C) 4 NEW NASA/Skylab: Full metadata build
  D) Build Maulwurf playlist (chronological)

Quota estimate: ~714 for metadata + ~800 for playlist = ~1,514

Usage:
  python fix_uploads_2026_02_12.py               # dry run
  python fix_uploads_2026_02_12.py --apply        # apply changes
  python fix_uploads_2026_02_12.py --playlist     # create/update playlist only
"""
import sys, json, time, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = r"D:\remaike.TV\token.json"
ROOT = r"D:\remaike.TV"
DRY = "--apply" not in sys.argv and "--playlist" not in sys.argv
DO_PLAYLIST = "--playlist" in sys.argv or "--apply" in sys.argv

def yt_client():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

yt = yt_client()
quota_used = 0

# ═══════════════════════════════════════════════════════════
# BUILDING BLOCKS
# ═══════════════════════════════════════════════════════════

CTA = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

MAULWURF_TAGS = [
    "Krtek", "Der kleine Maulwurf", "The Little Mole", "Krteček",
    "Zdeněk Miler", "Czech Animation", "Zeichentrick",
    "8K", "4K UHD", "remastered", "restored", "classic cartoon",
    "public domain", "vintage cartoon"
]

NASA_TAGS = [
    "NASA", "space", "8K", "4K UHD", "remastered", "restored",
    "public domain", "space exploration", "documentary",
    "vintage footage", "history"
]

def maulwurf_desc(ep_num, title_de, title_en, title_cs, year, composer):
    return f"""🎬 Classic Czech animation masterpiece, AI remastered in stunning 8K quality.
Der kleine Maulwurf (Krtek/Krteček) Episode {ep_num}: {title_de} ({year}).

Originally created by Zdeněk Miler at Krátký Film Praha.
Music by {composer}.

🇩🇪 {title_de}
🇬🇧 {title_en}
🇨🇿 {title_cs}

{CTA}

#Krtek #DerKleineMaulwurf #8K #ClassicCartoon #CzechAnimation"""

def maulwurf_locs(ep_num, titles, year):
    """Build 10-language localizations for Maulwurf."""
    ep_str = f"E{ep_num:02d}"
    return {
        "de": {"title": f"Krtek {ep_str}: {titles['de']} ({year}) | 8K HQ (4K UHD)"},
        "en": {"title": f"Krtek {ep_str}: {titles['en']} ({year}) | 8K HQ (4K UHD)"},
        "cs": {"title": f"Krtek {ep_str}: {titles['cs']} ({year}) | 8K HQ"},
        "ja": {"title": f"クルテク {ep_str}: {titles.get('ja', titles['en'])} ({year}) | 8K HQ"},
        "zh": {"title": f"鼹鼠的故事 {ep_str}: {titles.get('zh', titles['en'])} ({year}) | 8K HQ"},
        "es": {"title": f"Krtek {ep_str}: {titles.get('es', titles['en'])} ({year}) | 8K HQ"},
        "fr": {"title": f"Krtek {ep_str}: {titles.get('fr', titles['en'])} ({year}) | 8K HQ"},
        "ru": {"title": f"Кротик {ep_str}: {titles.get('ru', titles['en'])} ({year}) | 8K HQ"},
        "ko": {"title": f"두더지 {ep_str}: {titles.get('ko', titles['en'])} ({year}) | 8K HQ"},
        "pl": {"title": f"Krecik {ep_str}: {titles.get('pl', titles['en'])} ({year}) | 8K HQ"},
    }

def nasa_desc(title, year, details):
    return f"""🚀 {details}
Originally recorded by NASA in {year}. AI remastered in stunning 8K quality.

{CTA}

#NASA #Space #8K #PublicDomain #SpaceExploration"""

# ═══════════════════════════════════════════════════════════
# EPISODE DATABASE (CZ Wikipedia expanded 63-episode list)
# Cross-referenced by German title + year
# ═══════════════════════════════════════════════════════════

# Load complete episode list for reference
with open(os.path.join(ROOT, "config", "maulwurf_complete_database.json"), "r", encoding="utf-8") as f:
    maulwurf_db = json.load(f)

EP_LIST = {ep["ep"]: ep for ep in maulwurf_db["complete_episode_list"]}

# ═══════════════════════════════════════════════════════════
# FIX PLAN
# ═══════════════════════════════════════════════════════════

# B) EXISTING Maulwurf: Fix wrong episode numbers
# The previous maulwurf_epnum_fix.py set WRONG numbers!
# Truth = complete_episode_list matched by German title
EXISTING_FIXES = [
    {
        "id": "wjpCNxf5SsY",
        "old_title": "Krtek E17: Der Maulwurf und die Streichhölzer (1974) | 8K HQ (4K UHD)",
        "new_title": "Krtek E16: Der Maulwurf und die Streichhölzer (1974) | 8K HQ (4K UHD)",
        "reason": "ep16 per CZ Wikipedia, not ep17 (ep17 = Der Maulwurf als Chemiker)",
        "ep": 16,
    },
    {
        "id": "3GM123aC4bE",
        "old_title": "Krtek E22: Der Maulwurf und das Hühnerei (1975) | 8K HQ (4K UHD)",
        "new_title": "Krtek E20: Der Maulwurf und das Hühnerei (1975) | 8K HQ (4K UHD)",
        "reason": "ep20 per CZ Wikipedia, not ep22 (ep22 = Der Bulldozer)",
        "ep": 20,
    },
    {
        "id": "j4aBiGJcEY8",
        "old_title": "Krtek E23: Der Maulwurf als Fotograf (1975) | 8K HQ (4K UHD)",
        "new_title": "Krtek E21: Der Maulwurf als Fotograf (1975) | 8K HQ (4K UHD)",
        "reason": "ep21 per CZ Wikipedia, not ep23 (ep23 = In der Wüste = NEW upload!)",
        "ep": 21,
    },
    {
        "id": "EZxjMpAY9Wk",
        "old_title": "Krtek E45: Der Maulwurf und die Quelle (1999) | 8K HQ (4K UHD)",
        "new_title": "Krtek E59: Der Maulwurf und die Quelle (1999) | 8K HQ (4K UHD)",
        "reason": "ep59 per CZ Wikipedia, not ep45 (ep45 = Frosch Clip)",
        "ep": 59,
    },
    {
        "id": "tMaYrApYlxc",
        "old_title": "Krtek E44: Der Maulwurf und die Flöte (1999) | 8K HQ (4K UHD)",
        "new_title": "Krtek E60: Der Maulwurf und die Flöte (1999) | 8K HQ (4K UHD)",
        "reason": "ep60 per CZ Wikipedia, not ep44 (ep44 = TV Clip)",
        "ep": 60,
    },
    {
        "id": "MlzpyJ6CyHw",
        "old_title": "Krtek E49: Der Maulwurf und der kleine Frosch (2002) | 8K HQ (4K UHD)",
        "new_title": "Krtek E63: Der Maulwurf und der kleine Frosch (2002) | 8K HQ (4K UHD)",
        "reason": "ep63 per CZ Wikipedia (LAST episode ever!), not ep49 (ep49 = Haus Clip)",
        "ep": 63,
    },
]

# A) NEW Maulwurf uploads — full metadata build
NEW_MAULWURF = [
    {
        "id": "_SXNNnFHzqc",
        "ep": 23,
        "year": 1975,
        "composer": "Vadim Petrov",
        "category": "1",
        "titles": {
            "de": "Der Maulwurf in der Wüste",
            "cs": "Krtek na poušti",
            "en": "The Mole in the Desert",
            "ja": "もぐらくんと砂漠",
            "zh": "鼹鼠在沙漠",
            "es": "El Topito en el desierto",
            "fr": "La Petite Taupe dans le désert",
            "ru": "Кротик в пустыне",
            "ko": "사막의 두더지",
            "pl": "Krecik na pustyni",
        },
        "tags": MAULWURF_TAGS + ["Wüste", "desert", "1975"],
    },
    {
        "id": "DMV0tGHgfG0",
        "ep": 24,
        "year": 1975,
        "composer": "Vadim Petrov",
        "category": "1",
        "titles": {
            "de": "Der Maulwurf und das Weihnachtsfest",
            "cs": "Krtek o vánocích",
            "en": "The Mole at Christmas",
            "ja": "もぐらくんのクリスマス",
            "zh": "鼹鼠的圣诞节",
            "es": "El Topito y la Navidad",
            "fr": "La Petite Taupe à Noël",
            "ru": "Кротик и Рождество",
            "ko": "두더지의 크리스마스",
            "pl": "Krecik i Boże Narodzenie",
        },
        "tags": MAULWURF_TAGS + ["Weihnachten", "Christmas", "Vánoce", "1975"],
    },
    {
        "id": "fqIV8eZRJyE",
        "ep": 42,
        "year": 1997,
        "composer": "Jiří Strohner",
        "category": "1",
        "titles": {
            "de": "Der Maulwurf und die Überschwemmung",
            "cs": "Krtek a potopa",
            "en": "The Mole and the Flood",
            "ja": "もぐらくんと洪水",
            "zh": "鼹鼠和洪水",
            "es": "El Topito y la inundación",
            "fr": "La Petite Taupe et l'inondation",
            "ru": "Кротик и наводнение",
            "ko": "두더지와 홍수",
            "pl": "Krecik i powódź",
        },
        "tags": MAULWURF_TAGS + ["Überschwemmung", "flood", "1997"],
    },
    {
        "id": "p-98Kku-tB4",
        "ep": 43,
        "year": 1997,
        "composer": "Jiří Strohner",
        "category": "1",
        "titles": {
            "de": "Der Maulwurf und der Schneemann",
            "cs": "Krtek a sněhulák",
            "en": "The Mole and the Snowman",
            "ja": "もぐらくんと雪だるま",
            "zh": "鼹鼠和雪人",
            "es": "El Topito y el muñeco de nieve",
            "fr": "La Petite Taupe et le bonhomme de neige",
            "ru": "Кротик и снеговик",
            "ko": "두더지와 눈사람",
            "pl": "Krecik i bałwan",
        },
        "tags": MAULWURF_TAGS + ["Schneemann", "snowman", "sněhulák", "1997"],
    },
]

# C) NEW NASA/Skylab uploads
NEW_NASA = [
    {
        "id": "OWT520VIjxI",
        "title": "Skylab Space Station (1973) | NASA | 8K HQ (4K UHD)",
        "category": "27",  # Education
        "desc": nasa_desc("Skylab Space Station", "1973",
            "Skylab Space Station — America's first space station, launched in 1973. "
            "This documentary shows the construction, launch, and operations of Skylab."),
        "tags": NASA_TAGS + ["Skylab", "space station", "1973", "Raumstation"],
        "locs": {
            "de": {"title": "Skylab Raumstation (1973) | NASA | 8K HQ (4K UHD)"},
            "en": {"title": "Skylab Space Station (1973) | NASA | 8K HQ (4K UHD)"},
            "es": {"title": "Skylab Estación Espacial (1973) | NASA | 8K HQ"},
            "fr": {"title": "Skylab Station Spatiale (1973) | NASA | 8K HQ"},
            "ja": {"title": "スカイラブ宇宙ステーション (1973) | NASA | 8K HQ"},
        },
    },
    {
        "id": "-Gz34LVx90U",
        "title": "Skylab 2: Launch (1973) | NASA Archive | 8K HQ (4K UHD)",
        "category": "27",
        "desc": nasa_desc("Skylab 2 Launch", "1973",
            "Skylab 2 — First crewed mission to Skylab space station, launched May 25, 1973. "
            "Archive footage restored in 8K."),
        "tags": NASA_TAGS + ["Skylab 2", "launch", "1973", "archive"],
        "locs": {
            "de": {"title": "Skylab 2: Start (1973) | NASA Archiv | 8K HQ (4K UHD)"},
            "en": {"title": "Skylab 2: Launch (1973) | NASA Archive | 8K HQ (4K UHD)"},
        },
    },
    {
        "id": "Wmldi8lMuSU",
        "title": "Apollo 11: Onboard Camera (1969) | NASA Archive | 8K HQ (4K UHD)",
        "category": "27",
        "desc": nasa_desc("Apollo 11 Onboard Camera", "1969",
            "Apollo 11 — Onboard camera footage from humanity's first Moon landing, July 1969. "
            "Archive footage restored in 8K."),
        "tags": NASA_TAGS + ["Apollo 11", "Moon landing", "1969", "onboard", "Mondlandung"],
        "locs": {
            "de": {"title": "Apollo 11: Bordkamera (1969) | NASA Archiv | 8K HQ (4K UHD)"},
            "en": {"title": "Apollo 11: Onboard Camera (1969) | NASA Archive | 8K HQ (4K UHD)"},
        },
    },
    {
        "id": "ySxErhBGbx0",
        "title": "Apollo 11: Descent & Landing (1969) | NASA Archive | 8K HQ (4K UHD)",
        "category": "27",
        "desc": nasa_desc("Apollo 11 Descent & Landing", "1969",
            "Apollo 11 — Descent and landing footage from the first Moon landing, July 20, 1969. "
            "Archive footage restored in 8K."),
        "tags": NASA_TAGS + ["Apollo 11", "Moon landing", "descent", "landing", "1969", "Mondlandung"],
        "locs": {
            "de": {"title": "Apollo 11: Abstieg & Landung (1969) | NASA Archiv | 8K HQ (4K UHD)"},
            "en": {"title": "Apollo 11: Descent & Landing (1969) | NASA Archive | 8K HQ (4K UHD)"},
        },
    },
]

# ═══════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════

def apply_video_update(vid_id, snippet_update, label=""):
    """Apply a single video update. Returns True on success."""
    global quota_used
    try:
        yt.videos().update(
            part="snippet",
            body={"id": vid_id, "snippet": snippet_update}
        ).execute()
        quota_used += 50
        print(f"  ✅ {vid_id} | {label} ({quota_used}q)")
        time.sleep(1)
        return True
    except Exception as e:
        print(f"  ❌ {vid_id} | ERROR: {str(e)[:120]}")
        if "quotaExceeded" in str(e):
            print("\n🛑 QUOTA EXHAUSTED!")
            sys.exit(1)
        return False

def apply_localizations(vid_id, locs, label=""):
    """Apply localizations to a video."""
    global quota_used
    try:
        # First fetch current video to get snippet
        resp = yt.videos().list(part="localizations", id=vid_id).execute()
        quota_used += 1
        if not resp.get("items"):
            print(f"  ❓ {vid_id} not found for localizations")
            return False
        
        current_locs = resp["items"][0].get("localizations", {})
        current_locs.update(locs)
        
        yt.videos().update(
            part="localizations",
            body={"id": vid_id, "localizations": current_locs}
        ).execute()
        quota_used += 50
        print(f"  🌍 {vid_id} | {len(locs)} localizations ({quota_used}q)")
        time.sleep(0.5)
        return True
    except Exception as e:
        print(f"  ⚠️ {vid_id} | Locs error: {str(e)[:80]}")
        return False

print("=" * 70)
print(f"FIX UPLOADS 2026-02-12 {'(DRY RUN)' if DRY else '🔴 APPLYING'}")
print("=" * 70)

# ── STEP 1: Fetch all videos we need to update ──
all_ids = [f["id"] for f in EXISTING_FIXES] + [m["id"] for m in NEW_MAULWURF] + [n["id"] for n in NEW_NASA]
print(f"\n📡 Fetching {len(all_ids)} videos...")

current = {}
for i in range(0, len(all_ids), 50):
    batch = all_ids[i:i+50]
    resp = yt.videos().list(part="snippet", id=",".join(batch)).execute()
    quota_used += 1
    for item in resp.get("items", []):
        current[item["id"]] = item["snippet"]
    print(f"  Fetched {len(resp.get('items', []))} videos ({quota_used}q)")

print(f"  Found {len(current)}/{len(all_ids)} videos")

# ── STEP 2: Fix existing Maulwurf episode numbers ──
print(f"\n{'─'*70}")
print("STEP 2: Fix existing Maulwurf episode numbers")
print(f"{'─'*70}")
fix_ok = 0
fix_fail = 0

for fix in EXISTING_FIXES:
    vid = fix["id"]
    if vid not in current:
        print(f"  ❓ {vid} not found — skipping")
        fix_fail += 1
        continue
    
    snippet = current[vid]
    actual_title = snippet["title"]
    
    # Verify the old title matches
    if fix["old_title"] not in actual_title and actual_title != fix["old_title"]:
        # Title might have changed slightly - check if we still need the fix
        if f"E{fix['ep']:02d}:" in actual_title:
            print(f"  ⏭️ {vid} | Already correct: {actual_title[:60]}")
            continue
        print(f"  ⚠️ {vid} | Title mismatch!")
        print(f"       Expected: {fix['old_title'][:60]}")
        print(f"       Actual:   {actual_title[:60]}")
    
    print(f"  📝 {vid}")
    print(f"     OLD: {actual_title[:65]}")
    print(f"     NEW: {fix['new_title'][:65]}")
    print(f"     WHY: {fix['reason']}")
    
    if not DRY:
        new_snippet = {
            "title": fix["new_title"],
            "description": snippet.get("description", ""),
            "tags": list(snippet.get("tags", [])),
            "categoryId": snippet["categoryId"],
        }
        if apply_video_update(vid, new_snippet, fix["new_title"][:45]):
            fix_ok += 1
        else:
            fix_fail += 1
    else:
        fix_ok += 1

print(f"\n  Existing fixes: {fix_ok} OK, {fix_fail} fail")

# ── STEP 3: Name new Maulwurf uploads ──
print(f"\n{'─'*70}")
print("STEP 3: Name new Maulwurf uploads")
print(f"{'─'*70}")
new_ok = 0

for m in NEW_MAULWURF:
    vid = m["id"]
    ep = m["ep"]
    year = m["year"]
    ep_data = EP_LIST.get(ep, {})
    
    new_title = f"Krtek E{ep:02d}: {m['titles']['de']} ({year}) | 8K HQ (4K UHD)"
    new_desc = maulwurf_desc(ep, m["titles"]["de"], m["titles"]["en"], m["titles"]["cs"], year, m["composer"])
    
    print(f"  🆕 {vid}")
    print(f"     TITLE: {new_title}")
    
    if vid not in current:
        print(f"     ❓ Not found — might be private/processing")
        continue
    
    snippet = current[vid]
    old_title = snippet["title"]
    print(f"     FROM:  {old_title[:65]}")
    
    if not DRY:
        new_snippet = {
            "title": new_title,
            "description": new_desc,
            "tags": m["tags"][:15],
            "categoryId": m["category"],
        }
        if apply_video_update(vid, new_snippet, new_title[:45]):
            new_ok += 1
            # Also set localizations
            locs = maulwurf_locs(ep, m["titles"], year)
            apply_localizations(vid, locs, f"Maulwurf E{ep:02d}")
    else:
        new_ok += 1

print(f"\n  New Maulwurf: {new_ok} OK")

# ── STEP 4: Name new NASA/Skylab uploads ──
print(f"\n{'─'*70}")
print("STEP 4: Name new NASA/Skylab uploads")
print(f"{'─'*70}")
nasa_ok = 0

for n in NEW_NASA:
    vid = n["id"]
    new_title = n["title"]
    
    print(f"  🚀 {vid}")
    print(f"     TITLE: {new_title}")
    
    if vid not in current:
        print(f"     ❓ Not found — might be private/processing")
        continue
    
    old_title = current[vid]["title"]
    print(f"     FROM:  {old_title[:65]}")
    
    if not DRY:
        new_snippet = {
            "title": new_title,
            "description": n["desc"],
            "tags": n["tags"][:15],
            "categoryId": n["category"],
        }
        if apply_video_update(vid, new_snippet, new_title[:45]):
            nasa_ok += 1
            if n.get("locs"):
                apply_localizations(vid, n["locs"], new_title[:30])
    else:
        nasa_ok += 1

print(f"\n  NASA/Skylab: {nasa_ok} OK")

# ── STEP 5: Build Maulwurf Playlist (chronological) ──
if DO_PLAYLIST or not DRY:
    print(f"\n{'─'*70}")
    print("STEP 5: Build Maulwurf Playlist (chronological)")
    print(f"{'─'*70}")
    
    # All Maulwurf video IDs in chronological order (by episode number)
    ALL_MAULWURF = [
        # Existing videos (correct ep numbers)
        {"id": "xG_2AhK-sVI", "ep": 3, "year": 1965, "title": "E03: Die Rakete"},
        {"id": "wtq09EZfO20", "ep": 8, "year": 1969, "title": "E08: Als Gärtner"},
        {"id": "ts5qtXqneq8", "ep": 13, "year": 1972, "title": "E13: Als Maler"},
        {"id": "wjpCNxf5SsY", "ep": 16, "year": 1974, "title": "E16: Streichhölzer"},
        {"id": "UsppP3mPwHM", "ep": 18, "year": 1974, "title": "E18: Als Uhrmacher"},
        {"id": "3GM123aC4bE", "ep": 20, "year": 1975, "title": "E20: Hühnerei"},
        {"id": "j4aBiGJcEY8", "ep": 21, "year": 1975, "title": "E21: Als Fotograf"},
        # NEW uploads
        {"id": "_SXNNnFHzqc", "ep": 23, "year": 1975, "title": "E23: In der Wüste"},
        {"id": "DMV0tGHgfG0", "ep": 24, "year": 1975, "title": "E24: Weihnachtsfest"},
        {"id": "fqIV8eZRJyE", "ep": 42, "year": 1997, "title": "E42: Überschwemmung"},
        {"id": "p-98Kku-tB4", "ep": 43, "year": 1997, "title": "E43: Schneemann"},
        # Clip
        {"id": "6MElwMSiT0E", "ep": 45, "year": 1998, "title": "Clip: Frosch"},
        # Later episodes
        {"id": "EZxjMpAY9Wk", "ep": 59, "year": 1999, "title": "E59: Die Quelle"},
        {"id": "tMaYrApYlxc", "ep": 60, "year": 1999, "title": "E60: Die Flöte"},
        {"id": "MlzpyJ6CyHw", "ep": 63, "year": 2002, "title": "E63: Kleiner Frosch"},
        # Compilation (last)
        {"id": "gGYWs-xw1VM", "ep": 999, "year": 9999, "title": "Best Of Mix"},
    ]
    
    # Sort by episode number
    ALL_MAULWURF.sort(key=lambda x: x["ep"])
    
    # Check if playlist exists
    print("  📋 Checking existing playlists...")
    pl_response = yt.playlists().list(
        part="snippet",
        channelId="UCVFv6Egpl0LDvigpFbQXNeQ",
        maxResults=50
    ).execute()
    quota_used += 1
    
    maulwurf_pl_id = None
    existing_playlists = {}
    for pl in pl_response.get("items", []):
        pl_title = pl["snippet"]["title"]
        existing_playlists[pl_title] = pl["id"]
        if "maulwurf" in pl_title.lower() or "krtek" in pl_title.lower():
            maulwurf_pl_id = pl["id"]
            print(f"  ✅ Found existing Maulwurf playlist: {pl_title} ({pl['id']})")
    
    print(f"  📋 Total playlists on channel: {len(existing_playlists)}")
    for name, pid in sorted(existing_playlists.items()):
        print(f"     {pid} | {name[:60]}")
    
    if not maulwurf_pl_id:
        # Create new playlist
        print("  🆕 Creating Maulwurf playlist...")
        if not DRY:
            pl_body = {
                "snippet": {
                    "title": "Der kleine Maulwurf | Krtek | 8K",
                    "description": (
                        "Der kleine Maulwurf (Krtek/Krteček) — Tschechischer Zeichentrick-Klassiker "
                        "von Zdeněk Miler, in 8K restauriert! Chronologisch sortiert.\n\n"
                        "The Little Mole — Classic Czech animation by Zdeněk Miler, "
                        "remastered in stunning 8K quality! Sorted chronologically.\n\n"
                        "🌐 www.remaike.IT\n"
                        "📺 https://www.youtube.com/@remAIke_IT"
                    ),
                },
                "status": {"privacyStatus": "public"},
            }
            pl_resp = yt.playlists().insert(part="snippet,status", body=pl_body).execute()
            maulwurf_pl_id = pl_resp["id"]
            quota_used += 50
            print(f"  ✅ Created playlist: {maulwurf_pl_id}")
        else:
            print(f"  (would create playlist)")
    
    if maulwurf_pl_id:
        # First, get existing items in playlist
        existing_items = []
        pt = None
        while True:
            req = yt.playlistItems().list(
                part="contentDetails",
                playlistId=maulwurf_pl_id,
                maxResults=50,
                pageToken=pt
            )
            resp = req.execute()
            quota_used += 1
            for it in resp.get("items", []):
                existing_items.append(it["contentDetails"]["videoId"])
            pt = resp.get("nextPageToken")
            if not pt:
                break
        
        existing_set = set(existing_items)
        print(f"  📋 Playlist has {len(existing_items)} items already")
        
        # Add missing videos in chronological order
        added = 0
        for m in ALL_MAULWURF:
            if m["id"] in existing_set:
                print(f"  ⏭️ Already in playlist: {m['title']}")
                continue
            
            print(f"  ➕ Adding: {m['title']}")
            if not DRY:
                try:
                    yt.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": maulwurf_pl_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": m["id"]
                                }
                            }
                        }
                    ).execute()
                    quota_used += 50
                    added += 1
                    print(f"     ✅ Added ({quota_used}q)")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"     ❌ Error: {str(e)[:80]}")
        
        print(f"\n  Playlist: {added} videos added")

# ── SUMMARY ──
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
print(f"  Existing Maulwurf title fixes: {fix_ok}")
print(f"  New Maulwurf named: {new_ok}")
print(f"  New NASA/Skylab named: {nasa_ok}")
print(f"  Quota used: ~{quota_used}")
print(f"  Mode: {'DRY RUN' if DRY else 'APPLIED'}")

# Save report
report = {
    "date": "2026-02-12",
    "script": "fix_uploads_2026_02_12.py",
    "existing_fixes": fix_ok,
    "new_maulwurf": new_ok,
    "new_nasa": nasa_ok,
    "quota_used": quota_used,
    "dry_run": DRY,
}
report_path = os.path.join(ROOT, "config", "fix_uploads_report_2026_02_12.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
print(f"\n📄 Report: {report_path}")
