#!/usr/bin/env python3
"""
Wochenschau Cross-Reference Inventory
Vergleicht: Todo-Originale vs Enhanced (MediaArchive) vs YouTube
Erstellt einen vollständigen Statusbericht.
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# === PATHS ===
TODO_DIR = Path(r"V:\OriginalSources\German_Historical\Wochenschau_Certified\Todo")
ENHANCED_DIR = Path(r"V:\MediaArchive\DeutscheWochenschau")
SNAPSHOT_FILE = Path(r"D:\remaike.TV\config\channel_snapshot_2026_02_06.json")
OUTPUT_FILE = Path(r"D:\remaike.TV\config\wochenschau_inventory.json")

def extract_nr(filename):
    """Extract Wochenschau number from filename."""
    m = re.search(r'Nr(\d+)', filename)
    return int(m.group(1)) if m else None

def extract_date(filename):
    """Extract date from filename like _1940-05-29_."""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return m.group(1) if m else None

def extract_duration(filename):
    """Extract duration from filename like _42min_."""
    m = re.search(r'(\d+)min', filename)
    return int(m.group(1)) if m else None

def scan_todo():
    """Scan Todo originals folder."""
    results = {}
    if not TODO_DIR.exists():
        print(f"⚠️ Todo dir not found: {TODO_DIR}")
        return results
    
    for f in TODO_DIR.iterdir():
        if f.suffix.lower() in ('.mp4', '.avi', '.mkv', '.mov', '.wmv'):
            nr = extract_nr(f.name)
            if nr and '_FIXED' not in f.name:
                results[nr] = {
                    'filename': f.name,
                    'date': extract_date(f.name),
                    'duration_min': extract_duration(f.name),
                    'size_mb': round(f.stat().st_size / 1024 / 1024, 1),
                    'has_fixed': False
                }
            elif nr and '_FIXED' in f.name:
                if nr in results:
                    results[nr]['has_fixed'] = True
                else:
                    results[nr] = {
                        'filename': f.name.replace('_FIXED', ''),
                        'date': extract_date(f.name),
                        'duration_min': extract_duration(f.name),
                        'size_mb': round(f.stat().st_size / 1024 / 1024, 1),
                        'has_fixed': True
                    }
    return results

def scan_enhanced():
    """Scan enhanced/upscaled versions folder."""
    results = {}
    if not ENHANCED_DIR.exists():
        print(f"⚠️ Enhanced dir not found: {ENHANCED_DIR}")
        return results
    
    for f in ENHANCED_DIR.iterdir():
        if f.suffix.lower() == '.mp4' and '.temp.' not in f.name:
            nr = extract_nr(f.name)
            if nr:
                results[nr] = {
                    'filename': f.name,
                    'date': extract_date(f.name),
                    'duration_min': extract_duration(f.name),
                    'size_mb': round(f.stat().st_size / 1024 / 1024, 1),
                    'has_sls': '_sls' in f.name
                }
    
    # Also check for temp files (incomplete upscales)
    temp_nrs = set()
    for f in ENHANCED_DIR.iterdir():
        if '.temp.' in f.name:
            nr = extract_nr(f.name)
            if nr and nr not in results:
                temp_nrs.add(nr)
    
    return results, temp_nrs

def scan_youtube():
    """Scan YouTube channel snapshot for Wochenschau videos."""
    results = {}
    if not SNAPSHOT_FILE.exists():
        print(f"⚠️ Snapshot not found: {SNAPSHOT_FILE}")
        return results
    
    with open(SNAPSHOT_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    # Handle nested format
    if isinstance(raw, dict) and 'all_videos' in raw:
        data = raw['all_videos']
    elif isinstance(raw, list):
        data = raw
    else:
        print("  ⚠️ Unknown snapshot format")
        return results
    
    for v in data:
        title = v.get('title', '')
        if 'wochenschau' in title.lower() or 'newsreel' in title.lower():
            nr = extract_nr(title)
            if not nr:
                # Try extracting from description or tags
                m = re.search(r'Nr\.?\s*(\d+)', title)
                if m:
                    nr = int(m.group(1))
            if not nr:
                # Try from number patterns like "751"
                m = re.search(r'(\d{3})', title)
                if m:
                    candidate = int(m.group(1))
                    if 459 <= candidate <= 755:
                        nr = candidate
            
            if nr:
                results[nr] = {
                    'video_id': v['id'],
                    'title': title,
                    'status': v.get('status', 'unknown'),
                    'views': v.get('views', 0)
                }
            else:
                print(f"  ⚠️ Could not extract Nr from: {title} (ID: {v['id']})")
    
    return results

def main():
    print("=" * 70)
    print("  WOCHENSCHAU CROSS-REFERENCE INVENTORY")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    # Scan all 3 sources
    print("\n📁 Scanning Todo originals...")
    todo = scan_todo()
    print(f"   Found: {len(todo)} episodes")
    
    print("\n📁 Scanning Enhanced (MediaArchive)...")
    enhanced, temp_nrs = scan_enhanced()
    print(f"   Found: {len(enhanced)} completed + {len(temp_nrs)} incomplete")
    
    print("\n📺 Scanning YouTube channel...")
    youtube = scan_youtube()
    print(f"   Found: {len(youtube)} episodes")
    
    # All known numbers
    all_nrs = sorted(set(list(todo.keys()) + list(enhanced.keys()) + list(youtube.keys())))
    
    # Categorize
    ready_to_upload = []     # Enhanced but NOT on YouTube
    needs_upscale = []       # In Todo but NOT enhanced
    already_done = []        # Enhanced AND on YouTube
    on_yt_only = []          # On YouTube but not in Todo (already removed from todo?)
    incomplete_upscale = []  # Has temp files (upscale in progress)
    
    for nr in all_nrs:
        in_todo = nr in todo
        in_enhanced = nr in enhanced
        in_youtube = nr in youtube
        in_temp = nr in temp_nrs
        
        entry = {
            'nr': nr,
            'date': todo[nr]['date'] if in_todo else (enhanced[nr]['date'] if in_enhanced else None),
        }
        
        if in_enhanced and in_youtube:
            entry['youtube_id'] = youtube[nr]['video_id']
            entry['youtube_title'] = youtube[nr]['title']
            entry['enhanced_file'] = enhanced[nr]['filename']
            entry['size_mb'] = enhanced[nr]['size_mb']
            already_done.append(entry)
        elif in_enhanced and not in_youtube:
            entry['enhanced_file'] = enhanced[nr]['filename']
            entry['size_mb'] = enhanced[nr]['size_mb']
            entry['duration_min'] = enhanced[nr]['duration_min']
            ready_to_upload.append(entry)
        elif in_todo and not in_enhanced and not in_youtube:
            if in_temp:
                entry['status'] = 'upscale_incomplete'
                entry['source_file'] = todo[nr]['filename']
                entry['duration_min'] = todo[nr]['duration_min']
                incomplete_upscale.append(entry)
            else:
                entry['source_file'] = todo[nr]['filename']
                entry['duration_min'] = todo[nr]['duration_min']
                entry['size_mb'] = todo[nr]['size_mb']
                needs_upscale.append(entry)
        elif in_youtube and not in_todo and not in_enhanced:
            entry['youtube_id'] = youtube[nr]['video_id']
            entry['youtube_title'] = youtube[nr]['title']
            on_yt_only.append(entry)
        elif in_todo and in_youtube and not in_enhanced:
            # On YouTube but enhanced file missing/cleaned up
            entry['youtube_id'] = youtube[nr]['video_id']
            entry['youtube_title'] = youtube[nr]['title']
            entry['source_file'] = todo[nr]['filename']
            already_done.append(entry)
    
    # === REPORT ===
    print("\n" + "=" * 70)
    print("  📊 ERGEBNISSE")
    print("=" * 70)
    
    print(f"\n✅ BEREITS FERTIG (Enhanced + YouTube): {len(already_done)}")
    for e in sorted(already_done, key=lambda x: x['nr']):
        yt = e.get('youtube_title', 'N/A')[:60]
        print(f"   Nr{e['nr']} ({e['date']}) → {yt}")
    
    print(f"\n🚀 BEREIT ZUM UPLOAD (Enhanced, noch nicht auf YT): {len(ready_to_upload)}")
    total_upload_size = 0
    total_upload_min = 0
    for e in sorted(ready_to_upload, key=lambda x: x['nr']):
        sz = e.get('size_mb', 0)
        dur = e.get('duration_min', 0)
        total_upload_size += sz
        total_upload_min += dur
        print(f"   Nr{e['nr']} ({e['date']}) | {dur}min | {sz:.0f} MB | {e['enhanced_file']}")
    if ready_to_upload:
        print(f"   {'─' * 50}")
        print(f"   TOTAL: {len(ready_to_upload)} Videos | {total_upload_min} min | {total_upload_size/1024:.1f} GB")
    
    print(f"\n⏳ UPSCALE NÖTIG (In Todo, noch nicht enhanced): {len(needs_upscale)}")
    total_todo_min = 0
    for e in sorted(needs_upscale, key=lambda x: x['nr']):
        dur = e.get('duration_min', 0)
        total_todo_min += dur
        print(f"   Nr{e['nr']} ({e['date']}) | {dur}min | {e['source_file']}")
    if needs_upscale:
        print(f"   {'─' * 50}")
        print(f"   TOTAL: {len(needs_upscale)} Videos | {total_todo_min} min")
    
    if incomplete_upscale:
        print(f"\n🔄 UPSCALE LÄUFT/ABGEBROCHEN (temp files): {len(incomplete_upscale)}")
        for e in sorted(incomplete_upscale, key=lambda x: x['nr']):
            print(f"   Nr{e['nr']} ({e['date']}) | {e.get('duration_min', '?')}min")
    
    if on_yt_only:
        print(f"\n📺 NUR AUF YOUTUBE (nicht im Todo-Ordner): {len(on_yt_only)}")
        for e in sorted(on_yt_only, key=lambda x: x['nr']):
            print(f"   Nr{e['nr']} ({e['date']}) → {e.get('youtube_title', 'N/A')[:60]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"  Gesamt-Episoden im System:        {len(all_nrs)}")
    print(f"  ✅ Fertig (Enhanced + YouTube):    {len(already_done)}")
    print(f"  🚀 Bereit zum Upload:             {len(ready_to_upload)}")
    print(f"  ⏳ Upscale nötig:                 {len(needs_upscale)}")
    print(f"  🔄 Upscale unvollständig:         {len(incomplete_upscale)}")
    print(f"  📺 Nur auf YouTube:               {len(on_yt_only)}")
    print(f"  ")
    print(f"  Nr-Range: {min(all_nrs)} – {max(all_nrs)}")
    if ready_to_upload:
        print(f"  Upload-Volumen: {total_upload_size/1024:.1f} GB ({total_upload_min} min)")
    if needs_upscale:
        print(f"  Upscale-Volumen: {total_todo_min} min Rohmaterial")
    
    # Missing numbers (gaps)
    full_range = set(range(min(all_nrs), max(all_nrs) + 1))
    missing = sorted(full_range - set(all_nrs))
    if missing:
        print(f"\n  ❓ Fehlende Nummern (Lücken): {len(missing)}")
        # Group consecutive
        groups = []
        start = missing[0]
        prev = missing[0]
        for n in missing[1:]:
            if n == prev + 1:
                prev = n
            else:
                groups.append((start, prev))
                start = n
                prev = n
        groups.append((start, prev))
        for s, e in groups:
            if s == e:
                print(f"     Nr{s}")
            else:
                print(f"     Nr{s}-Nr{e} ({e-s+1} Stück)")
    
    # Save JSON report
    report = {
        'generated': datetime.now().isoformat(),
        'summary': {
            'total_episodes': len(all_nrs),
            'done': len(already_done),
            'ready_to_upload': len(ready_to_upload),
            'needs_upscale': len(needs_upscale),
            'incomplete_upscale': len(incomplete_upscale),
            'youtube_only': len(on_yt_only),
            'missing_numbers': len(missing),
            'nr_range': f"{min(all_nrs)}-{max(all_nrs)}",
            'upload_volume_gb': round(total_upload_size / 1024, 1) if ready_to_upload else 0,
            'upscale_volume_min': total_todo_min
        },
        'ready_to_upload': sorted(ready_to_upload, key=lambda x: x['nr']),
        'needs_upscale': sorted(needs_upscale, key=lambda x: x['nr']),
        'incomplete_upscale': sorted(incomplete_upscale, key=lambda x: x['nr']),
        'already_done': sorted(already_done, key=lambda x: x['nr']),
        'youtube_only': sorted(on_yt_only, key=lambda x: x['nr']),
        'missing_numbers': missing
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Report gespeichert: {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
