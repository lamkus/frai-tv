#!/usr/bin/env python3
"""
WochenschauTV — 24/7 Chronologischer Livestream
================================================
Streamt alle Deutsche Wochenschau Episoden chronologisch als Permastream
auf den remAIke_IT YouTube Channel.

Usage:
    python wochenschautv.py --scan          # Scan video files
    python wochenschautv.py --playlist      # Generate FFmpeg playlist
    python wochenschautv.py --prerender     # Pre-render all episodes with HUD (RECOMMENDED)
    python wochenschautv.py --go            # Stream pre-rendered files (ZERO LAG)
    python wochenschautv.py --stream        # Start streaming (realtime, may lag)
    python wochenschautv.py --stream --nvenc  # Use GPU encoding
    python wochenschautv.py --status        # Show current status
    python wochenschautv.py --test          # Test with 1 episode (no upload)
    python wochenschautv.py --preview       # Generate HUD layout preview (no files needed)
"""

import json
import os
import sys
import subprocess
import time
import signal
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Force UTF-8 output on Windows (cp1252 console can't handle → ─ etc.)
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# === CONFIG ===
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'wochenschautv_config.json'
DB_PATH = ROOT_DIR / 'config' / 'wochenschau_complete_upload_database.json'
EVENTS_PATH = ROOT_DIR / 'config' / 'wochenschau_events.json'
LOCATIONS_PATH = ROOT_DIR / 'config' / 'wochenschau_complete_locations.json'

LOG_DIR = ROOT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'wochenschautv_stream.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('WochenschauTV')


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_episodes():
    """Load episode database sorted chronologically."""
    with open(DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    videos = db.get('videos', {})
    
    # Also load events for overlay info
    with open(EVENTS_PATH, 'r', encoding='utf-8') as f:
        ev = json.load(f)
    events = ev.get('events', {})
    
    # ONLY load 8K verified episodes — low-res originals are NOT acceptable for stream
    verified_8k = {}
    mapping_path_8k = os.path.join(os.path.dirname(DB_PATH), 'wochenschau_8k_verified_sources.json')
    if os.path.exists(mapping_path_8k):
        with open(mapping_path_8k, 'r', encoding='utf-8') as f:
            mapping_8k = json.load(f)
        verified_8k = mapping_8k.get('episodes', {})
        log.info(f"8K verified sources loaded: {len(verified_8k)} episodes")
    else:
        log.warning(f"8K mapping not found at {mapping_path_8k} — loading all episodes")
    
    episodes = []
    for num_str, v in sorted(videos.items(), key=lambda x: int(x[0])):
        # Skip episodes not in 8K verified list
        if verified_8k and num_str not in verified_8k:
            continue
        
        # Load location info
        loc_data = {}
        if os.path.exists(LOCATIONS_PATH):
            try:
                with open(LOCATIONS_PATH, 'r', encoding='utf-8') as lf:
                    all_locs = json.load(lf)
                loc_data = all_locs.get(num_str, {})
            except Exception:
                pass

        ep = {
            'number': int(num_str),
            'number_str': num_str,
            'date': v.get('date', ''),
            'year': v.get('year', 0),
            'event_de': v.get('event_de', events.get(num_str, {}).get('event_de', '')),
            'event_en': v.get('event_en', events.get(num_str, {}).get('event_en', '')),
            'historical_note': v.get('historical_note', events.get(num_str, {}).get('note', '')),
            'location': loc_data.get('location', {}).get('desc', ''),
            'tags': v.get('tags', []),
            'expected_filename': v.get('expected_filename', ''),
            'title': v.get('title', ''),
        }
        episodes.append(ep)
    
    return episodes


def scan_video_files(config, episodes):
    """Match episodes to video files.
    
    ONLY uses YouTube 4K downloads — these already have strike protection,
    watermark, and all overlays baked in from the uploaded channel videos.
    V:\\ originals are RAW without protection — NEVER use for streaming.
    """
    import re
    
    matched = 0
    unmatched = []
    
    # ── ONLY scan download dirs (YouTube 4K downloads) ──
    source_dirs = config['paths'].get('video_source_dirs', [])
    scan_dirs = [d for d in source_dirs if d and os.path.isdir(d)]
    
    if scan_dirs:
        # Index all video files by episode number
        files_by_num = {}
        for src_dir in scan_dirs:
            log.info(f"Scanning: {src_dir}")
            for root, dirs, files in os.walk(src_dir):
                for f in files:
                    if not f.lower().endswith(('.mp4', '.mkv', '.webm', '.mov')):
                        continue
                    if '.part' in f.lower() or '.temp.' in f.lower():
                        continue
                    # Extract episode number — handles:
                    # "Wochenschau 459： Pre-War Era..." (YouTube title format)
                    # "Deutsche_Wochenschau_Nr459_..." (original format)
                    m = re.search(r'wochenschau[^\d]*(\d{3,4})', f, re.IGNORECASE)
                    if not m:
                        m = re.search(r'(?:ws|nr|dw)[_\s-]*(\d{3,4})', f, re.IGNORECASE)
                    if m:
                        ep_num = int(m.group(1))
                        full_path = os.path.join(root, f)
                        fsize = os.path.getsize(full_path)
                        if fsize < 1_000_000:  # Skip incomplete downloads < 1MB
                            continue
                        if ep_num not in files_by_num or fsize > files_by_num[ep_num][1]:
                            files_by_num[ep_num] = (full_path, fsize)
        
        for ep in episodes:
            num = ep['number']
            if num in files_by_num:
                ep['file_path'] = files_by_num[num][0]
                ep['_source_type'] = 'yt_download'
                matched += 1
        
        log.info(f"YouTube downloads matched: {matched}")
    else:
        log.warning("No download directories found!")
    
    # Count unmatched
    for ep in episodes:
        if not ep.get('file_path'):
            unmatched.append(ep['number'])
    
    log.info(f"Total matched: {matched} | Unmatched: {len(unmatched)}")
    
    return matched, unmatched


def generate_playlist(episodes, config):
    """Generate FFmpeg concat playlist file."""
    playlist_path = ROOT_DIR / config['paths']['playlist_file']
    playlist_path.parent.mkdir(parents=True, exist_ok=True)
    
    available = [ep for ep in episodes if ep.get('file_path')]
    
    if not available:
        log.error("No video files found! Cannot generate playlist.")
        return None
    
    with open(playlist_path, 'w', encoding='utf-8') as f:
        f.write("# WochenschauTV Playlist - Chronological Order\n")
        f.write(f"# Generated: {datetime.now().isoformat()}\n")
        f.write(f"# Episodes: {len(available)}\n\n")
        
        for ep in available:
            fp = ep['file_path'].replace('\\', '/')
            f.write(f"file '{fp}'\n")
            # Add episode info as comment
            f.write(f"# Nr.{ep['number']} | {ep['date']} | {ep['event_de']}\n")
    
    log.info(f"Playlist generated: {playlist_path} ({len(available)} episodes)")
    return playlist_path


def generate_ffmpeg_concat_file(episodes):
    """Generate a simple concat demuxer file for FFmpeg."""
    concat_path = ROOT_DIR / 'config' / 'wochenschau_concat.txt'
    
    available = [ep for ep in episodes if ep.get('file_path')]
    
    with open(concat_path, 'w', encoding='utf-8') as f:
        for ep in available:
            fp = ep['file_path'].replace('\\', '/').replace("'", "'\\''")
            f.write(f"file '{fp}'\n")
    
    return concat_path, len(available)


def build_ffmpeg_command(concat_file, config, stream_key, use_nvenc=False, test_mode=False):
    """Build the FFmpeg command for streaming."""
    ff = config['ffmpeg']
    ov = config['overlay']
    
    # Video codec
    if use_nvenc:
        vcodec = ff['codec_video_nvenc']
        preset = ff['preset_nvenc']
    else:
        vcodec = ff['codec_video']
        preset = ff['preset']
    
    # Build filter chain
    filters = []
    
    # Scale to 1080p
    res_w, res_h = ff['resolution'].split('x')
    filters.append(f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease")
    filters.append(f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black")
    filters.append(f"fps={ff['fps']}")
    
    # Disclaimer overlay (if enabled in concat mode)
    if ov.get('disclaimer', {}).get('enabled'):
        d = ov['disclaimer']
        disclaimer_text = d['text'].replace("'", "\\'").replace(":", "\\:")
        filters.append(
            f"drawtext=text='{disclaimer_text}'"
            f":fontsize={d['font_size']}"
            f":fontcolor={d['font_color']}"
            f":x=(w-tw)/2:y=10"
            f":box=1:boxcolor={d['bg_color']}:boxborderw=8"
            f":font='Arial'"
        )
    
    filter_str = ','.join(filters)
    
    # RTMP URL
    rtmp_url = f"{ff['rtmp_url']}/{stream_key}"
    
    cmd = [
        'ffmpeg',
        '-re',
        '-stream_loop', '-1',
        '-f', 'concat',
        '-safe', '0',
        '-i', str(concat_file),
        '-vf', filter_str,
        '-c:v', vcodec,
        '-preset', preset,
        '-b:v', ff['video_bitrate'],
        '-maxrate', ff['video_bitrate'],
        '-bufsize', ff['bufsize'],
        '-pix_fmt', ff['pixel_format'],
        '-g', str(ff['max_keyframe_interval']),  # Keyframe interval
        '-c:a', ff['codec_audio'],
        '-b:a', ff['audio_bitrate'],
        '-ar', str(ff['audio_sample_rate']),
        '-f', 'flv',
    ]
    
    if test_mode:
        # Output to file instead of RTMP
        test_out = str(ROOT_DIR / 'output' / 'wochenschautv_test.flv')
        cmd.extend(['-t', '60', test_out])  # 60 seconds test
    else:
        cmd.append(rtmp_url)
    
    return cmd


def _esc(text):
    """Escape text for FFmpeg drawtext filter.
    
    FFmpeg filtergraph special chars that MUST be escaped:
    - \\  → \\\\  (backslash)
    - :   → \\:   (colon — separates filter options)
    - ,   → \\,   (comma — separates filters in chain)  
    - ;   → \\;   (semicolon — separates filter graph segments)
    - %   → %%    (percent — used for time expansion)
    
    Single quotes are REMOVED (they break FFmpeg text= quoting).
    Unicode chars are sanitized to ASCII equivalents.
    """
    # First: sanitize problematic Unicode to ASCII equivalents
    text = (text
            .replace('\u2014', '-')   # em dash → hyphen
            .replace('\u2013', '-')   # en dash → hyphen
            .replace('\u2018', '')    # left single quote → remove
            .replace('\u2019', '')    # right single quote → remove
            .replace('\u201c', '')    # left double quote → remove
            .replace('\u201d', '')    # right double quote → remove
            .replace('\u2026', '...')  # ellipsis
            )
    # Remove regular single quotes too (they break text='...' wrapper)
    text = text.replace("'", "")
    # Then: FFmpeg filter escaping
    return (text
            .replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace(",", "\\,")
            .replace(";", "\\;")
            .replace("%", "%%"))


def _probe_duration(file_path):
    """Get video duration in seconds via ffprobe. Returns 0 on error."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', file_path],
            capture_output=True, text=True, timeout=15
        )
        return int(float(result.stdout.strip()))
    except Exception:
        return 0


def _build_episode_keywords(episode):
    """Extract 3-5 ENGLISH keywords for the HUD from episode data.
    
    Sources (priority order):
    1. location.desc — always English (e.g. "London, England")
    2. tags — English-only filtered
    3. historical_note — extract names, operations, dates (language-neutral)
    4. event_en — fallback
    """
    import re as _re
    keywords = []

    # 1. Location (always English)
    loc = episode.get('location', '')
    if loc:
        keywords.append(loc)

    # 2. Episode-specific tags — SKIP ALL
    #    Tags are generic YouTube SEO metadata (same for all episodes).
    #    Examples: 'Wochenschau', 'prewar', '1939 Germany', 'Nazi Germany 1939'
    #    These add ZERO unique value to the HUD — rely on location + note instead.

    # 3. Historical note — extract internationally readable facts
    #    (operation names, person names, dates, troop counts are language-neutral)
    note = episode.get('historical_note', '')
    if note:
        # Extract operation/proper names (capitalized multi-word)
        # e.g. "Operation Bagration", "Operation Dynamo"
        ops = _re.findall(r'(?:Operation|Unternehmen)\s+(\w+)', note)
        for op in ops:
            kw = f"Operation {op}"
            if kw not in keywords:
                keywords.append(kw)
        
        # Extract dates in parentheses: (22.06.1944), (13.-15.02.1945)
        dates = _re.findall(r'\(([^)]*\d{2}\.\d{2}\.\d{4}[^)]*)\)', note)
        for d in dates[:1]:  # max 1 date
            if d not in keywords:
                keywords.append(d)
        
        # Extract troop numbers: "340.000 Soldaten" -> "340,000 troops"
        troops = _re.findall(r'([\d.]+)\s*(?:Soldaten|Mann|Gefangene)', note)
        for t in troops[:1]:
            num = t.replace('.', ',')
            kw = f"{num} troops"
            if kw not in keywords:
                keywords.append(kw)
        
        # Extract known historical figures (English-safe proper names only)
        KNOWN_PERSONS = {'Rommel', 'Hitler', 'Churchill', 'Stalin', 'Elser',
                         'Eisenhower', 'Montgomery', 'Patton', 'Manstein',
                         'Guderian', 'Paulus', 'Goebbels', 'Doenitz'}
        for person in KNOWN_PERSONS:
            if person in note and person not in keywords:
                keywords.append(person)
                break  # max 1 person

    # 4. Event English text as fallback
    event = episode.get('event_en', '')
    if event and event not in keywords and len(keywords) < 4:
        keywords.append(event)

    return keywords[:5]


def _calc_timeline_progress(episode_date_str):
    """Calculate progress 0.0-1.0 through the war timeline (1939-06 to 1945-03)."""
    from datetime import date
    try:
        parts = episode_date_str.split('-')
        ep_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return 0.5
    
    start = date(1939, 6, 1)   # First Wochenschau
    end = date(1945, 3, 1)     # Last Wochenschau
    total_days = (end - start).days  # ~2100 days
    
    current = (ep_date - start).days
    progress = max(0.0, min(1.0, current / total_days))
    return progress


# Timeline year markers with key events
TIMELINE_YEARS = {
    1939: "Pre-War / Invasion of Poland",
    1940: "Western Front",
    1941: "Operation Barbarossa",
    1942: "Stalingrad",
    1943: "Turning Point",
    1944: "D-Day & Collapse",
    1945: "Final Days",
}

def _get_era_text(episode):
    """Date-aware era text — much more accurate than year-only."""
    from datetime import date as _date
    try:
        parts = episode['date'].split('-')
        d = _date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError, KeyError):
        return ''
    if d < _date(1939, 9, 1):
        return 'Pre-War Europe'
    elif d < _date(1940, 4, 9):
        return 'Phoney War'
    elif d < _date(1940, 6, 25):
        return 'Fall of France'
    elif d < _date(1940, 11, 1):
        return 'Battle of Britain'
    elif d < _date(1941, 6, 22):
        return 'Fortress Europe'
    elif d < _date(1942, 8, 1):
        return 'Operation Barbarossa'
    elif d < _date(1943, 2, 3):
        return 'Stalingrad'
    elif d < _date(1944, 6, 6):
        return 'Turning Point'
    elif d < _date(1945, 1, 1):
        return 'Allied Advance'
    else:
        return 'Final Days'

# YouTube-native font (Segoe UI = Windows equivalent of Roboto)
YT_FONT = 'Segoe UI'
YT_FONT_SEMIBOLD = 'Segoe UI Semibold'
# YouTube brand colors
YT_RED = '#FF0000'
YT_RED_DARK = '#CC0000'
YT_BG_DARK = '#0D0D0D'
YT_BG_PILL = '#0D0D0D'
YT_TEXT_PRIMARY = '#FFFFFF'
YT_TEXT_SECONDARY = '#AAAAAA'
YT_TEXT_MUTED = '#717171'


def build_timeline_filters(episode, config):
    """
    HUD v3 — "Historical Documentary" design.
    
    Combines competitor research (minimal chrome) with RICH historical context
    from our hand-curated episode database. Every episode gets:
    - Era label (e.g. "BATTLE OF BRITAIN")
    - Event title (e.g. "Eagle Day")  
    - 2-4 lines of detailed historical context
    - Precise date + location
    - Timeline progress bar
    
    Data source: config/wochenschau_hud_context.json (32 episodes, English)
    Fallback: episode dict fields (event_en, historical_note, location)
    
    ┌────────────────────┐
    │   remAIke.TV       │  Brand (22px)
    │                    │
    │   ── NOW PLAYING ──│  Red divider label
    │                    │
    │   INVASION OF      │  Era (12px, red, uppercase)
    │   POLAND           │
    │                    │
    │   War Begins       │  Event title (26px, bold)
    │                    │
    │   FIRST WARTIME    │  Context block (14px)
    │   NEWSREEL EVER    │  2-5 lines of rich text
    │   PRODUCED.        │  ← THE KEY IMPROVEMENT
    │   Germany invades  │
    │   Poland on        │
    │   September 1,     │
    │   1939.            │
    │                    │
    │   ─────────────    │  Separator
    │   Warsaw, Poland   │  Location (14px)
    │   Sept 6, 1939     │  Precise date (13px)
    │                    │
    │   ████████░░░░     │  Timeline bar
    │   1939      1945   │
    │     12 / 32        │
    └────────────────────┘
    """
    import json as _json
    import os as _os
    filters = []

    res = config.get('ffmpeg', {}).get('resolution', '1920x1080')
    out_w, out_h = [int(x) for x in res.split('x')]
    scale = out_h / 1080  # 2.0 at 4K, 1.0 at 1080p

    def px(val):
        """Scale-aware pixel value. Input = intended size at 1080p base."""
        return max(1, int(val * scale))

    # --- Load rich context data ---
    hud_context = {}
    ctx_path = _os.path.join(_os.path.dirname(__file__), '..', '..', 'config', 'wochenschau_hud_context.json')
    if not _os.path.exists(ctx_path):
        # Try absolute path as fallback
        ctx_path = r'D:\remaike.TV\config\wochenschau_hud_context.json'
    try:
        with open(ctx_path, 'r', encoding='utf-8') as _f:
            _ctx_data = _json.load(_f)
            hud_context = _ctx_data.get('episodes', {})
    except (FileNotFoundError, _json.JSONDecodeError):
        pass

    ep_num_str = str(episode.get('number', ''))
    ctx = hud_context.get(ep_num_str, {})

    # --- Data prep ---
    progress = _calc_timeline_progress(episode['date'])
    ep_date = episode['date']

    # Rich context fields (with fallbacks)
    era_text = ctx.get('era', _get_era_text(episode).upper())
    event_text = ctx.get('title', episode.get('event_en', episode.get('event_de', '')))
    context_text = ctx.get('context', '')
    exact_date = ctx.get('exact_date', '')

    # If no exact_date from context, format from ISO date
    if not exact_date:
        try:
            from datetime import datetime as dt
            d = dt.strptime(ep_date, '%Y-%m-%d')
            exact_date = d.strftime('%B %d, %Y')  # "September 06, 1939"
        except (ValueError, ImportError):
            exact_date = ep_date

    # If no context text, try to build from historical_note
    if not context_text:
        note = episode.get('historical_note', '')
        if note:
            context_text = note  # German fallback — better than nothing

    ep_idx = episode.get('_index', 0)
    ep_total = episode.get('_total', 39)
    ep_year = episode.get('year', 0)

    # Location — from context or episode data
    location = ctx.get('location', '')
    if not location:
        loc_data = episode.get('location', '')
        if isinstance(loc_data, dict):
            location = loc_data.get('desc', '')
        elif isinstance(loc_data, str):
            location = loc_data

    # === PANEL DIMENSIONS ===
    panel_w = px(240)
    pad = px(24)
    inner_w = panel_w - 2 * pad

    # Shadows
    shadow = f":shadowcolor=black@0.8:shadowx={px(2)}:shadowy={px(2)}"
    shadow_lg = f":shadowcolor=black@0.9:shadowx={px(3)}:shadowy={px(3)}"

    # === Helper: word-wrap text to fit panel ===
    def wrap_text(text, max_chars_per_line):
        words = text.split()
        lines = []
        current = ''
        for word in words:
            test = f"{current} {word}".strip() if current else word
            if len(test) <= max_chars_per_line:
                current = test
            else:
                if current:
                    lines.append(current)
                # Handle words longer than max_chars
                if len(word) > max_chars_per_line:
                    lines.append(word[:max_chars_per_line])
                    current = word[max_chars_per_line:] if len(word) > max_chars_per_line else ''
                else:
                    current = word
        if current:
            lines.append(current)
        return lines

    # ================================================================
    # PANEL BACKGROUND — dark, clean
    # ================================================================
    filters.append(
        f"drawbox=x=0:y=0:w={panel_w}:h=ih"
        f":color=#0A0A0F@0.92:t=fill"
    )

    # ================================================================
    # TOP: RED ACCENT LINE
    # ================================================================
    filters.append(
        f"drawbox=x=0:y=0:w={panel_w}:h={px(3)}"
        f":color={YT_RED}@0.95:t=fill"
    )
    # Right edge — hairline red separator
    filters.append(
        f"drawbox=x={panel_w - px(1)}:y=0:w={px(1)}:h=ih"
        f":color={YT_RED}@0.20:t=fill"
    )

    # ================================================================
    # RIGHT PANEL — matching red accent
    # ================================================================
    right_x = out_w - panel_w
    filters.append(
        f"drawbox=x={right_x}:y=0:w={panel_w}:h={px(3)}"
        f":color={YT_RED}@0.95:t=fill"
    )
    filters.append(
        f"drawbox=x={right_x}:y=0:w={px(1)}:h=ih"
        f":color={YT_RED}@0.20:t=fill"
    )

    # ================================================================
    # ================================================================
    # STREAM BRAND — "WWII NEWSREEL ARCHIVE" (two-line for readability)
    # ================================================================
    filters.append(
        f"drawtext=text='WWII NEWSREEL'"
        f":fontsize={px(22)}:fontcolor=#FFFFFF@0.95"
        f":x={pad}:y={px(16)}"
        f":font='{YT_FONT_SEMIBOLD}'"
        f"{shadow_lg}"
    )
    filters.append(
        f"drawtext=text='ARCHIVE'"
        f":fontsize={px(16)}:fontcolor=#FFFFFF@0.65"
        f":x={pad}:y={px(38)}"
        f":font='{YT_FONT_SEMIBOLD}'"
        f":borderw=0"
        f"{shadow}"
    )
    # ================================================================
    # "NOW PLAYING" divider
    # ================================================================
    np_y = px(76)
    np_line_w = px(28)
    filters.append(
        f"drawbox=x={pad}:y={np_y + px(7)}:w={np_line_w}:h={px(1)}"
        f":color={YT_RED}@0.60:t=fill"
    )
    filters.append(
        f"drawtext=text='NOW PLAYING'"
        f":fontsize={px(16)}:fontcolor=#FFFFFF@0.92"
        f":x={pad + np_line_w + px(6)}:y={np_y}"
        f":font='{YT_FONT_SEMIBOLD}'"
        f"{shadow}"
    )
    filters.append(
        f"drawbox=x={pad + np_line_w + px(120)}:y={np_y + px(7)}:w={np_line_w}:h={px(1)}"
        f":color={YT_RED}@0.60:t=fill"
    )

    # ================================================================
    # ERA LABEL — uppercase, red-tinted, provides war-phase context
    # e.g. "INVASION OF POLAND", "BATTLE OF BRITAIN", "NORTH AFRICA"
    # ================================================================
    y_cursor = np_y + px(36)

    if era_text:
        era_lines = wrap_text(era_text, 22)
        for i, line in enumerate(era_lines[:2]):
            filters.append(
                f"drawtext=text='{_esc(line)}'"
                f":fontsize={px(18)}:fontcolor=#FFFFFF@0.90"
                f":x={pad}:y={y_cursor + i * px(22)}"
                f":font='{YT_FONT_SEMIBOLD}'"
                f"{shadow}"
            )
        y_cursor += len(era_lines[:2]) * px(22) + px(8)

    # ================================================================
    # EVENT TITLE — bold, large, the main identifier
    # Sized to be readable on mobile but leave room for context below
    # ================================================================
    event_fontsize = px(34)

    if event_text:
        title_lines = wrap_text(event_text, 14)
        for i, line in enumerate(title_lines[:2]):
            filters.append(
                f"drawtext=text='{_esc(line)}'"
                f":fontsize={event_fontsize}:fontcolor=#FFFFFF@0.98"
                f":x={pad}:y={y_cursor + i * px(40)}"
                f":font='{YT_FONT_SEMIBOLD}'"
                f"{shadow_lg}"
            )
        y_cursor += len(title_lines[:2]) * px(40) + px(12)

    # ================================================================
    # CONTEXT BLOCK — THE KEY ADDITION IN v3
    # Rich historical text: 2-5 lines describing what happened.
    # This is what makes us "historical profi niveau".
    # ================================================================
    if context_text:
        # At fontsize 14px @1080 = 28px @4K, ~24-26 chars per line
        ctx_lines = wrap_text(context_text, 24)
        for i, line in enumerate(ctx_lines[:6]):  # max 6 lines
            filters.append(
                f"drawtext=text='{_esc(line)}'"
                f":fontsize={px(18)}:fontcolor=#FFFFFF@0.86"
                f":x={pad}:y={y_cursor + i * px(24)}"
                f":font='{YT_FONT}'"
                f"{shadow}"
            )
        y_cursor += len(ctx_lines[:6]) * px(24) + px(14)

    # ================================================================
    # SEPARATOR LINE
    # ================================================================
    filters.append(
        f"drawbox=x={pad}:y={y_cursor}:w={inner_w}:h={px(1)}"
        f":color=#FFFFFF@0.15:t=fill"
    )
    y_cursor += px(12)

    # ================================================================
    # LOCATION — with pin icon text
    # ================================================================
    if location:
        filters.append(
            f"drawtext=text='{_esc(location)}'"
            f":fontsize={px(19)}:fontcolor=#FFFFFF@0.90"
            f":x={pad}:y={y_cursor}"
            f":font='{YT_FONT}'"
            f"{shadow}"
        )
        y_cursor += px(26)

    # ================================================================
    # PRECISE DATE
    # ================================================================
    if exact_date:
        filters.append(
            f"drawtext=text='{_esc(exact_date)}'"
            f":fontsize={px(18)}:fontcolor=#FFFFFF@0.82"
            f":x={pad}:y={y_cursor}"
            f":font='{YT_FONT}'"
            f"{shadow}"
        )

    # ================================================================
    # BOTTOM: Timeline progress bar + year labels + counter
    # ================================================================
    bar_y = out_h - px(100)
    bar_h = px(5)

    # Track background
    filters.append(
        f"drawbox=x={pad}:y={bar_y}:w={inner_w}:h={bar_h}"
        f":color=#FFFFFF@0.12:t=fill"
    )
    # Red progress fill
    progress_w = max(px(3), int(inner_w * progress))
    filters.append(
        f"drawbox=x={pad}:y={bar_y}:w={progress_w}:h={bar_h}"
        f":color={YT_RED}@0.90:t=fill"
    )

    # Year labels
    label_y = bar_y + bar_h + px(8)
    filters.append(
        f"drawtext=text='1939'"
        f":fontsize={px(16)}:fontcolor=#FFFFFF@0.72"
        f":x={pad}:y={label_y}"
        f":font='{YT_FONT}'"
        f"{shadow}"
    )
    filters.append(
        f"drawtext=text='1945'"
        f":fontsize={px(16)}:fontcolor=#FFFFFF@0.72"
        f":x={pad + inner_w - px(34)}:y={label_y}"
        f":font='{YT_FONT}'"
        f"{shadow}"
    )

    # Year tick mark
    if 1939 <= ep_year <= 1945:
        yr_progress = _calc_timeline_progress(f"{ep_year}-07-01")
        yr_x = pad + int(inner_w * yr_progress)
        filters.append(
            f"drawbox=x={yr_x}:y={bar_y - px(2)}:w={px(2)}:h={bar_h + px(4)}"
            f":color=#FFFFFF@0.70:t=fill"
        )

    # DISCLAIMER WATERMARK REMOVED  center text bug fixed 2026-02-22
    # Was: HISTORICAL DOCUMENT  EDUCATIONAL PURPOSE ONLY (centered)
    # Info already in right panel (HISTORICAL ARCHIVE)

    # ================================================================
    # RUNTIME PROGRESS BAR — shows playback position in current episode
    # Uses stepped drawbox with enable='gte(t, threshold)' per-frame
    # NOTE: drawbox w='expr' is NOT dynamic! enable IS dynamic.
    # ================================================================
    duration = episode.get('_duration', 0)
    if duration and duration > 0:
        rt_bar_y = bar_y - px(30)  # Above the war-timeline bar
        rt_bar_h = px(3)

        # Track background (static white line)
        filters.append(
            f"drawbox=x={pad}:y={rt_bar_y}:w={inner_w}:h={rt_bar_h}"
            f":color=#FFFFFF@0.10:t=fill"
        )

        # Stepped red progress fill — 20 steps (5% resolution)
        # Each step is a wider drawbox, enabled when t >= threshold
        # Later (wider) bars draw over earlier ones
        STEPS = 20
        for step_i in range(1, STEPS + 1):
            step_w = int(inner_w * step_i / STEPS)
            t_thresh = duration * (step_i - 1) / STEPS
            filters.append(
                f"drawbox=x={pad}:y={rt_bar_y}:w={step_w}:h={rt_bar_h}"
                f":color={YT_RED}@0.70:t=fill"
                f":enable='gte(t,{t_thresh:.2f})'"
            )

        # ETA label — remaining time as MM:SS
        eta_y = rt_bar_y - px(22)
        dur_int = int(duration)
        filters.append(
            f"drawtext=text="
            f"'%{{eif\:({dur_int}-t)/60\:d}}\:%{{eif\:mod({dur_int}-t\,60)\:d\:2}}"
            f" remaining'"
            f":fontsize={px(14)}:fontcolor=#FFFFFF@0.60"
            f":x={pad}:y={eta_y}"
            f":font='{YT_FONT}'"
            f"{shadow}"
        )


    # Episode counter — clean, centered
    counter_y = out_h - px(50)
    counter_text = f"{ep_idx} / {ep_total}"
    filters.append(
        f"drawtext=text='{_esc(counter_text)}'"
        f":fontsize={px(22)}:fontcolor=#FFFFFF@0.92"
        f":x={pad}:y={counter_y}"
        f":font='{YT_FONT}'"
        f"{shadow}"
    )

    return filters


def build_ffmpeg_command_per_episode(episode, config, stream_key, use_nvenc=False):
    """Build FFmpeg command for a single episode with full timeline HUD overlay.
    
    This does REALTIME processing — for lag-free streaming, use pre-render instead.
    """
    ff = config['ffmpeg']
    
    if use_nvenc:
        vcodec = ff['codec_video_nvenc']
        preset = ff['preset_nvenc']
    else:
        vcodec = ff['codec_video']
        preset = ff['preset']
    
    # Build filter chain
    filters = []
    
    # Scale to output resolution
    res_w, res_h = ff['resolution'].split('x')
    filters.append(f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease")
    filters.append(f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black")
    filters.append(f"fps={ff['fps']}")
    
    # Add full timeline HUD
    filters.extend(build_timeline_filters(episode, config))
    
    filter_str = ','.join(filters)
    rtmp_url = f"{ff['rtmp_url']}/{stream_key}"
    
    cmd = [
        'ffmpeg',
        '-re',
        '-i', episode['file_path'],
        '-vf', filter_str,
        '-c:v', vcodec,
        '-preset', preset,
        '-b:v', ff['video_bitrate'],
        '-maxrate', ff['video_bitrate'],
        '-bufsize', ff['bufsize'],
        '-pix_fmt', ff['pixel_format'],
        '-g', str(ff['max_keyframe_interval']),
        '-c:a', ff['codec_audio'],
        '-b:a', ff['audio_bitrate'],
        '-ar', str(ff['audio_sample_rate']),
        '-f', 'flv',
        rtmp_url,
    ]
    
    return cmd


def prerender_episode(episode, config, output_dir, use_nvenc=True):
    """Pre-render a single episode with HUD baked in to an H.264 file.
    
    This is the KEY to lag-free streaming:
    - Software AV1 decode (RTX 3090 has no AV1 hw decode — only RTX 4000+)
    - NVENC H.264 encode on GPU (fast)
    - All filters applied OFFLINE (no realtime pressure)
    - Output: clean H.264 + AAC file ready for stream
    - During streaming: just `-c copy` = zero processing = zero lag
    
    Resolution is read from config['ffmpeg']['resolution']:
    - 3840x2160 → 4K output, 20Mbps (slow render, ~30min/episode)
    - 1920x1080 → 1080p output, 8Mbps (fast render, ~5min/episode)
    """
    ff = config['ffmpeg']
    res = config.get('ffmpeg', {}).get('resolution', '1920x1080')
    out_w, out_h = [int(x) for x in res.split('x')]
    
    # Bitrate scales with resolution
    if out_h >= 2160:
        bitrate, maxrate, bufsize = '20000k', '25000k', '40000k'
    else:
        bitrate, maxrate, bufsize = '8000k', '10000k', '16000k'
    
    out_path = os.path.join(output_dir, f"WochenschauTV_Nr{episode['number']:03d}.mp4")
    
    # Skip if already rendered AND valid (probe checks moov atom + duration)
    if os.path.exists(out_path):
        out_size = os.path.getsize(out_path)
        if out_size > 10_000_000:  # > 10MB
            # Verify file is actually valid (has moov atom, has duration)
            try:
                probe = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                     '-of', 'csv=p=0', out_path],
                    capture_output=True, text=True, timeout=10
                )
                dur = float(probe.stdout.strip()) if probe.stdout.strip() else 0
                if dur > 30:  # At least 30 seconds = valid
                    log.info(f"  Already rendered: {out_path} ({out_size // 1_000_000}MB, {dur:.0f}s)")
                    return out_path
                else:
                    log.warning(f"  Corrupt render detected (dur={dur:.0f}s), re-rendering: {out_path}")
                    try:
                        os.remove(out_path)
                    except OSError:
                        # File locked? Skip for now, will retry next run
                        log.warning(f"  Cannot delete locked file, skipping")
                        return None
            except Exception:
                log.warning(f"  Cannot probe {out_path}, re-rendering")
                try:
                    os.remove(out_path)
                except OSError:
                    return None
    
    # Build filter chain at target resolution
    filters = []
    filters.append(f"scale={out_w}:{out_h}:force_original_aspect_ratio=decrease")
    filters.append(f"pad={out_w}:{out_h}:(ow-iw)/2:(oh-ih)/2:black")
    filters.append(f"fps={ff['fps']}")
    
    # Config for HUD sizing (uses resolution for px() scaling)
    render_config = json.loads(json.dumps(config))
    filters.extend(build_timeline_filters(episode, render_config))
    
    filter_str = ','.join(filters)
    
    # Detect source codec to log info
    probe_codec = subprocess.run(
        ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
         '-show_entries', 'stream=codec_name', '-of', 'csv=p=0',
         episode['file_path']],
        capture_output=True, text=True, timeout=10
    )
    src_codec = probe_codec.stdout.strip().lower()
    log.info(f"  Source codec: {src_codec}")
    
    # All codecs: pure software decode (CPU) + CPU filters + NVENC
    # VP9 cuvid + hwdownload causes "Invalid argument" with drawtext filter chain
    # AV1 cuvid fails on YouTube AV1 bitstream (obu_forbidden_bit=1)
    # Solution: software decode all, CPU drawtext filters, NVENC for GPU encode
    log.info(f"  Pipeline: {src_codec} software (CPU) -> CPU filters -> h264_nvenc (GPU)")
    
    # Software decode + NVENC encode
    cmd = [
        'ffmpeg', '-y',
        '-threads', '0',              # Use ALL CPU cores for decode
        '-i', episode['file_path'],
        '-vf', filter_str,
        '-c:v', 'h264_nvenc',
        '-preset', 'p5',              # Quality preset
        '-b:v', bitrate,
        '-maxrate', maxrate,
        '-bufsize', bufsize,
        '-pix_fmt', 'yuv420p',
        '-g', '50',                   # Keyframe every 2 sec
        '-bf', '2',                   # B-frames
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-movflags', '+faststart',    # Web-optimized
        '-async', '1',                # Force A/V sync
        out_path,
    ]
    
    log.info(f"  Pre-rendering Nr.{episode['number']} @ {res} {bitrate} -> {out_path}")
    log.info(f"  Filters: {len(filters)}")
    
    # Redirect FFmpeg stderr to file instead of capture_output=True
    # This prevents Python from buffering all stderr in memory (which can crash)
    ffmpeg_log = os.path.join(str(ROOT_DIR / 'logs'), f"ffmpeg_nr{episode['number']:03d}.log")
    
    try:
        with open(ffmpeg_log, 'w', encoding='utf-8') as stderr_file:
            process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=stderr_file
            )
            returncode = process.wait(timeout=7200)
        
        if returncode != 0:
            # Read error details from log
            try:
                with open(ffmpeg_log, 'r', encoding='utf-8', errors='replace') as f:
                    stderr_text = f.read()
                log.error(f"  Pre-render FAILED (rc={returncode})")
                log.error(f"  STDERR START:\n{stderr_text[:800]}")
                log.error(f"  STDERR END:\n{stderr_text[-300:]}")
            except Exception:
                log.error(f"  Pre-render FAILED (rc={returncode}), no stderr available")
            # Clean up partial file
            if os.path.exists(out_path):
                os.remove(out_path)
            return None
        
        out_size = os.path.getsize(out_path) // 1_000_000
        log.info(f"  Pre-render OK: {out_size}MB | Log: {ffmpeg_log}")
        return out_path
    except subprocess.TimeoutExpired:
        log.error(f"  Pre-render TIMEOUT (2h limit)")
        process.kill()
        if os.path.exists(out_path):
            os.remove(out_path)
        return None
    except Exception as e:
        import traceback
        log.error(f"  Pre-render ERROR: {e}")
        log.error(traceback.format_exc())
        if os.path.exists(out_path):
            os.remove(out_path)
        return None


def prerender_all(episodes, config):
    """Pre-render ALL episodes with HUD. Run once, stream forever."""
    output_dir = str(ROOT_DIR / 'watch' / 'wochenschau_rendered')
    os.makedirs(output_dir, exist_ok=True)
    
    available = [ep for ep in episodes if ep.get('file_path')]
    res = config['ffmpeg'].get('resolution', '1920x1080')
    out_w, out_h = [int(x) for x in res.split('x')]
    bitrate = '20Mbps' if out_h >= 2160 else '8Mbps'
    log.info(f"=== PRE-RENDER: {len(available)} episodes ===")
    log.info(f"Output: {output_dir}")
    log.info(f"Codec: AV1 (software) -> H.264 (NVENC) @ {res} {bitrate}")
    
    success = 0
    failed = 0
    
    for i, ep in enumerate(available):
        ep['_index'] = i + 1
        ep['_total'] = len(available)
        
        # Probe duration
        try:
            ep['_duration'] = _probe_duration(ep['file_path'])
        except Exception:
            ep['_duration'] = 0
        
        # Set next episode
        if i + 1 < len(available):
            ep['_next_episode'] = available[i + 1]
        else:
            ep['_next_episode'] = available[0]
        
        log.info(f"\n[{i+1}/{len(available)}] Nr.{ep['number']} | {ep.get('event_en', '')} | {ep['date']}")
        
        result = prerender_episode(ep, config, output_dir)
        if result:
            success += 1
        else:
            failed += 1
    
    log.info(f"\n=== PRE-RENDER COMPLETE ===")
    log.info(f"Success: {success} | Failed: {failed}")
    log.info(f"Files in: {output_dir}")
    return output_dir


def stream_prerendered(config, stream_key):
    """Stream pre-rendered episodes — ZERO processing, ZERO lag.
    
    This is the production streaming mode:
    - Reads pre-rendered H.264 files (HUD already baked in)
    - Sends via -c copy (no re-encoding)
    - Perfect A/V sync guaranteed
    - Minimal CPU/GPU usage
    - Rock-solid 24/7 operation
    """
    prerender_dir = str(ROOT_DIR / 'watch' / 'wochenschau_rendered')
    
    if not os.path.isdir(prerender_dir):
        log.error(f"Pre-rendered directory not found: {prerender_dir}")
        log.error("Run: python wochenschautv.py --prerender first!")
        return
    
    # Find all pre-rendered files
    files = sorted([
        os.path.join(prerender_dir, f)
        for f in os.listdir(prerender_dir)
        if f.endswith('.mp4') and f.startswith('WochenschauTV_')
    ])
    
    if not files:
        log.error("No pre-rendered files found!")
        return
    
    log.info(f"=== WochenschauTV STREAMING (Pre-rendered) ===")
    log.info(f"Episodes: {len(files)}")
    log.info(f"Mode: -c copy (zero processing)")
    log.info(f"Quality: 4K H.264 20Mbps + AAC 192k")
    
    rtmp_url = f"{config['ffmpeg']['rtmp_url']}/{stream_key}"
    
    running = True
    loop_count = 0
    consecutive_failures = 0
    
    def signal_handler(sig, frame):
        nonlocal running
        log.info("Received shutdown signal...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while running:
        loop_count += 1
        log.info(f"\n{'='*60}")
        log.info(f"=== LOOP {loop_count} — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
        
        for i, filepath in enumerate(files):
            if not running:
                break
            
            fname = os.path.basename(filepath)
            log.info(f"\n--- [{i+1}/{len(files)}] {fname} ---")
            
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1_000_000:
                log.warning(f"File missing or too small, skipping")
                continue
            
            # Stream with -c copy — NO re-encoding, NO filters
            # This is literally just reading the file and sending it to RTMP
            cmd = [
                'ffmpeg',
                '-re',                    # Realtime pacing
                '-i', filepath,
                '-c:v', 'copy',           # NO re-encode — passthrough
                '-c:a', 'copy',           # NO re-encode — passthrough
                '-f', 'flv',
                '-flvflags', 'no_duration_filesize',
                rtmp_url,
            ]
            
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    consecutive_failures += 1
                    stderr_text = stderr.decode('utf-8', errors='replace')[-500:]
                    log.warning(f"FFmpeg exit code {process.returncode} (fail #{consecutive_failures})")
                    log.warning(f"stderr: {stderr_text}")
                    
                    if 'Connection refused' in stderr_text or 'I/O error' in stderr_text:
                        log.warning("RTMP connection error — waiting 60s...")
                        time.sleep(60)
                    elif consecutive_failures >= 10:
                        log.warning("10 consecutive failures! Pausing 5 min...")
                        time.sleep(300)
                        consecutive_failures = 0
                    else:
                        time.sleep(30)
                else:
                    consecutive_failures = 0
                    log.info(f"Episode done OK")
                
                # Brief pause between episodes
                pause = config['schedule'].get('pause_between_episodes_seconds', 5)
                if pause > 0 and running:
                    time.sleep(pause)
                    
            except Exception as e:
                consecutive_failures += 1
                log.error(f"Exception: {e}")
                time.sleep(30)
        
        if running:
            log.info(f"\n=== LOOP {loop_count} COMPLETE — Restarting ===")
    
    log.info("WochenschauTV stopped.")


def stream_episodes_sequential(episodes, config, stream_key, use_nvenc=False):
    """
    Stream episodes one by one — CRASH-PROOF, NEVER-STOP design.
    
    - Each episode gets its own FFmpeg process with unique HUD overlay
    - Auto-rescans for new downloads between loops
    - Retries failed episodes, skips corrupt files
    - Catches ALL exceptions — the show must go on
    - Only stops on explicit SIGINT/SIGTERM (dashboard STOP button)
    """
    available = [ep for ep in episodes if ep.get('file_path')]
    
    if not available:
        log.error("No video files available! Waiting for downloads...")
        # Don't exit — wait for files to appear
        for _ in range(60):  # Wait up to 10 min
            time.sleep(10)
            fresh = load_episodes()
            scan_video_files(config, fresh)
            available = [ep for ep in fresh if ep.get('file_path')]
            if available:
                log.info(f"Found {len(available)} episodes after waiting!")
                break
        if not available:
            log.error("Still no files after 10 min. Exiting.")
            return
    
    log.info(f"=== WochenschauTV STARTING ===")
    log.info(f"Episodes: {len(available)}")
    log.info(f"Range: Nr.{available[0]['number']} ({available[0]['date']}) -> Nr.{available[-1]['number']} ({available[-1]['date']})")
    log.info(f"Encoder: {'NVENC (GPU)' if use_nvenc else 'libx264 (CPU)'}")
    log.info(f"Resolution: {config['ffmpeg']['resolution']}")
    
    loop_count = 0
    running = True
    consecutive_failures = 0
    MAX_CONSECUTIVE_FAILURES = 10  # If 10 eps in a row fail, pause longer
    
    def signal_handler(sig, frame):
        nonlocal running
        log.info("Received shutdown signal, finishing current episode...")
        running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    while running:
        loop_count += 1
        
        # ── RESCAN: Pick up newly downloaded files every loop ──
        try:
            if loop_count > 1:
                log.info("Rescanning for new downloads...")
                fresh_episodes = load_episodes()
                scan_video_files(config, fresh_episodes)
                new_available = [ep for ep in fresh_episodes if ep.get('file_path')]
                if new_available:
                    if len(new_available) != len(available):
                        log.info(f"Playlist updated: {len(available)} -> {len(new_available)} episodes")
                    available = new_available
                else:
                    log.warning("Rescan found 0 files — keeping previous playlist")
        except Exception as e:
            log.warning(f"Rescan error (keeping previous playlist): {e}")
        
        # ── Also reload config for hot-changes ──
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            pass  # Keep old config if file is being written
        
        log.info(f"\n{'='*60}")
        log.info(f"=== LOOP {loop_count} START — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
        log.info(f"Episodes this loop: {len(available)}")
        
        for i, ep in enumerate(available):
            if not running:
                break
            
            # Add index info for the HUD counter
            ep['_index'] = i + 1
            ep['_total'] = len(available)
            
            # Probe duration for runtime display
            try:
                ep['_duration'] = _probe_duration(ep['file_path'])
                if ep['_duration'] > 0:
                    log.info(f"Duration: {ep['_duration'] // 60}m {ep['_duration'] % 60}s")
            except Exception:
                ep['_duration'] = 0
            
            # Pass next episode info for "UP NEXT" section
            if i + 1 < len(available):
                ep['_next_episode'] = available[i + 1]
            else:
                ep['_next_episode'] = available[0] if available else None  # Loop back to first
            
            log.info(f"\n--- Episode {i+1}/{len(available)} ---")
            log.info(f"Nr.{ep['number']} | {ep['date']} | {ep.get('event_de', '')}")
            log.info(f"File: {ep['file_path']}")
            
            # Verify file still exists and is not empty
            try:
                fpath = ep['file_path']
                if not os.path.exists(fpath):
                    log.warning(f"File missing, skipping: {fpath}")
                    continue
                if os.path.getsize(fpath) < 1_000_000:  # Skip files < 1MB (corrupt/incomplete)
                    log.warning(f"File too small ({os.path.getsize(fpath)} bytes), skipping: {fpath}")
                    continue
            except Exception as e:
                log.warning(f"File check error, skipping: {e}")
                continue
            
            try:
                cmd = build_ffmpeg_command_per_episode(ep, config, stream_key, use_nvenc)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                
                # Wait for episode to finish
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    consecutive_failures += 1
                    stderr_text = stderr.decode('utf-8', errors='replace')[-500:]
                    log.warning(f"FFmpeg exited with code {process.returncode} (fail #{consecutive_failures})")
                    log.warning(f"Last stderr: {stderr_text}")
                    
                    # Detect RTMP connection errors -> longer wait
                    if 'Connection refused' in stderr_text or 'I/O error' in stderr_text:
                        log.warning("RTMP connection error — waiting 60s before retry...")
                        time.sleep(60)
                    elif consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                        log.warning(f"{MAX_CONSECUTIVE_FAILURES} consecutive failures! Pausing 5 min...")
                        time.sleep(300)
                        consecutive_failures = 0
                    else:
                        time.sleep(config['schedule']['restart_delay_seconds'])
                else:
                    consecutive_failures = 0  # Reset on success
                    log.info(f"Episode {ep['number']} finished OK")
                
                # Pause between episodes
                pause = config['schedule']['pause_between_episodes_seconds']
                if pause > 0 and running:
                    log.info(f"Pause {pause}s before next episode...")
                    time.sleep(pause)
                    
            except Exception as e:
                consecutive_failures += 1
                log.error(f"EXCEPTION streaming ep {ep['number']}: {e}")
                log.error(f"Continuing to next episode... (fail #{consecutive_failures})")
                time.sleep(config['schedule'].get('restart_delay_seconds', 30))
        
        if running:
            log.info(f"\n=== LOOP {loop_count} COMPLETE ({len(available)} episodes) — Rescanning & restarting ===\n")
    
    log.info("WochenschauTV stopped gracefully.")


def stream_concat_loop(episodes, config, stream_key, use_nvenc=False):
    """
    Stream using FFmpeg concat demuxer with infinite loop.
    Simpler but: same overlay for all episodes.
    """
    concat_file, count = generate_ffmpeg_concat_file(episodes)
    
    if count == 0:
        log.error("No video files available!")
        return
    
    log.info(f"=== WochenschauTV CONCAT MODE ===")
    log.info(f"Episodes in playlist: {count}")
    
    cmd = build_ffmpeg_command(concat_file, config, stream_key, use_nvenc)
    log.info(f"Command: {' '.join(cmd[:10])}...")
    
    while True:
        try:
            process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            process.wait()
            
            log.warning(f"FFmpeg exited (code {process.returncode}), restarting in {config['schedule']['restart_delay_seconds']}s...")
            time.sleep(config['schedule']['restart_delay_seconds'])
            
        except KeyboardInterrupt:
            log.info("Stopped by user.")
            break
        except Exception as e:
            log.error(f"Error: {e}")
            time.sleep(config['schedule']['restart_delay_seconds'])


def show_status(episodes):
    """Show current WochenschauTV status."""
    available = [ep for ep in episodes if ep.get('file_path')]
    missing = [ep for ep in episodes if not ep.get('file_path')]
    
    print(f"\n{'='*60}")
    print(f"  WochenschauTV Status")
    print(f"{'='*60}")
    print(f"  Total episodes in DB:  {len(episodes)}")
    print(f"  Files found:           {len(available)}")
    print(f"  Files missing:         {len(missing)}")
    
    if available:
        print(f"\n  Available range:")
        print(f"    First: Nr.{available[0]['number']} ({available[0]['date']}) — {available[0]['event_de']}")
        print(f"    Last:  Nr.{available[-1]['number']} ({available[-1]['date']}) — {available[-1]['event_de']}")
        
        # Estimate total runtime
        # Average Wochenschau ~20-30 min
        est_hours = len(available) * 25 / 60
        print(f"\n  Estimated total runtime: ~{est_hours:.0f} hours ({est_hours/24:.1f} days)")
        print(f"  Loop frequency: every {est_hours/24:.1f} days")
    
    if missing and len(missing) <= 20:
        print(f"\n  Missing episodes:")
        for ep in missing:
            print(f"    Nr.{ep['number']} ({ep['date']}) — {ep['event_de']}")
    elif missing:
        print(f"\n  First 10 missing:")
        for ep in missing[:10]:
            print(f"    Nr.{ep['number']} ({ep['date']}) — {ep['event_de']}")
        print(f"    ... and {len(missing)-10} more")
    
    print(f"\n  Stream config:")
    config = load_config()
    print(f"    Resolution:   {config['ffmpeg']['resolution']}")
    print(f"    Bitrate:      {config['ffmpeg']['video_bitrate']}")
    print(f"    FPS:          {config['ffmpeg']['fps']}")
    print(f"    Disclaimer:   {'ON' if config['overlay']['disclaimer']['enabled'] else 'OFF'}")
    print(f"    Episode Info: {'ON' if config['overlay']['episode_info']['enabled'] else 'OFF'}")
    print(f"{'='*60}\n")


def main():
    args = sys.argv[1:]
    
    if not args:
        print(__doc__)
        return
    
    config = load_config()
    episodes = load_episodes()
    
    if '--scan' in args:
        log.info("Scanning for video files...")
        matched, unmatched = scan_video_files(config, episodes)
        log.info(f"\nScan complete: {matched} matched, {len(unmatched)} unmatched")
        if unmatched:
            log.info(f"Unmatched episode numbers: {unmatched[:20]}{'...' if len(unmatched) > 20 else ''}")
        show_status(episodes)
    
    elif '--playlist' in args:
        log.info("Generating playlist...")
        matched, _ = scan_video_files(config, episodes)
        if matched > 0:
            generate_playlist(episodes, config)
            concat_file, count = generate_ffmpeg_concat_file(episodes)
            log.info(f"Concat file: {concat_file} ({count} episodes)")
        else:
            log.error("No files found!")
    
    elif '--stream' in args:
        stream_key = os.environ.get('YOUTUBE_STREAM_KEY', '')
        if not stream_key:
            # Try to read from config file
            key_path = ROOT_DIR / 'config' / 'stream_key.txt'
            if key_path.exists():
                stream_key = key_path.read_text().strip()
        
        if not stream_key:
            log.error("No stream key! Set YOUTUBE_STREAM_KEY env var or create config/stream_key.txt")
            print("\nTo get your stream key:")
            print("1. Go to https://studio.youtube.com/channel/UCVFv6Egpl0LDvigpFbQXNeQ/livestreaming")
            print("2. Create a new livestream")
            print("3. Copy the Stream Key")
            print("4. Set: $env:YOUTUBE_STREAM_KEY = 'your-key-here'")
            print("   Or save to: config/stream_key.txt")
            return
        
        use_nvenc = '--nvenc' in args
        sequential = '--sequential' in args or '--per-episode' in args
        
        log.info("Scanning files...")
        matched, _ = scan_video_files(config, episodes)
        
        if matched == 0:
            log.error("No video files found!")
            return
        
        if sequential:
            stream_episodes_sequential(episodes, config, stream_key, use_nvenc)
        else:
            # Default: sequential mode (better overlays)
            stream_episodes_sequential(episodes, config, stream_key, use_nvenc)
    
    elif '--test' in args:
        log.info("Test mode: generating test output with timeline HUD...")
        matched, _ = scan_video_files(config, episodes)
        available = [ep for ep in episodes if ep.get('file_path')]
        if available:
            # Pick a mid-war episode for visual variety (or first if few available)
            test_idx = len(available) // 3 if len(available) > 3 else 0
            ep = available[test_idx]
            ep['_index'] = test_idx + 1
            ep['_total'] = len(available)
            log.info(f"Testing with: Nr.{ep['number']} ({ep['event_de']}) [{test_idx+1}/{len(available)}]")
            
            # Build test command (output to file, no realtime pacing)
            config_copy = json.loads(json.dumps(config))
            cmd = build_ffmpeg_command_per_episode(ep, config_copy, 'TEST', False)
            
            # Replace RTMP output with file output
            cmd = cmd[:-1]  # Remove RTMP URL
            # Remove -re flag (realtime pacing not needed for test)
            if '-re' in cmd:
                cmd.remove('-re')
            test_out = str(ROOT_DIR / 'output' / 'wochenschautv_test.mp4')
            os.makedirs(ROOT_DIR / 'output', exist_ok=True)
            # Add -y (overwrite) and -t (duration limit)
            cmd.insert(1, '-y')
            cmd.extend(['-t', '15', '-f', 'mp4', test_out])
            
            log.info(f"Running FFmpeg...")
            log.info(f"Filter preview:")
            # Show the filter string for debugging
            vf_idx = cmd.index('-vf')
            if vf_idx >= 0:
                filter_str = cmd[vf_idx + 1]
                for f in filter_str.split(',drawtext'):
                    log.info(f"  {f[:100]}...")
            
            log.info(f"FFmpeg command: {' '.join(cmd[:6])} ... {cmd[-1]}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                size_mb = os.path.getsize(test_out) / 1024 / 1024
                log.info(f"Test output: {test_out} ({size_mb:.1f} MB)")
                log.info("Open the file to see the timeline HUD overlay!")
                # Try to open it
                try:
                    os.startfile(test_out)
                except Exception:
                    pass
            else:
                log.error(f"FFmpeg exit code: {result.returncode}")
                log.error(f"FFmpeg stderr (last 1000 chars):\n{result.stderr[-1000:]}")
                if result.stdout:
                    log.error(f"FFmpeg stdout: {result.stdout[-500:]}")
        else:
            log.error("No files to test with!")
    
    elif '--preview' in args:
        log.info("Preview mode: generating HUD layout image (no video files needed)...")
        # Use a sample episode from the middle of the war for interesting timeline
        sample = None
        for ep in episodes:
            if ep['number'] == 515:  # A good mid-war episode
                sample = ep
                break
        if not sample:
            sample = episodes[len(episodes) // 2]
        
        sample['_index'] = 26
        sample['_total'] = 48
        sample['_duration'] = 642  # ~10:42 typical runtime
        sample['file_path'] = 'dummy'  # Not actually used
        
        # Find a next episode for UP NEXT preview
        sample_idx = episodes.index(sample) if sample in episodes else len(episodes) // 2
        if sample_idx + 1 < len(episodes):
            sample['_next_episode'] = episodes[sample_idx + 1]
        elif episodes:
            sample['_next_episode'] = episodes[0]
        
        # Build just the filter chain
        filters = []
        ff = config['ffmpeg']
        res_w, res_h = ff['resolution'].split('x')
        filters.append(f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease")
        filters.extend(build_timeline_filters(sample, config))
        filter_str = ','.join(filters)
        
        preview_path = str(ROOT_DIR / 'output' / 'wochenschautv_preview.png')
        os.makedirs(ROOT_DIR / 'output', exist_ok=True)
        
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f"color=c=#1a1a2e:s={ff['resolution']}:d=1",
            '-vf', filter_str,
            '-frames:v', '1',
            '-update', '1',
            preview_path,
        ]
        
        log.info(f"Rendering preview frame...")
        log.info(f"Episode: Nr.{sample['number']} | {sample['date']} | {sample['event_de']}")
        log.info(f"Filter count: {len(filters)}")
        log.info(f"Full filter string:\n{filter_str}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log.info(f"Preview saved: {preview_path}")
            log.info("Open the image to see the timeline HUD layout!")
            # Try to open it
            os.startfile(preview_path)
        else:
            log.error(f"FFmpeg error:\n{result.stderr[-800:]}")
    
    elif '--prerender' in args:
        res = config['ffmpeg'].get('resolution', '1920x1080')
        log.info("=== PRE-RENDER MODE ===")
        log.info(f"Rendering all episodes with HUD baked in @ {res}")
        log.info("Uses: AV1 software decode -> H.264 NVENC encode")
        log.info("After this: use --go for lag-free streaming\n")
        
        matched, _ = scan_video_files(config, episodes)
        if matched == 0:
            log.error("No video files found!")
            return
        
        prerender_all(episodes, config)
    
    elif '--go' in args:
        log.info("=== LAG-FREE STREAM MODE ===")
        log.info("Streaming pre-rendered episodes (zero processing)")
        
        stream_key = os.environ.get('YOUTUBE_STREAM_KEY', '')
        if not stream_key:
            key_path = ROOT_DIR / 'config' / 'stream_key.txt'
            if key_path.exists():
                stream_key = key_path.read_text().strip()
        
        if not stream_key:
            log.error("No stream key! Set YOUTUBE_STREAM_KEY or create config/stream_key.txt")
            return
        
        stream_prerendered(config, stream_key)
    
    elif '--status' in args:
        scan_video_files(config, episodes)
        show_status(episodes)
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
# restored
