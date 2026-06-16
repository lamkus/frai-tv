"""
Channel Manager DB Enhancement + Full Sync
============================================
Adds research tables, IST/SOLL tracking, and syncs all ~373 videos.

New tables:
- series_research:  Series master data (CZ Wikipedia verified)
- video_research:   Per-video episode data (ep#, year, sources)
- video_targets:    SOLL state per video (planned title/desc/tags)
- video_i18n:       Internationalization status per video per language

Then: Full YouTube sync + populate research from existing config JSONs.
"""

import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'channel_manager', 'channel_manager.db')
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
CLIENT_SECRET = os.path.join(CONFIG_DIR, 'client_secret.json')
API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

# ═══════════════════════════════════════════════════════════════
# STEP 1: Schema Migration — Add new tables
# ═══════════════════════════════════════════════════════════════

MIGRATION_SQL = """
-- Series research master data
CREATE TABLE IF NOT EXISTS series_research (
    series_key TEXT PRIMARY KEY,
    name_de TEXT,
    name_en TEXT,
    name_original TEXT,
    creator TEXT,
    country TEXT,
    year_start INTEGER,
    year_end INTEGER,
    total_episodes INTEGER,
    episode_numbering_source TEXT,     -- 'CZ Wikipedia', 'Production order', etc.
    wikipedia_de TEXT,
    wikipedia_en TEXT,
    wikipedia_original TEXT,
    imdb_url TEXT,
    notes TEXT,
    verified_date TEXT
);

-- Per-video research data
CREATE TABLE IF NOT EXISTS video_research (
    video_id TEXT PRIMARY KEY,
    series_key TEXT,
    episode_num INTEGER,
    episode_num_alt INTEGER,           -- alternative numbering (EN Wikipedia vs CZ, etc.)
    numbering_note TEXT,               -- e.g. "CZ#17 = EN Short#14"
    production_year INTEGER,
    original_title TEXT,               -- original language title (Czech, etc.)
    duration_verified TEXT,
    composer TEXT,
    director TEXT,
    copyright_status TEXT,             -- 'public_domain', 'copyrighted', 'fair_use'
    copyright_holder TEXT,
    research_source TEXT,              -- URL or reference
    verified INTEGER DEFAULT 0,
    verified_date TEXT,
    notes TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(id),
    FOREIGN KEY (series_key) REFERENCES series_research(series_key)
);

-- IST/SOLL tracking (target state per video)
CREATE TABLE IF NOT EXISTS video_targets (
    video_id TEXT PRIMARY KEY,
    target_title TEXT,
    target_description TEXT,
    target_tags TEXT,                   -- JSON array
    target_category_id INTEGER,
    target_default_language TEXT,
    target_localizations TEXT,          -- JSON: {lang: {title, description}}
    status TEXT DEFAULT 'unknown',      -- 'matched', 'diverged', 'planned', 'unknown'
    last_compared TEXT,
    divergence_details TEXT,            -- JSON: which fields differ
    created_at TEXT,
    pushed_at TEXT,
    verified_at TEXT,
    notes TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

-- I18n tracking per video per language
CREATE TABLE IF NOT EXISTS video_i18n (
    video_id TEXT NOT NULL,
    language TEXT NOT NULL,
    title TEXT,
    description_length INTEGER,
    status TEXT DEFAULT 'missing',      -- 'missing', 'planned', 'pushed', 'verified'
    pushed_at TEXT,
    PRIMARY KEY (video_id, language),
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

-- Research rules and conventions per series
CREATE TABLE IF NOT EXISTS research_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    series_key TEXT,                     -- NULL = global rule
    rule_type TEXT NOT NULL,             -- 'title_format', 'category', 'tag_limit', 'naming', etc.
    rule_value TEXT NOT NULL,            -- the actual rule
    priority INTEGER DEFAULT 0,
    source TEXT,                         -- where the rule comes from
    FOREIGN KEY (series_key) REFERENCES series_research(series_key)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_research_series ON video_research(series_key);
CREATE INDEX IF NOT EXISTS idx_targets_status ON video_targets(status);
CREATE INDEX IF NOT EXISTS idx_i18n_status ON video_i18n(status);
CREATE INDEX IF NOT EXISTS idx_i18n_video ON video_i18n(video_id);
CREATE INDEX IF NOT EXISTS idx_rules_series ON research_rules(series_key);
"""


def migrate_schema(conn):
    """Add new tables to the Channel Manager DB."""
    print("📐 Running schema migration...")
    conn.executescript(MIGRATION_SQL)
    conn.commit()
    
    # Verify
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    new_tables = ['series_research', 'video_research', 'video_targets', 'video_i18n', 'research_rules']
    for t in new_tables:
        status = "✅" if t in tables else "❌"
        print(f"  {status} {t}")
    print(f"  Total tables: {len(tables)}")
    return True


# ═══════════════════════════════════════════════════════════════
# STEP 2: Full YouTube Sync (Public API for READ)
# ═══════════════════════════════════════════════════════════════

def get_youtube_public():
    """Get YouTube API client using API key (read-only, separate quota)."""
    import requests
    return None  # We'll use requests directly

def get_youtube_oauth():
    """Get authenticated YouTube client."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)


def fetch_all_videos_public():
    """Fetch all channel videos using public API (API key = separate quota)."""
    import requests
    
    CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
    UPLOADS_PL = "UUVFv6Egpl0LDvigpFbQXNeQ"
    
    if not API_KEY:
        print("  ⚠️  No YOUTUBE_API_KEY set, falling back to OAuth for read")
        return fetch_all_videos_oauth()
    
    print(f"  Using Public API (separate quota)")
    
    # Step 1: Get all video IDs from uploads playlist
    video_ids = []
    next_page = None
    while True:
        params = {
            'part': 'contentDetails',
            'playlistId': UPLOADS_PL,
            'maxResults': 50,
            'key': API_KEY
        }
        if next_page:
            params['pageToken'] = next_page
        
        resp = requests.get('https://youtube.googleapis.com/youtube/v3/playlistItems', params=params)
        data = resp.json()
        
        if 'error' in data:
            print(f"  ❌ API Error: {data['error']['message']}")
            return fetch_all_videos_oauth()
        
        for item in data.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page = data.get('nextPageToken')
        if not next_page:
            break
    
    print(f"  Found {len(video_ids)} video IDs")
    
    # Step 2: Fetch full details in batches of 50
    all_videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        params = {
            'part': 'snippet,contentDetails,statistics,status,localizations',
            'id': ','.join(batch),
            'key': API_KEY
        }
        resp = requests.get('https://youtube.googleapis.com/youtube/v3/videos', params=params)
        data = resp.json()
        
        if 'error' in data:
            print(f"  ❌ Batch error: {data['error']['message']}")
            continue
        
        all_videos.extend(data.get('items', []))
        print(f"  Fetched {len(all_videos)}/{len(video_ids)} videos...")
    
    return all_videos


def fetch_all_videos_oauth():
    """Fallback: Fetch using OAuth."""
    youtube = get_youtube_oauth()
    
    UPLOADS_PL = "UUVFv6Egpl0LDvigpFbQXNeQ"
    
    video_ids = []
    next_page = None
    while True:
        resp = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=UPLOADS_PL,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in resp.get('items', []):
            video_ids.append(item['contentDetails']['videoId'])
        
        next_page = resp.get('nextPageToken')
        if not next_page:
            break
    
    print(f"  Found {len(video_ids)} video IDs (OAuth)")
    
    all_videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part='snippet,contentDetails,statistics,status,localizations',
            id=','.join(batch)
        ).execute()
        all_videos.extend(resp.get('items', []))
        print(f"  Fetched {len(all_videos)}/{len(video_ids)} videos...")
    
    return all_videos


def detect_series(title, tags):
    """Detect which series a video belongs to."""
    title_lower = title.lower()
    tags_lower = [t.lower() for t in (tags or [])]
    all_text = title_lower + ' ' + ' '.join(tags_lower)
    
    SERIES_MAP = {
        'alfred_kwak': ['alfred', 'kwak', 'quack'],
        'betty_boop': ['betty boop', 'bettyboop'],
        'superman': ['superman', 'fleischer'],
        'popeye': ['popeye'],
        'felix': ['felix the cat', 'felix'],
        'maulwurf': ['maulwurf', 'krtek', 'krteček', 'little mole'],
        'looney_tunes': ['looney tunes', 'merrie melodies', 'porky pig', 'bugs bunny', 'daffy duck'],
        'casper': ['casper', 'friendly ghost'],
        'soundies': ['soundie'],
        'wochenschau': ['wochenschau', 'newsreel'],
        'bravestarr': ['bravestarr', 'brave starr'],
        'christmas': ['christmas', 'weihnacht', 'xmas'],
        'ken_block': ['ken block', 'gymkhana'],
        'nasa': ['nasa', 'skylab', 'apollo'],
        'clever_smart': ['clever', 'smart', 'mortadelo'],
        'mausemusketiere': ['mäuse-musketiere', 'mausemusketiere', 'three musketeers'],
        'kleene_punker': ['kleene punker'],
        'gluecksbaerchi': ['glücksbärchi', 'care bear'],
    }
    
    for key, keywords in SERIES_MAP.items():
        for kw in keywords:
            if kw in all_text:
                return key
    return 'other'


def sync_videos_to_db(conn, videos):
    """Upsert all videos into the database."""
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    synced = 0
    for v in videos:
        vid_id = v['id']
        snippet = v.get('snippet', {})
        stats = v.get('statistics', {})
        status = v.get('status', {})
        content = v.get('contentDetails', {})
        locs = v.get('localizations', {})
        
        title = snippet.get('title', '')
        desc = snippet.get('description', '')
        tags = json.dumps(snippet.get('tags', []), ensure_ascii=False)
        cat_id = int(snippet.get('categoryId', 0))
        published = snippet.get('publishedAt', '')
        privacy = status.get('privacyStatus', 'unknown')
        thumb = snippet.get('thumbnails', {}).get('maxres', snippet.get('thumbnails', {}).get('high', {})).get('url', '')
        lang = snippet.get('defaultLanguage', snippet.get('defaultAudioLanguage', ''))
        duration = content.get('duration', '')
        
        views = int(stats.get('viewCount', 0)) if stats.get('viewCount') else None
        likes = int(stats.get('likeCount', 0)) if stats.get('likeCount') else None
        comments = int(stats.get('commentCount', 0)) if stats.get('commentCount') else None
        
        series = detect_series(title, snippet.get('tags', []))
        
        # Simple SEO scoring
        seo_score, seo_issues = score_video_simple(title, desc, tags, cat_id, thumb, lang, locs, series)
        
        has_thumb = 1 if thumb and 'maxres' in str(thumb) else 0
        is_short = 1 if '#shorts' in desc.lower() or '#shorts' in title.lower() else None
        
        locs_json = json.dumps(locs, ensure_ascii=False) if locs else '{}'
        
        cur.execute("""
            INSERT OR REPLACE INTO videos 
            (id, title, description, tags, category_id, published_at, duration, 
             view_count, like_count, comment_count, privacy_status, thumbnail_url,
             series, is_short, seo_score, seo_issues, has_custom_thumbnail,
             default_language, localizations, last_synced, custom_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                    COALESCE((SELECT custom_data FROM videos WHERE id=?), '{}'))
        """, (vid_id, title, desc, tags, cat_id, published, duration,
              views, likes, comments, privacy, thumb,
              series, is_short, seo_score, json.dumps(seo_issues), has_thumb,
              lang, locs_json, now, vid_id))
        
        synced += 1
    
    conn.commit()
    return synced


def score_video_simple(title, desc, tags_json, cat_id, thumb, lang, locs, series):
    """Simple SEO scoring (inline to avoid import issues)."""
    score = 0
    issues = []
    
    # Title (40 pts)
    if title:
        score += 10  # has title
        if '8K' in title or '4K' in title:
            score += 10
        if '|' in title:
            score += 5
        if '@' not in title:
            score += 5
        if len(title) <= 70:
            score += 5
        else:
            issues.append({"field": "title", "severity": "warning", "msg": f"Title too long ({len(title)} chars)"})
        if any(c in title for c in '()'):
            score += 5  # has year
    else:
        issues.append({"field": "title", "severity": "error", "msg": "Missing title"})
    
    # Description (30 pts)
    if desc:
        score += 5
        if 'remaike' in desc.lower() or 'remaike.it' in desc.lower():
            score += 5
        if '@remAIke_IT' in desc or 'youtube.com/@remAIke_IT' in desc:
            score += 5
        if any(cta in desc.upper() for cta in ['LIKE', 'SUBSCRIBE', 'COMMENT']):
            score += 5
        if '#' in desc:
            score += 5
        desc_len = len(desc)
        if desc_len > 200:
            score += 5
        else:
            issues.append({"field": "description", "severity": "info", "msg": f"Short description ({desc_len} chars)"})
    else:
        issues.append({"field": "description", "severity": "error", "msg": "Missing description"})
    
    # Tags (10 pts)
    try:
        tag_list = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
    except:
        tag_list = []
    if tag_list:
        score += 5
        if len(tag_list) <= 15:
            score += 5
        else:
            issues.append({"field": "tags", "severity": "warning", "msg": f"Too many tags ({len(tag_list)})"})
    
    # Thumbnail (10 pts)
    if thumb:
        score += 10
    
    # Localizations (10 pts)
    if locs and len(locs) > 0:
        loc_count = len(locs) if isinstance(locs, dict) else 0
        if loc_count >= 5:
            score += 10
        elif loc_count >= 2:
            score += 5
    
    return min(score, 100), issues


# ═══════════════════════════════════════════════════════════════
# STEP 3: Populate research data from existing JSONs
# ═══════════════════════════════════════════════════════════════

def populate_series_research(conn):
    """Insert series master data from verified Wikipedia research."""
    cur = conn.cursor()
    
    series_data = [
        ("maulwurf", "Der kleine Maulwurf", "The Little Mole", "Krteček / O krtkovi",
         "Zdeněk Miler", "Tschechoslowakei / Tschechien", 1957, 2002, 49,
         "CZ Wikipedia (49 episodes: 43 shorts + 6 features)",
         "https://de.wikipedia.org/wiki/Der_kleine_Maulwurf",
         "https://en.wikipedia.org/wiki/The_Little_Mole",
         "https://cs.wikipedia.org/wiki/Seznam_d%C3%ADl%C5%AF_seri%C3%A1lu_O_krtkovi",
         "https://www.imdb.com/title/tt0841927/",
         "Numbering follows CZ Wikipedia episode list",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("alfred_kwak", "Alfred J. Kwak", "Alfred J. Kwak", "Alfred Jodocus Kwak",
         "Herman van Veen / Harald Siepermann", "Niederlande / Japan / Deutschland", 1989, 1991, 52,
         "Production order (DE broadcast)",
         "https://de.wikipedia.org/wiki/Alfred_J._Kwak",
         "https://en.wikipedia.org/wiki/Alfred_J._Kwak",
         None, None,
         "Dutch-Japanese co-production, broadcast in 80+ countries",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("betty_boop", "Betty Boop", "Betty Boop", "Betty Boop",
         "Max Fleischer / Grim Natwick", "USA", 1930, 1939, 96,
         "Production chronological",
         "https://de.wikipedia.org/wiki/Betty_Boop",
         "https://en.wikipedia.org/wiki/Betty_Boop",
         None, "https://www.imdb.com/title/tt0208701/",
         "Public domain (pre-1964 US copyright). 96 theatrical shorts.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("superman", "Superman (Fleischer)", "Superman (Fleischer Studios)", "Superman",
         "Max Fleischer / Dave Fleischer", "USA", 1941, 1943, 17,
         "Production chronological",
         "https://de.wikipedia.org/wiki/Superman_(Zeichentrickfilm)",
         "https://en.wikipedia.org/wiki/Superman_(1940s_cartoons)",
         None, None,
         "17 theatrical shorts. Public domain.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("felix", "Felix the Cat", "Felix the Cat", "Felix the Cat",
         "Pat Sullivan / Otto Messmer", "USA", 1919, 1930, None,
         "Production chronological",
         "https://de.wikipedia.org/wiki/Felix_the_Cat",
         "https://en.wikipedia.org/wiki/Felix_the_Cat",
         None, None,
         "Silent era + early sound cartoons. Public domain (pre-1929).",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("soundies", "Soundies", "Soundies", "Soundies",
         "Various", "USA", 1940, 1947, None,
         "Not a series — individual music films for jukeboxes",
         None,
         "https://en.wikipedia.org/wiki/Soundies",
         None, None,
         "Short music films (3 min) for visual jukeboxes (Panoram). Public domain.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("wochenschau", "Wochenschau", "German Weekly Newsreel", "Deutsche Wochenschau",
         "Various / UFA / Nazi Propaganda Ministry", "Deutschland", 1940, 1945, None,
         "Production number",
         "https://de.wikipedia.org/wiki/Deutsche_Wochenschau",
         "https://en.wikipedia.org/wiki/Die_Deutsche_Wochenschau",
         None, None,
         "⚠️ NS-Propaganda! Requires in-video disclaimer. Category 27 (Education).",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("popeye", "Popeye der Seemann", "Popeye the Sailor", "Popeye the Sailor",
         "Max Fleischer / Dave Fleischer", "USA", 1933, 1957, None,
         "Production chronological",
         "https://de.wikipedia.org/wiki/Popeye",
         "https://en.wikipedia.org/wiki/Popeye_the_Sailor_(film_series)",
         None, None,
         "Public domain (pre-1964). Fleischer Studios / Famous Studios.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("casper", "Casper", "Casper the Friendly Ghost", "Casper the Friendly Ghost",
         "Famous Studios", "USA", 1945, 1963, None,
         "Production chronological",
         "https://de.wikipedia.org/wiki/Casper_(Zeichentrickfigur)",
         "https://en.wikipedia.org/wiki/Casper_the_Friendly_Ghost",
         None, None,
         "Public domain (pre-1964). Famous Studios / Harvey Comics.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("bravestarr", "BraveStarr", "BraveStarr", "BraveStarr",
         "Filmation / Lou Scheimer", "USA", 1987, 1988, 65,
         "Production number (⚠️ ≠ broadcast order!)",
         "https://de.wikipedia.org/wiki/Bravestarr",
         "https://en.wikipedia.org/wiki/BraveStarr",
         None, None,
         "⚠️ Prod-Nr ≠ Ausstrahlung! Dateinamen = Prod-Nr. All 4 currently PRIVATE.",
         datetime.now().strftime("%Y-%m-%d")),
         
        ("clever_smart", "Clever & Smart", "Clever & Smart / Mortadelo y Filemón", "Mortadelo y Filemón",
         "Francisco Ibáñez (Comic) / Javier Fesser (Film)", "Spanien", 2014, 2014, None,
         "N/A — film, not series",
         "https://de.wikipedia.org/wiki/Clever_%26_Smart",
         "https://en.wikipedia.org/wiki/Mortadelo_y_Filem%C3%B3n",
         None, None,
         "Copyrighted (Warner Bros). Based on Ibáñez comic since 1958.",
         datetime.now().strftime("%Y-%m-%d")),
        
        ("nasa", "NASA Dokumentationen", "NASA Documentaries", "NASA Films",
         "NASA / JSC / MSFC", "USA", 1960, 2000, None,
         "N/A — individual documentaries",
         None,
         "https://en.wikipedia.org/wiki/NASA",
         None, None,
         "Public domain (US Government works). Category 27 (Education).",
         datetime.now().strftime("%Y-%m-%d")),
    ]
    
    count = 0
    for s in series_data:
        cur.execute("""
            INSERT OR REPLACE INTO series_research 
            (series_key, name_de, name_en, name_original, creator, country,
             year_start, year_end, total_episodes, episode_numbering_source,
             wikipedia_de, wikipedia_en, wikipedia_original, imdb_url, notes, verified_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, s)
        count += 1
    
    conn.commit()
    print(f"  ✅ {count} series inserted into series_research")
    return count


def populate_maulwurf_research(conn):
    """Populate video_research from maulwurf_complete_database.json."""
    db_path = os.path.join(CONFIG_DIR, 'maulwurf_complete_database.json')
    if not os.path.exists(db_path):
        print("  ⚠️ Maulwurf database not found")
        return 0
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    cur = conn.cursor()
    count = 0
    
    for vid in db.get('our_videos', []):
        if not vid.get('video_id'):
            continue
        
        cur.execute("""
            INSERT OR REPLACE INTO video_research
            (video_id, series_key, episode_num, production_year, original_title,
             duration_verified, composer, copyright_status, research_source,
             verified, verified_date, notes)
            VALUES (?, 'maulwurf', ?, ?, ?, ?, ?, 'public_domain', ?, 1, ?, ?)
        """, (
            vid['video_id'],
            vid.get('ep_num'),
            vid.get('year'),
            vid.get('titles', {}).get('cs', ''),
            vid.get('duration'),
            vid.get('composer'),
            vid.get('source', 'CZ Wikipedia'),
            datetime.now().strftime("%Y-%m-%d"),
            vid.get('type', 'short')
        ))
        count += 1
    
    conn.commit()
    print(f"  ✅ {count} Maulwurf videos → video_research")
    return count


def populate_bravestarr_research(conn):
    """Populate from bravestarr_episodes.json."""
    db_path = os.path.join(CONFIG_DIR, 'bravestarr_episodes.json')
    if not os.path.exists(db_path):
        print("  ⚠️ BraveStarr episodes config not found")
        return 0
    
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    cur = conn.cursor()
    count = 0
    
    episodes = db.get('episodes', {}) if isinstance(db, dict) else db
    
    # Handle dict format {prod_num: {de_title, en_title, broadcast_nr, ...}}
    if isinstance(episodes, dict):
        for prod_num, ep in episodes.items():
            if not isinstance(ep, dict):
                continue
            # No video_ids in this config — just store episode mapping as notes
            # We'll match by title later when videos are found
            count += 1
        print(f"  ℹ️  {count} BraveStarr episodes found (no video_ids in config, series is private)")
        count = 0  # Nothing to insert without video_ids
    else:
        for ep in episodes:
            vid_id = ep.get('video_id')
            if not vid_id:
                continue
            
            cur.execute("""
                INSERT OR REPLACE INTO video_research
                (video_id, series_key, episode_num, episode_num_alt, numbering_note,
                 production_year, original_title, copyright_status, notes,
                 verified, verified_date)
                VALUES (?, 'bravestarr', ?, ?, ?, ?, ?, 'copyrighted', ?, 1, ?)
            """, (
                vid_id,
                ep.get('production_num', ep.get('ep_num')),
                ep.get('broadcast_num', ep.get('air_num')),
                'Prod-Nr ≠ Broadcast-Nr! Filename = Prod-Nr.',
                ep.get('year', 1987),
                ep.get('en_title', ep.get('title_en', '')),
                ep.get('de_title', ep.get('title_de', '')),
                datetime.now().strftime("%Y-%m-%d")
            ))
            count += 1
    
    conn.commit()
    print(f"  ✅ {count} BraveStarr episodes → video_research")
    return count


def populate_research_rules(conn):
    """Insert global and per-series research/SEO rules."""
    cur = conn.cursor()
    
    rules = [
        # Global rules
        (None, 'title_format', '[KEYWORD]: [Titel] ([Jahr]) | 8K HQ', 100, 'copilot-instructions.md'),
        (None, 'title_max_length', '70 characters', 100, 'YouTube SEO 2026'),
        (None, 'title_no_handle', 'NEVER put @remAIke_IT in title', 100, 'copilot-instructions.md'),
        (None, 'tag_limit', 'Max 15 tags', 90, 'YouTube policy'),
        (None, 'hashtag_limit', 'Max 5 hashtags in description', 90, 'YouTube policy'),
        (None, 'description_links', 'MUST include: 🌐 www.remaike.IT + 📺 youtube.com/@remAIke_IT', 100, 'copilot-instructions.md'),
        (None, 'description_cta', 'MUST include: LIKE/SUBSCRIBE/COMMENT CTA block', 90, 'YouTube 2026 algo'),
        (None, 'category', 'Default: 1 (Film & Animation)', 50, 'copilot-instructions.md'),
        (None, 'i18n_minimum', 'At least 5 localizations for discoverability', 80, 'YouTube 2026 SEO'),
        (None, 'research_verify', 'ALL facts MUST be verified from Wikipedia/IMDB before pushing', 100, 'User requirement'),
        
        # Maulwurf
        ('maulwurf', 'title_format', 'Krtek E{num:02d}: {de_title} ({year}) | 8K HQ', 100, 'Verified CZ Wiki'),
        ('maulwurf', 'numbering', 'Use CZ Wikipedia list (1-49)', 100, 'cs.wikipedia.org/wiki/Seznam_dílů_seriálu_O_krtkovi'),
        ('maulwurf', 'i18n_languages', 'de, cs, en, ja, zh, es, fr, ru, ko, pl', 90, 'maulwurf_international_seo.py'),
        ('maulwurf', 'category', '1 (Film & Animation)', 100, 'Animation series'),
        ('maulwurf', 'naming', 'Include "Krtek" in title (Czech name for discoverability)', 100, 'User requirement'),
        
        # Soundies
        ('soundies', 'category', '10 (Music) — NOT Film & Animation!', 100, 'copilot-instructions.md'),
        ('soundies', 'title_format', 'Soundie: {Song Title} | {Artist} | 8K HQ', 90, 'soundies_seo_template.md'),
        
        # Wochenschau
        ('wochenschau', 'category', '27 (Education) — PFLICHT!', 100, 'YouTube compliance'),
        ('wochenschau', 'disclaimer', 'In-video disclaimer REQUIRED (pixel-level)', 100, 'EDSA Policy 2026'),
        ('wochenschau', 'title_format', 'Wochenschau: {Event} ({DD.MM.YYYY}) | 8K HQ (4K UHD)', 100, 'copilot-instructions.md'),
        ('wochenschau', 'default_audio_language', 'de (German original audio)', 100, 'YouTube audio language signal'),
        ('wochenschau', 'authority_links', 'https://frai.tv/watch/{VIDEO_ID}, https://www.remaike.IT, https://www.youtube.com/@remAIke_IT', 100, 'GEO/AEO external authority'),
        ('wochenschau', 'made_for_kids', 'MUST be set to NO', 100, 'YouTube policy'),
        
        # BraveStarr
        ('bravestarr', 'numbering', 'Use PRODUCTION number (001-065), NOT broadcast order!', 100, 'copilot-instructions.md'),
        ('bravestarr', 'naming', 'ALWAYS verify filename Prod-Nr → DE title via mapping', 100, 'User requirement'),
        
        # Alfred J. Kwak
        ('alfred_kwak', 'naming', 'Include BOTH "Kwak" AND "Quack" for all spellings', 90, 'copilot-instructions.md'),
        
        # Clever & Smart
        ('clever_smart', 'copyright', 'Warner Bros copyright claim — do NOT monetize', 100, 'YouTube Studio'),
    ]
    
    count = 0
    for r in rules:
        cur.execute("""
            INSERT OR IGNORE INTO research_rules 
            (series_key, rule_type, rule_value, priority, source)
            VALUES (?, ?, ?, ?, ?)
        """, r)
        count += 1
    
    conn.commit()
    print(f"  ✅ {count} research rules inserted")
    return count


def populate_i18n_status(conn):
    """Populate video_i18n from current localizations in videos table."""
    cur = conn.cursor()
    
    cur.execute("SELECT id, localizations FROM videos WHERE localizations IS NOT NULL AND localizations != '{}'")
    rows = cur.fetchall()
    
    count = 0
    for vid_id, locs_json in rows:
        try:
            locs = json.loads(locs_json) if isinstance(locs_json, str) else locs_json
        except:
            continue
        
        if not isinstance(locs, dict):
            continue
            
        for lang, data in locs.items():
            title = data.get('title', '') if isinstance(data, dict) else ''
            desc_len = len(data.get('description', '')) if isinstance(data, dict) else 0
            
            cur.execute("""
                INSERT OR REPLACE INTO video_i18n
                (video_id, language, title, description_length, status, pushed_at)
                VALUES (?, ?, ?, ?, 'pushed', ?)
            """, (vid_id, lang, title, desc_len, datetime.now().strftime("%Y-%m-%d")))
            count += 1
    
    conn.commit()
    print(f"  ✅ {count} i18n entries from existing localizations")
    return count


def compute_ist_soll(conn):
    """Compare current video state against rules and populate video_targets."""
    cur = conn.cursor()
    
    cur.execute("SELECT id, title, description, tags, category_id, localizations, series FROM videos")
    rows = cur.fetchall()
    
    now = datetime.now().isoformat()
    count = 0
    matched = 0
    diverged = 0
    
    for vid_id, title, desc, tags, cat_id, locs_json, series in rows:
        issues = []
        
        # Check title rules
        if '@remAIke_IT' in (title or '') or '@remaike' in (title or '').lower():
            issues.append('title_has_handle')
        if title and len(title) > 70:
            issues.append('title_too_long')
        if '8K' not in (title or '') and '4K' not in (title or ''):
            issues.append('missing_quality_tag')
        
        # Check description rules
        if not desc:
            issues.append('missing_description')
        else:
            if 'remaike.it' not in desc.lower() and 'remaike.IT' not in desc:
                issues.append('missing_website_link')
            if '@remAIke_IT' not in desc:
                issues.append('missing_channel_link')
            if not any(cta in desc.upper() for cta in ['LIKE', 'SUBSCRIBE']):
                issues.append('missing_cta')
        
        # Check category for specific series
        if series == 'soundies' and cat_id != 10:
            issues.append(f'wrong_category_{cat_id}_should_be_10')
        if series == 'wochenschau' and cat_id != 27:
            issues.append(f'wrong_category_{cat_id}_should_be_27')
        
        # Check tags
        try:
            tag_list = json.loads(tags) if isinstance(tags, str) else (tags or [])
        except:
            tag_list = []
        if len(tag_list) > 15:
            issues.append(f'too_many_tags_{len(tag_list)}')
        if len(tag_list) == 0:
            issues.append('no_tags')
        
        # Check localizations
        try:
            locs = json.loads(locs_json) if isinstance(locs_json, str) else (locs_json or {})
        except:
            locs = {}
        if len(locs) < 5:
            issues.append(f'low_i18n_{len(locs)}_languages')
        
        status = 'matched' if not issues else 'diverged'
        if status == 'matched':
            matched += 1
        else:
            diverged += 1
        
        cur.execute("""
            INSERT OR REPLACE INTO video_targets
            (video_id, status, divergence_details, last_compared, created_at)
            VALUES (?, ?, ?, ?, COALESCE((SELECT created_at FROM video_targets WHERE video_id=?), ?))
        """, (vid_id, status, json.dumps(issues), now, vid_id, now))
        count += 1
    
    conn.commit()
    print(f"  ✅ {count} videos analyzed: {matched} matched, {diverged} diverged")
    return count


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("CHANNEL MANAGER DB ENHANCEMENT + FULL SYNC")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"DB: {DB_PATH}")
    print("=" * 70)
    
    # Backup first
    import shutil
    backup_name = f"channel_manager_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_dir = os.path.join(os.path.dirname(DB_PATH), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    backup_path = os.path.join(backup_dir, backup_name)
    shutil.copy2(DB_PATH, backup_path)
    print(f"\n💾 Backup: {backup_name}")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Step 1: Schema migration
    print("\n" + "=" * 70)
    print("STEP 1: SCHEMA MIGRATION")
    print("=" * 70)
    migrate_schema(conn)
    
    # Step 2: Full YouTube sync
    print("\n" + "=" * 70)
    print("STEP 2: FULL YOUTUBE SYNC")
    print("=" * 70)
    
    print("  Fetching all channel videos...")
    videos = fetch_all_videos_public()
    
    if videos:
        print(f"  Total videos fetched: {len(videos)}")
        # Use inline scoring instead of importing
        synced = sync_videos_to_db(conn, videos)
        print(f"  ✅ {synced} videos synced to database")
        
        # Update video count
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM videos")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM videos WHERE privacy_status='public'")
        public = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM videos WHERE privacy_status='private'")
        private = cur.fetchone()[0]
        print(f"  📊 Total in DB: {total} (public: {public}, private: {private})")
    else:
        print("  ❌ No videos fetched!")
    
    # Step 3: Populate series research
    print("\n" + "=" * 70)
    print("STEP 3: SERIES RESEARCH DATA")
    print("=" * 70)
    populate_series_research(conn)
    populate_maulwurf_research(conn)
    populate_bravestarr_research(conn)
    
    # Step 4: Research rules
    print("\n" + "=" * 70)
    print("STEP 4: RESEARCH RULES")
    print("=" * 70)
    populate_research_rules(conn)
    
    # Step 5: I18n status
    print("\n" + "=" * 70)
    print("STEP 5: I18N STATUS")
    print("=" * 70)
    populate_i18n_status(conn)
    
    # Step 6: IST/SOLL analysis
    print("\n" + "=" * 70)
    print("STEP 6: IST/SOLL ANALYSIS")
    print("=" * 70)
    compute_ist_soll(conn)
    
    # Final summary
    print("\n" + "=" * 70)
    print("FINAL DATABASE SUMMARY")
    print("=" * 70)
    cur = conn.cursor()
    tables = ['videos', 'playlists', 'series_research', 'video_research', 
              'video_targets', 'video_i18n', 'research_rules',
              'video_snapshots', 'video_revisions', 'activity_log']
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cur.fetchone()[0]
            print(f"  {t:25s} {cnt:>6} rows")
        except:
            print(f"  {t:25s}  ERROR")
    
    # Show diverged videos summary
    cur.execute("""
        SELECT v.series, COUNT(*) as cnt, 
               SUM(CASE WHEN vt.status='matched' THEN 1 ELSE 0 END) as ok,
               SUM(CASE WHEN vt.status='diverged' THEN 1 ELSE 0 END) as bad
        FROM videos v
        LEFT JOIN video_targets vt ON v.id = vt.video_id
        GROUP BY v.series
        ORDER BY cnt DESC
    """)
    rows = cur.fetchall()
    print(f"\n  {'Series':25s} {'Total':>6} {'✅ OK':>6} {'⚠️ Fix':>6}")
    print(f"  {'-'*50}")
    for series, total, ok, bad in rows:
        print(f"  {(series or 'unknown'):25s} {total:>6} {(ok or 0):>6} {(bad or 0):>6}")
    
    conn.close()
    print(f"\n✅ Database enhancement complete!")
    print(f"   Access via Channel Manager: http://127.0.0.1:8420")


if __name__ == '__main__':
    main()
