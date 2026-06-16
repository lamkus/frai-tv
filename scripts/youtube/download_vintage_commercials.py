#!/usr/bin/env python3
"""
Vintage Commercials Downloader & Processor
==========================================
Downloads public domain commercials from Archive.org,
splits compilations into individual clips, and prepares them
for the WochenschauKino streaming experience.

Usage:
    python download_vintage_commercials.py --list          # Show catalog
    python download_vintage_commercials.py --download       # Download tier1
    python download_vintage_commercials.py --download --all # Download all tiers
    python download_vintage_commercials.py --split          # Split compilations
    python download_vintage_commercials.py --scan           # Scan local inventory
    python download_vintage_commercials.py --status         # Show download status
"""

import json
import os
import sys
import re
import subprocess
import logging
import time
from pathlib import Path
from datetime import datetime

# === PATHS ===
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent
CATALOG_PATH = ROOT_DIR / 'config' / 'vintage_commercials_catalog.json'
LOG_DIR = ROOT_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'vintage_commercials.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('VintageAds')

ARCHIVE_ORG_DL = "https://archive.org/download"


def _clean_title_for_filename(title, year):
    """Create a clean, descriptive filename from catalog title + year."""
    clean = title.replace(':', ' -').replace('/', '_').replace('\\', '_')
    clean = clean.replace('  ', ' ').strip()
    clean = clean.replace(' ', '_')
    for c in ['<', '>', '|', '?', '*', '"', "'", '(', ')']:
        clean = clean.replace(c, '')
    return f"Commercial_{year}_{clean}.mp4"


def _lookup_catalog_item(catalog, ident):
    """Find catalog item by Archive.org identifier, return (title, year, category)."""
    for cat_id, cat in catalog.get('categories', {}).items():
        for item in cat.get('items', []):
            if item.get('id', '').lower() == ident.lower():
                return {
                    'title': item.get('title', ident),
                    'year': item.get('year', ''),
                    'category': cat_id,
                }
    return None


def _find_existing_file(dl_dir, ident, catalog=None):
    """Check if a file for this identifier already exists (old or new naming)."""
    # Check new naming: Commercial_YEAR_*
    if catalog:
        info = _lookup_catalog_item(catalog, ident)
        if info:
            proper_name = _clean_title_for_filename(info['title'], info['year'])
            if (dl_dir / proper_name).exists():
                return dl_dir / proper_name
    # Check old naming: {ident}_*
    matches = list(dl_dir.glob(f"{ident}*"))
    if matches:
        return matches[0]
    return None


def load_catalog():
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_download_dir(catalog):
    dl_dir = Path(catalog.get('download_dir', 'V:\\Commercials\\Vintage'))
    dl_dir.mkdir(parents=True, exist_ok=True)
    return dl_dir


def list_catalog(catalog):
    """Print the full commercial catalog with download status."""
    dl_dir = get_download_dir(catalog)
    total_items = 0
    total_downloaded = 0

    print(f"\n{'=' * 70}")
    print(f"  [CATALOG] Vintage Commercials for WochenschauKino")
    print(f"{'=' * 70}")
    print(f"  Download dir: {dl_dir}")
    print()

    for cat_id, cat in catalog.get('categories', {}).items():
        items = cat.get('items', [])
        label = cat.get('label', cat_id)
        era = cat.get('era', '?')
        print(f"  [{cat_id}] {label} ({era}) -- {len(items)} items")

        for item in items:
            total_items += 1
            title = item.get('title', '?')
            year = item.get('year', '?')
            dl = item.get('downloads', 0)
            ident = item.get('id', '')
            local = item.get('local_path', '')
            needs_split = item.get('needs_splitting', False)

            # Check if already downloaded (supports old & new naming)
            status = '[ ]'
            if local:
                if Path(local).exists() or _find_existing_file(dl_dir, ident, catalog):
                    status = '[x]'
                    total_downloaded += 1
                else:
                    status = '[L]'  # Local path configured but file missing
            elif ident:
                if _find_existing_file(dl_dir, ident, catalog):
                    status = '[x]'
                    total_downloaded += 1

            split_tag = ' [SPLIT]' if needs_split else ''
            dl_tag = f' (DL:{dl:,})' if dl else ''
            print(f"    {status} {title} ({year}){split_tag}{dl_tag}")

        print()

    print(f"  Total: {total_items} items, {total_downloaded} downloaded")
    print(f"{'=' * 70}\n")


def _get_tier_ids(priority, tier_key):
    """Extract identifiers from a tier entry (list or dict with 'items')."""
    val = priority.get(tier_key, [])
    if isinstance(val, dict):
        return val.get('items', [])
    if isinstance(val, list):
        return val
    return []


def _all_tier_keys(priority):
    """Return all tier keys sorted (skip _info and other metadata)."""
    return [k for k in priority if k.startswith('tier')]


def download_items(catalog, tier='tier1', force=False):
    """Download commercials from Archive.org by priority tier."""
    dl_dir = get_download_dir(catalog)
    priority = catalog.get('download_priority', {})
    tier_keys = _all_tier_keys(priority)

    if tier == 'all':
        identifiers = []
        for tk in tier_keys:
            identifiers.extend(_get_tier_ids(priority, tk))
    else:
        # Match tier1 -> tier1_wartime_era, tier2 -> tier2_kino_classics, etc.
        matched = [tk for tk in tier_keys if tk.startswith(tier)]
        if matched:
            identifiers = _get_tier_ids(priority, matched[0])
        else:
            identifiers = _get_tier_ids(priority, tier_keys[0]) if tier_keys else []

    log.info(f"Downloading {len(identifiers)} items (tier: {tier})")
    log.info(f"Target directory: {dl_dir}")

    downloaded = 0
    skipped = 0
    failed = 0

    for ident in identifiers:
        # Check if already downloaded (old or new naming)
        existing = _find_existing_file(dl_dir, ident, catalog)
        if existing and not force:
            log.info(f"  SKIP (exists): {existing.name}")
            skipped += 1
            continue

        log.info(f"  Downloading: {ident}")

        # Get file list from Archive.org metadata
        try:
            import requests
            meta_url = f"https://archive.org/metadata/{ident}"
            r = requests.get(meta_url, timeout=30)
            meta = r.json()

            # Find the best video file (prefer mp4, then mpeg, then ogv)
            files = meta.get('files', [])
            video_files = []
            for f in files:
                name = f.get('name', '')
                fmt = f.get('format', '')
                size = int(f.get('size', 0))
                if any(ext in name.lower() for ext in ['.mp4', '.mpeg', '.ogv', '.avi']):
                    video_files.append({
                        'name': name,
                        'format': fmt,
                        'size': size,
                        'url': f"{ARCHIVE_ORG_DL}/{ident}/{name}"
                    })

            if not video_files:
                log.warning(f"  NO VIDEO FILES for {ident}")
                failed += 1
                continue

            # Prefer: MPEG4 > h.264 > OGV > others, larger = better quality
            def sort_key(vf):
                name = vf['name'].lower()
                fmt = vf['format'].lower()
                priority = 0
                if '.mp4' in name:
                    priority = 3
                if 'h.264' in fmt or 'mpeg4' in fmt:
                    priority = 4
                if '.ogv' in name:
                    priority = 1
                return (priority, vf['size'])

            video_files.sort(key=sort_key, reverse=True)
            best = video_files[0]

            log.info(f"    Best file: {best['name']} ({best['size'] // 1024 // 1024}MB)")

            # Generate proper descriptive filename from catalog
            cat_info = _lookup_catalog_item(catalog, ident)
            if cat_info:
                out_name = _clean_title_for_filename(cat_info['title'], cat_info['year'])
                log.info(f"    Catalog match: {cat_info['title']} ({cat_info['year']})")
            else:
                # Fallback: use archive ID + original name if not in catalog
                out_name = f"{ident}_{best['name']}"
                log.warning(f"    No catalog match for '{ident}' — using archive name")
            out_path = dl_dir / out_name

            # Use requests for download with progress
            with requests.get(best['url'], stream=True, timeout=60) as resp:
                resp.raise_for_status()
                total_size = int(resp.headers.get('content-length', 0))
                downloaded_bytes = 0
                with open(out_path, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=8192 * 16):
                        f.write(chunk)
                        downloaded_bytes += len(chunk)
                        if total_size > 0:
                            pct = (downloaded_bytes / total_size) * 100
                            if downloaded_bytes % (1024 * 1024 * 5) < 8192 * 16:
                                log.info(f"    {pct:.0f}% ({downloaded_bytes // 1024 // 1024}MB)")

            log.info(f"    OK: {out_path.name} ({out_path.stat().st_size // 1024 // 1024}MB)")
            downloaded += 1

        except Exception as e:
            log.error(f"    FAILED: {ident}: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"  Download complete: {downloaded} OK, {skipped} skipped, {failed} failed")
    print(f"{'=' * 50}\n")


def split_compilation(video_path, output_dir, min_clip_sec=15, max_clip_sec=120):
    """
    Split a compilation video into individual commercial clips.
    Uses FFmpeg scene detection to find cuts between ads.
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info(f"Splitting: {video_path.name}")

    # Step 1: Detect scenes using FFmpeg
    cmd = [
        'ffmpeg', '-i', str(video_path),
        '-vf', 'select=gt(scene\\,0.35),showinfo',
        '-vsync', 'vfr',
        '-f', 'null', '-'
    ]

    log.info("  Detecting scene changes...")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        log.error("  Scene detection timed out")
        return []

    # Parse scene change timestamps
    scene_times = [0.0]
    for line in stderr.split('\n'):
        if 'pts_time:' in line:
            m = re.search(r'pts_time:(\d+\.?\d*)', line)
            if m:
                t = float(m.group(1))
                scene_times.append(t)

    if len(scene_times) < 2:
        log.warning("  No scene changes detected, trying lower threshold...")
        # Retry with lower threshold
        cmd[4] = 'select=gt(scene\\,0.20),showinfo'
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            for line in result.stderr.split('\n'):
                if 'pts_time:' in line:
                    m = re.search(r'pts_time:(\d+\.?\d*)', line)
                    if m:
                        t = float(m.group(1))
                        if t not in scene_times:
                            scene_times.append(t)
        except:
            pass

    scene_times.sort()

    # Get total duration
    probe_cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)
    ]
    try:
        dur_result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)
        total_duration = float(dur_result.stdout.strip())
        scene_times.append(total_duration)
    except:
        pass

    log.info(f"  Found {len(scene_times) - 1} scene changes")

    # Step 2: Merge very short segments into clips of min_clip_sec to max_clip_sec
    clips = []
    clip_start = scene_times[0]

    for i in range(1, len(scene_times)):
        clip_duration = scene_times[i] - clip_start
        if clip_duration >= min_clip_sec:
            clips.append((clip_start, scene_times[i]))
            clip_start = scene_times[i]

    # Don't forget the last segment
    if clip_start < scene_times[-1]:
        clips.append((clip_start, scene_times[-1]))

    log.info(f"  Merged into {len(clips)} clips")

    # Step 3: Extract clips
    stem = video_path.stem
    # Try to extract year from filename
    year_match = re.search(r'(19[3-6]\d)', stem)
    year = year_match.group(1) if year_match else '1950'

    extracted = []
    for idx, (start, end) in enumerate(clips):
        duration = end - start
        if duration < min_clip_sec:
            continue
        if duration > max_clip_sec * 2:
            # Skip very long segments (likely not individual ads)
            log.info(f"    Skipping segment {idx + 1}: {duration:.0f}s (too long)")
            continue

        out_name = f"commercial_{year}_{stem[:20]}_{idx + 1:03d}.mp4"
        out_path = output_dir / out_name

        extract_cmd = [
            'ffmpeg', '-y',
            '-ss', str(start),
            '-i', str(video_path),
            '-t', str(duration),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-c:a', 'aac', '-b:a', '192k',
            '-movflags', '+faststart',
            str(out_path)
        ]

        try:
            subprocess.run(extract_cmd, capture_output=True, timeout=120)
            if out_path.exists() and out_path.stat().st_size > 10000:
                extracted.append({
                    'file': str(out_path),
                    'start': start,
                    'end': end,
                    'duration': duration,
                    'year': int(year),
                })
                log.info(f"    Clip {idx + 1}: {start:.1f}s-{end:.1f}s ({duration:.0f}s) -> {out_name}")
        except Exception as e:
            log.error(f"    Failed clip {idx + 1}: {e}")

    log.info(f"  Extracted {len(extracted)} clips from {video_path.name}")
    return extracted


def split_all_compilations(catalog):
    """Find and split all compilation videos."""
    dl_dir = get_download_dir(catalog)
    split_dir = dl_dir / 'split'
    split_dir.mkdir(parents=True, exist_ok=True)

    all_clips = []

    for cat_id, cat in catalog.get('categories', {}).items():
        for item in cat.get('items', []):
            if not item.get('needs_splitting', False):
                continue

            ident = item.get('id', '')
            local = item.get('local_path', '')

            # Find the file (supports old & new naming)
            video_path = None
            if local and Path(local).exists():
                video_path = Path(local)
            elif ident:
                found_file = _find_existing_file(dl_dir, ident, catalog)
                if found_file:
                    video_path = found_file

            if not video_path:
                log.warning(f"  Not found: {item.get('title', ident)}")
                continue

            clips = split_compilation(video_path, split_dir)
            all_clips.extend(clips)

    # Save clip inventory
    inventory_path = dl_dir / 'split_inventory.json'
    with open(inventory_path, 'w', encoding='utf-8') as f:
        json.dump(all_clips, f, indent=2, ensure_ascii=False)
    log.info(f"\nSplit inventory saved: {inventory_path} ({len(all_clips)} clips)")

    return all_clips


def scan_local_commercials(catalog):
    """Scan for all available commercial video files."""
    dl_dir = get_download_dir(catalog)
    video_exts = {'.mp4', '.mkv', '.avi', '.webm', '.mpeg', '.ogv'}
    found = []

    # Scan download directory
    if dl_dir.exists():
        for f in dl_dir.rglob('*'):
            if f.suffix.lower() in video_exts and f.stat().st_size > 10000:
                year = _extract_year(f.name)
                found.append({
                    'file': str(f),
                    'filename': f.name,
                    'year': year,
                    'size_mb': f.stat().st_size // 1024 // 1024,
                    'source': 'downloaded',
                })

    # Scan known local paths
    local_dirs = [
        Path('V:/OriginalSources/Commercials'),
        Path('V:/OriginalSources/MusicVideos'),
    ]
    for d in local_dirs:
        if d.exists():
            for f in d.rglob('*'):
                if f.suffix.lower() in video_exts and f.stat().st_size > 10000:
                    name_lower = f.name.lower()
                    if any(kw in name_lower for kw in
                           ['commercial', 'advert', 'lucky', 'cigarette',
                            'coca', 'pepsi', 'television commercial']):
                        year = _extract_year(f.name)
                        found.append({
                            'file': str(f),
                            'filename': f.name,
                            'year': year,
                            'size_mb': f.stat().st_size // 1024 // 1024,
                            'source': 'local',
                        })

    print(f"\n{'=' * 60}")
    print(f"  [SCAN] Vintage Commercials Inventory")
    print(f"{'=' * 60}")
    print(f"  Total files: {len(found)}")

    for item in sorted(found, key=lambda x: x['year']):
        print(f"    [{item['source']:10s}] ({item['year']}) {item['filename'][:55]} ({item['size_mb']}MB)")

    print(f"{'=' * 60}\n")

    return found


def _extract_year(filename):
    """Extract year from filename."""
    m = re.search(r'(19[2-6]\d)', filename)
    return int(m.group(1)) if m else 1950


def show_status(catalog):
    """Show download status overview."""
    dl_dir = get_download_dir(catalog)
    priority = catalog.get('download_priority', {})

    print(f"\n{'=' * 60}")
    print(f"  [STATUS] Vintage Commercials Download Progress")
    print(f"{'=' * 60}")

    tier_keys = _all_tier_keys(priority)
    for tk in tier_keys:
        val = priority.get(tk, {})
        note = val.get('note', tk) if isinstance(val, dict) else tk
        display_name = note[:40] if len(note) > 40 else note
        ids = _get_tier_ids(priority, tk)
        downloaded = 0
        for ident in ids:
            if _find_existing_file(dl_dir, ident, catalog):
                downloaded += 1

        pct = (downloaded / len(ids) * 100) if ids else 0
        bar = '#' * int(pct / 5) + '-' * (20 - int(pct / 5))
        print(f"  {display_name:42s} [{bar}] {downloaded}/{len(ids)} ({pct:.0f}%)")

    # Local files
    local_count = 0
    for cat_id, cat in catalog.get('categories', {}).items():
        for item in cat.get('items', []):
            local = item.get('local_path', '')
            if local:
                local_count += 1

    print(f"\n  Local files (no download needed): {local_count}")
    print(f"  Download directory: {dl_dir}")
    print(f"{'=' * 60}\n")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    args = sys.argv[1:]

    if '--help' in args or '-h' in args or not args:
        print(__doc__)
        sys.exit(0)

    catalog = load_catalog()

    if '--list' in args:
        list_catalog(catalog)

    elif '--download' in args:
        if '--all' in args:
            tier = 'all'
        elif '--tier2' in args:
            tier = 'tier2'
        elif '--tier3' in args:
            tier = 'tier3'
        elif '--tier4' in args:
            tier = 'tier4'
        else:
            tier = 'tier1'
        download_items(catalog, tier=tier)

    elif '--split' in args:
        split_all_compilations(catalog)

    elif '--scan' in args:
        scan_local_commercials(catalog)

    elif '--status' in args:
        show_status(catalog)

    else:
        print("Unknown command. Use --help for usage.")
