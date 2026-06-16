#!/usr/bin/env python3
"""Fix 31 YouTube videos: add localizations, fix tags, fix short descriptions."""

import json
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
import re
import os
import io
from datetime import datetime

# Fix console encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

CONFIG_DIR = r"D:\remaike.TV\config"

# ── 1. Load credentials & refresh token ──────────────────────────────────────

with open(f"{CONFIG_DIR}/token.json", "r", encoding="utf-8") as f:
    token_data = json.load(f)

with open(f"{CONFIG_DIR}/client_secret.json", "r", encoding="utf-8") as f:
    cs = json.load(f)["installed"]

def refresh_access_token():
    """Refresh the OAuth2 access token."""
    data = urllib.parse.urlencode({
        "client_id": cs["client_id"],
        "client_secret": cs["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    token_data["access_token"] = result["access_token"]
    # Save refreshed token
    with open(f"{CONFIG_DIR}/token.json", "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)
    print(f"[OK] Token refreshed: {result['access_token'][:20]}...")
    return result["access_token"]

ACCESS_TOKEN = refresh_access_token()

# ── 2. Helper: YouTube API calls ─────────────────────────────────────────────

def yt_api_get(url):
    """GET request to YouTube API."""
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  [ERROR] GET {e.code}: {body[:300]}")
        return None

def yt_api_put(url, body_dict):
    """PUT request to YouTube API."""
    data = json.dumps(body_dict).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {ACCESS_TOKEN}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"  [ERROR] PUT {e.code}: {body[:500]}")
        return None

# ── 3. Get channel's public videos ───────────────────────────────────────────

CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

def get_all_public_video_ids():
    """Get all public video IDs from the channel via search endpoint."""
    video_ids = []
    next_page = None
    while True:
        url = (f"https://www.googleapis.com/youtube/v3/search"
               f"?channelId={CHANNEL_ID}&type=video&maxResults=50&part=id"
               f"&order=viewCount")
        if next_page:
            url += f"&pageToken={next_page}"
        data = yt_api_get(url)
        if not data:
            break
        for item in data.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid:
                video_ids.append(vid)
        next_page = data.get("nextPageToken")
        if not next_page:
            break
        print(f"  Fetched {len(video_ids)} video IDs so far...")
    return video_ids

print("\n[STEP 1] Fetching all channel video IDs (sorted by views)...")
all_video_ids = get_all_public_video_ids()
print(f"  Found {len(all_video_ids)} videos total")

# ── 4. Fetch full details for all videos (batched by 50) ─────────────────────

def get_video_details_batch(vid_ids):
    """Get snippet + localizations + statistics for a batch of up to 50 IDs."""
    ids_str = ",".join(vid_ids)
    url = (f"https://www.googleapis.com/youtube/v3/videos"
           f"?part=snippet,localizations,statistics&id={ids_str}")
    return yt_api_get(url)

print("\n[STEP 2] Fetching video details in batches...")
all_videos = []
for i in range(0, len(all_video_ids), 50):
    batch = all_video_ids[i:i+50]
    result = get_video_details_batch(batch)
    if result and "items" in result:
        all_videos.extend(result["items"])
    time.sleep(0.3)
print(f"  Got details for {len(all_videos)} videos")

# ── 5. Sort by views (highest first) and identify issues ─────────────────────

for v in all_videos:
    v["_views"] = int(v.get("statistics", {}).get("viewCount", "0"))
all_videos.sort(key=lambda v: v["_views"], reverse=True)

REQUIRED_LANGS = {"de", "en", "ja", "fr", "es", "pt-BR", "hi", "ko"}

def detect_issues(video):
    """Detect issues with a video. Returns list of issue strings."""
    issues = []
    snippet = video.get("snippet", {})
    localizations = video.get("localizations", {})
    tags = snippet.get("tags", [])
    description = snippet.get("description", "")
    title = snippet.get("title", "")

    # Check localizations
    existing_langs = set(localizations.keys())
    missing = REQUIRED_LANGS - existing_langs
    if len(missing) > 0 and len(existing_langs) <= 1:
        issues.append(f"NO_LOCALIZATIONS (has {len(existing_langs)} lang, missing {len(missing)})")
    elif missing:
        issues.append(f"MISSING_LANGS: {', '.join(sorted(missing))}")

    # Check tags
    if len(tags) > 15:
        issues.append(f"TOO_MANY_TAGS ({len(tags)})")
    if len(tags) == 0:
        issues.append("ZERO_TAGS")

    # Check description
    if len(description) < 50:
        issues.append(f"SHORT_DESCRIPTION ({len(description)} chars)")

    return issues

print("\n[STEP 3] Scanning for issues...")
videos_with_issues = []
for v in all_videos:
    issues = detect_issues(v)
    if issues:
        v["_issues"] = issues
        videos_with_issues.append(v)

print(f"  Found {len(videos_with_issues)} videos with issues")
for v in videos_with_issues[:5]:
    print(f"    {v['snippet']['title'][:60]}... | views={v['_views']} | {v['_issues']}")

# ── 6. Series detection ──────────────────────────────────────────────────────

def detect_series(title):
    """Detect the series from the video title."""
    t = title.lower()
    if "wochenschau" in t:
        if "livestream" in t or "live" in t or "24/7" in t:
            return "wochenschau_live"
        return "wochenschau"
    if "betty boop" in t:
        return "betty_boop"
    if "alfred" in t and "kwak" in t:
        return "alfred_j_kwak"
    if "der 7. sinn" in t or "7th sense" in t or "7. sinn" in t:
        return "der_7_sinn"
    if "kleene punker" in t or "kleine punker" in t or "little punk" in t:
        return "der_kleene_punker"
    if "superman" in t:
        return "superman"
    if "popeye" in t:
        return "popeye"
    if "felix" in t and "cat" in t:
        return "felix_the_cat"
    if "casper" in t:
        return "casper"
    if "krtek" in t or "maulwurf" in t or "little mole" in t:
        return "krtek"
    if "looney" in t or "bugs bunny" in t or "daffy" in t:
        return "looney_tunes"
    if "soundie" in t:
        return "soundie"
    if "astro boy" in t or "tetsuwan" in t:
        return "astro_boy"
    if "bravestarr" in t:
        return "bravestarr"
    if "chaplin" in t:
        return "chaplin"
    if "keaton" in t:
        return "buster_keaton"
    if "nasa" in t or "skylab" in t or "apollo" in t:
        return "nasa"
    if "silly symph" in t:
        return "silly_symphony"
    if "film noir" in t or "noir" in t:
        return "film_noir"
    if "ken block" in t or "gymkhana" in t:
        return "ken_block"
    if "christmas" in t or "weihnacht" in t:
        return "christmas"
    if "teaserama" in t or "bettie page" in t or "burlesque" in t:
        return "teaserama"
    return "other"

def extract_event_from_title(title):
    """Extract event/topic part from title for localization."""
    # Try to extract the part after ": " and before " |" or " [" or " ("
    m = re.search(r':\s*(.+?)(?:\s*\||\s*\[|\s*\(8K|\s*8K|$)', title)
    if m:
        return m.group(1).strip()
    return title

def extract_year_from_title(title):
    """Extract year from title."""
    m = re.search(r'\((\d{4})\)', title)
    if m:
        return m.group(1)
    m = re.search(r'(\d{4})', title)
    if m:
        return m.group(1)
    return ""

# ── 7. Build localizations per series ─────────────────────────────────────────

def build_localizations(title, description, series, existing_locs):
    """Build 8-language localizations based on series type."""
    if series == "wochenschau_live":
        return None  # Skip livestream

    event = extract_event_from_title(title)
    year = extract_year_from_title(title)
    year_str = f" ({year})" if year else ""

    # Get existing DE description or use current description
    de_desc = description
    if "de" in existing_locs and existing_locs["de"].get("description"):
        de_desc = existing_locs["de"]["description"]

    # Get existing EN description
    en_desc = description
    if "en" in existing_locs and existing_locs["en"].get("description"):
        en_desc = existing_locs["en"]["description"]

    # For non-DE default languages, use the main description as EN
    locs = {}

    if series == "wochenschau":
        de_title = title  # Keep original DE title
        en_title = f"German WWII Newsreel: {event}{year_str} | 8K Restored"
        ja_title = f"ドイツ週間ニュース: {event} | 8K修復"
        fr_title = f"Actualités allemandes: {event}{year_str} | 8K"
        es_title = f"Noticiario alemán: {event}{year_str} | 8K"
        pt_title = f"Cinejornal alemão: {event}{year_str} | 8K"
        hi_title = f"जर्मन WWII न्यूज़रील: {event}{year_str} | 8K"
        ko_title = f"독일 전시뉴스: {event} | 8K 복원"

        locs = {
            "de": {"title": de_title, "description": de_desc},
            "en": {"title": en_title, "description": en_desc},
            "ja": {"title": ja_title, "description": en_desc},
            "fr": {"title": fr_title, "description": en_desc},
            "es": {"title": es_title, "description": en_desc},
            "pt-BR": {"title": pt_title, "description": en_desc},
            "hi": {"title": hi_title, "description": en_desc},
            "ko": {"title": ko_title, "description": en_desc},
        }
    elif series == "der_7_sinn":
        topic = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"The 7th Sense: {topic} | 8K Restored", "description": en_desc},
            "ja": {"title": f"第7の感覚: {topic} | 8K修復", "description": en_desc},
            "fr": {"title": f"Le 7e Sens: {topic} | 8K", "description": en_desc},
            "es": {"title": f"El 7° Sentido: {topic} | 8K", "description": en_desc},
            "pt-BR": {"title": f"O 7° Sentido: {topic} | 8K", "description": en_desc},
            "hi": {"title": f"7वीं इंद्रिय: {topic} | 8K", "description": en_desc},
            "ko": {"title": f"제7감: {topic} | 8K 복원", "description": en_desc},
        }
    elif series == "der_kleene_punker":
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": "The Little Punk | Full Movie | 8K Restored", "description": en_desc},
            "ja": {"title": "リトルパンク | 全編 | 8K修復", "description": en_desc},
            "fr": {"title": "Le Petit Punk | Film Complet | 8K", "description": en_desc},
            "es": {"title": "El Pequeño Punk | Película Completa | 8K", "description": en_desc},
            "pt-BR": {"title": "O Pequeno Punk | Filme Completo | 8K", "description": en_desc},
            "hi": {"title": "छोटा पंक | पूरी फिल्म | 8K", "description": en_desc},
            "ko": {"title": "꼬마 펑크 | 전체 영화 | 8K 복원", "description": en_desc},
        }
    elif series == "betty_boop":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Betty Boop: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"ベティ・ブープ: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Betty Boop: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Betty Boop: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Betty Boop: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"बेट्टी बूप: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"베티 붑: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "alfred_j_kwak":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Alfred J. Kwak: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"アルフレッド・J・クワック: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Alfred J. Kwak: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Alfred J. Kwak: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Alfred J. Kwak: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"अल्फ्रेड जे. क्वैक: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"알프레드 J. 콱: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "superman":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Superman: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"スーパーマン: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Superman: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Superman: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Superman: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"सुपरमैन: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"슈퍼맨: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "popeye":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Popeye: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"ポパイ: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Popeye: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Popeye: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Popeye: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"पोपाय: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"뽀빠이: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "casper":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Casper the Friendly Ghost: {ep}{year_str} | 8K", "description": en_desc},
            "ja": {"title": f"おばけのキャスパー: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Casper le Fantôme: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Gasparín: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Gasparzinho: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"कैस्पर: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"꼬마유령 캐스퍼: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "krtek":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"The Little Mole (Krtek): {ep}{year_str} | 8K", "description": en_desc},
            "ja": {"title": f"もぐらのクルテク: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"La Petite Taupe: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"El Pequeño Topo: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"A Toupeira: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"छोटा छछूंदर: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"두더지 크르텍: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "looney_tunes":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Looney Tunes: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"ルーニー・テューンズ: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Looney Tunes: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Looney Tunes: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Looney Tunes: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"लूनी ट्यून्स: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"루니 툰: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "soundie":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Soundie: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"サウンディー: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Soundie: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Soundie: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Soundie: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"साउंडी: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"사운디: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "astro_boy":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Astro Boy: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"鉄腕アトム: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Astro Boy: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Astro Boy: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Astro Boy: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"एस्ट्रो बॉय: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"우주소년 아톰: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "bravestarr":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"BraveStarr: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"ブレイブスター: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"BraveStarr: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"BraveStarr: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"BraveStarr: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"ब्रेवस्टार: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"브레이브스타: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "chaplin":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Charlie Chaplin: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"チャーリー・チャップリン: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Charlie Chaplin: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Charlie Chaplin: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Charlie Chaplin: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"चार्ली चैप्लिन: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"찰리 채플린: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "buster_keaton":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Buster Keaton: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"バスター・キートン: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Buster Keaton: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Buster Keaton: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Buster Keaton: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"बस्टर कीटन: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"버스터 키튼: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "nasa":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"{ep}{year_str} | NASA | 8K HQ", "description": en_desc},
            "ja": {"title": f"{ep} | NASA | 8K修復", "description": en_desc},
            "fr": {"title": f"{ep}{year_str} | NASA | 8K", "description": en_desc},
            "es": {"title": f"{ep}{year_str} | NASA | 8K", "description": en_desc},
            "pt-BR": {"title": f"{ep}{year_str} | NASA | 8K", "description": en_desc},
            "hi": {"title": f"{ep} | NASA | 8K", "description": en_desc},
            "ko": {"title": f"{ep} | NASA | 8K 복원", "description": en_desc},
        }
    elif series == "felix_the_cat":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Felix the Cat: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"フィリックス・ザ・キャット: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Félix le Chat: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"El Gato Félix: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Gato Félix: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"फ़ेलिक्स बिल्ली: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"고양이 펠릭스: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "silly_symphony":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Silly Symphony: {ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"シリー・シンフォニー: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Silly Symphony: {ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"Silly Symphony: {ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Silly Symphony: {ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"सिली सिम्फनी: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"실리 심포니: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "ken_block":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"Ken Block: {ep} | 8K Restored", "description": en_desc},
            "ja": {"title": f"ケン・ブロック: {ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"Ken Block: {ep} | 8K", "description": en_desc},
            "es": {"title": f"Ken Block: {ep} | 8K", "description": en_desc},
            "pt-BR": {"title": f"Ken Block: {ep} | 8K", "description": en_desc},
            "hi": {"title": f"केन ब्लॉक: {ep} | 8K", "description": en_desc},
            "ko": {"title": f"켄 블록: {ep} | 8K 복원", "description": en_desc},
        }
    elif series == "christmas":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"{ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"{ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"{ep} | 8K", "description": en_desc},
            "ko": {"title": f"{ep} | 8K 복원", "description": en_desc},
        }
    elif series == "film_noir":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"{ep}{year_str} | Film Noir | 8K Restored", "description": en_desc},
            "ja": {"title": f"{ep} | フィルム・ノワール | 8K修復", "description": en_desc},
            "fr": {"title": f"{ep}{year_str} | Film Noir | 8K", "description": en_desc},
            "es": {"title": f"{ep}{year_str} | Cine Negro | 8K", "description": en_desc},
            "pt-BR": {"title": f"{ep}{year_str} | Cinema Noir | 8K", "description": en_desc},
            "hi": {"title": f"{ep} | फिल्म नोयर | 8K", "description": en_desc},
            "ko": {"title": f"{ep} | 필름 누아르 | 8K 복원", "description": en_desc},
        }
    elif series == "teaserama":
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": f"{ep}{year_str} | 8K Restored", "description": en_desc},
            "ja": {"title": f"{ep} | 8K修復", "description": en_desc},
            "fr": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "es": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "pt-BR": {"title": f"{ep}{year_str} | 8K", "description": en_desc},
            "hi": {"title": f"{ep} | 8K", "description": en_desc},
            "ko": {"title": f"{ep} | 8K 복원", "description": en_desc},
        }
    else:
        # Generic "other" series
        ep = extract_event_from_title(title)
        locs = {
            "de": {"title": title, "description": de_desc},
            "en": {"title": title, "description": en_desc},
            "ja": {"title": f"{ep} | 8K修復", "description": en_desc},
            "fr": {"title": title, "description": en_desc},
            "es": {"title": title, "description": en_desc},
            "pt-BR": {"title": title, "description": en_desc},
            "hi": {"title": f"{ep} | 8K", "description": en_desc},
            "ko": {"title": f"{ep} | 8K 복원", "description": en_desc},
        }

    # Merge with existing localizations (keep existing descriptions if they exist)
    for lang, loc_data in locs.items():
        if lang in existing_locs and existing_locs[lang].get("description"):
            loc_data["description"] = existing_locs[lang]["description"]

    return locs

# ── 8. Tag templates per series ───────────────────────────────────────────────

SERIES_TAG_TEMPLATES = {
    "wochenschau": ["wochenschau", "german newsreel", "wwii history", "archive footage",
                    "historical film", "zeitgeschichte", "world history", "8K",
                    "documentary", "kino wochenschau", "third reich", "public domain"],
    "betty_boop": ["Betty Boop", "classic cartoon", "1930s animation", "Fleischer Studios",
                   "vintage cartoon", "8K restored", "public domain", "retro animation",
                   "golden age cartoon", "Max Fleischer", "cartoon classic", "animated short"],
    "alfred_j_kwak": ["Alfred J Kwak", "cartoon", "anime", "8K restored", "classic animation",
                      "Herman van Veen", "children cartoon", "80s cartoon", "retro anime",
                      "Alfred Jodocus Kwak", "Japanese anime", "Dutch cartoon",
                      "classic TV show", "nostalgia", "remastered"],
    "superman": ["Superman", "classic cartoon", "Fleischer Studios", "1940s animation",
                 "8K restored", "superhero", "DC Comics", "public domain",
                 "vintage animation", "golden age", "Max Fleischer"],
    "popeye": ["Popeye", "classic cartoon", "Fleischer Studios", "8K restored",
               "vintage animation", "public domain", "golden age cartoon",
               "Popeye the Sailor", "retro cartoon", "animated short", "1940s"],
    "casper": ["Casper", "Casper the Friendly Ghost", "classic cartoon", "8K restored",
               "vintage animation", "public domain", "Famous Studios",
               "ghost cartoon", "retro cartoon", "animated short"],
    "krtek": ["Krtek", "der kleine Maulwurf", "the little mole", "8K restored",
              "classic cartoon", "Czech animation", "Zdenek Miler",
              "children cartoon", "retro cartoon", "European animation"],
    "looney_tunes": ["Looney Tunes", "classic cartoon", "Warner Bros", "8K restored",
                     "golden age animation", "Bugs Bunny", "vintage cartoon",
                     "public domain", "Merrie Melodies", "retro animation", "animated short"],
    "soundie": ["Soundie", "music video", "1940s music", "vintage jazz",
                "8K restored", "public domain", "swing music", "retro music",
                "jazz age", "big band", "musical short", "panoram", "jukebox",
                "vintage music video"],
    "astro_boy": ["Astro Boy", "鉄腕アトム", "classic anime", "8K restored",
                  "Osamu Tezuka", "retro anime", "vintage anime", "Japanese animation"],
    "bravestarr": ["BraveStarr", "80s cartoon", "classic cartoon", "8K restored",
                   "Filmation", "retro cartoon", "western cartoon", "space western"],
    "chaplin": ["Charlie Chaplin", "silent film", "classic comedy", "8K restored",
                "vintage cinema", "slapstick", "public domain", "golden age"],
    "buster_keaton": ["Buster Keaton", "silent film", "classic comedy", "8K restored",
                      "vintage cinema", "slapstick", "public domain", "golden age"],
    "nasa": ["NASA", "space", "documentary", "8K restored", "public domain",
             "space exploration", "space history", "science", "astronomy"],
    "felix_the_cat": ["Felix the Cat", "classic cartoon", "silent animation", "8K restored",
                      "1920s cartoon", "vintage animation", "public domain",
                      "golden age", "retro cartoon", "animated short"],
    "silly_symphony": ["Silly Symphony", "Disney", "classic animation", "8K restored",
                       "golden age", "vintage Disney", "animated short", "public domain"],
    "ken_block": ["Ken Block", "Gymkhana", "drift", "rally", "8K restored",
                  "motorsport", "racing", "automotive", "car video"],
    "film_noir": ["film noir", "classic cinema", "8K restored", "vintage movie",
                  "black and white", "public domain", "golden age Hollywood", "thriller"],
    "christmas": ["Christmas", "holiday", "classic cartoon", "8K restored",
                  "vintage animation", "public domain", "holiday special",
                  "Christmas cartoon", "festive"],
    "teaserama": ["Bettie Page", "burlesque", "vintage", "8K restored",
                  "1950s", "pin-up", "classic film", "retro"],
    "der_7_sinn": ["Der 7. Sinn", "The 7th Sense", "traffic safety", "8K restored",
                   "German TV", "classic TV", "road safety", "vintage TV",
                   "driving safety", "ARD", "educational"],
    "der_kleene_punker": ["Der kleene Punker", "German film", "punk", "8K restored",
                          "1980s film", "comedy", "Berlin", "cult film",
                          "German cinema", "retro film"],
    "other": ["8K restored", "classic", "vintage", "public domain", "remastered",
              "retro", "golden age", "classic cinema", "high quality", "restored"],
}

def fix_tags(current_tags, series, title):
    """Fix tags: trim to 15 if too many, add 10-15 if zero."""
    if len(current_tags) > 15:
        # Keep first 15 tags (they tend to be the most relevant)
        return current_tags[:15]
    if len(current_tags) == 0:
        # Add tags from template
        template = SERIES_TAG_TEMPLATES.get(series, SERIES_TAG_TEMPLATES["other"])
        tags = list(template)
        # Add episode-specific tag
        ep = extract_event_from_title(title)
        if ep and ep not in tags:
            tags.append(ep)
        return tags[:15]
    return None  # No change needed

# ── 9. Process each video ────────────────────────────────────────────────────

# Videos already updated in first run (before crash)
ALREADY_DONE = set()
try:
    with open(f"{CONFIG_DIR}/fix_31_videos_2026_03_31.json", "r", encoding="utf-8") as f:
        prev_report = json.load(f)
        for fix in prev_report.get("fixes_applied", []):
            ALREADY_DONE.add(fix["id"])
        print(f"  Found {len(ALREADY_DONE)} previously updated videos, will skip them.")
except (FileNotFoundError, json.JSONDecodeError):
    pass

report = {
    "timestamp": datetime.now().isoformat(),
    "total_scanned": len(all_videos),
    "total_with_issues": len(videos_with_issues),
    "fixes_applied": [],
    "errors": [],
    "quota_used": 0,
    "skipped": []
}

# Carry forward previous fixes
if ALREADY_DONE:
    for fix in prev_report.get("fixes_applied", []):
        report["fixes_applied"].append(fix)
    report["quota_used"] = prev_report.get("quota_used", 0)

print(f"\n[STEP 4] Processing {len(videos_with_issues)} videos with issues...")
print("=" * 80)

updates_done = 0
MAX_UPDATES = 172  # Process all videos with issues (within quota budget of ~180)

for idx, video in enumerate(videos_with_issues):
    if updates_done >= MAX_UPDATES:
        print(f"\n[LIMIT] Reached {MAX_UPDATES} updates, stopping.")
        break

    vid_id = video["id"]
    snippet = video["snippet"]
    title = snippet["title"]
    description = snippet.get("description", "")
    tags = snippet.get("tags", [])
    category_id = snippet.get("categoryId", "22")
    existing_locs = video.get("localizations", {})
    issues = video["_issues"]
    views = video["_views"]
    series = detect_series(title)

    print(f"\n[{idx+1}/{len(videos_with_issues)}] {title[:65]}")
    print(f"  Series: {series} | Views: {views} | Issues: {issues}")

    if vid_id in ALREADY_DONE:
        print("  SKIP: Already updated in previous run")
        continue

    if series == "wochenschau_live":
        print("  SKIP: Livestream")
        report["skipped"].append({"id": vid_id, "title": title, "reason": "livestream"})
        continue

    # Determine what needs fixing
    needs_locs = any("LOCALIZ" in i or "MISSING_LANG" in i for i in issues)
    needs_tag_fix = any("TAGS" in i for i in issues)
    needs_desc_fix = any("DESCRIPTION" in i for i in issues)

    # Build the update body
    update_body = {
        "id": vid_id,
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": category_id,
            "tags": tags,
            "defaultLanguage": snippet.get("defaultLanguage", "de"),
            "defaultAudioLanguage": snippet.get("defaultAudioLanguage", "de"),
        }
    }

    parts = ["snippet"]
    changes = []

    # Fix localizations
    if needs_locs:
        new_locs = build_localizations(title, description, series, existing_locs)
        if new_locs:
            update_body["localizations"] = new_locs
            parts.append("localizations")
            changes.append(f"added {len(new_locs)} localizations")

    # Fix tags
    if needs_tag_fix:
        fixed_tags = fix_tags(tags, series, title)
        if fixed_tags is not None:
            update_body["snippet"]["tags"] = fixed_tags
            changes.append(f"tags: {len(tags)} -> {len(fixed_tags)}")
    elif len(tags) == 0:
        fixed_tags = fix_tags(tags, series, title)
        if fixed_tags is not None:
            update_body["snippet"]["tags"] = fixed_tags
            changes.append(f"tags: 0 -> {len(fixed_tags)}")

    # Fix short description
    if needs_desc_fix:
        # Build a proper description
        ep = extract_event_from_title(title)
        template_tags = SERIES_TAG_TEMPLATES.get(series, SERIES_TAG_TEMPLATES["other"])
        hashtags = " ".join([f"#{t.replace(' ', '')}" for t in template_tags[:5]])
        new_desc = (f"{title}\n\n"
                    f"Enjoy this classic in stunning 8K quality, carefully restored from the original source material.\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👆 LIKE if you enjoyed this!\n"
                    f"💬 COMMENT your thoughts below!\n"
                    f"🔔 SUBSCRIBE for more restored classics in 8K!\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🌐 www.remaike.IT\n"
                    f"📺 https://www.youtube.com/@remAIke_IT\n\n"
                    f"{hashtags}")
        update_body["snippet"]["description"] = new_desc
        changes.append(f"description: {len(description)} -> {len(new_desc)} chars")
        # Update localizations with new description too
        if "localizations" in update_body:
            for lang in update_body["localizations"]:
                if lang == "de":
                    update_body["localizations"][lang]["description"] = new_desc
                else:
                    update_body["localizations"][lang]["description"] = new_desc

    if not changes:
        print("  SKIP: No actionable changes")
        report["skipped"].append({"id": vid_id, "title": title, "reason": "no changes needed"})
        continue

    print(f"  Changes: {', '.join(changes)}")

    # PUT update
    url = f"https://www.googleapis.com/youtube/v3/videos?part={','.join(parts)}"
    result = yt_api_put(url, update_body)

    if result:
        updates_done += 1
        report["quota_used"] += 50
        report["fixes_applied"].append({
            "id": vid_id,
            "title": title,
            "series": series,
            "views": views,
            "changes": changes,
            "status": "success"
        })
        print(f"  [OK] Updated successfully (quota: {report['quota_used']})")
    else:
        report["errors"].append({
            "id": vid_id,
            "title": title,
            "series": series,
            "changes": changes,
            "status": "error"
        })
        print(f"  [FAIL] Update failed")

    # Rate limiting
    time.sleep(0.5)

# ── 10. Save report ──────────────────────────────────────────────────────────

report["total_updated"] = updates_done
report["total_errors"] = len(report["errors"])
report["total_skipped"] = len(report["skipped"])

report_path = f"{CONFIG_DIR}/fix_31_videos_2026_03_31.json"
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n{'=' * 80}")
print(f"[DONE] Report saved to {report_path}")
print(f"  Updated: {updates_done}")
print(f"  Errors:  {len(report['errors'])}")
print(f"  Skipped: {len(report['skipped'])}")
print(f"  Quota:   {report['quota_used']} units")
