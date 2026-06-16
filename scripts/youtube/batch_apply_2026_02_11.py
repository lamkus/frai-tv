#!/usr/bin/env python3
"""
Batch Apply Script – 2026-02-11
================================
Applies combined tag + description + title updates in ONE API call per video.
Reads from config/pending_updates/batch_2026_02_11.json (offline-prepared).

Usage:
  python batch_apply_2026_02_11.py --verify    # Offline validation only
  python batch_apply_2026_02_11.py --dry-run   # Fetch + compare (API read only)
  python batch_apply_2026_02_11.py --apply     # Apply changes (API write)
  python batch_apply_2026_02_11.py --apply --limit 50  # Apply first 50 only

Quota: Combined = 51 units per video (1 list + 50 update)
Bug fix: ONLY part="snippet" — NEVER add "status"!
"""

import json
import os
import sys
import time

# ---- Paths ----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
BATCH_PATH = os.path.join(ROOT_DIR, "config", "pending_updates", "batch_2026_02_11.json")
TOKEN_PATH = os.path.join(ROOT_DIR, "token.json")
REPORT_PATH = os.path.join(ROOT_DIR, "config", "pending_updates", "batch_report_2026_02_11.json")
PROGRESS_PATH = os.path.join(ROOT_DIR, "config", "pending_updates", "batch_progress_2026_02_11.json")
TODO_QUOTA_PATH = os.path.join(ROOT_DIR, ".copilot", "TODO_QUOTA.md")

# ---- Quota Config ----
DAILY_QUOTA = 10_000
RESERVE_PCT = 0.20
MAX_USABLE = int(DAILY_QUOTA * (1 - RESERVE_PCT))  # 8,000
COST_LIST = 1    # per batch of 50 IDs
COST_UPDATE = 50  # per video update


def load_batch():
    """Load the offline-prepared batch JSON."""
    if not os.path.exists(BATCH_PATH):
        print(f"❌ Batch file not found: {BATCH_PATH}")
        sys.exit(1)
    
    with open(BATCH_PATH, "r", encoding="utf-8") as f:
        batch = json.load(f)
    
    print(f"📦 Loaded batch v{batch['version']}")
    print(f"   Tag updates:  {batch['stats']['tag_updates']}")
    print(f"   Desc updates: {batch['stats']['desc_updates']}")
    print(f"   Title updates: {batch['stats']['title_updates']}")
    return batch


def build_combined_updates(batch):
    """Merge tag + desc + title changes per video ID, sorted by views (highest first)."""
    combined = {}  # id -> {tags_new, desc_hook, title_new, views, ...}
    
    # Index by video ID
    tag_map = {u['id']: u for u in batch.get('tag_updates', [])}
    desc_map = {u['id']: u for u in batch.get('desc_updates', [])}
    title_map = {u['id']: u for u in batch.get('title_updates', [])}
    
    all_ids = set(tag_map) | set(desc_map) | set(title_map)
    
    for vid in all_ids:
        entry = {
            'id': vid,
            'views': 0,
            'title_display': '',
            'changes': []
        }
        
        if vid in tag_map:
            t = tag_map[vid]
            entry['new_tags'] = t['new_tags']
            entry['added_tags'] = t.get('added', [])
            entry['removed_tags'] = t.get('removed', [])
            entry['views'] = max(entry['views'], t.get('views', 0))
            entry['title_display'] = t.get('title', '')
            entry['changes'].append('tags')
        
        if vid in desc_map:
            d = desc_map[vid]
            entry['new_line1'] = d['new_line1']
            entry['views'] = max(entry['views'], d.get('views', 0))
            entry['title_display'] = entry['title_display'] or d.get('title', '')
            entry['changes'].append('description')
        
        if vid in title_map:
            t = title_map[vid]
            entry['new_title'] = t['new_title']
            entry['views'] = max(entry['views'], t.get('views', 0))
            entry['title_display'] = entry['title_display'] or t.get('old_title', '')
            entry['changes'].append('title')
        
        combined[vid] = entry
    
    # Sort by views descending (highest impact first)
    sorted_updates = sorted(combined.values(), key=lambda x: -x['views'])
    
    print(f"\n📊 Combined: {len(sorted_updates)} unique videos")
    print(f"   Top-10 by views:")
    for u in sorted_updates[:10]:
        print(f"     {u['views']:>6} | {'+'.join(u['changes']):20} | {u['title_display'][:45]}")
    
    return sorted_updates


def get_youtube_service():
    """Build YouTube API service with OAuth credentials."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    if not os.path.exists(TOKEN_PATH):
        print(f"❌ token.json not found at {TOKEN_PATH}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print("🔄 Token refreshed")

    return build("youtube", "v3", credentials=creds)


def fetch_videos(youtube, video_ids):
    """Fetch video snippets in batches of 50. Uses part='snippet' ONLY."""
    videos = {}
    quota = 0
    
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        ids_str = ",".join(batch_ids)
        
        # ⚠️ CRITICAL: part="snippet" ONLY — NEVER add "status"!
        response = youtube.videos().list(
            part="snippet",
            id=ids_str
        ).execute()

        for item in response.get("items", []):
            videos[item["id"]] = item
        
        quota += COST_LIST
        batch_num = i // 50 + 1
        print(f"  📡 Batch {batch_num}: {len(response.get('items', []))} videos ({quota} quota used)")
        time.sleep(0.3)

    return videos, quota


def load_progress():
    """Load progress from previous run (for resume capability)."""
    if os.path.exists(PROGRESS_PATH):
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "quota_used": 0}


def save_progress(progress):
    """Save progress for resume capability."""
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def verify(batch):
    """Offline validation of all changes."""
    print("=" * 70)
    print("VERIFY — Offline Validation")
    print("=" * 70)
    
    updates = build_combined_updates(batch)
    
    errors = 0
    warnings = 0
    
    # Check tag changes
    print(f"\n── Tag Validation ──")
    for u in updates:
        if 'new_tags' in u:
            if len(u['new_tags']) > 15:
                print(f"  ❌ {u['id']}: {len(u['new_tags'])} tags (max 15!)")
                errors += 1
            elif len(u['new_tags']) < 10:
                print(f"  ⚠️  {u['id']}: Only {len(u['new_tags'])} tags (low)")
                warnings += 1
    
    # Check title changes
    print(f"\n── Title Validation ──")
    for u in updates:
        if 'new_title' in u:
            t = u['new_title']
            if len(t) > 70:
                print(f"  ❌ {u['id']}: [{len(t)}] {t}")
                errors += 1
            else:
                print(f"  ✅ {u['id']}: [{len(t)}] {t[:60]}")
    
    # Check desc hooks
    print(f"\n── Description Hook Validation ──")
    hook_count = sum(1 for u in updates if 'new_line1' in u)
    print(f"  {hook_count} videos will get new description Line 1")
    
    # Quota estimate
    print(f"\n── Quota Estimate ──")
    list_calls = (len(updates) + 49) // 50  # Ceiling division
    update_calls = len(updates)
    total_quota = list_calls * COST_LIST + update_calls * COST_UPDATE
    print(f"  List calls:   {list_calls} × {COST_LIST} = {list_calls * COST_LIST}")
    print(f"  Update calls: {update_calls} × {COST_UPDATE} = {update_calls * COST_UPDATE}")
    print(f"  Total:        {total_quota} / {DAILY_QUOTA}")
    print(f"  Budget:       {'✅ OK' if total_quota <= MAX_USABLE else '⚠️ OVER BUDGET'}")
    
    print(f"\n{'=' * 70}")
    print(f"  Errors:   {errors}")
    print(f"  Warnings: {warnings}")
    return errors == 0


def dry_run(youtube, batch, limit=None):
    """Fetch current state and show what would change."""
    print("=" * 70)
    print("DRY RUN — Fetch + Compare")
    print("=" * 70)
    
    updates = build_combined_updates(batch)
    if limit:
        updates = updates[:limit]
        print(f"  (limited to {limit} videos)")
    
    video_ids = [u['id'] for u in updates]
    print(f"\n📡 Fetching {len(video_ids)} videos from YouTube API...")
    current_videos, quota = fetch_videos(youtube, video_ids)
    
    changes_count = 0
    skipped = 0
    not_found = 0
    
    for u in updates:
        vid = u['id']
        if vid not in current_videos:
            print(f"  ❓ {vid} — NOT FOUND")
            not_found += 1
            continue
        
        snippet = current_videos[vid]["snippet"]
        has_change = False
        
        # Check tags
        if 'new_tags' in u:
            current_tags = set(snippet.get("tags", []))
            new_tags = set(u['new_tags'])
            if current_tags != new_tags:
                added = new_tags - current_tags
                removed = current_tags - new_tags
                print(f"  🏷️  {vid} | {u['title_display'][:40]}")
                if added:
                    print(f"      +TAGS: {', '.join(added)}")
                if removed:
                    print(f"      -TAGS: {', '.join(removed)}")
                has_change = True
        
        # Check title
        if 'new_title' in u:
            if snippet["title"] != u['new_title']:
                print(f"  📝 {vid} TITLE")
                print(f"      NOW: {snippet['title'][:55]}")
                print(f"      NEW: {u['new_title'][:55]}")
                has_change = True
        
        # Check desc
        if 'new_line1' in u:
            current_desc = snippet.get("description", "")
            current_line1 = current_desc.split('\n')[0][:80] if current_desc else ''
            print(f"  📄 {vid} DESC L1")
            print(f"      NOW: {current_line1[:60]}")
            print(f"      NEW: {u['new_line1'][:60]}")
            has_change = True
        
        if has_change:
            changes_count += 1
        else:
            skipped += 1
    
    print(f"\n{'=' * 70}")
    print(f"DRY RUN RESULTS")
    print(f"  Changes:  {changes_count} videos")
    print(f"  Skipped:  {skipped} (already correct)")
    print(f"  Missing:  {not_found}")
    print(f"  Quota (read): {quota} units used")
    print(f"  Quota (if apply): ~{quota + changes_count * COST_UPDATE} units")
    print(f"\nRun with --apply to execute.")


def apply_changes(youtube, batch, limit=None):
    """Apply all combined changes to YouTube API."""
    print("=" * 70)
    print("APPLYING Batch Updates")
    print("=" * 70)
    
    updates = build_combined_updates(batch)
    
    # Load progress for resume
    progress = load_progress()
    completed_ids = set(progress.get("completed", []))
    
    # Filter out already completed
    remaining = [u for u in updates if u['id'] not in completed_ids]
    if completed_ids:
        print(f"  ♻️  Resuming: {len(completed_ids)} already done, {len(remaining)} remaining")
    
    if limit:
        remaining = remaining[:limit]
        print(f"  (limited to {limit} videos)")
    
    video_ids = [u['id'] for u in remaining]
    if not video_ids:
        print("  ✅ Nothing to do — all videos already updated!")
        return
    
    print(f"\n📡 Fetching {len(video_ids)} videos from YouTube API...")
    current_videos, quota_used = fetch_videos(youtube, video_ids)
    
    updated = 0
    skipped = 0
    errors = 0
    
    for u in remaining:
        vid = u['id']
        
        if vid not in current_videos:
            print(f"  ❓ {vid} — NOT FOUND, skipping")
            continue
        
        snippet = current_videos[vid]["snippet"]
        need_update = False
        
        # Build snippet update — start with current values
        update_snippet = {
            "title": snippet["title"],
            "description": snippet.get("description", ""),
            "tags": list(snippet.get("tags", [])),
            "categoryId": snippet["categoryId"],
        }
        
        # Apply tag changes
        if 'new_tags' in u:
            current_set = set(update_snippet["tags"])
            new_set = set(u['new_tags'])
            if current_set != new_set:
                update_snippet["tags"] = u['new_tags']
                need_update = True
        
        # Apply title change
        if 'new_title' in u:
            if update_snippet["title"] != u['new_title']:
                update_snippet["title"] = u['new_title']
                need_update = True
        
        # Apply description Line 1 change
        if 'new_line1' in u:
            desc = update_snippet["description"]
            lines = desc.split('\n')
            current_line1 = lines[0].strip() if lines else ''
            title = snippet["title"]
            
            # Only replace if current Line 1 is still a title copy
            if current_line1.lower().strip() == title.lower().strip():
                lines[0] = u['new_line1']
                update_snippet["description"] = '\n'.join(lines)
                need_update = True
        
        if not need_update:
            print(f"  ⏭️  {vid} — Already correct: {snippet['title'][:45]}")
            skipped += 1
            completed_ids.add(vid)
            continue
        
        # Check quota budget
        if quota_used + COST_UPDATE > MAX_USABLE:
            print(f"\n⚠️  QUOTA BUDGET REACHED ({quota_used}/{MAX_USABLE})! Stopping.")
            print(f"    Remaining: {len(remaining) - updated - skipped} videos")
            break
        
        # ⚠️ CRITICAL: part="snippet" ONLY!
        try:
            youtube.videos().update(
                part="snippet",
                body={
                    "id": vid,
                    "snippet": update_snippet
                }
            ).execute()
            
            quota_used += COST_UPDATE
            updated += 1
            changes = '+'.join(u['changes'])
            print(f"  ✅ {vid} [{changes}] {snippet['title'][:40]} ({quota_used}q)")
            
            # Save progress after each success
            completed_ids.add(vid)
            save_progress({
                "completed": list(completed_ids),
                "quota_used": quota_used,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            time.sleep(1)  # Rate limit
            
        except Exception as e:
            error_msg = str(e)
            errors += 1
            print(f"  ❌ {vid} — ERROR: {error_msg[:120]}")
            
            if "quotaExceeded" in error_msg or "403" in error_msg:
                print("\n🛑 QUOTA EXHAUSTED! Stopping immediately.")
                print(f"   Progress saved — run again to resume.")
                break
    
    # Final report
    print(f"\n{'=' * 70}")
    print(f"BATCH RESULTS")
    print(f"  ✅ Updated:  {updated}")
    print(f"  ⏭️  Skipped:  {skipped}")
    print(f"  ❌ Errors:   {errors}")
    print(f"  💰 Quota:    ~{quota_used} units")
    print(f"  📊 Total done: {len(completed_ids)} / {len(updates)}")
    
    # Save final report
    report = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "script": "batch_apply_2026_02_11.py",
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "quota_used": quota_used,
        "total_completed": len(completed_ids),
        "total_planned": len(updates),
        "changes_breakdown": {
            "tag_updates": sum(1 for u in updates if 'new_tags' in u),
            "desc_updates": sum(1 for u in updates if 'new_line1' in u),
            "title_updates": sum(1 for u in updates if 'new_title' in u),
        }
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Report: {REPORT_PATH}")
    print(f"📄 Progress: {PROGRESS_PATH}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python batch_apply_2026_02_11.py --verify         # Offline validation")
        print("  python batch_apply_2026_02_11.py --dry-run        # Fetch + compare (read)")
        print("  python batch_apply_2026_02_11.py --apply          # Apply all changes")
        print("  python batch_apply_2026_02_11.py --apply --limit 50  # First 50 only")
        sys.exit(1)

    mode = sys.argv[1]
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    batch = load_batch()

    if mode == "--verify":
        verify(batch)
    elif mode == "--dry-run":
        youtube = get_youtube_service()
        dry_run(youtube, batch, limit)
    elif mode == "--apply":
        youtube = get_youtube_service()
        apply_changes(youtube, batch, limit)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
