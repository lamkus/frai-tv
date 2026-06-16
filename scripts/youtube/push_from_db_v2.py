"""
PUSH FROM DB v2 — Smart Change Pusher
=======================================
Reads video_master_db_v2.json and pushes changes to YouTube.
Features:
- Priority-ordered push queue
- Idempotency: skips already-correct videos
- Quota tracking with auto-stop
- Dry-run by default (--apply to push)
- Detailed before/after logging

Usage:
  python push_from_db_v2.py              # Dry run (shows what would change)
  python push_from_db_v2.py --apply      # Actually push changes
  python push_from_db_v2.py --apply --limit 50   # Push max 50 videos
  python push_from_db_v2.py --only title         # Only push title changes
  python push_from_db_v2.py --only localizations # Only push loc changes
  python push_from_db_v2.py --series krtek       # Only push one series
"""
import json, os, sys, argparse
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
DB_PATH    = "D:/remaike.TV/config/video_master_db_v2.json"
LOG_PATH   = "D:/remaike.TV/logs/push_log_v2.json"

DAILY_QUOTA_LIMIT = 10000  # YouTube daily limit
COST_VIDEO_UPDATE = 50     # videos.update = 50 units

def get_yt():
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"),
        refresh_token=d["refresh_token"],
        token_uri=d["token_uri"],
        client_id=d["client_id"],
        client_secret=d["client_secret"],
    )
    if not creds.valid:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)


def push_changes(args):
    db = json.load(open(DB_PATH, encoding="utf-8"))
    push_queue = db["push_queue"]
    
    # Filters
    if args.series:
        push_queue = [p for p in push_queue if p["series"] == args.series]
    if args.only:
        push_queue = [p for p in push_queue if args.only in p["change_types"]]
    if args.limit:
        push_queue = push_queue[:args.limit]
    
    print("=" * 72)
    print(f"  PUSH FROM DB v2 — {'🔴 LIVE' if args.apply else '🟡 DRY RUN'}")
    print("=" * 72)
    print(f"\n  📊 {len(push_queue)} videos to process")
    total_quota = sum(p["quota_cost"] for p in push_queue)
    print(f"  💰 Estimated quota: {total_quota:,d} units")
    
    if total_quota > DAILY_QUOTA_LIMIT:
        days = total_quota // DAILY_QUOTA_LIMIT + 1
        print(f"  ⚠️  Exceeds daily limit! Need ~{days} days")
    
    if not push_queue:
        print("\n  ✅ Nothing to push!")
        return
    
    # Group by change type for summary
    from collections import Counter
    type_summary = Counter()
    for p in push_queue:
        for ct in p["change_types"]:
            type_summary[ct] += 1
    
    print(f"\n  📋 Change Types:")
    for ct, count in type_summary.most_common():
        print(f"     {ct:20s}: {count}")
    
    if not args.apply:
        print(f"\n  🟡 DRY RUN — showing first 20 changes:")
        for i, p in enumerate(push_queue[:20]):
            print(f"\n  [{i+1}] {p['series']:15s} | {p['title'][:50]}")
            for change_type, change in p["changes"].items():
                if change_type == "localizations":
                    for lang, lc in change.items():
                        print(f"       loc[{lang}]: {lc['from'][:40]} → {lc['to'][:40]}")
                else:
                    print(f"       {change_type}: {change['from'][:40]} → {change['to'][:40]}")
        if len(push_queue) > 20:
            print(f"\n  ... and {len(push_queue) - 20} more")
        print(f"\n  ➡️  Run with --apply to push these changes")
        return
    
    # ── LIVE PUSH ──
    print(f"\n  🔴 PUSHING CHANGES...")
    yt = get_yt()
    
    quota_used = 0
    success = 0
    skipped = 0
    failed = 0
    log_entries = []
    
    for i, p in enumerate(push_queue):
        vid = p["id"]
        changes = p["changes"]
        
        # Quota guard
        if quota_used + COST_VIDEO_UPDATE > DAILY_QUOTA_LIMIT:
            print(f"\n  ⚠️  Quota limit reached ({quota_used} used). Stopping.")
            break
        
        try:
            # Fetch current state for idempotency check
            current = yt.videos().list(
                part="snippet,localizations",
                id=vid
            ).execute()
            
            if not current.get("items"):
                print(f"  ⚠️  {vid} not found, skipping")
                skipped += 1
                continue
            
            item = current["items"][0]
            snippet = item["snippet"]
            needs_update = False
            update_body = {"id": vid, "snippet": snippet}
            
            # Title change
            if "title" in changes:
                new_title = changes["title"]["to"]
                if snippet["title"] != new_title:
                    snippet["title"] = new_title
                    needs_update = True
            
            # Category change
            if "category" in changes:
                new_cat = changes["category"]["to"]
                if snippet["categoryId"] != new_cat:
                    snippet["categoryId"] = new_cat
                    needs_update = True
            
            # Localization changes
            loc_update = False
            if "localizations" in changes:
                current_locs = item.get("localizations", {})
                for lang, lc in changes["localizations"].items():
                    new_title = lc["to"]
                    cur_title = current_locs.get(lang, {}).get("title", "")
                    if cur_title != new_title:
                        if lang not in current_locs:
                            current_locs[lang] = {}
                        current_locs[lang]["title"] = new_title
                        # Keep existing description
                        if "description" not in current_locs[lang]:
                            current_locs[lang]["description"] = snippet.get("description", "")
                        loc_update = True
                
                if loc_update:
                    update_body["localizations"] = current_locs
                    needs_update = True
            
            if not needs_update:
                print(f"  ✅ {vid} [{p['series']}] already correct, skipping")
                skipped += 1
                continue
            
            # Build parts
            parts = ["snippet"]
            if loc_update:
                parts.append("localizations")
            
            # Push!
            update_body["snippet"] = snippet
            yt.videos().update(
                part=",".join(parts),
                body=update_body
            ).execute()
            
            quota_used += COST_VIDEO_UPDATE
            success += 1
            
            change_desc = ", ".join(changes.keys())
            print(f"  ✅ [{i+1}/{len(push_queue)}] {vid} [{p['series']}] {change_desc} | Q:{quota_used}")
            
            log_entries.append({
                "id": vid,
                "series": p["series"],
                "changes": list(changes.keys()),
                "title": p["title"],
                "timestamp": datetime.now().isoformat(),
                "status": "success",
            })
            
        except Exception as e:
            err_msg = str(e)
            failed += 1
            print(f"  ❌ {vid} [{p['series']}] ERROR: {err_msg[:80]}")
            
            if "quota" in err_msg.lower():
                print(f"\n  🛑 QUOTA EXHAUSTED after {quota_used} units. Stopping.")
                break
            
            log_entries.append({
                "id": vid,
                "series": p["series"],
                "error": err_msg[:200],
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
            })
    
    # Save log
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    log = {
        "run_date": datetime.now().isoformat(),
        "mode": "apply",
        "filters": {
            "series": args.series,
            "only": args.only,
            "limit": args.limit,
        },
        "results": {
            "success": success,
            "skipped": skipped,
            "failed": failed,
            "quota_used": quota_used,
        },
        "entries": log_entries,
    }
    json.dump(log, open(LOG_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n{'=' * 72}")
    print(f"  📊 PUSH COMPLETE")
    print(f"{'=' * 72}")
    print(f"  ✅ Success:  {success}")
    print(f"  ⏭️  Skipped:  {skipped}")
    print(f"  ❌ Failed:   {failed}")
    print(f"  💰 Quota:    {quota_used:,d} units")
    print(f"  📝 Log:      {LOG_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push changes from Video Master DB v2")
    parser.add_argument("--apply", action="store_true", help="Actually push (default: dry run)")
    parser.add_argument("--limit", type=int, help="Max videos to process")
    parser.add_argument("--only", choices=["title", "localizations", "category"], help="Only push specific change type")
    parser.add_argument("--series", type=str, help="Only push specific series (e.g. krtek, betty_boop)")
    args = parser.parse_args()
    
    push_changes(args)
