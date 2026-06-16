"""
VIDEO MASTER DATABASE — Single Source of Truth
================================================
Fetches ALL video data once, builds a complete local database with:
- Current YouTube state
- Computed "ideal" state based on ALL rules
- Diff between current and ideal
- Ready-to-push change sets

This eliminates the need to re-audit constantly.
Quota: ~7 units (read only), then 0 quota for all planning.
"""
import json, os, re
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
SNAPSHOT_PATH = "D:/remaike.TV/config/channel_snapshot_2026_02_06.json"
DB_PATH = "D:/remaike.TV/config/video_master_db.json"

def get_yt():
    creds_data = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=creds_data.get("access_token"),
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
    )
    if creds.expired:
        creds.refresh(Request())
        creds_data["access_token"] = creds.token
        json.dump(creds_data, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)

# ═══════════════════════════════════════════
# SERIES DETECTION (expanded)
# ═══════════════════════════════════════════
def detect_series(title):
    t = title.lower()
    if 'betty boop' in t: return 'betty_boop'
    if 'soundie' in t: return 'soundie'
    if 'wochenschau' in t: return 'wochenschau'
    if 'alfred' in t and ('kwak' in t or 'quack' in t): return 'alfred_j_kwak'
    if 'superman' in t and ('fleischer' in t or '/17)' in title or '/17 )' in title): return 'superman'
    if 'popeye' in t: return 'popeye'
    if 'felix' in t and ('cat' in t or '/175)' in title): return 'felix_the_cat'
    if 'casper' in t: return 'casper'
    if 'maulwurf' in t or 'krtek' in t: return 'krtek'  # CZECH, not German!
    if 'ken block' in t or 'gymkhana' in t or 'getaway in stockholm' in t: return 'ken_block'
    if any(x in t for x in ['looney', 'porky', 'merrie', 'bosko']): return 'looney_tunes'
    if any(x in t for x in ['christmas', 'santa', 'snowflake', 'rudolph']): return 'christmas'
    if 'astro boy' in t: return 'astro_boy'
    if 'bravestarr' in t: return 'bravestarr'
    if 'chaplin' in t: return 'chaplin'
    if 'buster keaton' in t: return 'buster_keaton'
    if 'skylab' in t or 'nasa' in t: return 'nasa'
    if 'silly symphony' in t or 'skeleton dance' in t: return 'silly_symphony'
    return 'other'

# ═══════════════════════════════════════════
# SERIES RULES (the knowledge base)
# ═══════════════════════════════════════════
SERIES_RULES = {
    "krtek": {
        "origin": "Czech (Czechoslovakia)",
        "creator": "Zdeněk Miler",
        "language_nature": "mostly_silent",  # pantomime, no dialogue
        "international_name": "Krtek / The Little Mole",
        "correct_category": "1",  # Film & Animation
        "title_prefix_by_lang": {
            "en": "Krtek (The Little Mole)",
            "de": "Der kleine Maulwurf",
            "cs": "Krtek",
            "es": "El Topito",
            "fr": "La Petite Taupe",
            "pt": "A Toupeira",
        },
        "episode_titles": {
            "Die Rakete": {"en": "The Rocket", "cs": "Krtek a raketa", "es": "El Cohete", "fr": "La Fusée", "pt": "O Foguete", "year": 1965},
            "Als Gärtner": {"en": "The Gardener", "cs": "Krtek zahradníkem", "es": "El Jardinero", "fr": "Le Jardinier", "pt": "O Jardineiro", "year": 1969},
            "Der Frosch": {"en": "The Frog", "cs": "Krtek a žabka", "es": "La Rana", "fr": "La Grenouille", "pt": "O Sapo", "year": 1998},
            "Die Flöte": {"en": "The Flute", "cs": "Krtek a flétna", "es": "La Flauta", "fr": "La Flûte", "pt": "A Flauta", "year": 1999},
            "Die Quelle": {"en": "The Spring", "cs": "Krtek a pramen", "es": "La Fuente", "fr": "La Source", "pt": "A Nascente", "year": 1999},
            "Im Urlaub": {"en": "On Vacation", "cs": "Krtek na prázdninách", "es": "De Vacaciones", "fr": "En Vacances", "pt": "De Férias", "year": None},
        },
        "cta": "🌍 What's the Mole called in YOUR language? Comment below!",
        "description_note": "Silent animated series — no dialogue, universally accessible.",
        "tags_base": ["Krtek", "The Little Mole", "Der kleine Maulwurf", "Zdenek Miler", 
                       "Czech animation", "silent cartoon", "8K", "public domain", 
                       "classic animation", "children cartoon"],
    },
    "betty_boop": {
        "origin": "USA",
        "correct_category": "1",
        "language_nature": "english",
        "cta": "💋 Describe Betty in ONE word!",
    },
    "soundie": {
        "origin": "USA",
        "correct_category": "10",  # Music
        "language_nature": "music",
        "cta": "🎵 Name this genre in ONE word!",
    },
    "wochenschau": {
        "origin": "Germany (Nazi era)",
        "correct_category": "27",  # Education
        "language_nature": "german_narration",
        "cta": "📚 How is this era taught in your country?",
        "requires_disclaimer": True,
    },
    "alfred_j_kwak": {
        "origin": "Netherlands/Japan/Germany",
        "correct_category": "1",
        "language_nature": "dubbed_multilingual",
        "cta": "🦆 Who showed you Alfred as a kid? Comment below!",
    },
    "superman": {
        "origin": "USA",
        "correct_category": "1",
        "language_nature": "english",
        "cta": "💪 What's YOUR favorite Superman moment?",
    },
    "ken_block": {
        "origin": "USA",
        "correct_category": "2",  # Autos
        "language_nature": "minimal_english",
        "cta": "🏎️ What car would YOU pick for a Gymkhana?",
    },
    "nasa": {
        "origin": "USA",
        "correct_category": "27",
        "language_nature": "english",
        "cta": "🚀 One word for 'space' in your language?",
    },
}

# ═══════════════════════════════════════════
# IDEAL STATE COMPUTER
# ═══════════════════════════════════════════
def compute_ideal_localizations_krtek(current_title, series_rules):
    """Compute proper multi-language titles for Krtek episodes."""
    rules = series_rules
    episode_map = rules["episode_titles"]
    prefix_map = rules["title_prefix_by_lang"]
    
    # Find which episode this is
    ep_key = None
    for key in episode_map:
        if key.lower() in current_title.lower():
            ep_key = key
            break
    
    if not ep_key:
        return None
    
    ep = episode_map[ep_key]
    year = ep.get("year")
    year_str = f" ({year})" if year else ""
    
    locs = {}
    for lang in ["en", "de", "es", "fr", "pt"]:
        prefix = prefix_map.get(lang, prefix_map["en"])
        ep_title = ep.get(lang, ep.get("en", ep_key))
        title = f"{prefix}: {ep_title}{year_str} | 8K HQ"
        if len(title) > 70:
            # Shorten prefix
            title = f"Krtek: {ep_title}{year_str} | 8K HQ"
        locs[lang] = {"title": title}
    
    return locs

def compute_ideal(item, series_id):
    """Compute what this video SHOULD look like based on all rules."""
    s = item["snippet"]
    current = {
        "title": s["title"],
        "categoryId": s["categoryId"],
        "defaultLanguage": s.get("defaultLanguage", ""),
        "loc_titles": {},
    }
    
    # Current loc titles
    for lang, loc in item.get("localizations", {}).items():
        current["loc_titles"][lang] = loc.get("title", "")
    
    ideal = dict(current)  # start from current
    rules = SERIES_RULES.get(series_id, {})
    
    # Correct category
    if "correct_category" in rules:
        ideal["categoryId"] = rules["correct_category"]
    
    # Krtek specific: proper international titles
    if series_id == "krtek":
        locs = compute_ideal_localizations_krtek(s["title"], rules)
        if locs:
            ideal["loc_titles"] = {lang: loc["title"] for lang, loc in locs.items()}
            ideal["title"] = locs["de"]["title"]  # Main title in German
    
    # Remove (4K UHD) suffix
    if "(4K UHD)" in ideal["title"]:
        ideal["title"] = ideal["title"].replace(" (4K UHD)", "").replace("(4K UHD)", "")
    
    # Title length check
    if len(ideal["title"]) > 70:
        ideal["_warning"] = f"Title still too long: {len(ideal['title'])}"
    
    # CTA
    if "cta" in rules:
        ideal["recommended_cta"] = rules["cta"]
    
    return current, ideal

# ═══════════════════════════════════════════
# MAIN — Build the database
# ═══════════════════════════════════════════
print("=" * 70)
print("  VIDEO MASTER DATABASE — Building Single Source of Truth")
print("=" * 70)

# Get all public video IDs from snapshot
snap = json.load(open(SNAPSHOT_PATH, encoding="utf-8"))
all_snap = snap.get("all_videos", [])
seen = set()
public_ids = []
for v in all_snap:
    vid = v.get("id", "")
    if vid and vid not in seen and v.get("privacy") == "public":
        seen.add(vid)
        public_ids.append(vid)

print(f"\n  📺 {len(public_ids)} public videos")

# Fetch live data
yt = get_yt()
all_items = []
for i in range(0, len(public_ids), 50):
    batch = public_ids[i:i+50]
    resp = yt.videos().list(
        part="snippet,contentDetails,status,statistics,localizations",
        id=",".join(batch)
    ).execute()
    all_items.extend(resp.get("items", []))
    print(f"  Fetched {len(all_items)}/{len(public_ids)}...")

print(f"  ✅ {len(all_items)} videos fetched\n")

# Build DB
db = {
    "meta": {
        "created": datetime.now().isoformat(),
        "total_videos": len(all_items),
        "series_rules": list(SERIES_RULES.keys()),
    },
    "videos": {},
    "diffs": [],
    "stats": {"by_series": {}, "issues_found": 0},
}

for item in all_items:
    vid = item["id"]
    series_id = detect_series(item["snippet"]["title"])
    current, ideal = compute_ideal(item, series_id)
    
    # Compute diff
    changes = {}
    if current["title"] != ideal["title"]:
        changes["title"] = {"from": current["title"], "to": ideal["title"]}
    if current["categoryId"] != ideal["categoryId"]:
        changes["categoryId"] = {"from": current["categoryId"], "to": ideal["categoryId"]}
    
    # Check loc titles
    loc_changes = {}
    for lang in ["en", "de", "es", "fr", "pt"]:
        cur_t = current["loc_titles"].get(lang, "")
        ideal_t = ideal["loc_titles"].get(lang, cur_t)
        if cur_t != ideal_t:
            loc_changes[lang] = {"from": cur_t, "to": ideal_t}
    if loc_changes:
        changes["localizations"] = loc_changes
    
    entry = {
        "id": vid,
        "series": series_id,
        "current_title": current["title"],
        "ideal_title": ideal["title"],
        "current_category": current["categoryId"],
        "ideal_category": ideal["categoryId"],
        "privacy": item["status"]["privacyStatus"],
        "views": int(item.get("statistics", {}).get("viewCount", 0)),
        "duration": item["contentDetails"]["duration"],
        "has_changes": bool(changes),
        "changes": changes,
    }
    
    if "recommended_cta" in ideal:
        entry["recommended_cta"] = ideal["recommended_cta"]
    
    db["videos"][vid] = entry
    
    # Stats
    db["stats"]["by_series"].setdefault(series_id, 0)
    db["stats"]["by_series"][series_id] += 1
    
    if changes:
        db["diffs"].append({
            "id": vid,
            "series": series_id,
            "title": current["title"],
            "changes": changes,
        })
        db["stats"]["issues_found"] += 1

# Summary
print("=" * 70)
print(f"  DATABASE BUILT: {len(db['videos'])} videos")
print(f"  Diffs found:    {len(db['diffs'])} videos need changes")
print("=" * 70)

print(f"\n  📊 BY SERIES:")
for series, count in sorted(db["stats"]["by_series"].items(), key=lambda x: -x[1]):
    rules = SERIES_RULES.get(series, {})
    origin = rules.get("origin", "?")
    print(f"     {series:20s}: {count:3d} videos | {origin}")

if db["diffs"]:
    print(f"\n  🔴 CHANGES NEEDED ({len(db['diffs'])}):")
    for d in db["diffs"]:
        print(f"\n     {d['id']} [{d['series']}]")
        print(f"     Current: {d['title']}")
        for key, change in d["changes"].items():
            if key == "localizations":
                for lang, lc in change.items():
                    print(f"       loc[{lang}]: {lc['from'][:50]} → {lc['to'][:50]}")
            else:
                print(f"       {key}: {change['from']} → {change['to']}")

# Save
json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"\n  💾 Saved: {DB_PATH}")
print(f"  Quota used: ~{(len(public_ids)//50)+1} units (read only)")
