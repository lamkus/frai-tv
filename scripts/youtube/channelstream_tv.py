#!/usr/bin/env python3
"""
ChannelStream TV — 24/7 Retro TV Station for remAIke_IT
========================================================
Time-based programming blocks like a real TV station:
  06:00-12:00  🎨 Cartoon Morning
  12:00-18:00  🎵 Vintage Afternoon
  18:00-00:00  🎬 Prime Time
  00:00-06:00  📜 Night Docs

Usage:
    python channelstream_tv.py --scan              # Scan all source dirs for videos
    python channelstream_tv.py --epg               # Show today's EPG / schedule
    python channelstream_tv.py --status            # Show status + file inventory
    python channelstream_tv.py --preview           # Generate HUD overlay preview image
    python channelstream_tv.py --test              # Test: render 30s of current block
    python channelstream_tv.py --stream            # Start 24/7 livestream
    python channelstream_tv.py --stream --nvenc    # Start with GPU encoding
    python channelstream_tv.py --stream --1080p    # Stream at 1080p (less CPU)
"""

import json
import os
import sys
import subprocess
import time
import signal
import logging
import random
import re
import fnmatch
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# === PATHS ===
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CONFIG_PATH = ROOT_DIR / 'config' / 'channelstream_tv_config.json'
STATE_PATH = ROOT_DIR / 'config' / 'channelstream_tv_state.json'

LOG_DIR = ROOT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'channelstream_tv.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('ChannelStreamTV')


# ═══════════════════════════════════════════════════════════════
#  CONFIG & STATE
# ═══════════════════════════════════════════════════════════════

def load_config():
    """Load the TV station config."""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_state():
    """Load persistent state (last played, positions, etc.)."""
    if STATE_PATH.exists():
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_block': None,
        'last_video': None,
        'block_positions': {},
        'play_history': [],
        'started_at': None,
        'total_videos_played': 0
    }


def save_state(state):
    """Persist state to disk."""
    state['updated_at'] = datetime.now().isoformat()
    with open(STATE_PATH, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_stream_key(config):
    """Retrieve stream key from env or file."""
    enc = config['encoding']
    key = os.environ.get(enc.get('stream_key_env', ''), '')
    if not key:
        key_file = ROOT_DIR / enc.get('stream_key_file', 'config/stream_key.txt')
        if key_file.exists():
            key = key_file.read_text().strip()
    return key


# ═══════════════════════════════════════════════════════════════
#  TIMEZONE HELPERS
# ═══════════════════════════════════════════════════════════════

def get_station_now(config):
    """Get current time in station timezone."""
    tz_name = config.get('station', {}).get('timezone', 'Europe/Berlin')
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(tz_name)
    except (ImportError, KeyError):
        # Fallback: assume CET (UTC+1)
        tz = timezone(timedelta(hours=1))
    return datetime.now(tz)


def parse_time(time_str):
    """Parse 'HH:MM' to (hour, minute) tuple."""
    h, m = time_str.split(':')
    return int(h), int(m)


def time_to_minutes(time_str):
    """Convert 'HH:MM' to minutes since midnight."""
    h, m = parse_time(time_str)
    return h * 60 + m


# ═══════════════════════════════════════════════════════════════
#  SCHEDULE / EPG
# ═══════════════════════════════════════════════════════════════

def get_current_block(config):
    """Determine which programming block is currently active."""
    now = get_station_now(config)
    current_minutes = now.hour * 60 + now.minute

    blocks = config['schedule']['blocks']
    for block in blocks:
        start = time_to_minutes(block['start_time'])
        end = time_to_minutes(block['end_time'])

        if end == 0:
            end = 24 * 60  # midnight = 1440

        if start <= current_minutes < end:
            return block

    # Fallback: if between midnight blocks (00:00-06:00)
    for block in blocks:
        if block['start_time'] == '00:00':
            return block

    return blocks[0]


def get_next_block(config, current_block):
    """Get the block that follows the current one."""
    blocks = config['schedule']['blocks']
    for i, block in enumerate(blocks):
        if block['id'] == current_block['id']:
            return blocks[(i + 1) % len(blocks)]
    return blocks[0]


def minutes_until_block_end(config, block):
    """Calculate minutes remaining in current block."""
    now = get_station_now(config)
    current_minutes = now.hour * 60 + now.minute
    end = time_to_minutes(block['end_time'])

    if end == 0:
        end = 24 * 60

    remaining = end - current_minutes
    if remaining < 0:
        remaining += 24 * 60

    return remaining


def print_epg(config):
    """Print today's TV schedule (EPG)."""
    now = get_station_now(config)
    blocks = config['schedule']['blocks']
    current = get_current_block(config)

    print(f"\n{'═' * 66}")
    print(f"  📺 remAIke TV — Programm {now.strftime('%A, %d.%m.%Y')}")
    print(f"  ⏰ Aktuelle Uhrzeit: {now.strftime('%H:%M')} ({config['station']['timezone']})")
    print(f"{'═' * 66}")

    for block in blocks:
        is_current = block['id'] == current['id']
        marker = " ◀ JETZT" if is_current else ""
        emoji = block.get('emoji', '📺')
        pools = block.get('content_pools', [])
        categories = ', '.join(p['label'] for p in pools[:4])
        if len(pools) > 4:
            categories += f' +{len(pools) - 4}'

        print(f"\n  {'▶' if is_current else '○'} {block['start_time']}–{block['end_time']}  "
              f"{emoji} {block['name']}{marker}")
        print(f"    {block['description']}")
        print(f"    Content: {categories}")

    remaining = minutes_until_block_end(config, current)
    next_block = get_next_block(config, current)
    print(f"\n  ⏳ Verbleibend im aktuellen Block: {remaining} Minuten")
    print(f"  ⏭  Nächster Block: {next_block['emoji']} {next_block['name']} "
          f"ab {next_block['start_time']}")
    print(f"{'═' * 66}\n")


# ═══════════════════════════════════════════════════════════════
#  CONTENT SCANNER
# ═══════════════════════════════════════════════════════════════

def scan_all_sources(config):
    """
    Scan all configured source directories for video files.
    Returns dict: { filename_lower: full_path }
    """
    sources = config.get('content_sources', {})
    all_dirs = []

    for key in ['primary', 'fallback', 'wochenschau']:
        dirs = sources.get(key, [])
        all_dirs.extend(d for d in dirs if os.path.isdir(d))

    extensions = set(sources.get('file_extensions', ['.mp4', '.mkv', '.avi', '.mov']))
    file_index = {}

    for src_dir in all_dirs:
        log.info(f"Scanning: {src_dir}")
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                if any(f.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, f)
                    # Index by lowercase filename and also full lowercase path
                    file_index[f.lower()] = full_path

    log.info(f"Total video files found: {len(file_index)}")
    return file_index


def match_files_to_pool(file_index, pool):
    """Match scanned files to a content pool using glob patterns."""
    patterns = pool.get('source_patterns', [])
    # Also check pool-specific source dirs
    pool_dirs = pool.get('source_dirs', [])

    matched = []

    for fname, fpath in file_index.items():
        # Check glob patterns against filename
        for pattern in patterns:
            if fnmatch.fnmatch(fname, pattern.lower()):
                matched.append(fpath)
                break
        else:
            # Check if file is in a pool-specific directory
            for pdir in pool_dirs:
                if fpath.lower().startswith(pdir.lower()):
                    matched.append(fpath)
                    break

    return sorted(set(matched))


def build_block_playlist(config, block, file_index, state):
    """
    Build an ordered playlist for a programming block.
    Respects play_mode: weighted_shuffle, sequential_loop, sequential_then_shuffle
    """
    pools = block.get('content_pools', [])
    play_mode = block.get('play_mode', 'weighted_shuffle')

    # Collect all files per pool
    pool_files = {}
    for pool in pools:
        files = match_files_to_pool(file_index, pool)
        if files:
            pool_files[pool['category']] = {
                'label': pool['label'],
                'files': files,
                'weight': pool.get('weight', 10),
                'requires_disclaimer': pool.get('requires_disclaimer', False),
                'disclaimer_text': pool.get('disclaimer_text', ''),
                'play_mode_override': pool.get('play_mode_override', None),
            }

    if not pool_files:
        log.warning(f"No files found for block '{block['name']}'!")
        return []

    total_files = sum(len(p['files']) for p in pool_files.values())
    log.info(f"Block '{block['name']}': {total_files} files across "
             f"{len(pool_files)} content pools")

    playlist = []

    if play_mode == 'sequential_loop':
        # Play all pools sequentially (good for Wochenschau night block)
        for cat, pdata in pool_files.items():
            if pdata.get('play_mode_override') == 'chronological':
                files = sorted(pdata['files'])
            else:
                files = pdata['files']

            for f in files:
                playlist.append({
                    'file': f,
                    'category': cat,
                    'label': pdata['label'],
                    'requires_disclaimer': pdata['requires_disclaimer'],
                    'disclaimer_text': pdata['disclaimer_text'],
                })

    elif play_mode == 'sequential_then_shuffle':
        # Play series episodes in order, then shuffle the rest
        series_items = []
        shuffle_items = []

        for cat, pdata in pool_files.items():
            if pdata.get('play_mode_override') == 'chronological' or \
               cat in ('alfred_j_quack', 'bravestarr', 'astro_boy'):
                # Keep in order for series
                for f in sorted(pdata['files']):
                    series_items.append({
                        'file': f,
                        'category': cat,
                        'label': pdata['label'],
                        'requires_disclaimer': pdata['requires_disclaimer'],
                        'disclaimer_text': pdata['disclaimer_text'],
                    })
            else:
                for f in pdata['files']:
                    shuffle_items.append({
                        'file': f,
                        'category': cat,
                        'label': pdata['label'],
                        'requires_disclaimer': pdata['requires_disclaimer'],
                        'disclaimer_text': pdata['disclaimer_text'],
                    })

        random.shuffle(shuffle_items)
        # Interleave: series episode, then some shuffled content
        playlist = []
        si, ri = 0, 0
        while si < len(series_items) or ri < len(shuffle_items):
            if si < len(series_items):
                playlist.append(series_items[si])
                si += 1
            # Add 1-2 shuffled items between series episodes
            for _ in range(min(2, len(shuffle_items) - ri)):
                if ri < len(shuffle_items):
                    playlist.append(shuffle_items[ri])
                    ri += 1

    elif play_mode == 'weighted_shuffle':
        # Build weighted playlist — more weight = more frequent appearance
        weighted_pool = []
        for cat, pdata in pool_files.items():
            weight = pdata['weight']
            # Normalize: each file appears proportional to weight
            for f in pdata['files']:
                weighted_pool.append({
                    'file': f,
                    'category': cat,
                    'label': pdata['label'],
                    'weight': weight,
                    'requires_disclaimer': pdata['requires_disclaimer'],
                    'disclaimer_text': pdata['disclaimer_text'],
                })

        # Weighted shuffle: sort by random * weight (higher weight = more likely to be early)
        random.shuffle(weighted_pool)
        weighted_pool.sort(key=lambda x: -x['weight'] * random.random())
        playlist = weighted_pool

    # Resume from last position if we have state
    block_id = block['id']
    last_pos = state.get('block_positions', {}).get(block_id, 0)
    if last_pos > 0 and play_mode in ('sequential_loop', 'sequential_then_shuffle'):
        if last_pos < len(playlist):
            log.info(f"Resuming block '{block['name']}' from position {last_pos}")
            playlist = playlist[last_pos:] + playlist[:last_pos]

    return playlist


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — OVERLAY FILTERS
# ═══════════════════════════════════════════════════════════════

def _esc(text):
    """Escape text for FFmpeg drawtext filter."""
    if not text:
        return ''
    return text.replace("\\", "\\\\").replace("'", "\\'").replace(":", "\\:").replace("%", "%%")


def build_overlay_filters(config, block, item, resolution):
    """Build FFmpeg drawtext filters for the TV station overlay."""
    ov = config.get('overlay', {})
    filters = []
    out_w, out_h = [int(x) for x in resolution.split('x')]
    scale = out_h / 1080  # 1.0 at 1080p, 2.0 at 4K

    def px(val):
        return max(1, int(val * scale))

    # === STATION BUG (top-right corner logo) ===
    bug = ov.get('station_bug', {})
    if bug.get('enabled'):
        bug_text = _esc(bug.get('text', 'remAIke TV'))
        margin = px(bug.get('margin', 20))
        filters.append(
            f"drawtext=text='{bug_text}'"
            f":fontsize={px(bug.get('font_size', 28))}"
            f":fontcolor={bug.get('font_color', 'white@0.6')}"
            f":x=w-tw-{margin}:y={margin}"
            f":font='Arial'"
        )

    # === BOTTOM BAR ===
    bar = ov.get('bottom_bar', {})
    if bar.get('enabled'):
        bar_h = px(bar.get('height', 48))
        opacity = bar.get('opacity', 0.75)

        # Bar background
        filters.append(
            f"drawbox=x=0:y=ih-{bar_h}:w=iw:h={bar_h}"
            f":color=black@{opacity}:t=fill"
        )

        # Block emoji + name (left side)
        block_emoji = block.get('emoji', '📺')
        block_name = block.get('name', 'remAIke TV')
        block_text = _esc(f"{block_emoji} {block_name}")
        text_y = bar_h - px(12) - px(bar.get('font_size_title', 18)) // 2
        filters.append(
            f"drawtext=text='{block_text}'"
            f":fontsize={px(bar.get('font_size_title', 18))}"
            f":fontcolor={bar.get('font_color', '#FFFFFF')}"
            f":x={px(16)}:y=h-{text_y}"
            f":font='Arial'"
        )

        # Current title (center)
        title = _esc(item.get('label', ''))
        fname = Path(item.get('file', '')).stem
        # Clean up the filename for display
        display_name = _clean_display_name(fname)
        now_playing = _esc(f"NOW\\: {title} — {display_name}")
        filters.append(
            f"drawtext=text='{now_playing}'"
            f":fontsize={px(bar.get('font_size_meta', 14))}"
            f":fontcolor={bar.get('meta_color', '#AAAAAA')}"
            f":x=(w-tw)/2:y=h-{text_y}"
            f":font='Arial'"
        )

        # Clock (right side)
        if bar.get('show_clock'):
            clock_fmt = bar.get('clock_format', '%H\\:%M')
            filters.append(
                f"drawtext=text='%{{localtime\\:{_esc(clock_fmt)}}}'"
                f":fontsize={px(bar.get('font_size_title', 18))}"
                f":fontcolor={bar.get('font_color', '#FFFFFF')}"
                f":x=w-tw-{px(16)}:y=h-{text_y}"
                f":font='Arial'"
            )

    # === WOCHENSCHAU DISCLAIMER (persistent, top-left) ===
    if item.get('requires_disclaimer'):
        disc = ov.get('wochenschau_disclaimer', {})
        if disc.get('enabled'):
            disc_text = _esc(item.get('disclaimer_text', disc.get('text', '')))
            filters.append(
                f"drawtext=text='{disc_text}'"
                f":fontsize={px(disc.get('font_size', 16))}"
                f":fontcolor={disc.get('font_color', '#CCCCCC')}"
                f":x={px(10)}:y={px(10)}"
                f":font='Arial'"
            )

    return filters


def _clean_display_name(filename):
    """Clean up a raw filename for on-screen display."""
    name = filename
    # Remove common suffixes
    for suffix in ['_8K_HQ', '_8K', '_4K', '_sls', '_ARCHIVE', '_BLURRED', '_PROTECTED',
                   'sls', 'HQ', 'ARCHIVE']:
        name = name.replace(suffix, '')
    # Replace underscores with spaces
    name = name.replace('_', ' ').replace('-', ' ')
    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name).strip()
    # Title case
    name = name.title()
    # Truncate for overlay
    if len(name) > 50:
        name = name[:47] + '...'
    return name


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — BLOCK INTRO SCREEN
# ═══════════════════════════════════════════════════════════════

def generate_block_intro(config, block, next_items, output_path, resolution='3840x2160'):
    """
    Generate a short intro screen video for a programming block transition.
    Shows: Block name, schedule, and coming-up-next preview.
    """
    ov = config.get('overlay', {}).get('block_intro', {})
    if not ov.get('enabled'):
        return None

    duration = ov.get('duration_seconds', 8)
    out_w, out_h = [int(x) for x in resolution.split('x')]
    scale = out_h / 1080

    def px(val):
        return max(1, int(val * scale))

    emoji = block.get('emoji', '📺')
    block_name = block.get('name', 'Program')
    desc = block.get('description', '')
    time_range = f"{block['start_time']} — {block['end_time']}"
    color = block.get('overlay_color', '#FFFFFF')

    filters = []

    # Title
    filters.append(
        f"drawtext=text='{_esc(f'{emoji} {block_name}')}'"
        f":fontsize={px(ov.get('title_size', 48))}:fontcolor={color}"
        f":x=(w-tw)/2:y=h/3-th/2"
        f":font='Arial Bold'"
    )

    # Time range
    filters.append(
        f"drawtext=text='{_esc(time_range)}'"
        f":fontsize={px(ov.get('subtitle_size', 24))}:fontcolor=white"
        f":x=(w-tw)/2:y=h/3+{px(40)}"
        f":font='Arial'"
    )

    # Description
    filters.append(
        f"drawtext=text='{_esc(desc)}'"
        f":fontsize={px(18)}:fontcolor=#AAAAAA"
        f":x=(w-tw)/2:y=h/3+{px(80)}"
        f":font='Arial'"
    )

    # "Coming up" preview if available
    if next_items:
        filters.append(
            f"drawtext=text='Coming up\\:'"
            f":fontsize={px(20)}:fontcolor=#888888"
            f":x=(w-tw)/2:y=h*2/3-{px(20)}"
            f":font='Arial'"
        )
        for i, item in enumerate(next_items[:3]):
            label = item.get('label', '')
            display = _clean_display_name(Path(item.get('file', '')).stem)
            text = _esc(f"• {label} — {display}")
            filters.append(
                f"drawtext=text='{text}'"
                f":fontsize={px(16)}:fontcolor=#CCCCCC"
                f":x=(w-tw)/2:y=h*2/3+{px(10 + i * 28)}"
                f":font='Arial'"
            )

    # Station name at bottom
    filters.append(
        f"drawtext=text='{_esc('remAIke TV')}'"
        f":fontsize={px(14)}:fontcolor=#555555"
        f":x=(w-tw)/2:y=h-{px(40)}"
        f":font='Arial'"
    )

    filter_str = ','.join(filters)

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f"color=c=#0a0a14:s={resolution}:d={duration}:r=25",
        '-f', 'lavfi',
        '-i', f"anullsrc=r=44100:cl=stereo",
        '-vf', filter_str,
        '-c:v', 'libx264', '-preset', 'ultrafast',
        '-c:a', 'aac', '-b:a', '128k',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        log.info(f"Block intro generated: {output_path}")
        return output_path
    else:
        log.warning(f"Block intro generation failed: {result.stderr[-300:]}")
        return None


# ═══════════════════════════════════════════════════════════════
#  FFMPEG — STREAMING ENGINE
# ═══════════════════════════════════════════════════════════════

def build_stream_command(input_file, config, block, item, stream_key,
                         use_nvenc=False, resolution=None):
    """Build FFmpeg command to stream a single video with overlay."""
    enc = config['encoding']

    if resolution:
        res = resolution
    else:
        res = enc['resolution']

    res_w, res_h = res.split('x')

    if use_nvenc:
        vcodec = enc['codec_gpu']
        preset = enc['preset_gpu']
    else:
        vcodec = enc['codec_cpu']
        preset = enc['preset_cpu']

    # Base video filters
    filters = [
        f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease",
        f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={enc['fps']}",
    ]

    # Add TV station overlay
    filters.extend(build_overlay_filters(config, block, item, res))

    filter_str = ','.join(filters)
    rtmp_url = f"{enc['rtmp_url']}/{stream_key}"

    cmd = [
        'ffmpeg',
        '-re',                              # Real-time playback speed
        '-i', input_file,
        '-vf', filter_str,
        '-c:v', vcodec,
        '-preset', preset,
        '-b:v', enc['video_bitrate'],
        '-maxrate', enc['video_bitrate'],
        '-bufsize', enc['bufsize'],
        '-pix_fmt', enc['pixel_format'],
        '-g', str(enc['max_keyframe_interval']),
        '-c:a', enc['codec_audio'] if 'codec_audio' in enc else 'aac',
        '-b:a', enc['audio_bitrate'],
        '-ar', str(enc['audio_sample_rate']),
        '-f', 'flv',
        rtmp_url,
    ]

    return cmd


def stream_loop(config, file_index, stream_key, use_nvenc=False, resolution=None):
    """
    Main streaming loop. Runs 24/7, switching blocks based on time.
    Each video is streamed individually with per-video overlay.
    """
    state = load_state()
    state['started_at'] = datetime.now().isoformat()
    save_state(state)

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        log.info("Received shutdown signal. Finishing current video...")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    res = resolution or config['encoding']['resolution']
    intro_dir = ROOT_DIR / 'output' / 'block_intros'
    intro_dir.mkdir(parents=True, exist_ok=True)

    current_block_id = None
    playlist = []
    playlist_idx = 0

    log.info("=" * 66)
    log.info("  📺 remAIke TV — Starting 24/7 Livestream")
    log.info(f"  Resolution: {res}")
    log.info(f"  Encoder: {'NVENC (GPU)' if use_nvenc else 'libx264 (CPU)'}")
    log.info(f"  Files indexed: {len(file_index)}")
    log.info("=" * 66)

    while running:
        # Determine current block
        block = get_current_block(config)

        # Block changed? Rebuild playlist & show intro
        if block['id'] != current_block_id:
            log.info(f"\n{'━' * 50}")
            log.info(f"  BLOCK CHANGE → {block['emoji']} {block['name']}")
            log.info(f"  {block['start_time']}–{block['end_time']}: {block['description']}")
            log.info(f"{'━' * 50}")

            playlist = build_block_playlist(config, block, file_index, state)
            playlist_idx = 0
            current_block_id = block['id']

            if not playlist:
                log.warning(f"No content for block '{block['name']}'! Waiting 60s...")
                time.sleep(60)
                continue

            log.info(f"Playlist: {len(playlist)} items")

            # Generate and stream block intro
            intro_path = intro_dir / f"intro_{block['id']}.mp4"
            intro_file = generate_block_intro(
                config, block, playlist[:3], intro_path, res
            )
            if intro_file and os.path.exists(intro_file):
                log.info("Streaming block intro...")
                intro_item = {
                    'file': str(intro_file),
                    'label': 'Block Intro',
                    'category': '_intro',
                    'requires_disclaimer': False,
                    'disclaimer_text': '',
                }
                cmd = build_stream_command(
                    str(intro_file), config, block, intro_item,
                    stream_key, use_nvenc, res
                )
                try:
                    proc = subprocess.run(cmd, capture_output=True, timeout=30)
                except (subprocess.TimeoutExpired, Exception) as e:
                    log.warning(f"Intro stream issue: {e}")

        # Check if we need to loop the playlist
        if playlist_idx >= len(playlist):
            log.info("Playlist finished, rebuilding with new shuffle...")
            playlist = build_block_playlist(config, block, file_index, state)
            playlist_idx = 0
            if not playlist:
                time.sleep(60)
                continue

        # Get next video
        item = playlist[playlist_idx]
        video_file = item['file']

        if not os.path.exists(video_file):
            log.warning(f"File not found, skipping: {video_file}")
            playlist_idx += 1
            continue

        # Display info
        display_name = _clean_display_name(Path(video_file).stem)
        log.info(f"\n  ▶ NOW PLAYING [{playlist_idx + 1}/{len(playlist)}]")
        log.info(f"    {item['label']}: {display_name}")
        log.info(f"    File: {video_file}")

        # Build and run FFmpeg command
        cmd = build_stream_command(
            video_file, config, block, item,
            stream_key, use_nvenc, res
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
                log.warning(f"FFmpeg exited with code {process.returncode}")
                log.warning(f"stderr: {stderr_text}")
                time.sleep(config['system'].get('restart_cooldown_seconds', 30))
            else:
                log.info(f"  ✓ Finished: {display_name}")

            # Update state
            state['last_block'] = block['id']
            state['last_video'] = video_file
            state['block_positions'][block['id']] = playlist_idx + 1
            state['total_videos_played'] = state.get('total_videos_played', 0) + 1
            state['play_history'].append({
                'time': datetime.now().isoformat(),
                'block': block['id'],
                'file': Path(video_file).name,
                'label': item['label'],
            })
            # Keep history manageable
            if len(state['play_history']) > 500:
                state['play_history'] = state['play_history'][-200:]
            save_state(state)

        except Exception as e:
            log.error(f"Error streaming: {e}")
            time.sleep(config['system'].get('restart_cooldown_seconds', 30))

        playlist_idx += 1

        # Brief pause between videos
        if running:
            pause = config.get('transitions', {}).get('between_videos', {}).get('duration_seconds', 2)
            time.sleep(pause)

        # Check if block has changed (time-based transition)
        new_block = get_current_block(config)
        if new_block['id'] != current_block_id:
            log.info(f"\n⏰ Block transition: {block['name']} → {new_block['name']}")
            current_block_id = None  # Force rebuild on next iteration

    # Graceful shutdown
    log.info("\n📺 remAIke TV — Stream stopped gracefully.")
    save_state(state)


# ═══════════════════════════════════════════════════════════════
#  STATUS & DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════

def show_status(config, file_index):
    """Show comprehensive station status."""
    state = load_state()
    now = get_station_now(config)
    block = get_current_block(config)

    print(f"\n{'═' * 66}")
    print(f"  📺 remAIke TV — Station Status")
    print(f"{'═' * 66}")
    print(f"  Time:         {now.strftime('%H:%M:%S')} ({config['station']['timezone']})")
    print(f"  Current Block: {block['emoji']} {block['name']} "
          f"({block['start_time']}–{block['end_time']})")
    print(f"  Remaining:    {minutes_until_block_end(config, block)} min")
    print(f"  Files Indexed: {len(file_index)}")

    # Per-block inventory
    print(f"\n  {'─' * 50}")
    print(f"  Content Inventory per Block:")
    print(f"  {'─' * 50}")

    total_files = 0
    for b in config['schedule']['blocks']:
        playlist = build_block_playlist(config, b, file_index, state)
        count = len(playlist)
        total_files += count
        is_current = b['id'] == block['id']
        marker = " ◀" if is_current else ""

        # Estimate duration (rough: avg 10 min per video)
        est_hours = count * 10 / 60
        print(f"  {b['emoji']} {b['name']:20s}: {count:4d} videos "
              f"(~{est_hours:.1f}h){marker}")

        # Show per-pool breakdown
        for pool in b.get('content_pools', []):
            pool_files = match_files_to_pool(file_index, pool)
            if pool_files:
                print(f"      └ {pool['label']:25s}: {len(pool_files)} files")

    print(f"\n  Total content: {total_files} video items")

    # State info
    if state.get('started_at'):
        print(f"\n  {'─' * 50}")
        print(f"  Session Info:")
        print(f"  {'─' * 50}")
        print(f"  Started:       {state['started_at']}")
        print(f"  Videos Played: {state.get('total_videos_played', 0)}")
        if state.get('last_video'):
            print(f"  Last Video:    {Path(state['last_video']).name}")
        if state.get('last_block'):
            print(f"  Last Block:    {state['last_block']}")

    # Hardware
    enc = config['encoding']
    gpu = config['system'].get('current_gpu', 'unknown')
    print(f"\n  {'─' * 50}")
    print(f"  Encoding:")
    print(f"  {'─' * 50}")
    print(f"  Resolution:    {enc['resolution']}")
    print(f"  Bitrate:       {enc['video_bitrate']}")
    print(f"  FPS:           {enc['fps']}")
    print(f"  GPU:           {gpu}")
    print(f"{'═' * 66}\n")


# ═══════════════════════════════════════════════════════════════
#  PREVIEW
# ═══════════════════════════════════════════════════════════════

def generate_preview(config):
    """Generate a preview image of the HUD overlay for the current block."""
    block = get_current_block(config)
    res = config['encoding']['resolution']
    out_w, out_h = res.split('x')

    sample_item = {
        'file': 'betty_boop_minnie_the_moocher_1932_8K_HQ.mp4',
        'label': 'Betty Boop',
        'category': 'betty_boop',
        'requires_disclaimer': False,
        'disclaimer_text': '',
    }

    filters = [
        f"scale={out_w}:{out_h}",
    ]
    filters.extend(build_overlay_filters(config, block, sample_item, res))
    filter_str = ','.join(filters)

    preview_path = str(ROOT_DIR / 'output' / 'channelstream_tv_preview.png')
    os.makedirs(ROOT_DIR / 'output', exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f"color=c=#1a1a2e:s={res}:d=1",
        '-vf', filter_str,
        '-frames:v', '1',
        '-update', '1',
        preview_path,
    ]

    log.info(f"Generating HUD preview for block: {block['emoji']} {block['name']}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        log.info(f"Preview saved: {preview_path}")
        try:
            os.startfile(preview_path)
        except Exception:
            pass
    else:
        log.error(f"Preview failed: {result.stderr[-500:]}")

    # Also generate block intro preview
    intro_path = ROOT_DIR / 'output' / f'channelstream_intro_preview_{block["id"]}.mp4'
    generate_block_intro(config, block, [sample_item] * 3, intro_path, res)


def test_stream(config, file_index, use_nvenc=False, resolution=None):
    """Test: render 30 seconds of current block to a file (no RTMP)."""
    block = get_current_block(config)
    state = load_state()
    playlist = build_block_playlist(config, block, file_index, state)

    if not playlist:
        log.error("No content available for current block!")
        return

    item = playlist[0]
    video_file = item['file']
    res = resolution or config['encoding']['resolution']

    log.info(f"Test render: {block['emoji']} {block['name']}")
    log.info(f"Video: {video_file}")

    # Build stream command but output to file
    enc = config['encoding']
    res_w, res_h = res.split('x')
    vcodec = enc['codec_gpu'] if use_nvenc else enc['codec_cpu']
    preset = enc['preset_gpu'] if use_nvenc else enc['preset_cpu']

    filters = [
        f"scale={res_w}:{res_h}:force_original_aspect_ratio=decrease",
        f"pad={res_w}:{res_h}:(ow-iw)/2:(oh-ih)/2:black",
        f"fps={enc['fps']}",
    ]
    filters.extend(build_overlay_filters(config, block, item, res))
    filter_str = ','.join(filters)

    test_out = str(ROOT_DIR / 'output' / 'channelstream_tv_test.mp4')
    os.makedirs(ROOT_DIR / 'output', exist_ok=True)

    cmd = [
        'ffmpeg', '-y',
        '-i', video_file,
        '-vf', filter_str,
        '-c:v', vcodec, '-preset', preset,
        '-b:v', enc['video_bitrate'],
        '-pix_fmt', enc['pixel_format'],
        '-c:a', 'aac', '-b:a', enc['audio_bitrate'],
        '-t', '30',
        '-f', 'mp4',
        test_out,
    ]

    log.info("Rendering 30s test clip...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        log.info(f"Test output: {test_out}")
        try:
            os.startfile(test_out)
        except Exception:
            pass
    else:
        log.error(f"Test render failed: {result.stderr[-500:]}")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        return

    config = load_config()

    # Determine resolution override
    resolution = None
    if '--1080p' in args:
        resolution = '1920x1080'
    elif '--720p' in args:
        resolution = '1280x720'

    use_nvenc = '--nvenc' in args

    if '--epg' in args:
        print_epg(config)

    elif '--scan' in args:
        log.info("Scanning all content sources...")
        file_index = scan_all_sources(config)
        log.info(f"\nScan complete: {len(file_index)} video files found")

        # Show per-block breakdown
        state = load_state()
        for block in config['schedule']['blocks']:
            playlist = build_block_playlist(config, block, file_index, state)
            log.info(f"{block['emoji']} {block['name']}: {len(playlist)} items")
            for pool in block.get('content_pools', []):
                files = match_files_to_pool(file_index, pool)
                if files:
                    log.info(f"  └ {pool['label']}: {len(files)} files")

    elif '--status' in args:
        file_index = scan_all_sources(config)
        show_status(config, file_index)

    elif '--preview' in args:
        generate_preview(config)

    elif '--test' in args:
        file_index = scan_all_sources(config)
        test_stream(config, file_index, use_nvenc, resolution)

    elif '--stream' in args:
        stream_key = get_stream_key(config)
        if not stream_key:
            log.error("No stream key! Set YOUTUBE_STREAM_KEY_REMAIKE env or create config/stream_key.txt")
            print("\nTo get your stream key:")
            print("1. Go to https://studio.youtube.com/channel/UCVFv6Egpl0LDvigpFbQXNeQ/livestreaming")
            print("2. Create a new livestream")
            print("3. Copy the Stream Key")
            print("4. Set: $env:YOUTUBE_STREAM_KEY_REMAIKE = 'xxxx-xxxx-xxxx'")
            print("   Or save to: config/stream_key.txt")
            return

        file_index = scan_all_sources(config)
        if not file_index:
            log.error("No video files found! Is V:\\ connected?")
            return

        stream_loop(config, file_index, stream_key, use_nvenc, resolution)

    else:
        print(__doc__)


if __name__ == '__main__':
    main()
