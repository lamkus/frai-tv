#!/usr/bin/env python3
"""
WochenschauKino — Retro Cinema Experience
==========================================
Wochenschau-Episoden mit zeitgenössischen Vorfilmen (Cartoons, Soundies)
— wie im echten Kino der 1940er Jahre.

Usage:
    python wochenschau_kino.py --epg               # Show Kino-Programm
    python wochenschau_kino.py --scan               # Scan sources, show inventory
    python wochenschau_kino.py --playlist           # Build & display full playlist
    python wochenschau_kino.py --playlist --export  # Export playlist to JSON
    python wochenschau_kino.py --preview            # Generate HUD overlay preview
    python wochenschau_kino.py --test               # Render 60s test clip
    python wochenschau_kino.py --stream             # Start 24/7 livestream
    python wochenschau_kino.py --stream --nvenc     # Stream with GPU encoding
    python wochenschau_kino.py --stream --1080p     # Stream at 1080p
"""

import json
import os
import sys
import re
import random
import fnmatch
import subprocess
import time
import signal
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict

# === PATHS ===
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'wochenschau_kino_config.json'
WS_DB_PATH = ROOT_DIR / 'config' / 'wochenschau_complete_upload_database.json'
WS_EVENTS_PATH = ROOT_DIR / 'config' / 'wochenschau_events.json'

LOG_DIR = ROOT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'wochenschau_kino.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('WochenschauKino')


# ═══════════════════════════════════════════════════════════════
#  CONFIG & STATE
# ═══════════════════════════════════════════════════════════════

def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_state(config):
    state_file = ROOT_DIR / config['system']['state_file']
    if state_file.exists():
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_episode': None,
        'last_episode_idx': 0,
        'interstitials_played': {},
        'total_items_played': 0,
        'play_history': [],
        'started_at': None,
    }


def save_state(config, state):
    state_file = ROOT_DIR / config['system']['state_file']
    state_file.parent.mkdir(parents=True, exist_ok=True)
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_stream_key(config):
    env_key = config['encoding'].get('stream_key_env', '')
    if env_key:
        key = os.environ.get(env_key, '')
        if key:
            return key
    key_file = ROOT_DIR / config['encoding'].get('stream_key_file', '')
    if key_file.exists():
        return key_file.read_text().strip()
    return None


# ═══════════════════════════════════════════════════════════════
#  WOCHENSCHAU EPISODE LOADING
# ═══════════════════════════════════════════════════════════════

def load_wochenschau_episodes():
    """Load Wochenschau episode database with event metadata."""
    episodes = []

    # Load events
    events = {}
    if WS_EVENTS_PATH.exists():
        with open(WS_EVENTS_PATH, 'r', encoding='utf-8') as f:
            ev = json.load(f)
        events = ev.get('events', {})

    # Load the full database if available
    if WS_DB_PATH.exists():
        with open(WS_DB_PATH, 'r', encoding='utf-8') as f:
            db = json.load(f)
        videos = db.get('videos', {})
        for num_str, v in sorted(videos.items(), key=lambda x: int(x[0])):
            ep = {
                'number': int(num_str),
                'number_str': num_str,
                'date': v.get('date', events.get(num_str, {}).get('date', '')),
                'year': v.get('year', 0),
                'event_de': v.get('event_de', events.get(num_str, {}).get('event_de', '')),
                'event_en': v.get('event_en', events.get(num_str, {}).get('event_en', '')),
                'note': v.get('historical_note', events.get(num_str, {}).get('note', '')),
                'expected_filename': v.get('expected_filename', ''),
                'title': v.get('title', ''),
                'file_path': None,
            }
            # Extract year from date if not set
            if not ep['year'] and ep['date']:
                try:
                    ep['year'] = int(ep['date'].split('-')[0])
                except (ValueError, IndexError):
                    pass
            episodes.append(ep)
    else:
        # Fallback: build from events only
        for num_str, ev_data in sorted(events.items(), key=lambda x: int(x[0])):
            ep_date = ev_data.get('date', '')
            ep_year = 0
            if ep_date:
                try:
                    ep_year = int(ep_date.split('-')[0])
                except (ValueError, IndexError):
                    pass
            episodes.append({
                'number': int(num_str),
                'number_str': num_str,
                'date': ep_date,
                'year': ep_year,
                'event_de': ev_data.get('event_de', ''),
                'event_en': ev_data.get('event_en', ''),
                'note': ev_data.get('note', ''),
                'expected_filename': '',
                'title': '',
                'file_path': None,
            })

    log.info(f"Loaded {len(episodes)} Wochenschau episodes "
             f"(Nr.{episodes[0]['number']}–{episodes[-1]['number']}, "
             f"{episodes[0]['date']}–{episodes[-1]['date']})" if episodes else "No episodes loaded!")

    return episodes


# ═══════════════════════════════════════════════════════════════
#  CONTENT SCANNING
# ═══════════════════════════════════════════════════════════════

def scan_all_sources(config):
    """Scan all configured source directories for video files."""
    sources = config.get('content_sources', {})
    all_dirs = []
    for key in ['primary', 'fallback', 'wochenschau', 'commercials']:
        all_dirs.extend(d for d in sources.get(key, []) if os.path.isdir(d))

    # Also scan source_dirs from individual era_pools (e.g. vintage_commercials)
    for pool in config.get('era_pools', []):
        for d in pool.get('source_dirs', []):
            if os.path.isdir(d) and d not in all_dirs:
                all_dirs.append(d)

    extensions = set(sources.get('file_extensions', ['.mp4', '.mkv', '.avi', '.mov']))
    file_index = {}

    for src_dir in all_dirs:
        log.info(f"Scanning: {src_dir}")
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if any(f.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, f)
                    file_index[f.lower()] = full_path

    log.info(f"Total video files found: {len(file_index)}")
    return file_index


def match_wochenschau_files(episodes, file_index):
    """Match Wochenschau episodes to actual video files."""
    matched = 0
    for ep in episodes:
        # Try expected filename first
        if ep['expected_filename']:
            fname = ep['expected_filename'].lower()
            if fname in file_index:
                ep['file_path'] = file_index[fname]
                matched += 1
                continue

        # Try pattern matching: *wochenschau*{number}*
        num = ep['number']
        for fname, fpath in file_index.items():
            if 'wochenschau' in fname and str(num) in fname:
                ep['file_path'] = fpath
                matched += 1
                break

    log.info(f"Wochenschau files matched: {matched}/{len(episodes)}")
    return episodes


def match_interstitial_files(config, file_index):
    """
    Match video files to era pools (interstitial content).
    Returns dict: { pool_id: [{ file, label, year_est, type }, ...] }
    """
    era_pools = config.get('era_pools', [])
    pool_files = {}

    # Files already assigned (avoid duplicates across pools)
    assigned = set()

    for pool in era_pools:
        pool_id = pool['id']
        patterns = pool.get('source_patterns', [])
        exclude = pool.get('exclude_patterns', [])
        matched = []

        for fname, fpath in file_index.items():
            # Skip if already assigned to another pool
            if fpath in assigned:
                continue

            # Skip Wochenschau files
            if 'wochenschau' in fname:
                continue

            # Check exclude patterns
            excluded = any(fnmatch.fnmatch(fname, p.lower()) for p in exclude)
            if excluded:
                continue

            # Check match patterns
            for pattern in patterns:
                if fnmatch.fnmatch(fname, pattern.lower()):
                    # Estimate year from filename
                    year_est = _extract_year_from_filename(fname)
                    if not year_est:
                        # Use pool midpoint
                        year_est = (pool['year_start'] + pool['year_end']) // 2

                    # Apply year filters if configured
                    year_min = pool.get('year_filter_min', 0)
                    year_max = pool.get('year_filter_max', 9999)
                    if year_min and year_est < year_min:
                        continue
                    if year_max and year_est > year_max:
                        continue

                    matched.append({
                        'file': fpath,
                        'filename': fname,
                        'label': pool['label'],
                        'pool_id': pool_id,
                        'type': pool.get('type', 'unknown'),
                        'year_est': year_est,
                        'avg_duration_min': pool.get('avg_duration_min', 7),
                        'priority_boost': pool.get('priority_boost', 0),
                    })
                    assigned.add(fpath)
                    break

        if matched:
            pool_files[pool_id] = matched
            log.info(f"  Pool '{pool['label']}': {len(matched)} files "
                     f"({pool['year_start']}–{pool['year_end']})")

    total = sum(len(v) for v in pool_files.values())
    log.info(f"Total interstitial files: {total} across {len(pool_files)} pools")
    return pool_files


def _extract_year_from_filename(filename):
    """Try to extract a production year from a filename."""
    # Common patterns: (1932), _1932_, -1932-
    m = re.search(r'[\(\[_\-\s](1[89]\d{2})[\)\]_\-\s]', filename)
    if m:
        year = int(m.group(1))
        if 1890 <= year <= 1970:
            return year
    # Also try plain 4-digit year
    m = re.search(r'(19[0-5]\d)', filename)
    if m:
        return int(m.group(1))
    return None


# ═══════════════════════════════════════════════════════════════
#  ERA-MATCHING ALGORITHM
# ═══════════════════════════════════════════════════════════════

def score_interstitial(interstitial, wochenschau_year, config, recent_pools):
    """
    Score an interstitial's fit for a specific Wochenschau episode year.
    Higher score = better match.
    """
    rules = config['matching']['rules']
    pool_id = interstitial['pool_id']
    year = interstitial['year_est']
    year_diff = abs(year - wochenschau_year)

    # Distance penalty
    if year_diff == 0:
        score = rules.get('exact_year_weight', 10)
    elif year_diff <= 2:
        score = rules.get('adjacent_year_weight', 7)
    elif year_diff <= 5:
        score = rules.get('same_decade_weight', 4)
    elif year_diff <= rules.get('max_year_distance', 15):
        score = rules.get('any_era_weight', 1)
    else:
        return -1  # Too far away, don't use

    # Priority boost (Superman, Soundies get bonus)
    score += interstitial.get('priority_boost', 0)

    # Variety bonus: penalize if same pool was used recently
    if pool_id in recent_pools:
        times_recent = recent_pools[pool_id]
        score -= rules.get('category_repeat_penalty', 5) * times_recent
    else:
        score += rules.get('variety_bonus', 3)

    # Preferred types for this year
    preferred = config['matching'].get('preferred_types_by_era', {}).get(
        str(wochenschau_year), [])
    if pool_id in preferred:
        idx = preferred.index(pool_id)
        score += max(0, 5 - idx)  # First preferred = +5, second = +4, etc.

    # Small random factor to avoid too predictable sequences
    score += random.uniform(0, 1.5)

    return score


def select_interstitials(wochenschau_ep, pool_files, config, state):
    """
    Select era-matched interstitials for a Wochenschau episode.
    Returns list of interstitial items to play before/around the episode.
    """
    ws_year = wochenschau_ep.get('year', 1940)
    rules = config['matching']
    per_ep = rules.get('per_episode_interstitials', {})
    num_interstitials = per_ep.get('default', 2)

    # Build recent-pool tracking AND recent-file tracking
    recent_pools = defaultdict(int)
    recent_files = set()
    # Short window (8 entries = ~4 recent blocks) to allow pool re-use
    history_window = state.get('play_history', [])[-8:]
    for entry in history_window:
        if entry.get('type') == 'interstitial':
            pid = entry.get('pool_id', '')
            if pid:
                recent_pools[pid] += 1
            fname = entry.get('file', '')
            if fname:
                recent_files.add(fname)

    # Flatten all interstitials
    all_interstitials = []
    for pool_id, items in pool_files.items():
        all_interstitials.extend(items)

    if not all_interstitials:
        return []

    # Score each interstitial, with file-level repeat penalty
    scored = []
    for item in all_interstitials:
        s = score_interstitial(item, ws_year, config, recent_pools)
        if s <= 0:
            continue
        # Moderate penalty for recently-played FILES (not just pools)
        # With 454 interstitials and ~290 needed, allow some repeats
        item_fname = Path(item['file']).name
        if item_fname in recent_files:
            s -= 8  # File-repeat penalty (enough to prefer other files)
        scored.append((s, item))

    scored.sort(key=lambda x: -x[0])

    # Soundie constraint: ensure at least one Soundie if available
    min_soundie_prob = rules.get('rules', {}).get('soundie_min_probability', 0.4)
    soundie_items = [x for x in scored if x[1]['type'] == 'musical']
    cartoon_items = [x for x in scored if x[1]['type'] in ('cartoon', 'propaganda_cartoon')]

    selected = []
    used_files = set()

    if num_interstitials >= 2 and soundie_items:
        # Standard format: Soundie + Cartoon (or 2 Soundies)
        # First slot: Soundie (musical opener, like in real 1940s cinema)
        selected.append(soundie_items[0][1])
        used_files.add(soundie_items[0][1]['file'])
        recent_pools[soundie_items[0][1]['pool_id']] += 1

        # Second slot: prefer a cartoon for variety (exclude already selected)
        remaining = [x for x in scored
                     if x[1]['file'] not in used_files]
        # Try cartoon first
        cartoons_remaining = [x for x in remaining if x[1]['type'] != 'musical']
        if cartoons_remaining:
            selected.append(cartoons_remaining[0][1])
            used_files.add(cartoons_remaining[0][1]['file'])
        elif remaining:
            selected.append(remaining[0][1])
            used_files.add(remaining[0][1]['file'])

    elif num_interstitials >= 1 and scored:
        # Just pick the best match
        selected.append(scored[0][1])
        used_files.add(scored[0][1]['file'])

    # If 3 interstitials requested and available
    if num_interstitials >= 3 and len(scored) > len(selected):
        remaining = [x for x in scored
                     if x[1]['file'] not in used_files]
        if remaining:
            selected.append(remaining[0][1])

    return selected


# ═══════════════════════════════════════════════════════════════
#  KINO PLAYLIST BUILDER
# ═══════════════════════════════════════════════════════════════

def build_kino_playlist(episodes, pool_files, config, state):
    """
    Build the full Kino playlist: interstitials interleaved with Wochenschau.

    Format per episode-block:
      [Soundie/Cartoon]  →  [WOCHENSCHAU]  →  [Cartoon/Soundie]
    """
    available_eps = [ep for ep in episodes if ep.get('file_path')]

    if not available_eps:
        log.error("No Wochenschau files available!")
        return []

    playlist = []
    format_key = config.get('program_format', {}).get('active_format', 'standard')
    format_def = config.get('program_format', {}).get(format_key, {})
    sequence = format_def.get('sequence', ['soundie_or_cartoon', 'wochenschau'])

    log.info(f"\nBuilding Kino playlist: {len(available_eps)} episodes, "
             f"format='{format_key}'")

    for i, ep in enumerate(available_eps):
        ws_year = ep.get('year', 1940)
        event = ep.get('event_en', ep.get('event_de', ''))

        # Select interstitials for this episode
        interstitials = select_interstitials(ep, pool_files, config, state)

        # Build block according to sequence format
        block_items = []

        if len(sequence) >= 3 and len(interstitials) >= 2:
            # Standard: [interstitial] [wochenschau] [interstitial]
            pre = interstitials[0]
            post = interstitials[1] if len(interstitials) > 1 else interstitials[0]

            block_items.append({
                'type': 'interstitial',
                'role': 'vorfilm',
                'file': pre['file'],
                'label': pre['label'],
                'pool_id': pre['pool_id'],
                'content_type': pre['type'],
                'year_est': pre['year_est'],
                'wochenschau_year': ws_year,
                'episode_number': ep['number'],
            })

            block_items.append({
                'type': 'wochenschau',
                'role': 'hauptfilm',
                'file': ep['file_path'],
                'label': f"Wochenschau Nr. {ep['number']}",
                'number': ep['number'],
                'date': ep['date'],
                'year': ws_year,
                'event_de': ep.get('event_de', ''),
                'event_en': event,
                'note': ep.get('note', ''),
                'episode_index': i + 1,
                'total_episodes': len(available_eps),
            })

            block_items.append({
                'type': 'interstitial',
                'role': 'nachfilm',
                'file': post['file'],
                'label': post['label'],
                'pool_id': post['pool_id'],
                'content_type': post['type'],
                'year_est': post['year_est'],
                'wochenschau_year': ws_year,
                'episode_number': ep['number'],
            })

        elif len(interstitials) >= 1:
            # Minimal: [interstitial] [wochenschau]
            pre = interstitials[0]
            block_items.append({
                'type': 'interstitial',
                'role': 'vorfilm',
                'file': pre['file'],
                'label': pre['label'],
                'pool_id': pre['pool_id'],
                'content_type': pre['type'],
                'year_est': pre['year_est'],
                'wochenschau_year': ws_year,
                'episode_number': ep['number'],
            })
            block_items.append({
                'type': 'wochenschau',
                'role': 'hauptfilm',
                'file': ep['file_path'],
                'label': f"Wochenschau Nr. {ep['number']}",
                'number': ep['number'],
                'date': ep['date'],
                'year': ws_year,
                'event_de': ep.get('event_de', ''),
                'event_en': event,
                'note': ep.get('note', ''),
                'episode_index': i + 1,
                'total_episodes': len(available_eps),
            })

        else:
            # No interstitials available — just Wochenschau
            block_items.append({
                'type': 'wochenschau',
                'role': 'hauptfilm',
                'file': ep['file_path'],
                'label': f"Wochenschau Nr. {ep['number']}",
                'number': ep['number'],
                'date': ep['date'],
                'year': ws_year,
                'event_de': ep.get('event_de', ''),
                'event_en': event,
                'note': ep.get('note', ''),
                'episode_index': i + 1,
                'total_episodes': len(available_eps),
            })

        playlist.extend(block_items)

        # Update state for variety tracking
        for item in block_items:
            if item['type'] == 'interstitial':
                state['play_history'].append({
                    'type': 'interstitial',
                    'pool_id': item.get('pool_id', ''),
                    'file': Path(item['file']).name,
                })

    # Stats
    ws_count = sum(1 for p in playlist if p['type'] == 'wochenschau')
    int_count = sum(1 for p in playlist if p['type'] == 'interstitial')
    log.info(f"Kino playlist built: {len(playlist)} total items "
             f"({ws_count} Wochenschau + {int_count} interstitials)")

    return playlist


# ═══════════════════════════════════════════════════════════════
#  EPG / PROGRAM VIEW
# ═══════════════════════════════════════════════════════════════

def print_kino_epg(episodes, pool_files, config, state, limit=20):
    """Print the Kino-Programm (cinema schedule)."""
    playlist = build_kino_playlist(episodes, pool_files, config, state)

    if not playlist:
        print("[ERROR] No playlist could be built. Check video sources.")
        return

    ws_count = sum(1 for p in playlist if p['type'] == 'wochenschau')
    int_count = sum(1 for p in playlist if p['type'] == 'interstitial')

    # Interstitial type breakdown
    type_counts = defaultdict(int)
    pool_counts = defaultdict(int)
    for p in playlist:
        if p['type'] == 'interstitial':
            type_counts[p.get('content_type', '?')] += 1
            pool_counts[p.get('label', '?')] += 1

    print(f"\n{'=' * 70}")
    print(f"  [KINO]  WochenschauKino -- Programm")
    print(f"{'=' * 70}")
    print(f"  Wochenschau-Episoden: {ws_count}")
    print(f"  Vorfilme/Nachfilme:   {int_count}")
    print(f"  Gesamt:               {len(playlist)} Items")
    print()

    # Type breakdown
    print(f"  Interstitial-Mix:")
    for label, count in sorted(pool_counts.items(), key=lambda x: -x[1]):
        bar = '#' * min(count, 40)
        print(f"    {label:30s} {count:3d} {bar}")

    # Show first N blocks
    print(f"\n{'-' * 70}")
    print(f"  [EPG] Programm (erste {limit} Blocks):")
    print(f"{'-' * 70}")

    block_num = 0
    current_ep = None

    for i, item in enumerate(playlist):
        if i >= limit * 3:  # ~3 items per block
            print(f"\n  ... und {len(playlist) - i} weitere Items")
            break

        if item['type'] == 'wochenschau':
            block_num += 1
            ep_num = item.get('number', '?')
            ep_date = item.get('date', '?')
            event = item.get('event_en', item.get('event_de', ''))
            idx = item.get('episode_index', '?')
            total = item.get('total_episodes', '?')

            print(f"\n  +-- Block {block_num} {'- ' * 20}")
            print(f"  |  >> WOCHENSCHAU Nr. {ep_num}  ({ep_date})")
            print(f"  |     {event}")
            print(f"  |     [{idx}/{total}]")

        elif item['type'] == 'interstitial':
            role = item.get('role', 'vorfilm')
            label = item.get('label', '?')
            year = item.get('year_est', '?')
            ws_year = item.get('wochenschau_year', '?')
            ctype = item.get('content_type', '?')
            fname = Path(item['file']).stem[:45]
            if ctype == 'commercial':
                role_icon = '[AD]'
                role_label = 'WERBUNG'
            elif ctype == 'musical':
                role_icon = '[MUSIC]'
                role_label = 'VORFILM' if role == 'vorfilm' else 'NACHFILM'
            else:
                role_icon = '[FILM]'
                role_label = 'VORFILM' if role == 'vorfilm' else 'NACHFILM'

            print(f"  |  {role_icon} {role_label}: {label} ({year}) -- {fname}")

    print(f"  +{'-' * 68}")
    print(f"{'=' * 70}\n")


def print_era_inventory(pool_files, episodes):
    """Print interstitial inventory organized by era/Wochenschau year."""
    available_eps = [ep for ep in episodes if ep.get('file_path')]

    print(f"\n{'=' * 70}")
    print(f"  [INVENTORY] Era-Match Inventory")
    print(f"{'=' * 70}")

    # Build year-to-content-pool coverage
    ws_years = sorted(set(ep['year'] for ep in available_eps if ep.get('year')))

    print(f"\n  Wochenschau years: {ws_years[0]}-{ws_years[-1]}" if ws_years else "")
    print(f"  Episodes with files: {len(available_eps)}")

    print(f"\n  {'Year':>6} {'Wochenschau':>12} {'Matching Interstitials':>25}")
    print(f"  {'-' * 50}")

    for year in range(1939, 1946):
        ws_in_year = sum(1 for ep in available_eps if ep.get('year') == year)

        # Count matching interstitials (within ±3 years)
        matching = 0
        pool_matches = defaultdict(int)
        for pool_id, items in pool_files.items():
            for item in items:
                if abs(item['year_est'] - year) <= 3:
                    matching += 1
                    pool_matches[item['label']] += 1

        bar = '#' * min(matching, 30)
        print(f"  {year:>6} {ws_in_year:>4} episodes  -> {matching:>3} interstitials {bar}")
        for label, count in sorted(pool_matches.items(), key=lambda x: -x[1]):
            print(f"         {'':>16} {label}: {count}")

    print(f"{'=' * 70}\n")


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — OVERLAY FILTERS
# ═══════════════════════════════════════════════════════════════

def _esc(text):
    """Escape text for FFmpeg drawtext filter."""
    if not text:
        return ''
    return text.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:").replace("%", "%%")


def _clean_display_name(filename):
    """Clean up a raw filename for on-screen display."""
    name = filename
    for suffix in ['_8K_HQ', '_8K', '_4K', '_sls', '_ARCHIVE', '_BLURRED',
                   '_PROTECTED', 'sls', 'HQ', 'ARCHIVE', '_xvid']:
        name = name.replace(suffix, '')
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.title()
    if len(name) > 50:
        name = name[:47] + '...'
    return name


def _calc_war_progress(ep_date):
    """Calculate war timeline progress (0.0–1.0)."""
    try:
        parts = ep_date.split('-')
        ep_d = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return 0.5
    start = date(1939, 6, 1)
    end = date(1945, 3, 1)
    total_days = (end - start).days
    current = (ep_d - start).days
    return max(0.0, min(1.0, current / total_days))


def build_kino_overlay(config, item, resolution):
    """Build FFmpeg overlay filters for the Kino experience."""
    ov = config.get('overlay', {})
    filters = []
    out_w, out_h = [int(x) for x in resolution.split('x')]
    scale = out_h / 1080

    def px(val):
        return max(1, int(val * scale))

    is_wochenschau = item.get('type') == 'wochenschau'
    is_interstitial = item.get('type') == 'interstitial'

    # === STATION BUG (top-right) ===
    bug = ov.get('station_bug', {})
    if bug.get('enabled'):
        filters.append(
            f"drawtext=text='{_esc(bug.get('text', 'WochenschauKino'))}'"
            f":fontsize={px(bug.get('font_size', 24))}"
            f":fontcolor={bug.get('font_color', 'white@0.5')}"
            f":x=w-tw-{px(20)}:y={px(20)}"
            f":font='Arial'"
        )

    # === WOCHENSCHAU DISCLAIMER (persistent during newsreel) ===
    if is_wochenschau:
        disc = ov.get('wochenschau_disclaimer', {})
        if disc.get('enabled'):
            filters.append(
                f"drawtext=text='{_esc(disc.get('text', 'HISTORICAL DOCUMENT'))}'"
                f":fontsize={px(disc.get('font_size', 16))}"
                f":fontcolor={disc.get('font_color', '#CCCCCC')}"
                f":x={px(10)}:y={px(10)}"
                f":font='Arial'"
            )

    # === BOTTOM BAR ===
    bar = ov.get('kino_bottom_bar', {})
    if bar.get('enabled'):
        bar_h = px(bar.get('height', 44))
        opacity = bar.get('opacity', 0.7)

        # Bar background
        filters.append(
            f"drawbox=x=0:y=ih-{bar_h}:w=iw:h={bar_h}"
            f":color=black@{opacity}:t=fill"
        )

        text_y = bar_h - px(12) - px(bar.get('font_size_title', 18)) // 2

        if is_wochenschau:
            # Wochenschau info bar
            ep_num = item.get('number', '?')
            ep_date = item.get('date', '')
            event = item.get('event_en', item.get('event_de', ''))
            idx = item.get('episode_index', 0)
            total = item.get('total_episodes', 0)

            # Format date nicely
            try:
                d = datetime.strptime(ep_date, '%Y-%m-%d')
                date_str = d.strftime('%b %d, %Y')
            except (ValueError, TypeError):
                date_str = ep_date

            info = f"📰 Wochenschau Nr. {ep_num}  ·  {date_str}  ·  {event}  ·  [{idx}/{total}]"
            filters.append(
                f"drawtext=text='{_esc(info)}'"
                f":fontsize={px(bar.get('font_size_title', 18))}"
                f":fontcolor={bar.get('font_color', '#FFFFFF')}"
                f":x={px(16)}:y=h-{text_y}"
                f":font='Arial'"
            )

            # War progress mini-bar (right side, above clock)
            progress = _calc_war_progress(ep_date)
            prog_w = px(120)
            prog_h = px(4)
            prog_x = out_w - prog_w - px(16)
            prog_y = bar_h - px(8)
            filters.append(
                f"drawbox=x={prog_x}:y=ih-{prog_y}:w={prog_w}:h={prog_h}"
                f":color=#333333@0.8:t=fill"
            )
            filled = max(2, int(prog_w * progress))
            filters.append(
                f"drawbox=x={prog_x}:y=ih-{prog_y}:w={filled}:h={prog_h}"
                f":color=#CC3333@0.9:t=fill"
            )

        elif is_interstitial:
            # Interstitial info bar
            role = item.get('role', 'vorfilm')
            label = item.get('label', '')
            year = item.get('year_est', '')
            ws_year = item.get('wochenschau_year', '')
            ctype = item.get('content_type', '')

            if ctype == 'commercial':
                role_label = 'WERBUNG'
                info = f"WERBUNG  .  {label} ({year})"
            elif ctype == 'musical':
                role_label = 'VORFILM' if role == 'vorfilm' else 'NACHFILM'
                info = f"VORFILM  .  {label} ({year})  .  Era {ws_year}"
            else:
                role_label = 'VORFILM' if role == 'vorfilm' else 'NACHFILM'
                info = f"{role_label}  .  {label} ({year})  .  Era {ws_year}"

            filters.append(
                f"drawtext=text='{_esc(info)}'"
                f":fontsize={px(bar.get('font_size_title', 18))}"
                f":fontcolor={bar.get('font_color', '#FFFFFF')}"
                f":x={px(16)}:y=h-{text_y}"
                f":font='Arial'"
            )

        # Clock (always, right side)
        if bar.get('show_clock'):
            clock_y = text_y + px(4) if is_wochenschau else text_y
            filters.append(
                f"drawtext=text='%{{localtime\\:%H\\\\:%M}}'"
                f":fontsize={px(bar.get('font_size_meta', 14))}"
                f":fontcolor={bar.get('meta_color', '#AAAAAA')}"
                f":x=w-tw-{px(16)}:y=h-{clock_y}"
                f":font='Arial'"
            )

    return filters


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — TRANSITION SCREENS
# ═══════════════════════════════════════════════════════════════

def generate_transition_screen(config, current_item, next_item, output_path,
                               resolution='3840x2160'):
    """
    Generate a short transition card between Kino segments.
    Shows what's coming next (like a cinema 'Jetzt kommt...' slide).
    """
    ov = config.get('overlay', {}).get('transition_screen', {})
    if not ov.get('enabled'):
        return None

    duration = ov.get('duration_seconds', 5)
    out_w, out_h = [int(x) for x in resolution.split('x')]
    scale = out_h / 1080

    def px(val):
        return max(1, int(val * scale))

    filters = []

    # What's next?
    if next_item['type'] == 'wochenschau':
        next_type = '📰 WOCHENSCHAU'
        next_title = f"Nr. {next_item.get('number', '?')}"
        next_detail = f"{next_item.get('date', '')}  ·  {next_item.get('event_en', '')}"
    else:
        ctype = next_item.get('content_type', '')
        emoji = '🎵' if ctype == 'musical' else '🎨'
        next_type = f"{emoji} {next_item.get('label', 'Vorfilm')}"
        next_title = _clean_display_name(Path(next_item['file']).stem)
        next_detail = f"({next_item.get('year_est', '?')})"

    # "Und jetzt..." header
    filters.append(
        f"drawtext=text='{_esc('📽️ Und jetzt...')}'"
        f":fontsize={px(24)}:fontcolor=#888888"
        f":x=(w-tw)/2:y=h/3-{px(30)}"
        f":font='Arial'"
    )

    # Next type
    filters.append(
        f"drawtext=text='{_esc(next_type)}'"
        f":fontsize={px(36)}:fontcolor=#FFFFFF"
        f":x=(w-tw)/2:y=h/3+{px(20)}"
        f":font='Arial Bold'"
    )

    # Next title
    filters.append(
        f"drawtext=text='{_esc(next_title)}'"
        f":fontsize={px(28)}:fontcolor=#CCCCCC"
        f":x=(w-tw)/2:y=h/3+{px(70)}"
        f":font='Arial'"
    )

    # Detail
    filters.append(
        f"drawtext=text='{_esc(next_detail)}'"
        f":fontsize={px(18)}:fontcolor=#888888"
        f":x=(w-tw)/2:y=h/3+{px(110)}"
        f":font='Arial'"
    )

    # Station name at bottom
    filters.append(
        f"drawtext=text='{_esc('WochenschauKino · remAIke TV')}'"
        f":fontsize={px(14)}:fontcolor=#444444"
        f":x=(w-tw)/2:y=h-{px(40)}"
        f":font='Arial'"
    )

    filter_str = ','.join(filters)
    bg_color = ov.get('bg_color', '#0a0a14')

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f"color=c={bg_color}:s={resolution}:d={duration}:r=25",
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-vf', filter_str,
        '-c:v', 'libx264', '-preset', 'ultrafast',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return str(output_path)
    else:
        log.warning(f"Transition screen failed: {result.stderr[-300:]}")
        return None


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — STREAMING ENGINE
# ═══════════════════════════════════════════════════════════════

def build_stream_command(input_file, config, item, stream_key,
                         use_nvenc=False, resolution=None):
    """Build FFmpeg command to stream a single segment with Kino overlay."""
    enc = config['encoding']
    res = resolution or enc['resolution']
    res_w, res_h = res.split('x')

    if use_nvenc:
        vcodec = enc['codec_gpu']
        preset = enc['preset_gpu']
    else:
        vcodec = enc['codec_cpu']
        preset = enc['preset_cpu']

    filters = [
        f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease",
        f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={enc['fps']}",
    ]
    filters.extend(build_kino_overlay(config, item, res))
    filter_str = ','.join(filters)

    rtmp_url = f"{enc['rtmp_url']}/{stream_key}"

    cmd = [
        'ffmpeg',
        '-re',
        '-i', input_file,
        '-vf', filter_str,
        '-c:v', vcodec,
        '-preset', preset,
        '-b:v', enc['video_bitrate'],
        '-maxrate', enc['video_bitrate'],
        '-bufsize', enc['bufsize'],
        '-pix_fmt', enc['pixel_format'],
        '-g', str(enc['max_keyframe_interval']),
        '-c:a', enc.get('codec_audio', 'aac'),
        '-b:a', enc['audio_bitrate'],
        '-ar', str(enc['audio_sample_rate']),
        '-f', 'flv',
        rtmp_url,
    ]

    return cmd


def stream_kino(playlist, config, stream_key, use_nvenc=False, resolution=None):
    """
    Main Kino streaming loop.
    Streams the built playlist 24/7 with transitions between segments.
    """
    state = load_state(config)
    state['started_at'] = datetime.now().isoformat()

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        log.info("Received shutdown signal. Finishing current segment...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    res = resolution or config['encoding']['resolution']
    transition_dir = ROOT_DIR / 'output' / 'kino_transitions'
    transition_dir.mkdir(parents=True, exist_ok=True)

    # Resume from last position
    start_idx = state.get('last_playlist_idx', 0)
    if start_idx >= len(playlist):
        start_idx = 0

    loop_count = 0

    ws_total = sum(1 for p in playlist if p['type'] == 'wochenschau')
    int_total = sum(1 for p in playlist if p['type'] == 'interstitial')

    log.info("=" * 66)
    log.info("  📽️  WochenschauKino — Starting Livestream")
    log.info(f"  Resolution: {res}")
    log.info(f"  Encoder: {'NVENC (GPU)' if use_nvenc else 'libx264 (CPU)'}")
    log.info(f"  Playlist: {len(playlist)} items "
             f"({ws_total} Wochenschau + {int_total} interstitials)")
    if start_idx > 0:
        log.info(f"  Resuming from position {start_idx}")
    log.info("=" * 66)

    while running:
        loop_count += 1
        log.info(f"\n{'━' * 50}")
        log.info(f"  LOOP {loop_count} — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        log.info(f"{'━' * 50}")

        for idx in range(start_idx, len(playlist)):
            if not running:
                break

            item = playlist[idx]
            video_file = item['file']

            if not os.path.exists(video_file):
                log.warning(f"File not found, skipping: {video_file}")
                continue

            # === TRANSITION SCREEN ===
            if idx > 0 and config.get('schedule', {}).get('transition_screen_between'):
                next_item = item
                trans_path = transition_dir / f"trans_{idx}.mp4"
                trans_file = generate_transition_screen(
                    config, playlist[idx - 1], next_item, trans_path, res
                )
                if trans_file and os.path.exists(trans_file):
                    trans_item = {
                        'type': 'transition',
                        'file': trans_file,
                    }
                    trans_cmd = build_stream_command(
                        trans_file, config, trans_item, stream_key,
                        use_nvenc, res
                    )
                    try:
                        subprocess.run(trans_cmd, capture_output=True, timeout=15)
                    except Exception:
                        pass

            # === STREAM SEGMENT ===
            type_emoji = '📰' if item['type'] == 'wochenschau' else '🎵' if item.get('content_type') == 'musical' else '🎨'
            display_name = _clean_display_name(Path(video_file).stem)

            log.info(f"\n  {type_emoji} [{idx + 1}/{len(playlist)}] "
                     f"{item.get('label', '?')}: {display_name}")

            if item['type'] == 'wochenschau':
                log.info(f"     Nr. {item.get('number')} | {item.get('date')} | "
                         f"{item.get('event_en', '')}")

            cmd = build_stream_command(
                video_file, config, item, stream_key, use_nvenc, res
            )

            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    stderr_text = stderr.decode('utf-8', errors='replace')[-500:]
                    log.warning(f"FFmpeg code {process.returncode}: {stderr_text}")
                    time.sleep(config['system'].get('restart_delay_seconds', 30))
                else:
                    log.info(f"  ✓ Done: {display_name}")

            except Exception as e:
                log.error(f"Error: {e}")
                time.sleep(config['system'].get('restart_delay_seconds', 30))

            # Update state
            state['last_playlist_idx'] = idx + 1
            state['total_items_played'] = state.get('total_items_played', 0) + 1
            state['play_history'].append({
                'time': datetime.now().isoformat(),
                'type': item['type'],
                'pool_id': item.get('pool_id', ''),
                'file': Path(video_file).name,
                'label': item.get('label', ''),
            })
            if len(state['play_history']) > 500:
                state['play_history'] = state['play_history'][-200:]
            save_state(config, state)

            # Pause between items
            pause = config.get('schedule', {}).get('pause_between_items_seconds', 2)
            time.sleep(pause)

        # Loop completed — reset to beginning
        start_idx = 0
        state['last_playlist_idx'] = 0
        save_state(config, state)
        log.info("\n📽️ Full program completed! Restarting from beginning...")

    log.info("\n📽️ WochenschauKino — Stream stopped gracefully.")
    save_state(config, state)


# ═══════════════════════════════════════════════════════════════
#  PREVIEW & TEST
# ═══════════════════════════════════════════════════════════════

def generate_preview(config, playlist):
    """Generate HUD overlay preview images for both Wochenschau and interstitial."""
    res = config['encoding']['resolution']
    out_w, out_h = res.split('x')
    output_dir = ROOT_DIR / 'output'
    output_dir.mkdir(exist_ok=True)

    # Find one of each type
    ws_item = next((p for p in playlist if p['type'] == 'wochenschau'), None)
    int_item = next((p for p in playlist if p['type'] == 'interstitial'), None)

    for item, name in [(ws_item, 'wochenschau'), (int_item, 'interstitial')]:
        if not item:
            continue

        filters = [f"scale={out_w}:{out_h}"]
        filters.extend(build_kino_overlay(config, item, res))
        filter_str = ','.join(filters)

        preview_path = str(output_dir / f'wochenschau_kino_preview_{name}.png')

        # Use SMPTE bars background for visibility
        cmd = [
            'ffmpeg', '-y',
            '-f', 'lavfi',
            '-i', f"smptebars=s={res}:d=1",
            '-vf', filter_str,
            '-frames:v', '1',
            '-update', '1',
            preview_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            log.info(f"Preview ({name}): {preview_path}")
            try:
                os.startfile(preview_path)
            except Exception:
                pass
        else:
            log.error(f"Preview failed ({name}): {result.stderr[-300:]}")


def test_render(config, playlist, use_nvenc=False, resolution=None):
    """Render a 60s test clip from the first block (Soundie + Wochenschau start)."""
    if not playlist:
        log.error("No playlist to test!")
        return

    res = resolution or config['encoding']['resolution']
    res_w, res_h = res.split('x')
    enc = config['encoding']
    vcodec = enc['codec_gpu'] if use_nvenc else enc['codec_cpu']
    preset = enc['preset_gpu'] if use_nvenc else enc['preset_cpu']

    test_out = str(ROOT_DIR / 'output' / 'wochenschau_kino_test.mp4')
    os.makedirs(ROOT_DIR / 'output', exist_ok=True)

    # Test with first item that has a real file
    for item in playlist:
        if os.path.exists(item.get('file', '')):
            break
    else:
        log.error("No playable files found in playlist!")
        return

    log.info(f"Test render: {item.get('label')} ({item['type']})")
    log.info(f"File: {item['file']}")

    filters = [
        f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease",
        f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={enc['fps']}",
    ]
    filters.extend(build_kino_overlay(config, item, res))
    filter_str = ','.join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-i', item['file'],
        '-vf', filter_str,
        '-c:v', vcodec, '-preset', preset,
        '-b:v', enc['video_bitrate'],
        '-pix_fmt', enc['pixel_format'],
        '-c:a', 'aac', '-b:a', enc['audio_bitrate'],
        '-t', '60',
        '-f', 'mp4',
        test_out,
    ]

    log.info("Rendering 60s test clip...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        log.info(f"✓ Test output: {test_out}")
        try:
            os.startfile(test_out)
        except Exception:
            pass
    else:
        log.error(f"Test failed: {result.stderr[-500:]}")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    config = load_config()
    state = load_state(config)

    resolution = None
    if '--1080p' in args:
        resolution = '1920x1080'
    elif '--720p' in args:
        resolution = '1280x720'

    use_nvenc = '--nvenc' in args

    # Load Wochenschau episodes
    log.info("Loading Wochenschau episodes...")
    episodes = load_wochenschau_episodes()

    if '--scan' in args:
        log.info("\nScanning content sources...")
        file_index = scan_all_sources(config)

        # Match Wochenschau files
        episodes = match_wochenschau_files(episodes, file_index)
        available = sum(1 for ep in episodes if ep.get('file_path'))

        # Match interstitial files
        log.info("\nMatching interstitial pools...")
        pool_files = match_interstitial_files(config, file_index)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"  [SCAN] WochenschauKino -- Scan Results")
        print(f"{'=' * 60}")
        print(f"  Video files found:       {len(file_index)}")
        print(f"  Wochenschau available:   {available}/{len(episodes)}")
        total_int = sum(len(v) for v in pool_files.values())
        print(f"  Interstitial content:    {total_int}")
        print()
        for pool_id, items in sorted(pool_files.items(), key=lambda x: -len(x[1])):
            years = [i['year_est'] for i in items]
            yr_range = f"{min(years)}-{max(years)}" if years else "?"
            print(f"    {items[0]['label']:30s} {len(items):3d} files  ({yr_range})")
        print(f"{'=' * 60}\n")

        # Show era inventory
        print_era_inventory(pool_files, episodes)

    elif '--epg' in args or '--playlist' in args:
        file_index = scan_all_sources(config)
        episodes = match_wochenschau_files(episodes, file_index)
        pool_files = match_interstitial_files(config, file_index)

        if '--export' in args:
            playlist = build_kino_playlist(episodes, pool_files, config, state)
            export_path = ROOT_DIR / 'output' / 'wochenschau_kino_playlist.json'
            os.makedirs(ROOT_DIR / 'output', exist_ok=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(playlist, f, indent=2, ensure_ascii=False)
            log.info(f"Playlist exported: {export_path}")
        else:
            limit = 30 if '--playlist' in args else 15
            # print_kino_epg builds its own playlist, so don't build here
            print_kino_epg(episodes, pool_files, config, state, limit=limit)

    elif '--preview' in args:
        file_index = scan_all_sources(config)
        episodes = match_wochenschau_files(episodes, file_index)
        pool_files = match_interstitial_files(config, file_index)
        playlist = build_kino_playlist(episodes, pool_files, config, state)
        generate_preview(config, playlist)

    elif '--test' in args:
        file_index = scan_all_sources(config)
        episodes = match_wochenschau_files(episodes, file_index)
        pool_files = match_interstitial_files(config, file_index)
        playlist = build_kino_playlist(episodes, pool_files, config, state)
        test_render(config, playlist, use_nvenc, resolution)

    elif '--stream' in args:
        stream_key = get_stream_key(config)
        if not stream_key:
            log.error("No stream key! Set YOUTUBE_STREAM_KEY_REMAIKE env or config/stream_key.txt")
            return

        file_index = scan_all_sources(config)
        if not file_index:
            log.error("No video files found! Is V:\\ connected?")
            return

        episodes = match_wochenschau_files(episodes, file_index)
        pool_files = match_interstitial_files(config, file_index)
        playlist = build_kino_playlist(episodes, pool_files, config, state)

        if not playlist:
            log.error("Playlist is empty! Cannot stream.")
            return

        stream_kino(playlist, config, stream_key, use_nvenc, resolution)

    else:
        print(__doc__)


if __name__ == '__main__':
    main()
