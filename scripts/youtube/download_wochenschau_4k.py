#!/usr/bin/env python3
"""Download all public Wochenschau videos from remAIke_IT in 4K for streaming.

Usage:
    python scripts/youtube/download_wochenschau_4k.py           # Download all
    python scripts/youtube/download_wochenschau_4k.py --status  # Check status
    python scripts/youtube/download_wochenschau_4k.py --dry-run # Show what would download
"""

import json
import os
import sys
import subprocess
import argparse
import re

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path
from datetime import datetime

# ─── Config ─────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
CHANNEL_SCAN = ROOT / 'config' / 'fresh_channel_scan.json'
DOWNLOAD_DIR = Path(r'D:\remaike.TV\watch\wochenschau_stream')  # 4K downloads for streaming
LOG_FILE = ROOT / 'logs' / 'wochenschau_download.log'

# yt-dlp format: best 4K (2160p) video + best audio, merge to mp4
FORMAT_4K = 'bestvideo[height<=2160]+bestaudio/best[height<=2160]/best'

# Output template: Wochenschau_Nr{episode}_{date}.mp4
OUTPUT_TEMPLATE = str(DOWNLOAD_DIR / '%(title)s.%(ext)s')


def log(msg):
    """Log to console and file."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def get_wochenschau_videos():
    """Extract public Wochenschau video IDs from channel scan."""
    with open(CHANNEL_SCAN, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    ws = [v for v in videos 
          if 'wochenschau' in v.get('snippet', {}).get('title', '').lower()
          and v.get('status', {}).get('privacyStatus', '') == 'public']
    
    # Deduplicate by title (keep first occurrence)
    seen_titles = set()
    unique = []
    for v in ws:
        title = v['snippet']['title']
        if title not in seen_titles:
            seen_titles.add(title)
            unique.append({
                'id': v['id'],
                'title': title,
                'url': f"https://www.youtube.com/watch?v={v['id']}",
            })
    
    # Sort by episode number
    def extract_num(item):
        m = re.search(r'wochenschau\s*(\d+)', item['title'], re.IGNORECASE)
        return int(m.group(1)) if m else 9999
    
    unique.sort(key=extract_num)
    return unique


def get_downloaded():
    """Check what's already downloaded."""
    if not DOWNLOAD_DIR.exists():
        return set()
    
    downloaded = set()
    for f in DOWNLOAD_DIR.iterdir():
        if f.suffix.lower() in ('.mp4', '.mkv', '.webm'):
            # Extract episode number from filename
            m = re.search(r'wochenschau\s*(\d+)', f.name, re.IGNORECASE)
            if m:
                downloaded.add(int(m.group(1)))
    return downloaded


def download_video(video, dry_run=False):
    """Download a single video in 4K using yt-dlp."""
    vid_id = video['id']
    title = video['title']
    url = video['url']
    
    if dry_run:
        log(f"[DRY-RUN] Would download: {title}")
        return True
    
    log(f"Downloading: {title}")
    
    cmd = [
        'yt-dlp',
        '--format', FORMAT_4K,
        '--merge-output-format', 'mp4',
        '--output', OUTPUT_TEMPLATE,
        '--no-playlist',
        '--retries', '10',
        '--fragment-retries', '10',
        '--no-overwrites',
        '--embed-metadata',
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode == 0:
            log(f"  ✅ OK: {title}")
            return True
        else:
            # Check if already downloaded
            if 'has already been downloaded' in result.stdout:
                log(f"  ⏭️ Already exists: {title}")
                return True
            log(f"  ❌ FAILED: {title}")
            log(f"  stderr: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        log(f"  ⏰ TIMEOUT: {title}")
        return False
    except Exception as e:
        log(f"  ❌ ERROR: {title} - {e}")
        return False


def rename_to_standard(download_dir):
    """Rename downloaded files to standard format: Wochenschau_Nr{NUM}_{title}.mp4"""
    if not download_dir.exists():
        return
    
    for f in download_dir.iterdir():
        if not f.suffix.lower() == '.mp4':
            continue
        
        # Extract episode number
        m = re.search(r'wochenschau\s*(\d+)', f.name, re.IGNORECASE)
        if not m:
            continue
        
        num = m.group(1)
        # Already in standard format?
        if f.name.startswith(f'Wochenschau_Nr{num}'):
            continue
        
        # Extract event from title: "Wochenschau 513: Channel Islands (Jul 1940) | 8K"
        event_m = re.search(r':\s*(.+?)\s*\(', f.name)
        event = event_m.group(1).replace(' ', '_') if event_m else 'Unknown'
        
        new_name = f'Wochenschau_Nr{num}_{event}.mp4'
        new_path = f.parent / new_name
        
        if not new_path.exists():
            f.rename(new_path)
            print(f"  Renamed: {f.name} → {new_name}")


def main():
    parser = argparse.ArgumentParser(description='Download Wochenschau videos in 4K')
    parser.add_argument('--status', action='store_true', help='Show download status')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded')
    parser.add_argument('--rename', action='store_true', help='Rename downloads to standard format')
    parser.add_argument('--count', type=int, default=0, help='Limit number of downloads (0=all)')
    args = parser.parse_args()
    
    videos = get_wochenschau_videos()
    downloaded = get_downloaded()
    
    print(f"\n{'='*60}")
    print(f"  Wochenschau 4K Downloader")
    print(f"{'='*60}")
    print(f"  Channel videos:  {len(videos)}")
    print(f"  Already downloaded: {len(downloaded)}")
    print(f"  Remaining:       {len(videos) - len(downloaded)}")
    print(f"  Download dir:    {DOWNLOAD_DIR}")
    print(f"{'='*60}\n")
    
    if args.rename:
        rename_to_standard(DOWNLOAD_DIR)
        return
    
    if args.status:
        for v in videos:
            m = re.search(r'wochenschau\s*(\d+)', v['title'], re.IGNORECASE)
            num = int(m.group(1)) if m else 0
            status = '[x]' if num in downloaded else '[ ]'
            print(f"  {status} {v['title']}")
        return
    
    # Download
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    to_download = []
    for v in videos:
        m = re.search(r'wochenschau\s*(\d+)', v['title'], re.IGNORECASE)
        num = int(m.group(1)) if m else 0
        if num not in downloaded:
            to_download.append(v)
    
    if args.count > 0:
        to_download = to_download[:args.count]
    
    if not to_download:
        print("  All videos already downloaded!")
        return
    
    log(f"Starting download of {len(to_download)} videos...")
    
    success = 0
    failed = 0
    for i, v in enumerate(to_download, 1):
        log(f"\n[{i}/{len(to_download)}]")
        if download_video(v, dry_run=args.dry_run):
            success += 1
        else:
            failed += 1
    
    log(f"\n{'='*60}")
    log(f"  Done! {success} downloaded, {failed} failed")
    log(f"{'='*60}")
    
    # Auto-rename after download
    if not args.dry_run:
        rename_to_standard(DOWNLOAD_DIR)


if __name__ == '__main__':
    main()
