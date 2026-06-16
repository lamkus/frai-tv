#!/usr/bin/env python3
"""
Curate 100 Vintage Commercial Clips for WochenschauKino
========================================================
Takes downloaded compilations + individual clips from V:\Commercials\Vintage,
splits compilations via FFmpeg scene detection, and curates the best 100
clips chronologically sorted for the educational Wochenschau stream.

Usage:
    python curate_100_clips.py --analyze       # Show what we have
    python curate_100_clips.py --split         # Split compilations into clips
    python curate_100_clips.py --curate        # Select best 100 & build playlist
    python curate_100_clips.py --all           # Full pipeline: split + curate
"""

import json
import os
import sys
import re
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# === PATHS ===
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent.parent
SOURCE_DIR = Path("V:/Commercials/Vintage")
SPLIT_DIR = SOURCE_DIR / "split"
CURATED_DIR = SOURCE_DIR / "curated_100"
INVENTORY_PATH = ROOT_DIR / "config" / "curated_clips_inventory.json"
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'curate_clips.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger('Curator')

# === THRESHOLDS ===
MIN_CLIP_SEC = 10       # Minimum clip length (skip intros/jingles)
MAX_CLIP_SEC = 180      # Maximum clip length (3 min - Shorts-compatible)
IDEAL_MIN = 20          # Ideal range lower bound
IDEAL_MAX = 90          # Ideal range upper bound
SCENE_THRESHOLD = 0.30  # FFmpeg scene detection threshold (lower = more cuts)
TARGET_CLIPS = 100      # How many clips we want

# === FILES TO SKIP (not real commercials) ===
SKIP_FILES = {
    "Commercial_1943_Wartime_Nutrition_1943.mp4",  # 0 duration / corrupt
}

# === CLASSIFICATION ===
# Files that are compilations (multiple ads in one file) — need splitting
# Everything else is a standalone clip
def is_compilation(name, duration_sec):
    """Determine if a file is a compilation needing splitting."""
    compilation_patterns = [
        r"Classic_Television_Commercials_Part",
        r"Television_Commercials_1950s",
        r"Chevrolet_Screen_Ads",
        r"Classic_Television_Commercials_Master",
        r"Chevrolet_Leader_News",
    ]
    for pat in compilation_patterns:
        if re.search(pat, name):
            return True
    # Any file > 5 min that looks like it has multiple ads
    if duration_sec > 300 and any(kw in name for kw in ["Part", "Collection", "Compilation"]):
        return True
    return False


def is_educational_film(name, duration_sec):
    """Long-form propaganda/educational films — split these too for wartime clips."""
    edu_patterns = [
        r"Hemp_for_Victory",
        r"To_Market.*Part",
        r"War_Bond",
        r"Make_Mine_Freedom",
        r"Always_Tomorrow",
        r"Wartime_Nutrition",
        r"1st_War_Bond",
    ]
    for pat in edu_patterns:
        if re.search(pat, name):
            return True
    return False


def is_splittable(name, duration_sec):
    """Any file that should be split into individual clips."""
    if is_compilation(name, duration_sec):
        return True
    if is_educational_film(name, duration_sec) and duration_sec > MAX_CLIP_SEC:
        return True
    # Any file > 5 min that isn't classified as a short clip — split it
    if duration_sec > 300:
        return True
    return False


def get_duration(filepath):
    """Get video duration in seconds."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', str(filepath)],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except:
        return 0.0


def extract_year(filename):
    """Extract year from Commercial_YEAR_... pattern."""
    m = re.search(r'Commercial_(\d{4})_', filename)
    if m:
        return int(m.group(1))
    m = re.search(r'(19[2-6]\d)', filename)
    return int(m.group(1)) if m else 1950


def analyze_inventory():
    """Analyze what we have and classify each file."""
    files = sorted(SOURCE_DIR.glob("*.mp4"))
    
    singles = []
    compilations = []
    edu_films = []
    skipped = []
    
    print(f"\n{'='*70}")
    print(f"  VINTAGE COMMERCIALS INVENTORY")
    print(f"{'='*70}")
    
    for f in files:
        if f.name in SKIP_FILES:
            skipped.append(f)
            continue
            
        dur = get_duration(f)
        year = extract_year(f.name)
        size_mb = f.stat().st_size / 1024 / 1024
        
        if dur == 0:
            skipped.append(f)
            continue
        
        info = {
            'path': str(f),
            'name': f.name,
            'duration': dur,
            'year': year,
            'size_mb': round(size_mb, 1),
        }
        
        if is_educational_film(f.name, dur) and dur <= MAX_CLIP_SEC:
            # Short edu films keep as individual clips
            singles.append(info)
            tag = "CLIP"
        elif is_splittable(f.name, dur):
            compilations.append(info)
            tag = "COMP"
        elif is_educational_film(f.name, dur):
            edu_films.append(info)
            tag = "EDU "
        elif is_compilation(f.name, dur):
            compilations.append(info)
            tag = "COMP"
        else:
            singles.append(info)
            tag = "CLIP"
        
        print(f"  {tag}  ({year}) {f.name[:55]:<55} {dur:6.0f}s  {size_mb:6.0f}MB")
    
    total_comp_dur = sum(c['duration'] for c in compilations)
    est_clips = int(total_comp_dur / 45)  # avg 45s per ad
    
    print(f"\n{'-'*70}")
    print(f"  INDIVIDUAL CLIPS:   {len(singles):3d} files  ({sum(s['duration'] for s in singles)/60:.0f} min)")
    print(f"  COMPILATIONS:       {len(compilations):3d} files  ({total_comp_dur/60:.0f} min) -> ~{est_clips} clips after split")
    print(f"  EDUCATIONAL FILMS:  {len(edu_films):3d} files  ({sum(e['duration'] for e in edu_films)/60:.0f} min)")
    print(f"  SKIPPED/CORRUPT:    {len(skipped):3d} files")
    print(f"  EXPECTED TOTAL:     ~{len(singles) + est_clips} clips available for curation")
    print(f"{'='*70}\n")
    
    return singles, compilations, edu_films


def detect_scenes(video_path, threshold=SCENE_THRESHOLD):
    """Detect scene changes in a video using FFmpeg."""
    cmd = [
        'ffmpeg', '-i', str(video_path),
        '-vf', f'select=gt(scene\\,{threshold}),showinfo',
        '-vsync', 'vfr', '-f', 'null', '-'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        log.error(f"Scene detection timeout: {video_path}")
        return []
    
    times = [0.0]
    for line in stderr.split('\n'):
        if 'pts_time:' in line:
            m = re.search(r'pts_time:(\d+\.?\d*)', line)
            if m:
                t = float(m.group(1))
                times.append(t)
    
    dur = get_duration(video_path)
    if dur > 0:
        times.append(dur)
    
    times = sorted(set(times))
    return times


def merge_scenes_to_clips(scene_times, min_sec=MIN_CLIP_SEC, max_sec=MAX_CLIP_SEC):
    """
    Merge rapid scene changes into logical commercial clips.
    
    Strategy: Scene detection finds EVERY cut within a commercial too.
    Real ad boundaries have longer gaps. We merge consecutive short scenes
    until we hit a reasonable clip duration.
    """
    if len(scene_times) < 2:
        return []
    
    clips = []
    clip_start = scene_times[0]
    
    for i in range(1, len(scene_times)):
        segment_dur = scene_times[i] - clip_start
        
        # Check for a "big gap" between scenes (> 1s black/silence between ads)
        if i < len(scene_times) - 1:
            gap_to_next = scene_times[i] - scene_times[i-1] if i > 0 else 0
        
        # Natural break: clip is in ideal range
        if IDEAL_MIN <= segment_dur <= IDEAL_MAX:
            # Look ahead: is there a significant scene boundary here?
            # Accept this as a clip boundary
            clips.append((clip_start, scene_times[i]))
            clip_start = scene_times[i]
        elif segment_dur > max_sec:
            # Too long - force a split at max_sec intervals
            while clip_start + max_sec < scene_times[i]:
                # Find the closest scene change near max_sec
                best_cut = clip_start + max_sec
                for j in range(len(scene_times)):
                    if clip_start + min_sec < scene_times[j] <= clip_start + max_sec:
                        best_cut = scene_times[j]
                clips.append((clip_start, best_cut))
                clip_start = best_cut
            if scene_times[i] - clip_start >= min_sec:
                clips.append((clip_start, scene_times[i]))
                clip_start = scene_times[i]
    
    # Don't forget the trailing segment
    if scene_times[-1] - clip_start >= min_sec:
        clips.append((clip_start, scene_times[-1]))
    
    return clips


def extract_clip(input_path, output_path, start, duration):
    """Extract a single clip using stream copy (fast, no re-encode)."""
    cmd = [
        'ffmpeg', '-y', '-nostdin',
        '-ss', f'{start:.3f}',
        '-i', str(input_path),
        '-t', f'{duration:.3f}',
        '-c', 'copy',        # Stream copy = instant, no quality loss
        '-avoid_negative_ts', 'make_zero',
        '-movflags', '+faststart',
        str(output_path)
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if output_path.exists() and output_path.stat().st_size > 5000:
            return True
    except:
        pass
    
    # Fallback: re-encode if stream copy fails
    cmd_reencode = [
        'ffmpeg', '-y', '-nostdin',
        '-ss', f'{start:.3f}',
        '-i', str(input_path),
        '-t', f'{duration:.3f}',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
        '-c:a', 'aac', '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ]
    try:
        subprocess.run(cmd_reencode, capture_output=True, text=True, timeout=120)
        return output_path.exists() and output_path.stat().st_size > 5000
    except:
        return False


def split_compilations():
    """Split all compilation files into individual clips."""
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    
    singles, compilations, edu_films = analyze_inventory()
    
    all_extracted = []
    
    for comp in compilations:
        src = Path(comp['path'])
        year = comp['year']
        dur = comp['duration']
        
        log.info(f"\n{'-'*50}")
        log.info(f"SPLITTING: {src.name} ({dur:.0f}s = {dur/60:.1f}min)")
        log.info(f"{'-'*50}")
        
        # Step 1: Scene detection
        log.info("  Detecting scenes...")
        scene_times = detect_scenes(src)
        log.info(f"  Found {len(scene_times)} scene markers")
        
        if len(scene_times) < 3:
            # Try lower threshold
            log.info("  Retrying with lower threshold (0.20)...")
            scene_times = detect_scenes(src, threshold=0.20)
            log.info(f"  Found {len(scene_times)} scene markers (lower threshold)")
        
        if len(scene_times) < 3:
            # Last resort: fixed interval splitting
            log.warning("  No scenes found — splitting by fixed 60s intervals")
            scene_times = [i * 60.0 for i in range(int(dur / 60) + 1)]
            scene_times.append(dur)
        
        # Step 2: Merge scenes to clip boundaries
        clips = merge_scenes_to_clips(scene_times)
        log.info(f"  Merged to {len(clips)} clips")
        
        # Step 3: Extract each clip
        stem = src.stem[:30]  # Short stem for naming
        extracted_count = 0
        
        for idx, (start, end) in enumerate(clips):
            clip_dur = end - start
            if clip_dur < MIN_CLIP_SEC:
                continue
            
            out_name = f"clip_{year}_{stem}_{idx+1:03d}.mp4"
            out_path = SPLIT_DIR / out_name
            
            if out_path.exists() and out_path.stat().st_size > 5000:
                # Already extracted
                all_extracted.append({
                    'file': str(out_path),
                    'name': out_name,
                    'year': year,
                    'duration': round(clip_dur, 1),
                    'source': src.name,
                    'start': round(start, 1),
                    'end': round(end, 1),
                    'type': 'split',
                })
                extracted_count += 1
                continue
            
            ok = extract_clip(src, out_path, start, clip_dur)
            if ok:
                extracted_count += 1
                all_extracted.append({
                    'file': str(out_path),
                    'name': out_name,
                    'year': year,
                    'duration': round(clip_dur, 1),
                    'source': src.name,
                    'start': round(start, 1),
                    'end': round(end, 1),
                    'type': 'split',
                })
                log.info(f"    [{extracted_count:3d}] {start:6.1f}s -> {end:6.1f}s ({clip_dur:.0f}s) OK")
            else:
                log.warning(f"    FAILED: {out_name}")
        
        log.info(f"  -> {extracted_count} clips from {src.name}")
    
    # Save split inventory
    inv_path = SPLIT_DIR / "split_inventory.json"
    with open(inv_path, 'w', encoding='utf-8') as f:
        json.dump(all_extracted, f, indent=2, ensure_ascii=False)
    
    log.info(f"\n{'='*50}")
    log.info(f"  SPLIT COMPLETE: {len(all_extracted)} clips extracted")
    log.info(f"  Inventory: {inv_path}")
    log.info(f"{'='*50}")
    
    return all_extracted


def curate_100():
    """
    Select the best 100 clips from all available material.
    Priority:
    1. Individual clips (already curated quality)
    2. Best split clips (ideal duration, good era match)
    3. Short educational films (< 3 min segments)
    
    Sorted chronologically by year.
    """
    CURATED_DIR.mkdir(parents=True, exist_ok=True)
    
    # Gather all candidates
    candidates = []
    
    # 1. Individual clips from source dir
    for f in sorted(SOURCE_DIR.glob("*.mp4")):
        if f.name in SKIP_FILES:
            continue
        dur = get_duration(f)
        if dur == 0:
            continue
        year = extract_year(f.name)
        
        if is_splittable(f.name, dur):
            continue  # Skip compilations/long edu films (use their splits instead)
        
        if is_educational_film(f.name, dur):
            # Keep educational films under 3 min; skip the long ones
            if dur > MAX_CLIP_SEC:
                continue
        
        candidates.append({
            'file': str(f),
            'name': f.name,
            'year': year,
            'duration': round(dur, 1),
            'source': 'original',
            'type': 'individual',
            'score': _score_clip(f.name, year, dur),
        })
    
    # 2. Split clips — load inventory for source tracking
    source_map = {}  # clip filename -> source compilation
    inv_path = SPLIT_DIR / "split_inventory.json"
    if inv_path.exists():
        with open(inv_path, 'r', encoding='utf-8') as f:
            inv_data = json.load(f)
        for item in inv_data:
            source_map[Path(item['file']).name] = item.get('source', 'unknown')
    
    if SPLIT_DIR.exists():
        for f in sorted(SPLIT_DIR.glob("clip_*.mp4")):
            dur = get_duration(f)
            if dur < MIN_CLIP_SEC or dur == 0:
                continue
            year = extract_year(f.name)
            
            candidates.append({
                'file': str(f),
                'name': f.name,
                'year': year,
                'duration': round(dur, 1),
                'source': source_map.get(f.name, 'unknown'),
                'type': 'split',
                'score': _score_clip(f.name, year, dur),
            })
    
    log.info(f"\nTotal candidates: {len(candidates)}")
    
    # Sort by score (best first)
    candidates.sort(key=lambda c: c['score'], reverse=True)
    
    # DIVERSITY: Max clips per source to avoid 50x Chevrolet Leader News
    MAX_PER_SOURCE = 10  # Max clips from any single source file
    MAX_PER_YEAR = 10    # Max clips from any single year (ensures era spread)
    
    selected = []
    source_counts = {}
    year_counts = {}
    
    for c in candidates:
        if len(selected) >= TARGET_CLIPS:
            break
        
        # Group by actual source compilation (e.g. "Part_I.mp4" vs "Part_II.mp4")
        if c['type'] == 'individual':
            src_key = c['name']
        else:
            src_key = c.get('source', c['name'][:35])
        
        year_key = c['year']
        
        if source_counts.get(src_key, 0) >= MAX_PER_SOURCE:
            continue
        if year_counts.get(year_key, 0) >= MAX_PER_YEAR:
            continue
        
        selected.append(c)
        source_counts[src_key] = source_counts.get(src_key, 0) + 1
        year_counts[year_key] = year_counts.get(year_key, 0) + 1
    
    # Re-sort chronologically
    selected.sort(key=lambda c: (c['year'], c['name']))
    
    # Create symlinks or copy to curated dir + generate playlist
    playlist = []
    
    print(f"\n{'='*70}")
    print(f"  TOP {TARGET_CLIPS} CURATED CLIPS — Chronological Order")
    print(f"{'='*70}")
    
    for idx, clip in enumerate(selected):
        num = idx + 1
        src = Path(clip['file'])
        # Numbered + chronological name
        out_name = f"{num:03d}_{clip['year']}_{src.stem[len('clip_YYYY_'):] if clip['type']=='split' else src.stem}.mp4"
        # Clean up long names
        if len(out_name) > 80:
            out_name = out_name[:76] + ".mp4"
        
        dst = CURATED_DIR / out_name
        
        clip['curated_name'] = out_name
        clip['curated_index'] = num
        playlist.append(clip)
        
        # Create hardlink (no disk space wasted)
        if not dst.exists():
            try:
                os.link(str(src), str(dst))
            except OSError:
                # Cross-drive? Use copy
                import shutil
                shutil.copy2(str(src), str(dst))
        
        dur_str = f"{clip['duration']:.0f}s"
        print(f"  {num:3d}. ({clip['year']}) {out_name[:55]:<55} {dur_str:>5}")
    
    # Year distribution
    years = {}
    for c in selected:
        y = c['year']
        years[y] = years.get(y, 0) + 1
    
    total_dur = sum(c['duration'] for c in selected)
    
    print(f"\n{'-'*70}")
    print(f"  STATISTICS:")
    print(f"  Total clips:    {len(selected)}")
    print(f"  Total duration: {total_dur/60:.0f} min ({total_dur/3600:.1f} hours)")
    print(f"  Year range:     {min(c['year'] for c in selected)}-{max(c['year'] for c in selected)}")
    print(f"  Duration range: {min(c['duration'] for c in selected):.0f}s - {max(c['duration'] for c in selected):.0f}s")
    print(f"  Avg duration:   {total_dur/len(selected):.0f}s")
    print(f"\n  Year distribution:")
    for y in sorted(years):
        bar = '#' * years[y]
        print(f"    {y}: {bar} ({years[y]})")
    print(f"{'='*70}")
    
    # Save inventory
    with open(INVENTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump({
            'created': datetime.now().isoformat(),
            'total_clips': len(selected),
            'total_duration_sec': round(total_dur),
            'year_distribution': dict(sorted(years.items())),
            'clips': playlist,
        }, f, indent=2, ensure_ascii=False)
    
    log.info(f"Inventory saved: {INVENTORY_PATH}")
    
    # Save M3U playlist
    m3u_path = CURATED_DIR / "playlist_100_clips.m3u"
    with open(m3u_path, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for clip in playlist:
            f.write(f"#EXTINF:{int(clip['duration'])},{clip['curated_name']}\n")
            f.write(f"{clip['curated_name']}\n")
    log.info(f"Playlist saved: {m3u_path}")
    
    return selected


def _score_clip(name, year, duration):
    """
    Score a clip for quality/relevance (higher = better).
    
    Scoring factors:
    - Duration in ideal range (20-90s): +30 points
    - Era match for Wochenschau (1935-1955): +20 points
    - Known brand/type keywords: +10 points
    - Not too short (>15s): +5 points
    - Not too long (<180s): +5 points
    """
    score = 50  # Base score
    
    # Duration scoring
    if IDEAL_MIN <= duration <= IDEAL_MAX:
        score += 30  # Perfect length for commercial break
    elif MIN_CLIP_SEC <= duration <= MAX_CLIP_SEC:
        score += 15  # Acceptable
    elif duration < MIN_CLIP_SEC:
        score -= 20  # Too short
    elif duration > MAX_CLIP_SEC:
        score -= 10  # Too long
    
    # Era scoring (Wochenschau is 1939-1945, broader era 1935-1960)
    if 1939 <= year <= 1945:
        score += 25  # Perfect wartime match
    elif 1935 <= year <= 1955:
        score += 15  # Good era
    elif 1930 <= year <= 1960:
        score += 5   # Acceptable
    
    # Content scoring (known good content types)
    name_lower = name.lower()
    brand_keywords = [
        ('coca-cola', 15), ('coca_cola', 15),
        ('lucky_strike', 15), ('cigarette', 10),
        ('war_bond', 20), ('victory', 15),
        ('chevrolet', 10), ('lincoln', 10),
        ('general_electric', 12), ('frigidaire', 12),
        ('kodak', 12), ('univac', 15),
        ('cheerios', 8), ('pepsi', 10),
    ]
    for kw, bonus in brand_keywords:
        if kw in name_lower:
            score += bonus
            break  # Only one brand bonus
    
    # Individual clips (already curated) get a bonus
    if not name.startswith('clip_'):
        score += 10
    
    return score


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    args = sys.argv[1:]

    if '--help' in args or '-h' in args or not args:
        print(__doc__)
        sys.exit(0)

    if '--analyze' in args:
        analyze_inventory()

    elif '--split' in args:
        split_compilations()

    elif '--curate' in args:
        curate_100()

    elif '--all' in args:
        log.info("FULL PIPELINE: Split -> Curate")
        split_compilations()
        curate_100()

    else:
        print("Unknown command. Use --help for usage.")
