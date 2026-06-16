"""
VIDEO MASTER DATABASE v2 — NEXT LEVEL Single Source of Truth
==============================================================
Comprehensive database that:
1. Fetches ALL videos (public + private) with FULL metadata
2. Detects series & applies ALL rules (titles, descriptions, tags, locs, category)
3. Computes IDEAL state for every field based on rules & templates
4. Runs inline SEO audit (score, issues, recommendations)
5. Checks playlist membership
6. Generates prioritized push queue with quota cost

Quota: ~14 units (read only) — 7 videos.list + 7 playlistItems.list
"""
import json, os, re, sys
from datetime import datetime
from collections import defaultdict

# ─── API / Auth ─────────────────────────────────────────────
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import requests

OAUTH_PATH  = "D:/remaike.TV/config/youtube_oauth.json"
DB_PATH     = "D:/remaike.TV/config/video_master_db_v2.json"
CHANNEL_ID  = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PL   = "UUVFv6Egpl0LDvigpFbQXNeQ"
API_KEY     = os.getenv("YOUTUBE_API_KEY", "")

# Helper: use public API key if set, else fall back to OAuth for reads
_yt_oauth_client = None
_oauth_token = None
def _ensure_token():
    """Ensure OAuth token is fresh, return access_token string."""
    global _oauth_token
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"),
        refresh_token=d["refresh_token"],
        token_uri=d["token_uri"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
    )
    if not creds.valid:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
        print(f"  🔄 Token refreshed")
    _oauth_token = creds.token
    return _oauth_token

def _public_get(url, params):
    """GET via public API key if available, else OAuth."""
    if API_KEY:
        params["key"] = API_KEY
        return requests.get(url, params=params).json()
    else:
        token = _ensure_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if "error" in data:
            print(f"  ⚠️  API error (status {resp.status_code}): {data['error'].get('message', '')}")
        return data

# Existing config files
WOCHENSCHAU_LOC_PATH = "D:/remaike.TV/config/wochenschau_complete_locations.json"
BRAVESTARR_PATH      = "D:/remaike.TV/config/bravestarr_episodes.json"
PLAYLIST_SCHEMA_PATH = "D:/remaike.TV/config/playlist_master_schema.json"

def get_yt_oauth():
    """OAuth client for private video access."""
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"),
        refresh_token=d["refresh_token"],
        token_uri=d["token_uri"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
    )
    if creds.expired:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)

# ═══════════════════════════════════════════════════════════════
# 1.  SERIES DETECTION  (expanded with regex precision)
# ═══════════════════════════════════════════════════════════════
SERIES_PATTERNS = [
    ("betty_boop",       re.compile(r'betty\s*boop',            re.I)),
    ("soundie",          re.compile(r'\bsoundie\b',             re.I)),
    ("wochenschau",      re.compile(r'wochenschau',             re.I)),
    ("alfred_j_kwak",    re.compile(r'alfred.*?(kwak|quack)',    re.I)),
    ("superman",         re.compile(r'superman.*(fleischer|/17\s*\))', re.I)),
    ("popeye",           re.compile(r'\bpopeye\b',              re.I)),
    ("felix_the_cat",    re.compile(r'felix.*cat|felix.*/175\)', re.I)),
    ("casper",           re.compile(r'\bcasper\b',              re.I)),
    ("krtek",            re.compile(r'maulwurf|krtek',          re.I)),
    ("ken_block",        re.compile(r'ken\s*block|gymkhana|getaway.*stockholm', re.I)),
    ("looney_tunes",     re.compile(r'looney|porky|merrie|bosko', re.I)),
    ("christmas",        re.compile(r'christmas|santa|snowflake|rudolph|twas.*night', re.I)),
    ("astro_boy",        re.compile(r'astro\s*boy',             re.I)),
    ("bravestarr",       re.compile(r'bravestarr|brave\s*starr', re.I)),
    ("chaplin",          re.compile(r'\bchaplin\b',             re.I)),
    ("buster_keaton",    re.compile(r'buster\s*keaton|sherlock\s*jr', re.I)),
    ("nasa",             re.compile(r'\bnasa\b|skylab',         re.I)),
    ("silly_symphony",   re.compile(r'silly\s*symphony|skeleton\s*dance', re.I)),
    ("film_noir",        re.compile(r'detour|scarlet\s*street|strange\s*love', re.I)),
]

def detect_series(title):
    for sid, pat in SERIES_PATTERNS:
        if pat.search(title):
            return sid
    return "other"


# ═══════════════════════════════════════════════════════════════
# 2.  SERIES RULES  — Complete knowledge base
# ═══════════════════════════════════════════════════════════════
SERIES_RULES = {
    # ─── KRTEK ──────────────────────────────────────────────
    "krtek": {
        "origin": "Czech (Czechoslovakia)",
        "creator": "Zdeněk Miler",
        "language_nature": "mostly_silent",
        "correct_category": "1",
        "title_prefix_by_lang": {
            "en": "Krtek (The Little Mole)", "de": "Der kleine Maulwurf",
            "cs": "Krtek", "es": "El Topito", "fr": "La Petite Taupe", "pt": "A Toupeira",
        },
        "episode_titles": {
            "Die Rakete":  {"en": "The Rocket",    "cs": "Krtek a raketa",       "es": "El Cohete",     "fr": "La Fusée",      "pt": "O Foguete",     "year": 1965},
            "Als Gärtner": {"en": "The Gardener",   "cs": "Krtek zahradníkem",    "es": "El Jardinero",  "fr": "Le Jardinier",  "pt": "O Jardineiro",  "year": 1969},
            "Der Frosch":  {"en": "The Frog",       "cs": "Krtek a žabka",        "es": "La Rana",       "fr": "La Grenouille", "pt": "O Sapo",        "year": 1998},
            "Die Flöte":   {"en": "The Flute",      "cs": "Krtek a flétna",       "es": "La Flauta",     "fr": "La Flûte",      "pt": "A Flauta",      "year": 1999},
            "Die Quelle":  {"en": "The Spring",     "cs": "Krtek a pramen",       "es": "La Fuente",     "fr": "La Source",     "pt": "A Nascente",    "year": 1999},
            "Im Urlaub":   {"en": "On Vacation",    "cs": "Krtek na prázdninách", "es": "De Vacaciones", "fr": "En Vacances",   "pt": "De Férias",     "year": None},
        },
        "cta": "🌍 What's the Mole called in YOUR language? Comment below!",
        "tags_base": ["Krtek", "The Little Mole", "Der kleine Maulwurf", "Zdenek Miler",
                      "Czech animation", "silent cartoon", "8K", "public domain",
                      "classic animation", "children cartoon"],
        "hashtags": ["#Krtek", "#TheLittleMole", "#CzechAnimation", "#8K", "#PublicDomain"],
        "description_note": "Silent animated series by Zdeněk Miler — no dialogue, universally accessible.",
    },

    # ─── BETTY BOOP ─────────────────────────────────────────
    "betty_boop": {
        "origin": "USA",
        "creator": "Max Fleischer",
        "language_nature": "english",
        "correct_category": "1",
        "title_format": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
        "total_episodes": 105,
        "cta": "💋 Describe Betty in ONE word! Comment below!",
        "tags_base": ["Betty Boop", "Max Fleischer", "Fleischer Studios", "1930s",
                      "vintage cartoon", "pre-code", "jazz age", "animation",
                      "8K", "public domain", "classic cartoon"],
        "hashtags": ["#BettyBoop", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
        "loc_titles": {
            "en": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
            "de": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
            "es": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
            "fr": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
            "pt": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
        },
    },

    # ─── SOUNDIES ───────────────────────────────────────────
    "soundie": {
        "origin": "USA",
        "language_nature": "music",
        "correct_category": "10",  # Music!
        "title_format": "Soundie: {song_title} | 8K HQ",
        "cta": "🎵 Name this genre in ONE word! Comment below!",
        "tags_base": ["soundie", "soundies", "1940s", "vintage music", "jazz", "swing",
                      "big band", "jukebox", "panoram", "8K", "public domain",
                      "classic music", "music video", "official audio"],
        "hashtags": ["#Soundie", "#VintageMusic", "#1940s", "#Jazz", "#8K"],
    },

    # ─── WOCHENSCHAU ────────────────────────────────────────
    "wochenschau": {
        "origin": "Germany (Nazi era)",
        "language_nature": "german_narration",
        "correct_category": "27",  # Education
        "requires_disclaimer": True,
        "title_format": "Wochenschau {nr}: {event} ({date}) | 8K HQ",
        "cta": "📚 How is this era taught in your country? Share in the comments!",
        "tags_base": ["wochenschau", "german newsreel", "wwii history", "archive footage",
                      "historical film", "zeitgeschichte", "world history", "8K",
                      "documentary", "kino wochenschau", "third reich", "public domain"],
        "hashtags": ["#Wochenschau", "#WWII", "#8K", "#History", "#PublicDomain"],
        "madeForKids": False,
    },

    # ─── ALFRED J. KWAK ─────────────────────────────────────
    "alfred_j_kwak": {
        "origin": "Netherlands/Japan/Germany",
        "creator": "Herman van Veen",
        "language_nature": "dubbed_multilingual",
        "correct_category": "1",
        "total_episodes": 52,
        "title_format": "Alfred Jodokus Quack ({ep}/52): {ep_title} | Deutsch | 8K HQ",
        "cta": "🦆 Who showed you Alfred as a kid? Comment below!",
        "tags_base": ["Alfred J. Kwak", "Alfred Jodokus Quack", "Alfred Jodokus Kwak",
                      "Alfred Jodocus Kwak", "Alfred Jodocus Quack", "Kwak", "Quack",
                      "Herman van Veen", "Harald Siepermann", "Zeichentrick",
                      "Kinderserie", "Deutsch", "80er", "90er", "Nostalgie",
                      "Classic Animation", "8K", "restored"],
        "hashtags": ["#AlfredJKwak", "#Zeichentrick", "#8K", "#Nostalgie", "#PublicDomain"],
        "loc_titles": {
            "en": "Alfred J. Kwak ({ep}/52): {ep_title_en} | 8K HQ",
            "de": "Alfred Jodokus Quack ({ep}/52): {ep_title} | Deutsch | 8K HQ",
            "es": "Alfred J. Kwak ({ep}/52): {ep_title_es} | 8K HQ",
            "fr": "Alfred J. Kwak ({ep}/52): {ep_title_fr} | 8K HQ",
            "pt": "Alfred J. Kwak ({ep}/52): {ep_title_pt} | 8K HQ",
        },
    },

    # ─── SUPERMAN / FLEISCHER ───────────────────────────────
    "superman": {
        "origin": "USA",
        "creator": "Fleischer Studios / Famous Studios",
        "language_nature": "english",
        "correct_category": "1",
        "total_episodes": 17,
        "title_format": "Superman ({ep}/17): {ep_title} ({year}) | Fleischer | 8K HQ",
        "cta": "💪 What's YOUR favorite Superman moment? Comment below!",
        "tags_base": ["Superman", "Fleischer Studios", "Fleischer Superman", "1940s",
                      "vintage cartoon", "animation", "superhero", "DC Comics",
                      "8K", "public domain", "classic cartoon"],
        "hashtags": ["#Superman", "#Fleischer", "#VintageCartoon", "#8K", "#PublicDomain"],
    },

    # ─── POPEYE ─────────────────────────────────────────────
    "popeye": {
        "origin": "USA",
        "creator": "Fleischer Studios",
        "language_nature": "english",
        "correct_category": "1",
        "cta": "💪 Popeye or Bluto — who wins in a REAL fight? Comment!",
        "tags_base": ["Popeye", "Popeye the Sailor", "Fleischer Studios", "1930s",
                      "vintage cartoon", "animation", "8K", "public domain",
                      "classic cartoon", "Olive Oyl"],
        "hashtags": ["#Popeye", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
    },

    # ─── FELIX THE CAT ──────────────────────────────────────
    "felix_the_cat": {
        "origin": "USA",
        "creator": "Pat Sullivan / Otto Messmer",
        "language_nature": "silent",
        "correct_category": "1",
        "cta": "🐱 Which era of animation do you love most? Comment!",
        "tags_base": ["Felix the Cat", "Pat Sullivan", "Otto Messmer", "1920s",
                      "silent cartoon", "vintage animation", "8K", "public domain",
                      "classic cartoon", "black and white"],
        "hashtags": ["#FelixTheCat", "#SilentCartoon", "#8K", "#PublicDomain", "#VintageAnimation"],
    },

    # ─── CASPER ─────────────────────────────────────────────
    "casper": {
        "origin": "USA",
        "creator": "Famous Studios",
        "language_nature": "english",
        "correct_category": "1",
        "cta": "👻 Were you scared of Casper as a kid? Comment below!",
        "tags_base": ["Casper", "Casper the Friendly Ghost", "Famous Studios",
                      "1940s", "1950s", "vintage cartoon", "animation",
                      "8K", "public domain", "classic cartoon"],
        "hashtags": ["#Casper", "#FriendlyGhost", "#8K", "#PublicDomain", "#VintageCartoon"],
    },

    # ─── KEN BLOCK ──────────────────────────────────────────
    "ken_block": {
        "origin": "USA",
        "language_nature": "minimal_english",
        "correct_category": "2",  # Autos & Vehicles
        "cta": "🏎️ What car would YOU pick for a Gymkhana? Comment!",
        "tags_base": ["Ken Block", "Gymkhana", "drift", "rally", "motorsport",
                      "8K", "Ford", "Subaru", "Hoonigan"],
        "hashtags": ["#KenBlock", "#Gymkhana", "#8K", "#Drift", "#Motorsport"],
    },

    # ─── LOONEY TUNES ───────────────────────────────────────
    "looney_tunes": {
        "origin": "USA",
        "creator": "Warner Bros.",
        "language_nature": "english",
        "correct_category": "1",
        "cta": "🐰 Who's YOUR favorite Looney Tunes character? Comment!",
        "tags_base": ["Looney Tunes", "Merrie Melodies", "Warner Bros", "1930s",
                      "vintage cartoon", "animation", "8K", "public domain",
                      "Porky Pig", "Bosko", "classic cartoon"],
        "hashtags": ["#LooneyTunes", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
    },

    # ─── CHRISTMAS ──────────────────────────────────────────
    "christmas": {
        "origin": "USA",
        "language_nature": "english",
        "correct_category": "1",
        "cta": "🎄 What's YOUR holiday tradition? Comment below!",
        "tags_base": ["Christmas", "holiday", "vintage", "classic", "animation",
                      "8K", "public domain", "Santa Claus", "holiday special"],
        "hashtags": ["#Christmas", "#VintageCartoon", "#8K", "#PublicDomain", "#Holiday"],
    },

    # ─── ASTRO BOY ──────────────────────────────────────────
    "astro_boy": {
        "origin": "Japan",
        "creator": "Osamu Tezuka",
        "language_nature": "japanese_dubbed",
        "correct_category": "1",
        "cta": "🤖 Did you grow up with Astro Boy? In which language? Comment!",
        "tags_base": ["Astro Boy", "Tetsuwan Atom", "Osamu Tezuka", "anime",
                      "1960s", "classic anime", "8K", "Japanese animation",
                      "robot", "vintage anime"],
        "hashtags": ["#AstroBoy", "#TetsuwanAtom", "#8K", "#Anime", "#OsamuTezuka"],
    },

    # ─── BRAVESTARR ─────────────────────────────────────────
    "bravestarr": {
        "origin": "USA",
        "creator": "Filmation",
        "language_nature": "dubbed_multilingual",
        "correct_category": "1",
        "total_episodes": 65,
        "cta": "🤠 Which BraveStarr power would you choose? Comment!",
        "tags_base": ["BraveStarr", "Brave Starr", "Filmation", "80s cartoon",
                      "space western", "8K", "animation", "New Texas",
                      "Marshal BraveStarr", "1987", "1988", "Zeichentrick"],
        "hashtags": ["#BraveStarr", "#Filmation", "#8K", "#80sCartoon", "#SpaceWestern"],
    },

    # ─── CHAPLIN ────────────────────────────────────────────
    "chaplin": {
        "origin": "USA/UK",
        "creator": "Charlie Chaplin",
        "language_nature": "silent",
        "correct_category": "1",
        "cta": "🎩 Chaplin or Keaton? Who's the GOAT? Comment!",
        "tags_base": ["Charlie Chaplin", "Chaplin", "silent film", "1920s",
                      "slapstick", "comedy", "8K", "public domain",
                      "black and white", "classic film"],
        "hashtags": ["#Chaplin", "#SilentFilm", "#8K", "#PublicDomain", "#ClassicComedy"],
    },

    # ─── BUSTER KEATON ──────────────────────────────────────
    "buster_keaton": {
        "origin": "USA",
        "creator": "Buster Keaton",
        "language_nature": "silent",
        "correct_category": "1",
        "cta": "🎩 Chaplin or Keaton? Who's the GOAT? Comment!",
        "tags_base": ["Buster Keaton", "silent film", "1920s", "slapstick",
                      "comedy", "8K", "public domain", "black and white",
                      "classic film", "Sherlock Jr"],
        "hashtags": ["#BusterKeaton", "#SilentFilm", "#8K", "#PublicDomain", "#ClassicComedy"],
    },

    # ─── NASA ───────────────────────────────────────────────
    "nasa": {
        "origin": "USA",
        "language_nature": "english",
        "correct_category": "27",  # Education
        "cta": "🚀 One word for 'space' in your language? Comment!",
        "tags_base": ["NASA", "space", "documentary", "Skylab", "space station",
                      "8K", "public domain", "science", "history"],
        "hashtags": ["#NASA", "#Space", "#8K", "#Documentary", "#PublicDomain"],
    },

    # ─── SILLY SYMPHONY ─────────────────────────────────────
    "silly_symphony": {
        "origin": "USA",
        "creator": "Walt Disney",
        "language_nature": "music",
        "correct_category": "1",
        "cta": "🎵 What's YOUR favorite classic Disney short? Comment!",
        "tags_base": ["Silly Symphony", "Walt Disney", "Disney", "1930s",
                      "animation", "8K", "public domain", "classic cartoon",
                      "Skeleton Dance"],
        "hashtags": ["#SillySymphony", "#Disney", "#8K", "#PublicDomain", "#VintageAnimation"],
    },
}

# ═══════════════════════════════════════════════════════════════
# 3.  TITLE CLEANER & IDEAL COMPUTER
# ═══════════════════════════════════════════════════════════════
# Patterns to strip from titles
TITLE_STRIP_PATTERNS = [
    (re.compile(r'\s*\(4K UHD\)'),          ''),     # (4K UHD) suffix
    (re.compile(r'\s*\|\s*@remAIke_IT'),    ''),     # @handle
    (re.compile(r'\s*\|\s*Best Online Version'), ''), # noise
    (re.compile(r'\s*SLS\b', re.I),         ''),     # SLS artifact
    (re.compile(r'\s{2,}'),                 ' '),    # double spaces
    (re.compile(r'\s*\|\s*$'),              ''),     # trailing pipe
]

def clean_title(title):
    """Apply all title cleaning rules."""
    t = title.strip()
    for pat, repl in TITLE_STRIP_PATTERNS:
        t = pat.sub(repl, t)
    return t.strip()


def extract_episode_info(title, series_id):
    """Extract episode number, total, title, year from a series title."""
    info = {}
    # Pattern: (31/52) or (05/17)
    m = re.search(r'\((\d+)/(\d+)\)', title)
    if m:
        info["ep_num"] = int(m.group(1))
        info["ep_total"] = int(m.group(2))
    # Pattern: Nr. 513 or Nr 751
    m = re.search(r'Nr\.?\s*(\d+)', title)
    if m:
        info["wochenschau_nr"] = int(m.group(1))
    # Pattern: (1932) or (10.07.1940)
    m = re.search(r'\((\d{4})\)', title)
    if m:
        info["year"] = int(m.group(1))
    m = re.search(r'\((\d{1,2}\.\d{2}\.\d{4})\)', title)
    if m:
        info["full_date"] = m.group(1)
    return info


# ═══════════════════════════════════════════════════════════════
# 4.  DESCRIPTION AUDIT
# ═══════════════════════════════════════════════════════════════
CTA_BLOCK_PATTERN = re.compile(r'(LIKE|SUBSCRIBE|COMMENT)', re.I)
WEBSITE_PATTERN   = re.compile(r'www\.remaike\.IT', re.I)
YT_LINK_PATTERN   = re.compile(r'youtube\.com/@remAIke_IT', re.I)
CHAPTER_PATTERN   = re.compile(r'^\d{1,2}:\d{2}\s', re.M)
HASHTAG_PATTERN   = re.compile(r'#\w+')
DISCLAIMER_PATTERN = re.compile(r'HISTORISCHES\s+DOKUMENT|historical\s+document', re.I)

def audit_description(desc, series_id):
    """Audit a description and return issues + metrics."""
    result = {
        "has_cta": bool(CTA_BLOCK_PATTERN.search(desc)),
        "has_website": bool(WEBSITE_PATTERN.search(desc)),
        "has_yt_link": bool(YT_LINK_PATTERN.search(desc)),
        "has_chapters": bool(CHAPTER_PATTERN.search(desc)),
        "hashtag_count": len(HASHTAG_PATTERN.findall(desc)),
        "desc_length": len(desc),
        "issues": [],
    }
    
    if not result["has_cta"]:
        result["issues"].append("NO_CTA")
    if not result["has_website"]:
        result["issues"].append("NO_WEBSITE_LINK")
    if not result["has_yt_link"]:
        result["issues"].append("NO_YT_LINK")
    if result["hashtag_count"] > 5:
        result["issues"].append(f"TOO_MANY_HASHTAGS ({result['hashtag_count']})")
    if result["hashtag_count"] == 0:
        result["issues"].append("NO_HASHTAGS")
    if result["desc_length"] < 100:
        result["issues"].append("DESC_TOO_SHORT")
    
    # Wochenschau must have disclaimer
    if series_id == "wochenschau" and not DISCLAIMER_PATTERN.search(desc):
        result["issues"].append("WOCHENSCHAU_NO_DISCLAIMER")
    
    return result


# ═══════════════════════════════════════════════════════════════
# 5.  TITLE AUDIT
# ═══════════════════════════════════════════════════════════════
def audit_title(title, series_id):
    """Audit title and return issues."""
    issues = []
    
    if len(title) > 70:
        issues.append(f"TITLE_TOO_LONG ({len(title)}ch)")
    if "(4K UHD)" in title:
        issues.append("HAS_4K_UHD_SUFFIX")
    if "@remAIke_IT" in title:
        issues.append("HAS_HANDLE_IN_TITLE")
    if "Best Online Version" in title:
        issues.append("HAS_BEST_ONLINE_VERSION")
    if "  " in title:
        issues.append("DOUBLE_SPACES")
    if title.endswith("|") or title.endswith("| "):
        issues.append("TRAILING_PIPE")
    if "SLS" in title.upper() and series_id != "other":
        issues.append("HAS_SLS_ARTIFACT")
    if "8K" not in title and "8k" not in title:
        issues.append("MISSING_8K")
    
    # Keyword at start check
    rules = SERIES_RULES.get(series_id, {})
    if series_id != "other":
        # Series name should be at start
        expected_starts = {
            "betty_boop": ["Betty Boop"],
            "soundie": ["Soundie"],
            "wochenschau": ["Wochenschau"],
            "alfred_j_kwak": ["Alfred"],
            "superman": ["Superman"],
            "popeye": ["Popeye"],
            "felix_the_cat": ["Felix"],
            "casper": ["Casper"],
            "krtek": ["Maulwurf", "Der kleine Maulwurf", "Krtek"],
            "ken_block": ["Ken Block", "Gymkhana", "Getaway"],
            "looney_tunes": ["Looney", "Porky", "Merrie", "Bosko"],
            "christmas": ["Christmas", "Santa", "Rudolph", "Snowflake"],
            "astro_boy": ["Astro Boy"],
            "bravestarr": ["BraveStarr"],
            "chaplin": ["Chaplin", "Charlie Chaplin"],
            "buster_keaton": ["Buster Keaton", "Sherlock"],
            "nasa": ["NASA", "Skylab"],
            "silly_symphony": ["Silly Symphony"],
        }
        starts = expected_starts.get(series_id, [])
        if starts and not any(title.startswith(s) for s in starts):
            issues.append("KEYWORD_NOT_AT_START")
    
    return issues


# ═══════════════════════════════════════════════════════════════
# 6.  TAG AUDIT
# ═══════════════════════════════════════════════════════════════
def audit_tags(tags, series_id):
    """Audit tags and return issues."""
    issues = []
    
    if len(tags) > 15:
        issues.append(f"TOO_MANY_TAGS ({len(tags)})")
    if len(tags) == 0:
        issues.append("NO_TAGS")
    if len(tags) < 5 and len(tags) > 0:
        issues.append(f"TOO_FEW_TAGS ({len(tags)})")
    
    # Check tag content quality
    tag_str = " ".join(tags).lower()
    if "8k" not in tag_str and "8K" not in " ".join(tags):
        issues.append("TAGS_MISSING_8K")
    if "public domain" not in tag_str and series_id not in ["ken_block"]:
        issues.append("TAGS_MISSING_PUBLIC_DOMAIN")
    
    return issues


# ═══════════════════════════════════════════════════════════════
# 7.  LOCALIZATION IDEAL STATE
# ═══════════════════════════════════════════════════════════════
def compute_ideal_localizations(item, series_id, ideal_title):
    """Compute what localizations SHOULD look like."""
    current_locs = item.get("localizations", {})
    rules = SERIES_RULES.get(series_id, {})
    s = item["snippet"]
    desc = s.get("description", "")
    
    ideal_locs = {}
    
    if series_id == "krtek":
        # Krtek: proper multi-language episode titles
        ep_map = rules.get("episode_titles", {})
        prefix_map = rules.get("title_prefix_by_lang", {})
        
        ep_key = None
        for key in ep_map:
            if key.lower() in s["title"].lower():
                ep_key = key
                break
        
        if ep_key:
            ep = ep_map[ep_key]
            year = ep.get("year")
            year_str = f" ({year})" if year else ""
            
            for lang in ["en", "de", "es", "fr", "pt"]:
                prefix = prefix_map.get(lang, prefix_map["en"])
                # DE uses the original German episode name (the dict key)
                if lang == "de":
                    ep_title = ep_key  # e.g. "Die Rakete"
                else:
                    ep_title = ep.get(lang, ep.get("en", ep_key))
                loc_title = f"{prefix}: {ep_title}{year_str} | 8K HQ"
                if len(loc_title) > 70:
                    loc_title = f"Krtek: {ep_title}{year_str} | 8K HQ"
                
                cur_title = current_locs.get(lang, {}).get("title", "")
                cur_desc  = current_locs.get(lang, {}).get("description", desc)
                
                ideal_locs[lang] = {
                    "title": loc_title,
                    "description": cur_desc,  # keep current desc unless we have a better one
                    "needs_update": cur_title != loc_title,
                }
    else:
        # Other series: check if current locs just copy German
        for lang in ["en", "de", "es", "fr", "pt"]:
            cur = current_locs.get(lang, {})
            cur_title = cur.get("title", "")
            cur_desc  = cur.get("description", "")
            
            # Remove (4K UHD) from loc titles too
            if cur_title:
                cleaned = clean_title(cur_title)
                ideal_locs[lang] = {
                    "title": cleaned,
                    "description": cur_desc,
                    "needs_update": cleaned != cur_title,
                }
    
    return ideal_locs


# ═══════════════════════════════════════════════════════════════
# 8.  SEO SCORE CALCULATOR
# ═══════════════════════════════════════════════════════════════
def compute_seo_score(title_issues, desc_audit, tag_issues):
    """Score 0-100 based on all issues found."""
    score = 100
    
    # Title issues (40 points max)
    title_deductions = {
        "TITLE_TOO_LONG": -5, "HAS_4K_UHD_SUFFIX": -3, "HAS_HANDLE_IN_TITLE": -3,
        "HAS_BEST_ONLINE_VERSION": -3, "DOUBLE_SPACES": -2, "TRAILING_PIPE": -2,
        "HAS_SLS_ARTIFACT": -5, "MISSING_8K": -5, "KEYWORD_NOT_AT_START": -8,
    }
    for issue in title_issues:
        key = issue.split(" (")[0]  # strip parenthetical
        score += title_deductions.get(key, -2)
    
    # Description issues (30 points max)
    desc_deductions = {
        "NO_CTA": -8, "NO_WEBSITE_LINK": -5, "NO_YT_LINK": -5,
        "NO_HASHTAGS": -3, "DESC_TOO_SHORT": -5,
        "WOCHENSCHAU_NO_DISCLAIMER": -10,
    }
    for issue in desc_audit.get("issues", []):
        key = issue.split(" (")[0]
        score += desc_deductions.get(key, -2)
    if desc_audit.get("has_chapters"):
        score += 3  # bonus
    
    # Tag issues (10 points max)
    tag_deductions = {
        "NO_TAGS": -8, "TAGS_MISSING_8K": -2, "TAGS_MISSING_PUBLIC_DOMAIN": -2,
    }
    for issue in tag_issues:
        key = issue.split(" (")[0]
        score += tag_deductions.get(key, -2)
    
    return max(0, min(100, score))


# ═══════════════════════════════════════════════════════════════
# 9.  COMPUTE COMPLETE IDEAL STATE
# ═══════════════════════════════════════════════════════════════
def compute_ideal_state(item, series_id):
    """Compute the complete ideal state for a video."""
    s = item["snippet"]
    rules = SERIES_RULES.get(series_id, {})
    
    # ── Title ──
    ideal_title = clean_title(s["title"])
    
    # For Krtek, use German title format
    if series_id == "krtek":
        ep_map = rules.get("episode_titles", {})
        prefix_map = rules.get("title_prefix_by_lang", {})
        for key in ep_map:
            if key.lower() in s["title"].lower():
                ep = ep_map[key]
                year = ep.get("year")
                year_str = f" ({year})" if year else ""
                # DE title: German prefix + German episode name
                ideal_title = f"{prefix_map['de']}: {key}{year_str} | 8K HQ"
                break
    
    # ── Category ──
    ideal_category = rules.get("correct_category", s["categoryId"])
    
    # ── Tags ──
    current_tags = s.get("tags", [])
    ideal_tags_base = rules.get("tags_base", [])
    
    # ── CTA ──
    ideal_cta = rules.get("cta", "")
    
    # ── Hashtags ──
    ideal_hashtags = rules.get("hashtags", [])
    
    # ── Localizations ──
    ideal_locs = compute_ideal_localizations(item, series_id, ideal_title)
    
    # ── Description checks ──
    desc = s.get("description", "")
    desc_audit = audit_description(desc, series_id)
    
    # ── Title checks ──
    title_issues = audit_title(s["title"], series_id)
    
    # ── Tag checks ──
    tag_issues = audit_tags(current_tags, series_id)
    
    # ── SEO Score ──
    seo_score = compute_seo_score(title_issues, desc_audit, tag_issues)
    
    # ── Build changes dict ──
    changes = {}
    
    if s["title"] != ideal_title:
        changes["title"] = {"from": s["title"], "to": ideal_title}
    
    if str(s["categoryId"]) != str(ideal_category):
        changes["category"] = {"from": s["categoryId"], "to": str(ideal_category)}
    
    loc_changes = {}
    for lang, loc in ideal_locs.items():
        if loc.get("needs_update"):
            current_loc_t = item.get("localizations", {}).get(lang, {}).get("title", "")
            loc_changes[lang] = {"from": current_loc_t, "to": loc["title"]}
    if loc_changes:
        changes["localizations"] = loc_changes
    
    return {
        "ideal_title": ideal_title,
        "ideal_category": str(ideal_category),
        "ideal_cta": ideal_cta,
        "ideal_hashtags": ideal_hashtags,
        "ideal_tags_base": ideal_tags_base,
        "ideal_locs": {lang: loc["title"] for lang, loc in ideal_locs.items()},
        "seo_score": seo_score,
        "title_issues": title_issues,
        "desc_issues": desc_audit["issues"],
        "tag_issues": tag_issues,
        "desc_metrics": {
            "length": desc_audit["desc_length"],
            "has_cta": desc_audit["has_cta"],
            "has_website": desc_audit["has_website"],
            "has_yt_link": desc_audit["has_yt_link"],
            "has_chapters": desc_audit["has_chapters"],
            "hashtag_count": desc_audit["hashtag_count"],
        },
        "changes": changes,
        "has_changes": bool(changes),
        "change_types": list(changes.keys()),
        "quota_cost": sum([
            50 if "title" in changes or "category" in changes else 0,
            50 if "localizations" in changes else 0,
        ]),
    }


# ═══════════════════════════════════════════════════════════════
# 10.  FETCH ALL VIDEOS (Public via API Key, Private via OAuth)
# ═══════════════════════════════════════════════════════════════
def fetch_all_videos():
    """Fetch ALL video IDs from upload playlist, then full details."""
    print("  📡 Fetching video list from upload playlist...")
    
    # Use Public API for playlist read (1 unit per page)
    video_ids = []
    next_page = None
    while True:
        url = "https://youtube.googleapis.com/youtube/v3/playlistItems"
        params = {
            "part": "contentDetails",
            "playlistId": UPLOAD_PL,
            "maxResults": 50,
        }
        if next_page:
            params["pageToken"] = next_page
        data = _public_get(url, params)
        if "items" not in data:
            print(f"  ⚠️  API error: {data.get('error', {}).get('message', 'unknown')}")
            break
        for it in data["items"]:
            video_ids.append(it["contentDetails"]["videoId"])
        next_page = data.get("nextPageToken")
        if not next_page:
            break
    
    print(f"  📺 {len(video_ids)} total video IDs found")
    
    # Use OAuth for video details (need private video access + localizations)
    yt = get_yt_oauth()
    all_items = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = yt.videos().list(
            part="snippet,contentDetails,status,statistics,localizations,topicDetails",
            id=",".join(batch)
        ).execute()
        all_items.extend(resp.get("items", []))
        print(f"  Fetched details {len(all_items)}/{len(video_ids)}...")
    
    print(f"  ✅ {len(all_items)} videos with full details")
    return all_items


# ═══════════════════════════════════════════════════════════════
# 11.  FETCH PLAYLIST MEMBERSHIP
# ═══════════════════════════════════════════════════════════════
def fetch_playlists():
    """Fetch all playlists and their video assignments."""
    print("\n  📋 Fetching playlists...")
    
    url = "https://youtube.googleapis.com/youtube/v3/playlists"
    params = {
        "part": "snippet,contentDetails",
        "channelId": CHANNEL_ID,
        "maxResults": 50,
    }
    data = _public_get(url, params)
    
    playlists = {}
    video_to_playlists = defaultdict(list)
    
    for pl in data.get("items", []):
        pl_id = pl["id"]
        if pl_id == UPLOAD_PL:
            continue  # skip uploads playlist
        pl_info = {
            "id": pl_id,
            "title": pl["snippet"]["title"],
            "count": pl["contentDetails"]["itemCount"],
        }
        playlists[pl_id] = pl_info
        
        # Get videos in this playlist
        next_page = None
        while True:
            purl = "https://youtube.googleapis.com/youtube/v3/playlistItems"
            pparams = {
                "part": "contentDetails",
                "playlistId": pl_id,
                "maxResults": 50,
            }
            if next_page:
                pparams["pageToken"] = next_page
            pdata = _public_get(purl, pparams)
            for pit in pdata.get("items", []):
                vid = pit["contentDetails"]["videoId"]
                video_to_playlists[vid].append({
                    "playlist_id": pl_id,
                    "playlist_title": pl_info["title"],
                })
            next_page = pdata.get("nextPageToken")
            if not next_page:
                break
    
    print(f"  ✅ {len(playlists)} playlists, {len(video_to_playlists)} videos mapped")
    return playlists, dict(video_to_playlists)


# ═══════════════════════════════════════════════════════════════
# 12.  MAIN — Build the Next-Level Database
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("  VIDEO MASTER DATABASE v2 — NEXT LEVEL")
    print("  Building comprehensive Single Source of Truth")
    print("=" * 72)
    
    # ── Fetch everything ──
    all_items = fetch_all_videos()
    playlists, video_playlists = fetch_playlists()
    
    # ── Build database ──
    db = {
        "meta": {
            "version": 2,
            "created": datetime.now().isoformat(),
            "total_videos": len(all_items),
            "series_rules": list(SERIES_RULES.keys()),
            "channel_id": CHANNEL_ID,
        },
        "series_rules": SERIES_RULES,
        "playlists": playlists,
        "videos": {},
        "push_queue": [],
        "stats": {
            "by_series": {},
            "by_category": {},
            "by_privacy": {},
            "seo_scores": {"avg": 0, "min": 100, "max": 0, "distribution": {}},
            "issues_total": 0,
            "issue_frequency": defaultdict(int),
            "videos_needing_changes": 0,
            "total_quota_needed": 0,
        },
    }
    
    all_scores = []
    
    for item in all_items:
        vid = item["id"]
        s = item["snippet"]
        st = item["status"]
        stats_raw = item.get("statistics", {})
        
        series_id = detect_series(s["title"])
        ideal = compute_ideal_state(item, series_id)
        
        # ── Episode info ──
        ep_info = extract_episode_info(s["title"], series_id)
        
        # ── Current tags ──
        current_tags = s.get("tags", [])
        
        # ── Current localizations ──
        current_locs = {}
        for lang, loc in item.get("localizations", {}).items():
            current_locs[lang] = {
                "title": loc.get("title", ""),
                "description": loc.get("description", "")[:100] + "..." if len(loc.get("description", "")) > 100 else loc.get("description", ""),
            }
        
        # ── Playlist membership ──
        in_playlists = video_playlists.get(vid, [])
        
        # ── Build full entry ──
        entry = {
            "id": vid,
            "series": series_id,
            "episode_info": ep_info if ep_info else None,
            
            # Current state (live from YouTube)
            "current": {
                "title": s["title"],
                "description_preview": s.get("description", "")[:200],
                "description_length": len(s.get("description", "")),
                "categoryId": s["categoryId"],
                "tags": current_tags,
                "tag_count": len(current_tags),
                "defaultLanguage": s.get("defaultLanguage", ""),
                "defaultAudioLanguage": s.get("defaultAudioLanguage", ""),
                "publishedAt": s.get("publishedAt", ""),
                "localizations": current_locs,
                "localization_langs": list(current_locs.keys()),
            },
            
            # Status
            "status": {
                "privacy": st.get("privacyStatus", ""),
                "license": st.get("license", ""),
                "embeddable": st.get("embeddable", True),
                "madeForKids": st.get("madeForKids", False),
                "selfDeclaredMadeForKids": st.get("selfDeclaredMadeForKids", False),
            },
            
            # Metrics
            "metrics": {
                "views": int(stats_raw.get("viewCount", 0)),
                "likes": int(stats_raw.get("likeCount", 0)),
                "comments": int(stats_raw.get("commentCount", 0)),
                "favorites": int(stats_raw.get("favoriteCount", 0)),
            },
            
            # Content info
            "content": {
                "duration": item["contentDetails"]["duration"],
                "definition": item["contentDetails"].get("definition", ""),
                "dimension": item["contentDetails"].get("dimension", ""),
                "caption": item["contentDetails"].get("caption", "false"),
            },
            
            # Playlist membership
            "playlists": in_playlists,
            "in_playlist": len(in_playlists) > 0,
            
            # Ideal state (computed from rules)
            "ideal": {
                "title": ideal["ideal_title"],
                "categoryId": ideal["ideal_category"],
                "cta": ideal["ideal_cta"],
                "hashtags": ideal["ideal_hashtags"],
                "tags_base": ideal["ideal_tags_base"],
                "localizations": ideal["ideal_locs"],
            },
            
            # Audit results
            "audit": {
                "seo_score": ideal["seo_score"],
                "title_issues": ideal["title_issues"],
                "desc_issues": ideal["desc_issues"],
                "tag_issues": ideal["tag_issues"],
                "desc_metrics": ideal["desc_metrics"],
                "all_issues": ideal["title_issues"] + ideal["desc_issues"] + ideal["tag_issues"],
                "issue_count": len(ideal["title_issues"]) + len(ideal["desc_issues"]) + len(ideal["tag_issues"]),
            },
            
            # Changes needed
            "changes": ideal["changes"],
            "has_changes": ideal["has_changes"],
            "change_types": ideal["change_types"],
            "quota_cost": ideal["quota_cost"],
        }
        
        # ── Flag madeForKids issues ──
        if entry["status"]["madeForKids"]:
            entry["audit"]["all_issues"].append("MADE_FOR_KIDS_TRUE")
            entry["audit"]["issue_count"] += 1
        
        # ── Flag no-playlist ──
        if not entry["in_playlist"] and entry["status"]["privacy"] == "public":
            entry["audit"]["all_issues"].append("NOT_IN_ANY_PLAYLIST")
            entry["audit"]["issue_count"] += 1
        
        db["videos"][vid] = entry
        
        # ── Stats ──
        db["stats"]["by_series"].setdefault(series_id, {"count": 0, "total_views": 0, "avg_score": 0, "scores": []})
        db["stats"]["by_series"][series_id]["count"] += 1
        db["stats"]["by_series"][series_id]["total_views"] += entry["metrics"]["views"]
        db["stats"]["by_series"][series_id]["scores"].append(ideal["seo_score"])
        
        cat_name = s["categoryId"]
        db["stats"]["by_category"].setdefault(cat_name, 0)
        db["stats"]["by_category"][cat_name] += 1
        
        priv = st.get("privacyStatus", "unknown")
        db["stats"]["by_privacy"].setdefault(priv, 0)
        db["stats"]["by_privacy"][priv] += 1
        
        all_scores.append(ideal["seo_score"])
        
        for issue in entry["audit"]["all_issues"]:
            db["stats"]["issue_frequency"][issue.split(" (")[0]] += 1
            db["stats"]["issues_total"] += 1
        
        if ideal["has_changes"]:
            db["stats"]["videos_needing_changes"] += 1
            db["stats"]["total_quota_needed"] += ideal["quota_cost"]
            
            db["push_queue"].append({
                "id": vid,
                "series": series_id,
                "title": s["title"],
                "priority": _compute_priority(entry),
                "changes": ideal["changes"],
                "change_types": ideal["change_types"],
                "quota_cost": ideal["quota_cost"],
            })
    
    # ── Finalize stats ──
    if all_scores:
        db["stats"]["seo_scores"]["avg"] = round(sum(all_scores) / len(all_scores), 1)
        db["stats"]["seo_scores"]["min"] = min(all_scores)
        db["stats"]["seo_scores"]["max"] = max(all_scores)
        for s in all_scores:
            bucket = f"{(s // 10) * 10}-{(s // 10) * 10 + 9}"
            db["stats"]["seo_scores"]["distribution"].setdefault(bucket, 0)
            db["stats"]["seo_scores"]["distribution"][bucket] += 1
    
    # Average scores per series
    for sid, sdata in db["stats"]["by_series"].items():
        if sdata["scores"]:
            sdata["avg_score"] = round(sum(sdata["scores"]) / len(sdata["scores"]), 1)
        del sdata["scores"]  # don't store raw scores
    
    # Sort push queue by priority (highest first)
    db["push_queue"].sort(key=lambda x: -x["priority"])
    
    # Convert defaultdict to dict for JSON
    db["stats"]["issue_frequency"] = dict(db["stats"]["issue_frequency"])
    
    # ── Print report ──
    _print_report(db)
    
    # ── Save ──
    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  💾 Saved: {DB_PATH}")
    print(f"  📦 Size: {os.path.getsize(DB_PATH) / 1024:.0f} KB")


def _compute_priority(entry):
    """Priority score for push queue: higher = fix first."""
    p = 0
    views = entry["metrics"]["views"]
    
    # High-view videos first
    if views > 1000: p += 50
    elif views > 100: p += 30
    elif views > 10: p += 10
    
    # Title fixes are high priority (visible to users)
    if "title" in entry["changes"]:
        p += 40
    
    # Category fixes matter for algorithm
    if "category" in entry["changes"]:
        p += 35
    
    # Localization fixes matter for international reach
    if "localizations" in entry["changes"]:
        p += 20
    
    # Series-specific boost (popular series first)
    series_boost = {
        "felix_the_cat": 15, "superman": 15, "ken_block": 15,
        "christmas": 12, "betty_boop": 10, "popeye": 10,
        "alfred_j_kwak": 8, "krtek": 8, "soundie": 5,
    }
    p += series_boost.get(entry["series"], 0)
    
    return p


def _print_report(db):
    """Print comprehensive report."""
    print("\n" + "=" * 72)
    print("  📊 VIDEO MASTER DATABASE v2 — REPORT")
    print("=" * 72)
    
    print(f"\n  📺 Total Videos:      {db['meta']['total_videos']}")
    print(f"  📋 Playlists:         {len(db['playlists'])}")
    
    # Privacy
    print(f"\n  🔒 Privacy:")
    for priv, count in sorted(db["stats"]["by_privacy"].items()):
        print(f"     {priv:12s}: {count}")
    
    # SEO Scores
    seo = db["stats"]["seo_scores"]
    print(f"\n  🎯 SEO Scores:")
    print(f"     Average: {seo['avg']}/100")
    print(f"     Min:     {seo['min']}/100")
    print(f"     Max:     {seo['max']}/100")
    print(f"     Distribution:")
    for bucket in sorted(seo["distribution"].keys()):
        count = seo["distribution"][bucket]
        bar = "█" * (count // 2)
        print(f"       {bucket}: {count:3d} {bar}")
    
    # By Series
    print(f"\n  📺 By Series:")
    print(f"     {'Series':20s} {'Count':>5s} {'Views':>8s} {'Avg SEO':>8s}")
    print(f"     {'─'*20} {'─'*5} {'─'*8} {'─'*8}")
    for sid, sdata in sorted(db["stats"]["by_series"].items(), key=lambda x: -x[1]["total_views"]):
        print(f"     {sid:20s} {sdata['count']:5d} {sdata['total_views']:8,d} {sdata['avg_score']:7.1f}")
    
    # Top Issues
    print(f"\n  ⚠️  Top Issues ({db['stats']['issues_total']} total):")
    freq = db["stats"]["issue_frequency"]
    for issue, count in sorted(freq.items(), key=lambda x: -x[1])[:15]:
        bar = "█" * (count // 5)
        print(f"     {count:4d}× {issue:35s} {bar}")
    
    # Push Queue Summary
    pq = db["push_queue"]
    print(f"\n  🚀 Push Queue:")
    print(f"     Videos needing changes: {db['stats']['videos_needing_changes']}")
    print(f"     Total quota needed:     {db['stats']['total_quota_needed']:,d} units")
    print(f"     Days needed (10k/day):  {max(1, db['stats']['total_quota_needed'] // 10000 + 1)}")
    
    if pq:
        print(f"\n  🔝 Top 10 Priority Fixes:")
        for item in pq[:10]:
            types = ", ".join(item["change_types"])
            print(f"     [{item['priority']:3d}] {item['series']:15s} | {types:20s} | {item['title'][:50]}")


if __name__ == "__main__":
    main()
