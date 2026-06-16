"""Analyze and rename downloaded vintage commercials to proper descriptive names."""
import json
import os
import shutil
from pathlib import Path

CATALOG = json.load(open('config/vintage_commercials_catalog.json', 'r', encoding='utf-8'))
DL_DIR = Path(r'V:\Commercials\Vintage')
LOCAL_DIRS = [
    Path(r'V:\OriginalSources\Commercials'),
    Path(r'V:\OriginalSources\MusicVideos'),
    Path(r'V:\OriginalSources\_sources\christmas\GERMANY'),
    Path(r'V:\OriginalSources\_sources\christmas\UK'),
    Path(r'V:\MediaArchive\HISTORIC_CATS\1903'),
]


def clean_filename(title, year):
    """Create a clean, descriptive filename from title and year."""
    clean = title.replace(':', ' -').replace('/', '_').replace('\\', '_')
    clean = clean.replace('  ', ' ').strip()
    clean = clean.replace(' ', '_')
    for c in ['<', '>', '|', '?', '*', '"', "'", '(', ')']:
        clean = clean.replace(c, '')
    return f"Commercial_{year}_{clean}.mp4"


def build_id_map():
    """Build mapping from archive ID to proper file info."""
    id_map = {}
    for cat_id, cat in CATALOG.get('categories', {}).items():
        for item in cat.get('items', []):
            aid = item.get('id', '')
            if aid:
                title = item.get('title', aid)
                year = item.get('year', '')
                id_map[aid.lower()] = {
                    'id': aid,
                    'title': title,
                    'year': year,
                    'category': cat_id,
                    'label': cat.get('label', cat_id),
                    'proper_name': clean_filename(title, year),
                }
    return id_map


def analyze():
    """Full analysis of all downloaded files."""
    id_map = build_id_map()
    
    print(f"\n{'='*72}")
    print(f"  VINTAGE COMMERCIALS - NAMING AUDIT")
    print(f"{'='*72}")
    print(f"  Catalog: {len(id_map)} items with Archive.org IDs")
    print()
    
    # 1. Downloaded files in V:\Commercials\Vintage
    print(f"{'─'*72}")
    print(f"  DOWNLOADED FILES (V:\\Commercials\\Vintage)")
    print(f"{'─'*72}")
    
    rename_plan = []
    
    if DL_DIR.exists():
        for f in sorted(DL_DIR.iterdir()):
            if not f.is_file():
                continue
            size_mb = f.stat().st_size / 1024 / 1024
            fname = f.name
            
            # Match to catalog
            matched = None
            for aid, info in id_map.items():
                if aid in fname.lower():
                    matched = info
                    break
            
            if matched:
                proper = matched['proper_name']
                needs_rename = fname != proper
                status = "RENAME" if needs_rename else "OK"
                
                print(f"\n  [{status}] {matched['label']} ({matched['year']})")
                print(f"    Current:  {fname}")
                print(f"    Proper:   {proper}")
                print(f"    Size:     {size_mb:.1f} MB")
                print(f"    Content:  {matched['title']}")
                
                if needs_rename:
                    rename_plan.append({
                        'old': f,
                        'new': DL_DIR / proper,
                        'title': matched['title'],
                    })
            else:
                print(f"\n  [???] NO CATALOG MATCH")
                print(f"    Current:  {fname}")
                print(f"    Size:     {size_mb:.1f} MB")
    else:
        print("  Directory does not exist!")
    
    # 2. Local source files 
    print(f"\n{'─'*72}")
    print(f"  LOCAL SOURCE FILES (already on disk)")
    print(f"{'─'*72}")
    
    for d in LOCAL_DIRS:
        if d.exists():
            for f in d.iterdir():
                if f.is_file() and f.suffix.lower() in ['.mp4', '.webm', '.avi', '.mkv']:
                    name_lower = f.name.lower()
                    if any(kw in name_lower for kw in ['commercial', 'advert', 'lucky', 'cigarette', 'coca', 'pepsi']):
                        size_mb = f.stat().st_size / 1024 / 1024
                        print(f"  [LOCAL] {f.name} ({size_mb:.1f} MB)")
                        print(f"    Path: {f}")
    
    # 3. Summary
    print(f"\n{'='*72}")
    print(f"  RENAME SUMMARY")
    print(f"{'='*72}")
    print(f"  Files to rename: {len(rename_plan)}")
    for item in rename_plan:
        print(f"    {item['old'].name}")
        print(f"    -> {item['new'].name}")
        print()
    
    return rename_plan


def rename_files(plan, dry_run=False):
    """Execute the rename plan."""
    print(f"\n{'='*72}")
    print(f"  RENAMING {'(DRY RUN)' if dry_run else '(EXECUTING)'}")
    print(f"{'='*72}")
    
    success = 0
    failed = 0
    
    for item in plan:
        old_path = item['old']
        new_path = item['new']
        
        if new_path.exists():
            print(f"  SKIP (target exists): {new_path.name}")
            continue
        
        print(f"  {old_path.name}")
        print(f"  -> {new_path.name}")
        
        if not dry_run:
            try:
                old_path.rename(new_path)
                print(f"  OK!")
                success += 1
            except Exception as e:
                print(f"  FAILED: {e}")
                failed += 1
        else:
            print(f"  (would rename)")
            success += 1
        print()
    
    print(f"  Done: {success} renamed, {failed} failed")


if __name__ == '__main__':
    import sys
    plan = analyze()
    
    if '--rename' in sys.argv:
        if plan:
            rename_files(plan, dry_run=False)
        else:
            print("\n  Nothing to rename!")
    elif '--dry-run' in sys.argv:
        if plan:
            rename_files(plan, dry_run=True)
    elif plan:
        print(f"\n  Run with --rename to execute, or --dry-run to preview")
