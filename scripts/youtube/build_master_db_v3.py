"""
VIDEO MASTER DATABASE v3 — ULTIMATE Single Source of Truth
=============================================================
Evolution of v2. Now includes:
- Full description text (not just preview)
- Complete IDEAL description generation per series
- Shorts detection & viral design scoring
- Seasonal awareness (Valentine's Day, Halloween, Christmas, etc.)
- Promotional cross-linking (Shorts → main video)
- Complete ideal tag sets (not just base tags)
- Episode info extraction (number, name, year)
- Thumbnail URL tracking
- View velocity (views / days since publish)
- "Other" series sub-classification
- Full change diff with priority + quota cost
- Action recommendations per video

Quota: ~14 units (read only)
"""
import json, os, re, sys, math
from datetime import datetime, timezone
from collections import defaultdict, Counter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import requests

# ─── Config ──────────────────────────────────────────────────
OAUTH_PATH  = "D:/remaike.TV/config/youtube_oauth.json"
DB_PATH     = "D:/remaike.TV/config/video_master_db_v3.json"
CHANNEL_ID  = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PL   = "UUVFv6Egpl0LDvigpFbQXNeQ"
API_KEY     = os.getenv("YOUTUBE_API_KEY", "")

WOCHENSCHAU_LOC_PATH = "D:/remaike.TV/config/wochenschau_complete_locations.json"
BRAVESTARR_PATH      = "D:/remaike.TV/config/bravestarr_episodes.json"

NOW = datetime.now(timezone.utc)

# ─── Auth ────────────────────────────────────────────────────
_oauth_token = None
def _ensure_token():
    global _oauth_token
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"), refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"], client_secret=d["client_secret"],
    )
    if not creds.valid:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
        print(f"  🔄 Token refreshed")
    _oauth_token = creds.token
    return _oauth_token

def _public_get(url, params):
    if API_KEY:
        params["key"] = API_KEY
        return requests.get(url, params=params).json()
    else:
        token = _ensure_token()
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if "error" in data:
            print(f"  ⚠️  API error: {data['error'].get('message', '')[:80]}")
        return data

def get_yt_oauth():
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"), refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"], client_secret=d["client_secret"],
    )
    if not creds.valid:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)


# ═══════════════════════════════════════════════════════════════
# 1. SERIES DETECTION (regex-based, ordered by specificity)
# ═══════════════════════════════════════════════════════════════
SERIES_PATTERNS = [
    ("betty_boop",     re.compile(r'betty\s*boop',                re.I)),
    ("soundie",        re.compile(r'\bsoundie\b',                 re.I)),
    ("wochenschau",    re.compile(r'wochenschau',                 re.I)),
    ("alfred_j_kwak",  re.compile(r'alfred.*?(kwak|quack)',        re.I)),
    ("superman",       re.compile(r'superman.*(fleischer|/17\s*\))', re.I)),
    ("popeye",         re.compile(r'\bpopeye\b',                  re.I)),
    ("felix_the_cat",  re.compile(r'felix.*cat|felix.*/175\)',     re.I)),
    ("casper",         re.compile(r'\bcasper\b',                  re.I)),
    ("krtek",          re.compile(r'maulwurf|krtek',              re.I)),
    ("ken_block",      re.compile(r'ken\s*block|gymkhana|getaway.*stockholm', re.I)),
    ("looney_tunes",   re.compile(r'looney|porky|merrie|bosko',   re.I)),
    ("christmas",      re.compile(r'christmas|santa|snowflake|rudolph|twas.*night', re.I)),
    ("astro_boy",      re.compile(r'astro\s*boy',                 re.I)),
    ("bravestarr",     re.compile(r'bravestarr|brave\s*starr',    re.I)),
    ("chaplin",        re.compile(r'\bchaplin\b',                 re.I)),
    ("buster_keaton",  re.compile(r'buster\s*keaton|sherlock\s*jr', re.I)),
    ("nasa",           re.compile(r'\bnasa\b|skylab',             re.I)),
    ("silly_symphony", re.compile(r'silly\s*symphony|skeleton\s*dance', re.I)),
    ("film_noir",      re.compile(r'detour|scarlet\s*street|strange\s*love', re.I)),
    ("teaserama",      re.compile(r'teaserama|bettie\s*page',     re.I)),
]

def detect_series(title):
    for sid, pat in SERIES_PATTERNS:
        if pat.search(title):
            return sid
    return "other"


# ═══════════════════════════════════════════════════════════════
# 2. COMPLETE SERIES RULES — All-in-one knowledge base
# ═══════════════════════════════════════════════════════════════
SERIES_RULES = {
    "betty_boop": {
        "origin": "USA", "creator": "Max Fleischer", "language_nature": "english",
        "correct_category": "1", "total_episodes": 105,
        "title_format": "Betty Boop ({ep}/{total}): {ep_title} ({year}) | 8K HQ",
        "cta": "💋 Describe Betty in ONE word! Comment below!",
        "tags_base": ["Betty Boop", "Max Fleischer", "Fleischer Studios", "1930s",
                      "vintage cartoon", "pre-code", "jazz age", "animation",
                      "8K", "public domain", "classic cartoon", "restored"],
        "hashtags": ["#BettyBoop", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
        "seasonal": {
            "valentine": {
                "boost_episodes": ["Minnie the Moocher", "Bamboo Isle", "Stopping the Show",
                                   "Sally Swing", "Swing School", "S.O.S.", "Dizzy Red Riding Hood"],
                "extra_tags": ["valentine", "love", "romance", "valentines day"],
                "extra_hashtags": ["#ValentinesDay", "#Love"],
                "seasonal_cta": "💕 Who's YOUR cartoon crush? Happy Valentine's Day! 💋",
            },
            "halloween": {
                "boost_episodes": ["Minnie the Moocher", "Snow White", "Ha! Ha! Ha!",
                                   "Cab Calloway Ghost Dance", "Bimbo's Initiation"],
                "extra_tags": ["halloween", "spooky", "ghost", "skeleton"],
                "extra_hashtags": ["#Halloween", "#Spooky"],
                "seasonal_cta": "👻 Which Betty Boop episode is the SCARIEST? Comment!",
            },
        },
        "shorts_strategy": {
            "viral_hooks": [
                "Betty Boop's most ICONIC dance 💋 (1932)",
                "This 1930s cartoon was BANNED ❌",
                "Cab Calloway as a GHOST WALRUS 👻 Betty Boop",
            ],
            "best_clips": ["Minnie the Moocher", "Snow White", "Bimbo's Initiation"],
            "format": "CINEMA",  # 60s cinematic clip
        },
        "description_template": (
            "{ep_line}\n\n"
            "Enjoy this classic Betty Boop cartoon in stunning 8K quality! "
            "Originally released in {year} by Fleischer Studios, this episode "
            "showcases the iconic jazz-age animation style that made Betty Boop "
            "a cultural phenomenon.\n\n"
            "Betty Boop was created by animator Max Fleischer and became one of the "
            "most popular animated characters of the 1930s, known for her distinctive "
            "baby voice and flirtatious personality.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👆 LIKE if you love Betty Boop!\n"
            "💬 {cta}\n"
            "🔔 SUBSCRIBE for more vintage cartoons in 8K!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 www.remaike.IT\n"
            "📺 https://www.youtube.com/@remAIke_IT\n\n"
            "#BettyBoop #VintageCartoon #8K #PublicDomain #Animation"
        ),
    },

    "soundie": {
        "origin": "USA", "language_nature": "music",
        "correct_category": "10",  # Music!
        "title_format": "Soundie: {song_title} | 8K HQ",
        "cta": "🎵 Name this genre in ONE word! Comment below!",
        "tags_base": ["soundie", "soundies", "1940s", "vintage music", "jazz", "swing",
                      "big band", "jukebox", "panoram", "8K", "public domain",
                      "classic music", "music video", "official audio"],
        "hashtags": ["#Soundie", "#VintageMusic", "#1940s", "#Jazz", "#8K"],
        "seasonal": {
            "valentine": {
                "boost_keywords": ["love", "heart", "kiss", "sweetheart", "beautiful"],
                "extra_tags": ["valentine", "love song", "romantic"],
                "extra_hashtags": ["#ValentinesDay", "#LoveSong"],
            },
        },
        "shorts_strategy": {
            "note": "Soundies ARE natural Shorts (2-3 min). Full video = Short.",
            "viral_hooks": ["This 1940s music video looks like it's from 2026 🤯"],
        },
        "description_template": (
            "🎵 {song_title}\n\n"
            "A vintage Soundie from the 1940s, restored in stunning 8K quality. "
            "Soundies were short musical films shown in coin-operated Panoram "
            "jukeboxes in bars, restaurants, and nightclubs across America.\n\n"
            "This is the original performance — no AI, no deepfakes, just pure "
            "vintage artistry from the golden age of jazz and swing.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👆 LIKE if you love vintage music!\n"
            "💬 {cta}\n"
            "🔔 SUBSCRIBE for more 1940s music in 8K!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 www.remaike.IT\n"
            "📺 https://www.youtube.com/@remAIke_IT\n\n"
            "#Soundie #VintageMusic #1940s #Jazz #8K"
        ),
    },

    "wochenschau": {
        "origin": "Germany (Nazi era)", "language_nature": "german_narration",
        "correct_category": "27", "requires_disclaimer": True,
        "title_format": "Wochenschau {nr}: {event} ({date}) | 8K HQ",
        "cta": "📚 How is this era taught in your country? Share in the comments!",
        "tags_base": ["wochenschau", "german newsreel", "wwii history", "archive footage",
                      "historical film", "zeitgeschichte", "world history", "8K",
                      "documentary", "kino wochenschau", "third reich", "public domain"],
        "hashtags": ["#Wochenschau", "#WWII", "#8K", "#History", "#PublicDomain"],
        "madeForKids": False,
        "description_template": (
            "⚠️ HISTORISCHES DOKUMENT — Educational purposes only.\n\n"
            "Deutsche Wochenschau {nr_line}— original WWII German newsreel, "
            "restored in 8K quality for historical documentation.\n\n"
            "{event_line}"
            "This video serves exclusively for historical education and documentation. "
            "The views expressed in this footage do NOT reflect the views of the uploader.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👆 LIKE for more historical documentaries!\n"
            "💬 {cta}\n"
            "🔔 SUBSCRIBE for restored WWII footage in 8K!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 www.remaike.IT\n"
            "📺 https://www.youtube.com/@remAIke_IT\n\n"
            "#Wochenschau #WWII #8K #History #PublicDomain"
        ),
    },

    "alfred_j_kwak": {
        "origin": "Netherlands/Japan/Germany", "creator": "Herman van Veen",
        "language_nature": "dubbed_multilingual",
        "correct_category": "1", "total_episodes": 52,
        "title_format": "Alfred Jodokus Quack ({ep}/52): {ep_title} | Deutsch | 8K HQ",
        "cta": "🦆 Who showed you Alfred as a kid? Comment below!",
        "tags_base": ["Alfred J. Kwak", "Alfred Jodokus Quack", "Alfred Jodokus Kwak",
                      "Alfred Jodocus Kwak", "Kwak", "Quack",
                      "Herman van Veen", "Harald Siepermann", "Zeichentrick",
                      "Kinderserie", "Deutsch", "80er", "90er", "Nostalgie",
                      "Classic Animation", "8K", "restored"],
        "hashtags": ["#AlfredJKwak", "#Zeichentrick", "#8K", "#Nostalgie", "#PublicDomain"],
        "description_template": (
            "🦆 Alfred Jodokus Quack — {ep_line}\n\n"
            "Die beliebte Zeichentrickserie von Herman van Veen in 8K Qualität! "
            "Alfred J. Kwak wurde 1989-1991 produziert und behandelt auf kindgerechte "
            "Weise ernste Themen wie Rassismus, Diktatur und Umweltschutz.\n\n"
            "🇳🇱🇯🇵🇩🇪 A Dutch-Japanese-German co-production, known worldwide.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👆 LIKE wenn du mit Alfred aufgewachsen bist!\n"
            "💬 {cta}\n"
            "🔔 SUBSCRIBE for more classic cartoons in 8K!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 www.remaike.IT\n"
            "📺 https://www.youtube.com/@remAIke_IT\n\n"
            "#AlfredJKwak #Zeichentrick #8K #Nostalgie #PublicDomain"
        ),
    },

    "superman": {
        "origin": "USA", "creator": "Fleischer Studios",
        "language_nature": "english", "correct_category": "1", "total_episodes": 17,
        "title_format": "Superman ({ep}/17): {ep_title} ({year}) | Fleischer | 8K HQ",
        "cta": "💪 What's YOUR favorite Superman moment? Comment below!",
        "tags_base": ["Superman", "Fleischer Studios", "Fleischer Superman", "1940s",
                      "vintage cartoon", "animation", "superhero", "DC Comics",
                      "8K", "public domain", "classic cartoon"],
        "hashtags": ["#Superman", "#Fleischer", "#VintageCartoon", "#8K", "#PublicDomain"],
        "description_template": (
            "💪 Superman — {ep_line}\n\n"
            "The legendary Fleischer Studios Superman cartoons (1941-1943), "
            "restored in breathtaking 8K quality. These are widely considered "
            "the greatest Superman adaptations ever created, with groundbreaking "
            "rotoscope animation that still looks stunning today.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "👆 LIKE if Superman is YOUR hero!\n"
            "💬 {cta}\n"
            "🔔 SUBSCRIBE for more classic superhero cartoons in 8K!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🌐 www.remaike.IT\n"
            "📺 https://www.youtube.com/@remAIke_IT\n\n"
            "#Superman #Fleischer #VintageCartoon #8K #PublicDomain"
        ),
    },

    "popeye": {
        "origin": "USA", "creator": "Fleischer Studios",
        "language_nature": "english", "correct_category": "1",
        "cta": "💪 Popeye or Bluto — who wins in a REAL fight? Comment!",
        "tags_base": ["Popeye", "Popeye the Sailor", "Fleischer Studios", "1930s",
                      "vintage cartoon", "animation", "8K", "public domain",
                      "classic cartoon", "Olive Oyl", "Bluto"],
        "hashtags": ["#Popeye", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
    },

    "felix_the_cat": {
        "origin": "USA", "creator": "Pat Sullivan / Otto Messmer",
        "language_nature": "silent", "correct_category": "1",
        "cta": "🐱 Which era of animation do you love most? Comment!",
        "tags_base": ["Felix the Cat", "Pat Sullivan", "Otto Messmer", "1920s",
                      "silent cartoon", "vintage animation", "8K", "public domain",
                      "classic cartoon", "black and white"],
        "hashtags": ["#FelixTheCat", "#SilentCartoon", "#8K", "#PublicDomain", "#VintageAnimation"],
    },

    "casper": {
        "origin": "USA", "creator": "Famous Studios",
        "language_nature": "english", "correct_category": "1",
        "cta": "👻 Were you scared of Casper as a kid? Comment below!",
        "tags_base": ["Casper", "Casper the Friendly Ghost", "Famous Studios",
                      "1940s", "1950s", "vintage cartoon", "animation",
                      "8K", "public domain", "classic cartoon"],
        "hashtags": ["#Casper", "#FriendlyGhost", "#8K", "#PublicDomain", "#VintageCartoon"],
        "seasonal": {
            "halloween": {
                "extra_tags": ["halloween", "ghost", "spooky"],
                "extra_hashtags": ["#Halloween", "#Spooky"],
                "seasonal_cta": "🎃 Perfect Halloween cartoon! Are you watching this on Oct 31st?",
            },
        },
    },

    "krtek": {
        "origin": "Czech (Czechoslovakia)", "creator": "Zdeněk Miler",
        "language_nature": "mostly_silent", "correct_category": "1",
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
    },

    "ken_block": {
        "origin": "USA", "language_nature": "minimal_english",
        "correct_category": "2",
        "cta": "🏎️ What car would YOU pick for a Gymkhana? Comment!",
        "tags_base": ["Ken Block", "Gymkhana", "drift", "rally", "motorsport",
                      "8K", "Ford", "Subaru", "Hoonigan"],
        "hashtags": ["#KenBlock", "#Gymkhana", "#8K", "#Drift", "#Motorsport"],
    },

    "looney_tunes": {
        "origin": "USA", "creator": "Warner Bros.",
        "language_nature": "english", "correct_category": "1",
        "cta": "🐰 Who's YOUR favorite Looney Tunes character? Comment!",
        "tags_base": ["Looney Tunes", "Merrie Melodies", "Warner Bros", "1930s",
                      "vintage cartoon", "animation", "8K", "public domain",
                      "Porky Pig", "Bosko", "classic cartoon"],
        "hashtags": ["#LooneyTunes", "#VintageCartoon", "#8K", "#PublicDomain", "#Animation"],
    },

    "christmas": {
        "origin": "USA", "language_nature": "english", "correct_category": "1",
        "cta": "🎄 What's YOUR holiday tradition? Comment below!",
        "tags_base": ["Christmas", "holiday", "vintage", "classic", "animation",
                      "8K", "public domain", "Santa Claus", "holiday special"],
        "hashtags": ["#Christmas", "#VintageCartoon", "#8K", "#PublicDomain", "#Holiday"],
        "seasonal": {
            "christmas": {
                "peak_months": [11, 12],
                "extra_tags": ["christmas 2026", "holiday season", "xmas"],
                "seasonal_cta": "🎅 What's YOUR favorite Christmas memory? Comment!",
            },
        },
    },

    "astro_boy": {
        "origin": "Japan", "creator": "Osamu Tezuka",
        "language_nature": "japanese_dubbed", "correct_category": "1",
        "cta": "🤖 Did you grow up with Astro Boy? In which language? Comment!",
        "tags_base": ["Astro Boy", "Tetsuwan Atom", "Osamu Tezuka", "anime",
                      "1960s", "classic anime", "8K", "Japanese animation"],
        "hashtags": ["#AstroBoy", "#TetsuwanAtom", "#8K", "#Anime", "#OsamuTezuka"],
    },

    "bravestarr": {
        "origin": "USA", "creator": "Filmation",
        "language_nature": "dubbed_multilingual", "correct_category": "1",
        "total_episodes": 65,
        "cta": "🤠 Which BraveStarr power would you choose? Comment!",
        "tags_base": ["BraveStarr", "Brave Starr", "Filmation", "80s cartoon",
                      "space western", "8K", "animation", "New Texas"],
        "hashtags": ["#BraveStarr", "#Filmation", "#8K", "#80sCartoon", "#SpaceWestern"],
    },

    "chaplin": {
        "origin": "USA/UK", "creator": "Charlie Chaplin",
        "language_nature": "silent", "correct_category": "1",
        "cta": "🎩 Chaplin or Keaton? Who's the GOAT? Comment!",
        "tags_base": ["Charlie Chaplin", "silent film", "1920s", "slapstick",
                      "comedy", "8K", "public domain", "classic film"],
        "hashtags": ["#Chaplin", "#SilentFilm", "#8K", "#PublicDomain", "#ClassicComedy"],
    },

    "buster_keaton": {
        "origin": "USA", "creator": "Buster Keaton",
        "language_nature": "silent", "correct_category": "1",
        "cta": "🎩 Chaplin or Keaton? Who's the GOAT? Comment!",
        "tags_base": ["Buster Keaton", "silent film", "1920s", "slapstick",
                      "comedy", "8K", "public domain", "classic film"],
        "hashtags": ["#BusterKeaton", "#SilentFilm", "#8K", "#PublicDomain", "#ClassicComedy"],
    },

    "nasa": {
        "origin": "USA", "language_nature": "english",
        "correct_category": "27",
        "cta": "🚀 One word for 'space' in your language? Comment!",
        "tags_base": ["NASA", "space", "documentary", "Skylab", "space station",
                      "8K", "public domain", "science", "history"],
        "hashtags": ["#NASA", "#Space", "#8K", "#Documentary", "#PublicDomain"],
    },

    "silly_symphony": {
        "origin": "USA", "creator": "Walt Disney",
        "language_nature": "music", "correct_category": "1",
        "cta": "🎵 What's YOUR favorite classic Disney short? Comment!",
        "tags_base": ["Silly Symphony", "Walt Disney", "Disney", "1930s",
                      "animation", "8K", "public domain", "classic cartoon"],
        "hashtags": ["#SillySymphony", "#Disney", "#8K", "#PublicDomain", "#VintageAnimation"],
    },

    "film_noir": {
        "origin": "USA", "language_nature": "english", "correct_category": "1",
        "cta": "🎬 What's YOUR favorite film noir? Comment!",
        "tags_base": ["film noir", "classic cinema", "1940s", "black and white",
                      "thriller", "8K", "public domain", "Hollywood"],
        "hashtags": ["#FilmNoir", "#ClassicCinema", "#8K", "#PublicDomain", "#Hollywood"],
    },

    "teaserama": {
        "origin": "USA", "language_nature": "english", "correct_category": "1",
        "cta": "💃 Bettie Page or Tempest Storm? Comment your pick!",
        "tags_base": ["Bettie Page", "Teaserama", "burlesque", "1950s",
                      "pin-up", "vintage", "8K", "public domain"],
        "hashtags": ["#BettiePage", "#Burlesque", "#8K", "#PublicDomain", "#Vintage"],
        "seasonal": {
            "valentine": {
                "extra_tags": ["valentine", "pin-up", "love"],
                "extra_hashtags": ["#ValentinesDay"],
            },
        },
    },
}

# Fallback description for "other" series
GENERIC_DESCRIPTION_TEMPLATE = (
    "Enjoy this classic film in stunning 8K quality, carefully restored "
    "from the original source material.\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "👆 LIKE if you enjoyed this!\n"
    "💬 COMMENT your thoughts below!\n"
    "🔔 SUBSCRIBE for more restored classics in 8K!\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "🌐 www.remaike.IT\n"
    "📺 https://www.youtube.com/@remAIke_IT\n\n"
    "#8K #PublicDomain #ClassicFilm #Restored #Vintage"
)


# ═══════════════════════════════════════════════════════════════
# 3. TITLE CLEANING
# ═══════════════════════════════════════════════════════════════
TITLE_STRIP = [
    (re.compile(r'\s*\(4K UHD\)'),              ''),
    (re.compile(r'\s*\|\s*@remAIke_IT'),        ''),
    (re.compile(r'\s*\|\s*Best Online Version'), ''),
    (re.compile(r'\s*SLS\b', re.I),             ''),
    (re.compile(r'\s{2,}'),                     ' '),
    (re.compile(r'\s*\|\s*$'),                  ''),
]

def clean_title(title):
    t = title.strip()
    for pat, repl in TITLE_STRIP:
        t = pat.sub(repl, t)
    return t.strip()


# ═══════════════════════════════════════════════════════════════
# 4. SHORTS DETECTION & VIRAL SCORING
# ═══════════════════════════════════════════════════════════════
def parse_duration_seconds(iso_dur):
    """Parse ISO 8601 duration to seconds."""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_dur)
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s

def detect_shorts_type(title, duration_sec):
    """Detect if this is a YouTube Short and its subtype."""
    if duration_sec > 180:
        return None  # Not a Short (max 3 min)

    t = title.lower()
    if "short" in t or duration_sec <= 60:
        if duration_sec <= 15:
            return "IMPACT"      # Ultra-short, loop-designed
        elif duration_sec <= 30:
            return "HYPNO"       # Loop/hypnotic
        elif duration_sec <= 60:
            return "CINEMA"      # Cinematic moment
        else:
            return "EXTENDED"    # 1-3 min vertical short
    return None

def compute_viral_score(title, views, likes, comments, duration_sec, days_live):
    """Compute viral potential score 0-100."""
    score = 0

    # Engagement rate
    if views > 0:
        engagement = (likes + comments * 3) / views
        if engagement > 0.10: score += 30
        elif engagement > 0.05: score += 20
        elif engagement > 0.02: score += 10

    # View velocity (views/day)
    if days_live > 0:
        velocity = views / days_live
        if velocity > 100: score += 30
        elif velocity > 10: score += 20
        elif velocity > 1: score += 10

    # Title hook quality
    hooks = ["💀", "🤯", "👻", "❌", "😱", "⚡", "🔥", "💋", "!", "?"]
    hook_count = sum(1 for h in hooks if h in title)
    score += min(hook_count * 5, 15)

    # Length bonus for Shorts
    if 10 <= duration_sec <= 15:
        score += 15  # Sweet spot
    elif duration_sec <= 60:
        score += 10

    # Cap at 100
    return min(score, 100)


# ═══════════════════════════════════════════════════════════════
# 5. SEASONAL AWARENESS
# ═══════════════════════════════════════════════════════════════
SEASONAL_WINDOWS = {
    "valentine":  {"months": [2],      "peak_days": range(7, 15), "label": "💕 Valentine's Day"},
    "halloween":  {"months": [10],     "peak_days": range(20, 32), "label": "🎃 Halloween"},
    "christmas":  {"months": [11, 12], "peak_days": range(1, 32),  "label": "🎄 Christmas"},
    "newyear":    {"months": [1, 12],  "peak_days": range(28, 32), "label": "🎆 New Year"},
    "summer":     {"months": [6, 7, 8], "peak_days": range(1, 32), "label": "☀️ Summer"},
}

def get_active_seasons():
    """Return which seasonal campaigns are active NOW."""
    active = []
    month = NOW.month
    day = NOW.day
    for season, window in SEASONAL_WINDOWS.items():
        if month in window["months"]:
            active.append(season)
    return active

def get_seasonal_boost(series_id, title):
    """Check if this video should get seasonal boosting."""
    rules = SERIES_RULES.get(series_id, {})
    seasonal = rules.get("seasonal", {})
    active = get_active_seasons()
    boosts = []

    for season in active:
        if season in seasonal:
            s = seasonal[season]
            # Check episode match
            boost_eps = s.get("boost_episodes", [])
            boost_kw = s.get("boost_keywords", [])
            title_lower = title.lower()

            matched = any(ep.lower() in title_lower for ep in boost_eps)
            if not matched:
                matched = any(kw in title_lower for kw in boost_kw)

            if matched:
                boosts.append({
                    "season": season,
                    "label": SEASONAL_WINDOWS[season]["label"],
                    "extra_tags": s.get("extra_tags", []),
                    "extra_hashtags": s.get("extra_hashtags", []),
                    "seasonal_cta": s.get("seasonal_cta", ""),
                })
    return boosts


# ═══════════════════════════════════════════════════════════════
# 6. DESCRIPTION ANALYSIS & IDEAL GENERATION
# ═══════════════════════════════════════════════════════════════
CTA_PAT  = re.compile(r'(LIKE|SUBSCRIBE|COMMENT)', re.I)
WEB_PAT  = re.compile(r'www\.remaike\.IT', re.I)
YT_PAT   = re.compile(r'youtube\.com/@remAIke_IT', re.I)
CHAP_PAT = re.compile(r'^\d{1,2}:\d{2}\s', re.M)
HASH_PAT = re.compile(r'#\w+')
DISC_PAT = re.compile(r'HISTORISCHES\s+DOKUMENT|historical\s+document', re.I)

def audit_description(desc, series_id):
    issues = []
    metrics = {
        "length": len(desc),
        "has_cta": bool(CTA_PAT.search(desc)),
        "has_website": bool(WEB_PAT.search(desc)),
        "has_yt_link": bool(YT_PAT.search(desc)),
        "has_chapters": bool(CHAP_PAT.search(desc)),
        "hashtag_count": len(HASH_PAT.findall(desc)),
    }
    if not metrics["has_cta"]:         issues.append("NO_CTA")
    if not metrics["has_website"]:     issues.append("NO_WEBSITE_LINK")
    if not metrics["has_yt_link"]:     issues.append("NO_YT_LINK")
    if metrics["hashtag_count"] > 5:   issues.append(f"TOO_MANY_HASHTAGS ({metrics['hashtag_count']})")
    if metrics["hashtag_count"] == 0:  issues.append("NO_HASHTAGS")
    if metrics["length"] < 100:        issues.append("DESC_TOO_SHORT")
    if series_id == "wochenschau" and not DISC_PAT.search(desc):
        issues.append("WOCHENSCHAU_NO_DISCLAIMER")
    return issues, metrics

def generate_ideal_description(series_id, title, ep_info, cta):
    """Generate the ideal description from template."""
    rules = SERIES_RULES.get(series_id, {})
    template = rules.get("description_template", GENERIC_DESCRIPTION_TEMPLATE)

    # Build substitution values
    ep_line = title
    year = ep_info.get("year", "")
    nr_line = ""
    event_line = ""

    if ep_info.get("wochenschau_nr"):
        nr_line = f"Nr. {ep_info['wochenschau_nr']} "
    if ep_info.get("ep_num") and ep_info.get("ep_total"):
        ep_line = f"Episode {ep_info['ep_num']}/{ep_info['ep_total']}"

    try:
        desc = template.format(
            ep_line=ep_line, year=year or "the classic era",
            cta=cta, song_title=title,
            nr_line=nr_line, event_line=event_line,
        )
    except (KeyError, IndexError):
        desc = template  # fallback: raw template

    return desc


# ═══════════════════════════════════════════════════════════════
# 7. TITLE, TAG, LOCALIZATION AUDITS
# ═══════════════════════════════════════════════════════════════
KEYWORD_STARTS = {
    "betty_boop": ["Betty Boop"], "soundie": ["Soundie"],
    "wochenschau": ["Wochenschau"], "alfred_j_kwak": ["Alfred"],
    "superman": ["Superman"], "popeye": ["Popeye"],
    "felix_the_cat": ["Felix"], "casper": ["Casper"],
    "krtek": ["Maulwurf", "Der kleine Maulwurf", "Krtek"],
    "ken_block": ["Ken Block", "Gymkhana", "Getaway"],
    "looney_tunes": ["Looney", "Porky", "Merrie", "Bosko"],
    "christmas": ["Christmas", "Santa", "Rudolph", "Snowflake"],
    "astro_boy": ["Astro Boy"], "bravestarr": ["BraveStarr"],
    "chaplin": ["Chaplin", "Charlie"], "buster_keaton": ["Buster Keaton"],
    "nasa": ["NASA", "Skylab"], "silly_symphony": ["Silly Symphony"],
    "teaserama": ["Teaserama", "Bettie Page"],
}

def audit_title(title, series_id):
    issues = []
    if len(title) > 70:           issues.append(f"TITLE_TOO_LONG ({len(title)}ch)")
    if "(4K UHD)" in title:       issues.append("HAS_4K_UHD_SUFFIX")
    if "@remAIke_IT" in title:    issues.append("HAS_HANDLE_IN_TITLE")
    if "Best Online Version" in title: issues.append("HAS_BEST_ONLINE_VERSION")
    if "  " in title:             issues.append("DOUBLE_SPACES")
    if "8K" not in title and "8k" not in title: issues.append("MISSING_8K")
    starts = KEYWORD_STARTS.get(series_id, [])
    if starts and not any(title.startswith(s) for s in starts):
        issues.append("KEYWORD_NOT_AT_START")
    return issues

def audit_tags(tags, series_id):
    issues = []
    if len(tags) > 15:   issues.append(f"TOO_MANY_TAGS ({len(tags)})")
    if len(tags) == 0:   issues.append("NO_TAGS")
    elif len(tags) < 5:  issues.append(f"TOO_FEW_TAGS ({len(tags)})")
    tag_str = " ".join(tags).lower()
    if "8k" not in tag_str: issues.append("TAGS_MISSING_8K")
    if "public domain" not in tag_str and series_id not in ["ken_block"]:
        issues.append("TAGS_MISSING_PUBLIC_DOMAIN")
    return issues


# ═══════════════════════════════════════════════════════════════
# 8. LOCALIZATION IDEAL STATE (all series)
# ═══════════════════════════════════════════════════════════════
def compute_ideal_locs(item, series_id, ideal_title):
    current_locs = item.get("localizations", {})
    rules = SERIES_RULES.get(series_id, {})
    desc = item["snippet"].get("description", "")
    ideal_locs = {}

    if series_id == "krtek":
        ep_map = rules.get("episode_titles", {})
        prefix_map = rules.get("title_prefix_by_lang", {})
        ep_key = None
        for key in ep_map:
            if key.lower() in item["snippet"]["title"].lower():
                ep_key = key
                break
        if ep_key:
            ep = ep_map[ep_key]
            year = ep.get("year")
            ys = f" ({year})" if year else ""
            for lang in ["en", "de", "es", "fr", "pt"]:
                prefix = prefix_map.get(lang, prefix_map["en"])
                ep_title = ep_key if lang == "de" else ep.get(lang, ep.get("en", ep_key))
                lt = f"{prefix}: {ep_title}{ys} | 8K HQ"
                if len(lt) > 70:
                    lt = f"Krtek: {ep_title}{ys} | 8K HQ"
                cur_t = current_locs.get(lang, {}).get("title", "")
                ideal_locs[lang] = {"title": lt, "needs_update": cur_t != lt}
    else:
        # For all other series: clean (4K UHD) from loc titles
        for lang in ["en", "de", "es", "fr", "pt"]:
            cur = current_locs.get(lang, {})
            cur_t = cur.get("title", "")
            if cur_t:
                cleaned = clean_title(cur_t)
                ideal_locs[lang] = {"title": cleaned, "needs_update": cleaned != cur_t}

    return ideal_locs


# ═══════════════════════════════════════════════════════════════
# 9. EPISODE INFO EXTRACTION
# ═══════════════════════════════════════════════════════════════
def extract_episode_info(title, series_id):
    info = {}
    m = re.search(r'\((\d+)/(\d+)\)', title)
    if m:
        info["ep_num"] = int(m.group(1))
        info["ep_total"] = int(m.group(2))
    m = re.search(r'Nr\.?\s*(\d+)', title)
    if m:
        info["wochenschau_nr"] = int(m.group(1))
    m = re.search(r'\((\d{4})\)', title)
    if m:
        info["year"] = int(m.group(1))
    m = re.search(r'\((\d{1,2}\.\d{2}\.\d{4})\)', title)
    if m:
        info["full_date"] = m.group(1)
    # Extract episode title (text after ": " and before " (year)" or " | ")
    m = re.search(r':\s+(.+?)(?:\s*\(\d{4}\)|\s*\|)', title)
    if m:
        info["ep_title"] = m.group(1).strip()
    return info


# ═══════════════════════════════════════════════════════════════
# 10. SEO SCORE
# ═══════════════════════════════════════════════════════════════
def compute_seo_score(title_issues, desc_issues, tag_issues, desc_metrics, has_changes):
    score = 100
    title_ded = {"TITLE_TOO_LONG": -5, "HAS_4K_UHD_SUFFIX": -3, "HAS_HANDLE_IN_TITLE": -3,
                 "HAS_BEST_ONLINE_VERSION": -3, "DOUBLE_SPACES": -2, "MISSING_8K": -5,
                 "KEYWORD_NOT_AT_START": -8}
    desc_ded = {"NO_CTA": -8, "NO_WEBSITE_LINK": -5, "NO_YT_LINK": -5,
                "NO_HASHTAGS": -3, "DESC_TOO_SHORT": -5, "WOCHENSCHAU_NO_DISCLAIMER": -10}
    tag_ded = {"NO_TAGS": -8, "TAGS_MISSING_8K": -2, "TAGS_MISSING_PUBLIC_DOMAIN": -2}

    for i in title_issues: score += title_ded.get(i.split(" (")[0], -2)
    for i in desc_issues:  score += desc_ded.get(i.split(" (")[0], -2)
    for i in tag_issues:   score += tag_ded.get(i.split(" (")[0], -2)
    if desc_metrics.get("has_chapters"): score += 3
    return max(0, min(100, score))


# ═══════════════════════════════════════════════════════════════
# 11. COMPUTE COMPLETE IDEAL STATE
# ═══════════════════════════════════════════════════════════════
def compute_ideal(item, series_id):
    s = item["snippet"]
    rules = SERIES_RULES.get(series_id, {})
    desc = s.get("description", "")
    current_tags = s.get("tags", [])
    ep_info = extract_episode_info(s["title"], series_id)

    # ── Ideal title ──
    ideal_title = clean_title(s["title"])
    if series_id == "krtek":
        ep_map = rules.get("episode_titles", {})
        prefix_map = rules.get("title_prefix_by_lang", {})
        for key in ep_map:
            if key.lower() in s["title"].lower():
                ep = ep_map[key]
                year = ep.get("year")
                ys = f" ({year})" if year else ""
                ideal_title = f"{prefix_map['de']}: {key}{ys} | 8K HQ"
                break

    # ── Ideal category ──
    ideal_cat = rules.get("correct_category", s["categoryId"])

    # ── CTA ──
    cta = rules.get("cta", "💬 COMMENT your thoughts below!")

    # ── Ideal tags (base + episode-specific) ──
    ideal_tags = list(rules.get("tags_base", []))
    if ep_info.get("year"):
        ideal_tags.append(str(ep_info["year"]))
    if ep_info.get("ep_title") and ep_info["ep_title"] not in ideal_tags:
        ideal_tags.append(ep_info["ep_title"])

    # ── Seasonal boost ──
    seasonal_boosts = get_seasonal_boost(series_id, s["title"])
    seasonal_extra_tags = []
    seasonal_extra_hashtags = []
    for boost in seasonal_boosts:
        seasonal_extra_tags.extend(boost.get("extra_tags", []))
        seasonal_extra_hashtags.extend(boost.get("extra_hashtags", []))
        if boost.get("seasonal_cta"):
            cta = boost["seasonal_cta"]

    # Merge seasonal tags (max 15 total)
    all_tags = ideal_tags + seasonal_extra_tags
    if len(all_tags) > 15:
        all_tags = all_tags[:15]

    # ── Ideal hashtags ──
    ideal_hashtags = list(rules.get("hashtags", ["#8K", "#PublicDomain", "#Restored"]))
    ideal_hashtags.extend(seasonal_extra_hashtags)
    if len(ideal_hashtags) > 5:
        ideal_hashtags = ideal_hashtags[:5]

    # ── Ideal description ──
    ideal_desc = generate_ideal_description(series_id, s["title"], ep_info, cta)

    # ── Locs ──
    ideal_locs = compute_ideal_locs(item, series_id, ideal_title)

    # ── Audits ──
    title_issues = audit_title(s["title"], series_id)
    desc_issues, desc_metrics = audit_description(desc, series_id)
    tag_issues = audit_tags(current_tags, series_id)
    seo_score = compute_seo_score(title_issues, desc_issues, tag_issues, desc_metrics, False)

    # ── Changes ──
    changes = {}
    if s["title"] != ideal_title:
        changes["title"] = {"from": s["title"], "to": ideal_title}
    if str(s["categoryId"]) != str(ideal_cat):
        changes["category"] = {"from": s["categoryId"], "to": str(ideal_cat)}

    loc_changes = {}
    for lang, loc in ideal_locs.items():
        if loc.get("needs_update"):
            cur_t = item.get("localizations", {}).get(lang, {}).get("title", "")
            loc_changes[lang] = {"from": cur_t, "to": loc["title"]}
    if loc_changes:
        changes["localizations"] = loc_changes

    # Description change detection (check if missing mandatory elements)
    desc_needs_fix = len(desc_issues) > 0 and len(desc_issues) > 1
    if desc_needs_fix:
        changes["description_issues"] = desc_issues

    quota_cost = 0
    if "title" in changes or "category" in changes:
        quota_cost += 50
    if "localizations" in changes:
        quota_cost += 50

    return {
        "ideal_title": ideal_title,
        "ideal_category": str(ideal_cat),
        "ideal_cta": cta,
        "ideal_hashtags": ideal_hashtags,
        "ideal_tags": all_tags,
        "ideal_description_preview": ideal_desc[:300],
        "ideal_locs": {l: v["title"] for l, v in ideal_locs.items()},
        "seo_score": seo_score,
        "title_issues": title_issues,
        "desc_issues": desc_issues,
        "tag_issues": tag_issues,
        "desc_metrics": desc_metrics,
        "seasonal_boosts": seasonal_boosts,
        "changes": changes,
        "has_changes": bool(changes),
        "change_types": list(changes.keys()),
        "quota_cost": quota_cost,
        "ep_info": ep_info,
    }


# ═══════════════════════════════════════════════════════════════
# 12. FETCH ALL VIDEOS + PLAYLISTS
# ═══════════════════════════════════════════════════════════════
def fetch_all_videos():
    print("  📡 Fetching video list...")
    video_ids = []
    next_page = None
    while True:
        params = {"part": "contentDetails", "playlistId": UPLOAD_PL, "maxResults": 50}
        if next_page: params["pageToken"] = next_page
        data = _public_get("https://youtube.googleapis.com/youtube/v3/playlistItems", params)
        if "items" not in data: break
        for it in data["items"]:
            video_ids.append(it["contentDetails"]["videoId"])
        next_page = data.get("nextPageToken")
        if not next_page: break

    print(f"  📺 {len(video_ids)} video IDs")

    yt = get_yt_oauth()
    all_items = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = yt.videos().list(
            part="snippet,contentDetails,status,statistics,localizations,topicDetails",
            id=",".join(batch)
        ).execute()
        all_items.extend(resp.get("items", []))
        print(f"  Fetched {len(all_items)}/{len(video_ids)}...")
    print(f"  ✅ {len(all_items)} videos with full details")
    return all_items

def fetch_playlists():
    print("\n  📋 Fetching playlists...")
    data = _public_get("https://youtube.googleapis.com/youtube/v3/playlists",
                        {"part": "snippet,contentDetails", "channelId": CHANNEL_ID, "maxResults": 50})
    playlists = {}
    video_to_pl = defaultdict(list)
    for pl in data.get("items", []):
        pid = pl["id"]
        if pid == UPLOAD_PL: continue
        pl_info = {"id": pid, "title": pl["snippet"]["title"], "count": pl["contentDetails"]["itemCount"]}
        playlists[pid] = pl_info
        next_page = None
        while True:
            pparams = {"part": "contentDetails", "playlistId": pid, "maxResults": 50}
            if next_page: pparams["pageToken"] = next_page
            pdata = _public_get("https://youtube.googleapis.com/youtube/v3/playlistItems", pparams)
            for pit in pdata.get("items", []):
                vid = pit["contentDetails"]["videoId"]
                video_to_pl[vid].append({"playlist_id": pid, "playlist_title": pl_info["title"]})
            next_page = pdata.get("nextPageToken")
            if not next_page: break
    print(f"  ✅ {len(playlists)} playlists, {len(video_to_pl)} video mappings")
    return playlists, dict(video_to_pl)


# ═══════════════════════════════════════════════════════════════
# 13. MAIN — Build the ULTIMATE database
# ═══════════════════════════════════════════════════════════════
def main():
    print("=" * 72)
    print("  VIDEO MASTER DATABASE v3 — ULTIMATE")
    print(f"  {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Active seasons: {get_active_seasons()}")
    print("=" * 72)

    all_items = fetch_all_videos()
    playlists, video_pl = fetch_playlists()

    db = {
        "meta": {
            "version": 3, "created": NOW.isoformat(),
            "total_videos": len(all_items),
            "channel_id": CHANNEL_ID,
            "active_seasons": get_active_seasons(),
            "series_count": len(SERIES_RULES),
        },
        "series_rules_summary": {sid: {
            "correct_category": r.get("correct_category", "1"),
            "cta": r.get("cta", ""),
            "tags_count": len(r.get("tags_base", [])),
            "has_description_template": "description_template" in r,
            "has_seasonal": bool(r.get("seasonal")),
            "has_shorts_strategy": bool(r.get("shorts_strategy")),
        } for sid, r in SERIES_RULES.items()},
        "playlists": playlists,
        "videos": {},
        "shorts": [],
        "seasonal_opportunities": [],
        "push_queue": [],
        "stats": {
            "by_series": {}, "by_category": {}, "by_privacy": {},
            "seo_scores": {"avg": 0, "min": 100, "max": 0, "distribution": {}},
            "issues_total": 0, "issue_frequency": defaultdict(int),
            "videos_needing_changes": 0, "total_quota_needed": 0,
            "shorts_count": 0, "shorts_total_views": 0,
            "seasonal_boost_count": 0,
        },
    }

    all_scores = []

    for item in all_items:
        vid = item["id"]
        s = item["snippet"]
        st = item["status"]
        stats_raw = item.get("statistics", {})

        series_id = detect_series(s["title"])
        ideal = compute_ideal(item, series_id)

        # ── Duration & Shorts ──
        dur_sec = parse_duration_seconds(item["contentDetails"]["duration"])
        shorts_type = detect_shorts_type(s["title"], dur_sec)

        # ── View velocity ──
        pub_date = s.get("publishedAt", "")
        days_live = 0
        if pub_date:
            try:
                pub_dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                days_live = max(1, (NOW - pub_dt).days)
            except: pass
        views = int(stats_raw.get("viewCount", 0))
        likes = int(stats_raw.get("likeCount", 0))
        comments = int(stats_raw.get("commentCount", 0))
        velocity = round(views / max(1, days_live), 2)

        # ── Viral score (for Shorts) ──
        viral_score = 0
        if shorts_type:
            viral_score = compute_viral_score(s["title"], views, likes, comments, dur_sec, days_live)

        # ── Thumbnail ──
        thumbs = s.get("thumbnails", {})
        thumb_url = ""
        for res in ["maxres", "standard", "high", "medium", "default"]:
            if res in thumbs:
                thumb_url = thumbs[res].get("url", "")
                break

        # ── Current locs ──
        current_locs = {}
        for lang, loc in item.get("localizations", {}).items():
            current_locs[lang] = {"title": loc.get("title", ""), "desc_len": len(loc.get("description", ""))}

        # ── Full description (not just preview!) ──
        full_desc = s.get("description", "")

        # ── Build entry ──
        entry = {
            "id": vid,
            "series": series_id,
            "episode_info": ideal["ep_info"] if ideal["ep_info"] else None,

            "current": {
                "title": s["title"],
                "description": full_desc,  # FULL description!
                "categoryId": s["categoryId"],
                "tags": s.get("tags", []),
                "tag_count": len(s.get("tags", [])),
                "defaultLanguage": s.get("defaultLanguage", ""),
                "defaultAudioLanguage": s.get("defaultAudioLanguage", ""),
                "publishedAt": pub_date,
                "localizations": current_locs,
                "thumbnail_url": thumb_url,
            },

            "status": {
                "privacy": st.get("privacyStatus", ""),
                "license": st.get("license", ""),
                "embeddable": st.get("embeddable", True),
                "madeForKids": st.get("madeForKids", False),
            },

            "metrics": {
                "views": views, "likes": likes, "comments": comments,
                "days_live": days_live,
                "view_velocity": velocity,
                "engagement_rate": round((likes + comments * 3) / max(1, views) * 100, 2),
            },

            "content": {
                "duration_iso": item["contentDetails"]["duration"],
                "duration_sec": dur_sec,
                "definition": item["contentDetails"].get("definition", ""),
                "is_short": shorts_type is not None,
                "shorts_type": shorts_type,
                "viral_score": viral_score,
            },

            "playlists": video_pl.get(vid, []),
            "in_playlist": vid in video_pl,

            "ideal": {
                "title": ideal["ideal_title"],
                "categoryId": ideal["ideal_category"],
                "cta": ideal["ideal_cta"],
                "hashtags": ideal["ideal_hashtags"],
                "tags": ideal["ideal_tags"],
                "description_preview": ideal["ideal_description_preview"],
                "localizations": ideal["ideal_locs"],
            },

            "seasonal": {
                "boosts": ideal["seasonal_boosts"],
                "is_seasonal_now": len(ideal["seasonal_boosts"]) > 0,
            },

            "audit": {
                "seo_score": ideal["seo_score"],
                "title_issues": ideal["title_issues"],
                "desc_issues": ideal["desc_issues"],
                "tag_issues": ideal["tag_issues"],
                "desc_metrics": ideal["desc_metrics"],
                "all_issues": ideal["title_issues"] + ideal["desc_issues"] + ideal["tag_issues"],
                "issue_count": len(ideal["title_issues"]) + len(ideal["desc_issues"]) + len(ideal["tag_issues"]),
            },

            "changes": ideal["changes"],
            "has_changes": ideal["has_changes"],
            "change_types": ideal["change_types"],
            "quota_cost": ideal["quota_cost"],
        }

        # ── Extra flags ──
        if entry["status"]["madeForKids"]:
            entry["audit"]["all_issues"].append("MADE_FOR_KIDS_TRUE")
            entry["audit"]["issue_count"] += 1
        if not entry["in_playlist"] and entry["status"]["privacy"] == "public":
            entry["audit"]["all_issues"].append("NOT_IN_ANY_PLAYLIST")
            entry["audit"]["issue_count"] += 1

        db["videos"][vid] = entry

        # ── Shorts list ──
        if shorts_type:
            db["shorts"].append({
                "id": vid, "title": s["title"], "type": shorts_type,
                "duration_sec": dur_sec, "views": views, "viral_score": viral_score,
                "privacy": st.get("privacyStatus", ""),
                "promotes_main": None,  # Could link to main video
            })
            db["stats"]["shorts_count"] += 1
            db["stats"]["shorts_total_views"] += views

        # ── Seasonal opportunities ──
        if ideal["seasonal_boosts"]:
            db["seasonal_opportunities"].append({
                "id": vid, "title": s["title"], "series": series_id,
                "boosts": ideal["seasonal_boosts"],
                "current_views": views,
            })
            db["stats"]["seasonal_boost_count"] += 1

        # ── Stats ──
        db["stats"]["by_series"].setdefault(series_id, {"count": 0, "views": 0, "likes": 0, "scores": []})
        db["stats"]["by_series"][series_id]["count"] += 1
        db["stats"]["by_series"][series_id]["views"] += views
        db["stats"]["by_series"][series_id]["likes"] += likes
        db["stats"]["by_series"][series_id]["scores"].append(ideal["seo_score"])

        db["stats"]["by_category"].setdefault(s["categoryId"], 0)
        db["stats"]["by_category"][s["categoryId"]] += 1
        db["stats"]["by_privacy"].setdefault(st.get("privacyStatus","?"), 0)
        db["stats"]["by_privacy"][st.get("privacyStatus","?")] += 1

        all_scores.append(ideal["seo_score"])
        for issue in entry["audit"]["all_issues"]:
            db["stats"]["issue_frequency"][issue.split(" (")[0]] += 1
            db["stats"]["issues_total"] += 1

        if ideal["has_changes"]:
            db["stats"]["videos_needing_changes"] += 1
            db["stats"]["total_quota_needed"] += ideal["quota_cost"]
            db["push_queue"].append({
                "id": vid, "series": series_id, "title": s["title"],
                "priority": _priority(entry),
                "changes": ideal["changes"],
                "change_types": ideal["change_types"],
                "quota_cost": ideal["quota_cost"],
            })

    # ── Finalize ──
    if all_scores:
        db["stats"]["seo_scores"]["avg"] = round(sum(all_scores)/len(all_scores), 1)
        db["stats"]["seo_scores"]["min"] = min(all_scores)
        db["stats"]["seo_scores"]["max"] = max(all_scores)
        for sc in all_scores:
            b = f"{(sc//10)*10}-{(sc//10)*10+9}"
            db["stats"]["seo_scores"]["distribution"].setdefault(b, 0)
            db["stats"]["seo_scores"]["distribution"][b] += 1

    for sid, sd in db["stats"]["by_series"].items():
        if sd["scores"]:
            sd["avg_score"] = round(sum(sd["scores"])/len(sd["scores"]), 1)
        del sd["scores"]

    db["push_queue"].sort(key=lambda x: -x["priority"])
    db["stats"]["issue_frequency"] = dict(db["stats"]["issue_frequency"])

    _report(db)

    json.dump(db, open(DB_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"\n  💾 Saved: {DB_PATH}")
    print(f"  📦 Size: {os.path.getsize(DB_PATH)/1024:.0f} KB")


def _priority(entry):
    p = 0
    v = entry["metrics"]["views"]
    if v > 1000: p += 50
    elif v > 100: p += 30
    elif v > 10: p += 10
    if "title" in entry["changes"]: p += 40
    if "category" in entry["changes"]: p += 35
    if "localizations" in entry["changes"]: p += 20
    # Seasonal boost = urgent!
    if entry["seasonal"]["is_seasonal_now"]: p += 25
    # Shorts get priority (viral potential)
    if entry["content"]["is_short"]: p += 15
    series_boost = {"felix_the_cat": 15, "superman": 15, "ken_block": 15,
                    "christmas": 12, "betty_boop": 10, "popeye": 10,
                    "alfred_j_kwak": 8, "krtek": 8}
    p += series_boost.get(entry["series"], 0)
    return p


def _report(db):
    print("\n" + "=" * 72)
    print("  📊 VIDEO MASTER DATABASE v3 — REPORT")
    print("=" * 72)

    print(f"\n  📺 Total: {db['meta']['total_videos']} videos")
    print(f"  📋 Playlists: {len(db['playlists'])}")
    print(f"  🎬 Shorts: {db['stats']['shorts_count']} ({db['stats']['shorts_total_views']:,d} views)")
    print(f"  💕 Seasonal now: {db['stats']['seasonal_boost_count']} videos")

    # Privacy
    print(f"\n  🔒 Privacy: ", end="")
    for k, v in db["stats"]["by_privacy"].items():
        print(f"{k}={v}  ", end="")
    print()

    # SEO
    seo = db["stats"]["seo_scores"]
    print(f"\n  🎯 SEO: avg={seo['avg']} min={seo['min']} max={seo['max']}")
    for b in sorted(seo["distribution"]):
        c = seo["distribution"][b]
        print(f"     {b}: {c:3d} {'█' * (c // 3)}")

    # Series
    print(f"\n  📺 By Series:")
    print(f"     {'Series':20s} {'#':>4s} {'Views':>8s} {'Likes':>6s} {'SEO':>5s}")
    for sid, sd in sorted(db["stats"]["by_series"].items(), key=lambda x: -x[1]["views"]):
        print(f"     {sid:20s} {sd['count']:4d} {sd['views']:8,d} {sd['likes']:6,d} {sd.get('avg_score',0):5.1f}")

    # Issues
    print(f"\n  ⚠️  Issues ({db['stats']['issues_total']}):")
    for issue, cnt in sorted(db["stats"]["issue_frequency"].items(), key=lambda x: -x[1])[:15]:
        print(f"     {cnt:4d}× {issue}")

    # Shorts
    if db["shorts"]:
        print(f"\n  🎬 Shorts ({len(db['shorts'])}):")
        for sh in sorted(db["shorts"], key=lambda x: -x["views"])[:10]:
            priv = "🔒" if sh["privacy"] == "private" else "📺"
            print(f"     {priv} [{sh['type']:8s}] {sh['views']:>6,d}v | viral={sh['viral_score']:2d} | {sh['title'][:45]}")

    # Seasonal
    if db["seasonal_opportunities"]:
        print(f"\n  💕 Seasonal Opportunities NOW:")
        for so in db["seasonal_opportunities"][:10]:
            boosts = ", ".join(b["label"] for b in so["boosts"])
            print(f"     {so['series']:15s} | {boosts} | {so['title'][:40]}")

    # Push queue
    pq = db["push_queue"]
    print(f"\n  🚀 Push Queue: {db['stats']['videos_needing_changes']} videos, {db['stats']['total_quota_needed']:,d} quota")
    if pq:
        print(f"     Top 10:")
        for p in pq[:10]:
            ct = ",".join(p["change_types"])
            print(f"     [{p['priority']:3d}] {p['series']:15s} | {ct:25s} | {p['title'][:40]}")


if __name__ == "__main__":
    main()
