#!/usr/bin/env python3
"""
Fix Private/Draft Videos – 2026-02-11
======================================
Adds pflicht-tags to 14 private/unlisted videos that were NEVER optimized
because all previous scripts filtered WHERE privacy_status='public'.

Quota: 14 * 51 = 714 units (1 list + 50 update per video)
Bug fix: ONLY part="snippet" — NEVER add "status"!
"""

import json
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
BATCH_PATH = os.path.join(ROOT_DIR, "config", "pending_updates", "batch_private_2026_02_11.json")
TOKEN_PATH = os.path.join(ROOT_DIR, "token.json")
REPORT_PATH = os.path.join(ROOT_DIR, "config", "pending_updates", "private_fix_report_2026_02_11.json")

COST_LIST = 1
COST_UPDATE = 50

PFLICHT_TAGS = {'remastered', 'restored', 'AI enhanced', 'upscaled', 'classic'}
JUNK_TAGS = {'Video', 'Archive', 'Film', 'High Quality', 'UHD'}

# Tennis Party (Z-0Xkt5czSY) needs a full description
TENNIS_DESC = """Vintage Tennis Competition Game | Classic Sports Entertainment | AI Remastered in 8K

Watch this charming vintage tennis party game, beautifully restored and upscaled to stunning 8K quality using AI enhancement technology.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Vintage #ClassicSports #8K #PublicDomain #Remastered"""


def get_youtube_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    if not os.path.exists(TOKEN_PATH):
        print(f"ERROR: token.json not found at {TOKEN_PATH}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
        print("[TOKEN] Refreshed")

    return build("youtube", "v3", credentials=creds)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    
    # Load batch
    with open(BATCH_PATH, "r", encoding="utf-8") as f:
        batch = json.load(f)
    
    updates = batch["updates"]
    print(f"=== PRIVATE VIDEO FIX ===")
    print(f"    Mode: {mode}")
    print(f"    Videos: {len(updates)}")
    print(f"    Quota: {len(updates) * 51} units")
    print()

    if mode == "--verify":
        for u in updates:
            changes = u["changes"]
            flags = []
            if "tags" in changes:
                flags.append(f"TAGS({len(changes['tags'])})")
            if "needs_desc" in changes:
                flags.append("DESC")
            print(f"  {u['video_id']} | {u['privacy']:>8} | {', '.join(flags):>15} | {u['title'][:50]}")
        print(f"\n  All {len(updates)} entries OK for apply.")
        return

    # API mode - build YouTube service
    youtube = get_youtube_service()
    
    # Fetch all video IDs at once (1 API call for up to 50 IDs)
    all_ids = [u["video_id"] for u in updates]
    ids_str = ",".join(all_ids)
    
    print(f"[FETCH] Getting {len(all_ids)} videos...")
    # CRITICAL: part="snippet" ONLY — NEVER add "status"!
    response = youtube.videos().list(
        part="snippet",
        id=ids_str
    ).execute()
    
    fetched = {item["id"]: item for item in response.get("items", [])}
    quota_used = COST_LIST
    print(f"[FETCH] Got {len(fetched)} of {len(all_ids)} ({quota_used} quota)")
    
    if mode == "--dry-run":
        print(f"\n--- DRY RUN (read-only) ---")
        for u in updates:
            vid = u["video_id"]
            if vid not in fetched:
                print(f"  SKIP  {vid} | NOT FOUND via API (deleted?)")
                continue
            
            snippet = fetched[vid]["snippet"]
            current_tags = snippet.get("tags", [])
            changes = u["changes"]
            
            tag_changes = ""
            if "tags" in changes:
                new_tags = changes["tags"]
                added = set(new_tags) - set(current_tags)
                removed = set(current_tags) - set(new_tags)
                tag_changes = f"+{len(added)}/-{len(removed)}"
            
            desc_change = "NEW_DESC" if "needs_desc" in changes else ""
            
            print(f"  WILL FIX {vid} | tags:{tag_changes:>7} desc:{desc_change:>8} | {snippet['title'][:45]}")
        
        print(f"\n  Quota used: {quota_used} (read only)")
        print(f"  Apply would cost: {len(fetched) * COST_UPDATE + quota_used} total")
        return

    if mode == "--apply":
        print(f"\n--- APPLYING CHANGES ---")
        success = 0
        fail = 0
        skipped = 0
        report = []
        
        for u in updates:
            vid = u["video_id"]
            if vid not in fetched:
                print(f"  SKIP  {vid} | NOT FOUND")
                skipped += 1
                continue
            
            item = fetched[vid]
            snippet = item["snippet"]
            current_tags = snippet.get("tags", [])
            changes = u["changes"]
            modified = False
            change_log = []
            
            # Apply tag changes
            if "tags" in changes:
                new_tags = list(changes["tags"])
                # But also incorporate any tags from the live video that aren't junk
                # (in case tags changed since our DB snapshot)
                for lt in current_tags:
                    if lt not in JUNK_TAGS and lt not in new_tags:
                        if len(new_tags) < 15:
                            new_tags.append(lt)
                
                # Ensure pflicht-tags are present
                for pt in sorted(PFLICHT_TAGS):
                    if pt not in new_tags and len(new_tags) < 15:
                        new_tags.append(pt)
                
                if set(new_tags) != set(current_tags):
                    snippet["tags"] = new_tags[:15]
                    modified = True
                    added = set(new_tags) - set(current_tags)
                    removed = set(current_tags) - set(new_tags)
                    change_log.append(f"tags: +{len(added)}/-{len(removed)}")
            
            # Apply description fix
            if "needs_desc" in changes and vid == "Z-0Xkt5czSY":
                snippet["description"] = TENNIS_DESC
                modified = True
                change_log.append("desc: NEW")
            
            if not modified:
                print(f"  NOOP  {vid} | No changes needed (live data matches)")
                skipped += 1
                continue
            
            # Apply update
            try:
                # CRITICAL: part="snippet" ONLY — NEVER add "status"!
                youtube.videos().update(
                    part="snippet",
                    body={
                        "id": vid,
                        "snippet": snippet
                    }
                ).execute()
                
                quota_used += COST_UPDATE
                success += 1
                print(f"  OK    {vid} | {', '.join(change_log)} | {snippet['title'][:40]} ({quota_used} quota)")
                report.append({"id": vid, "status": "ok", "changes": change_log})
                time.sleep(0.5)  # Be nice to API
                
            except Exception as e:
                fail += 1
                err = str(e)
                print(f"  FAIL  {vid} | {err[:80]}")
                report.append({"id": vid, "status": "fail", "error": err[:200]})
                
                if "quotaExceeded" in err:
                    print(f"\n  !!! QUOTA EXCEEDED !!! Stopping.")
                    break
        
        print(f"\n=== RESULT ===")
        print(f"  Success: {success}")
        print(f"  Failed:  {fail}")
        print(f"  Skipped: {skipped}")
        print(f"  Quota:   {quota_used} units")
        
        # Save report
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "success": success,
                "fail": fail,
                "skipped": skipped,
                "quota_used": quota_used,
                "details": report
            }, f, indent=2)
        print(f"  Report: {REPORT_PATH}")
    
    else:
        print(f"Usage: {sys.argv[0]} --verify|--dry-run|--apply")


if __name__ == "__main__":
    main()
