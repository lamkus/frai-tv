"""
PUSH FROM DB v3 — Smart Multi-Phase Change Pusher
====================================================
Reads video_master_db_v3.json and pushes changes to YouTube.

PHASES:
  1. valentine  — Seasonal Valentine boost (tags, CTA, desc) — URGENT
  2. titles     — Strip (4K UHD), fix keyword order
  3. tags       — Add "public domain", fix tag sets
  4. locs       — Fix localizations
  5. category   — Fix wrong categories
  6. all        — Push everything by priority

Features:
- Priority-ordered push queue
- Idempotency: fetches live state, skips already-correct
- Quota tracking with auto-stop (10,000/day)
- Dry-run by default (--apply to push)
- Phase-based targeting (--phase valentine)
- Proper quota cost: snippet=50, locs=50, both=50 (one API call)
- Detailed JSON logging

Usage:
  python push_from_db_v3.py                          # Dry run, all changes
  python push_from_db_v3.py --phase valentine        # Dry run Valentine only
  python push_from_db_v3.py --phase valentine --apply  # PUSH Valentine
  python push_from_db_v3.py --phase titles --apply --limit 100
  python push_from_db_v3.py --series betty_boop --apply
  python push_from_db_v3.py --only title             # Only title changes
"""
import json, os, sys, argparse
from datetime import datetime, timezone
from collections import Counter
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
DB_PATH    = "D:/remaike.TV/config/video_master_db_v3.json"
LOG_DIR    = "D:/remaike.TV/logs"

DAILY_QUOTA_LIMIT = 10000
# videos.update costs 50 quota regardless of how many parts you send
COST_VIDEO_UPDATE = 50


def get_yt():
    d = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=d.get("access_token"), refresh_token=d["refresh_token"],
        token_uri=d["token_uri"], client_id=d["client_id"], client_secret=d["client_secret"],
    )
    if not creds.valid:
        creds.refresh(Request())
        d["access_token"] = creds.token
        json.dump(d, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)


# ═══════════════════════════════════════════════════════════════
# PHASE FILTERS — select which videos to push
# ═══════════════════════════════════════════════════════════════

def filter_valentine(db):
    """Phase 1: Valentine's Day seasonal boost.
    Selects videos flagged with seasonal boosts + applies extra tags/CTAs."""
    queue = []
    for vid, entry in db["videos"].items():
        if entry["status"]["privacy"] != "public":
            continue
        if not entry["seasonal"]["is_seasonal_now"]:
            continue
        # Build Valentine-specific changes
        changes = {}
        current_tags = entry["current"]["tags"]
        ideal_tags = entry["ideal"]["tags"]

        # Add seasonal tags that are missing
        new_tags = list(current_tags)
        for boost in entry["seasonal"]["boosts"]:
            for tag in boost.get("extra_tags", []):
                if tag.lower() not in [t.lower() for t in new_tags]:
                    new_tags.append(tag)
        # Cap at 15
        new_tags = new_tags[:15]
        if set(t.lower() for t in new_tags) != set(t.lower() for t in current_tags):
            changes["tags"] = {"from": current_tags, "to": new_tags}

        # Check description for seasonal CTA
        desc = entry["current"]["description"]
        seasonal_cta = ""
        for boost in entry["seasonal"]["boosts"]:
            if boost.get("seasonal_cta"):
                seasonal_cta = boost["seasonal_cta"]
                break

        # If description is missing CTA or website, rebuild it
        desc_issues = entry["audit"]["desc_issues"]
        if desc_issues and ("NO_CTA" in desc_issues or "NO_WEBSITE_LINK" in desc_issues or "NO_YT_LINK" in desc_issues):
            changes["description_needs_fix"] = desc_issues

        # Title fix (strip 4K UHD)
        if entry["has_changes"] and "title" in entry["changes"]:
            changes["title"] = entry["changes"]["title"]

        # Loc fixes
        if entry["has_changes"] and "localizations" in entry["changes"]:
            changes["localizations"] = entry["changes"]["localizations"]

        if changes:
            queue.append({
                "id": vid, "series": entry["series"],
                "title": entry["current"]["title"],
                "priority": 200 + entry["metrics"]["views"],  # Valentine = highest
                "changes": changes,
                "change_types": list(changes.keys()),
                "quota_cost": COST_VIDEO_UPDATE,
                "seasonal_cta": seasonal_cta,
                "views": entry["metrics"]["views"],
            })

    queue.sort(key=lambda x: -x["priority"])
    return queue


def filter_titles(db):
    """Phase 2: Title cleanup — strip (4K UHD), fix double spaces, etc."""
    queue = []
    for vid, entry in db["videos"].items():
        if entry["status"]["privacy"] != "public":
            continue
        if not entry["has_changes"]:
            continue
        if "title" not in entry["changes"]:
            continue
        changes = {"title": entry["changes"]["title"]}
        # Also fix locs if they need it
        if "localizations" in entry["changes"]:
            changes["localizations"] = entry["changes"]["localizations"]
        queue.append({
            "id": vid, "series": entry["series"],
            "title": entry["current"]["title"],
            "priority": entry.get("_priority", 0),
            "changes": changes,
            "change_types": list(changes.keys()),
            "quota_cost": COST_VIDEO_UPDATE,
            "views": entry["metrics"]["views"],
        })
    # Compute priority from push_queue
    pq_map = {p["id"]: p["priority"] for p in db.get("push_queue", [])}
    for item in queue:
        item["priority"] = pq_map.get(item["id"], 0)
    queue.sort(key=lambda x: -x["priority"])
    return queue


def filter_tags(db):
    """Phase 3: Tag optimization — add missing public domain, 8K, series tags."""
    queue = []
    for vid, entry in db["videos"].items():
        if entry["status"]["privacy"] != "public":
            continue
        tag_issues = entry["audit"]["tag_issues"]
        if not tag_issues:
            continue

        current_tags = entry["current"]["tags"]
        ideal_tags = entry["ideal"]["tags"]

        # Build merged tag set
        new_tags = list(current_tags)
        for tag in ideal_tags:
            if tag.lower() not in [t.lower() for t in new_tags]:
                new_tags.append(tag)
        new_tags = new_tags[:15]

        if set(t.lower() for t in new_tags) != set(t.lower() for t in current_tags):
            queue.append({
                "id": vid, "series": entry["series"],
                "title": entry["current"]["title"],
                "priority": entry["metrics"]["views"],
                "changes": {"tags": {"from": current_tags, "to": new_tags}},
                "change_types": ["tags"],
                "quota_cost": COST_VIDEO_UPDATE,
                "views": entry["metrics"]["views"],
            })
    queue.sort(key=lambda x: -x["priority"])
    return queue


def filter_locs(db):
    """Phase 4: Localizations — fix translated titles."""
    queue = []
    for vid, entry in db["videos"].items():
        if entry["status"]["privacy"] != "public":
            continue
        if not entry["has_changes"]:
            continue
        if "localizations" not in entry["changes"]:
            continue
        queue.append({
            "id": vid, "series": entry["series"],
            "title": entry["current"]["title"],
            "priority": entry["metrics"]["views"],
            "changes": {"localizations": entry["changes"]["localizations"]},
            "change_types": ["localizations"],
            "quota_cost": COST_VIDEO_UPDATE,
            "views": entry["metrics"]["views"],
        })
    queue.sort(key=lambda x: -x["priority"])
    return queue


def filter_category(db):
    """Phase 5: Category fixes (e.g. Soundies → Music)."""
    queue = []
    for vid, entry in db["videos"].items():
        if entry["status"]["privacy"] != "public":
            continue
        if not entry["has_changes"]:
            continue
        if "category" not in entry["changes"]:
            continue
        queue.append({
            "id": vid, "series": entry["series"],
            "title": entry["current"]["title"],
            "priority": 100 + entry["metrics"]["views"],
            "changes": {"category": entry["changes"]["category"]},
            "change_types": ["category"],
            "quota_cost": COST_VIDEO_UPDATE,
            "views": entry["metrics"]["views"],
        })
    queue.sort(key=lambda x: -x["priority"])
    return queue


def filter_all(db):
    """Phase 6: Everything by priority (from push_queue)."""
    return db.get("push_queue", [])


PHASE_MAP = {
    "valentine": filter_valentine,
    "titles":    filter_titles,
    "tags":      filter_tags,
    "locs":      filter_locs,
    "category":  filter_category,
    "all":       filter_all,
}


# ═══════════════════════════════════════════════════════════════
# PUSH ENGINE
# ═══════════════════════════════════════════════════════════════

def push_changes(args):
    db = json.load(open(DB_PATH, encoding="utf-8"))

    # Select phase
    phase = args.phase or "all"
    filter_fn = PHASE_MAP.get(phase)
    if not filter_fn:
        print(f"  ❌ Unknown phase: {phase}")
        print(f"     Available: {', '.join(PHASE_MAP.keys())}")
        return

    queue = filter_fn(db)

    # Additional filters
    if args.series:
        queue = [p for p in queue if p["series"] == args.series]
    if args.only:
        queue = [p for p in queue if args.only in p["change_types"]]
    if args.limit:
        queue = queue[:args.limit]

    # ── Report header ──
    mode_label = "🔴 LIVE PUSH" if args.apply else "🟡 DRY RUN"
    print("=" * 72)
    print(f"  PUSH FROM DB v3 — {mode_label}")
    print(f"  Phase: {phase.upper()}")
    print(f"  Time:  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 72)
    print(f"\n  📊 {len(queue)} videos to process")
    total_quota = sum(p["quota_cost"] for p in queue)
    print(f"  💰 Estimated quota: {total_quota:,d} units")

    if total_quota > DAILY_QUOTA_LIMIT:
        days = total_quota // DAILY_QUOTA_LIMIT + 1
        print(f"  ⚠️  Exceeds daily limit! Need ~{days} days")

    if not queue:
        print("\n  ✅ Nothing to push for this phase!")
        return

    # Change type summary
    type_summary = Counter()
    series_summary = Counter()
    for p in queue:
        for ct in p["change_types"]:
            type_summary[ct] += 1
        series_summary[p["series"]] += 1

    print(f"\n  📋 Change Types:")
    for ct, count in type_summary.most_common():
        print(f"     {ct:25s}: {count}")

    print(f"\n  📺 Series:")
    for sid, count in series_summary.most_common(10):
        print(f"     {sid:20s}: {count}")

    # ── DRY RUN ──
    if not args.apply:
        show = min(30, len(queue))
        print(f"\n  🟡 DRY RUN — showing {show} of {len(queue)} changes:")

        for i, p in enumerate(queue[:show]):
            views_str = f"({p.get('views', 0):,d}v)" if p.get('views') else ""
            print(f"\n  [{i+1:3d}] {p['series']:15s} {views_str}")
            print(f"        {p['title'][:60]}")

            for change_type, change in p["changes"].items():
                if change_type == "localizations":
                    for lang, lc in change.items():
                        print(f"        loc[{lang}]: {lc['from'][:35]} → {lc['to'][:35]}")
                elif change_type == "tags":
                    added = [t for t in change["to"] if t not in change["from"]]
                    removed = [t for t in change["from"] if t not in change["to"]]
                    if added:   print(f"        tags +: {', '.join(added[:5])}")
                    if removed: print(f"        tags -: {', '.join(removed[:5])}")
                elif change_type == "description_needs_fix":
                    print(f"        desc: {change}")
                elif isinstance(change, dict) and "from" in change and "to" in change:
                    print(f"        {change_type}: {str(change['from'])[:35]} → {str(change['to'])[:35]}")

            if p.get("seasonal_cta"):
                print(f"        💕 CTA: {p['seasonal_cta'][:50]}")

        if len(queue) > show:
            print(f"\n  ... and {len(queue) - show} more")
        print(f"\n  ➡️  Run with --apply to push these changes")
        return

    # ═══════════════════════════════════════════════════════════
    # LIVE PUSH
    # ═══════════════════════════════════════════════════════════
    print(f"\n  🔴 PUSHING {len(queue)} CHANGES...")
    yt = get_yt()

    quota_used = 0
    success = 0
    skipped = 0
    failed = 0
    log_entries = []

    for i, p in enumerate(queue):
        vid = p["id"]
        changes = p["changes"]

        # Quota guard
        if quota_used + COST_VIDEO_UPDATE > DAILY_QUOTA_LIMIT:
            print(f"\n  ⚠️  Quota limit reached ({quota_used:,d} used). Stopping.")
            break

        try:
            # Fetch current state for idempotency
            parts_to_fetch = ["snippet"]
            if "localizations" in changes:
                parts_to_fetch.append("localizations")

            current = yt.videos().list(
                part=",".join(parts_to_fetch),
                id=vid
            ).execute()

            if not current.get("items"):
                print(f"  ⚠️  {vid} not found, skipping")
                skipped += 1
                continue

            item = current["items"][0]
            snippet = item["snippet"]
            needs_update = False
            update_parts = set()
            update_body = {"id": vid}

            # ── Title ──
            if "title" in changes:
                new_title = changes["title"]["to"]
                if snippet["title"] != new_title:
                    snippet["title"] = new_title
                    needs_update = True
                    update_parts.add("snippet")

            # ── Category ──
            if "category" in changes:
                new_cat = changes["category"]["to"]
                if snippet["categoryId"] != new_cat:
                    snippet["categoryId"] = new_cat
                    needs_update = True
                    update_parts.add("snippet")

            # ── Tags ──
            if "tags" in changes:
                new_tags = changes["tags"]["to"]
                current_tags = snippet.get("tags", [])
                if set(t.lower() for t in new_tags) != set(t.lower() for t in current_tags):
                    snippet["tags"] = new_tags
                    needs_update = True
                    update_parts.add("snippet")

            # ── Description (only fix missing elements, don't replace entire desc) ──
            # For now we only push tag/title/cat/loc changes.
            # Full description rewrite is a separate future phase.

            # ── Localizations ──
            if "localizations" in changes:
                current_locs = item.get("localizations", {})
                loc_changed = False
                for lang, lc in changes["localizations"].items():
                    new_title = lc["to"]
                    cur_title = current_locs.get(lang, {}).get("title", "")
                    if cur_title != new_title:
                        if lang not in current_locs:
                            current_locs[lang] = {}
                        current_locs[lang]["title"] = new_title
                        if "description" not in current_locs[lang]:
                            current_locs[lang]["description"] = snippet.get("description", "")
                        loc_changed = True

                if loc_changed:
                    update_body["localizations"] = current_locs
                    update_parts.add("localizations")
                    needs_update = True

            if not needs_update:
                print(f"  ✅ {vid} [{p['series']:12s}] already correct, skipping")
                skipped += 1
                continue

            # ── Push ──
            if "snippet" in update_parts:
                update_body["snippet"] = snippet

            yt.videos().update(
                part=",".join(update_parts),
                body=update_body
            ).execute()

            quota_used += COST_VIDEO_UPDATE
            success += 1

            change_desc = ", ".join(p["change_types"])
            views = p.get("views", 0)
            print(f"  ✅ [{i+1:3d}/{len(queue)}] {vid} [{p['series']:12s}] {change_desc} | Q:{quota_used:,d} | {views:,d}v")

            log_entries.append({
                "id": vid, "series": p["series"],
                "changes": p["change_types"],
                "title": p["title"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "success",
            })

        except Exception as e:
            err_msg = str(e)
            failed += 1
            print(f"  ❌ {vid} [{p['series']:12s}] ERROR: {err_msg[:80]}")

            if "quota" in err_msg.lower():
                print(f"\n  🛑 QUOTA EXHAUSTED after {quota_used:,d} units. Stopping.")
                break

            log_entries.append({
                "id": vid, "series": p["series"],
                "error": err_msg[:200],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "failed",
            })

    # ── Save log ──
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"push_v3_{phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    log = {
        "run_date": datetime.now(timezone.utc).isoformat(),
        "mode": "apply" if args.apply else "dry_run",
        "phase": phase,
        "filters": {
            "series": args.series, "only": args.only, "limit": args.limit,
        },
        "results": {
            "total_in_queue": len(queue),
            "success": success, "skipped": skipped, "failed": failed,
            "quota_used": quota_used,
        },
        "entries": log_entries,
    }
    json.dump(log, open(log_file, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    # ── Summary ──
    print(f"\n{'=' * 72}")
    print(f"  📊 PUSH COMPLETE — Phase: {phase.upper()}")
    print(f"{'=' * 72}")
    print(f"  ✅ Success:  {success}")
    print(f"  ⏭️  Skipped:  {skipped}")
    print(f"  ❌ Failed:   {failed}")
    print(f"  💰 Quota:    {quota_used:,d} / {DAILY_QUOTA_LIMIT:,d}")
    remaining = len(queue) - success - skipped - failed
    if remaining > 0:
        print(f"  ⏳ Remaining: {remaining} (quota limit reached)")
    print(f"  📝 Log:      {log_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Push changes from Video Master DB v3")
    parser.add_argument("--apply", action="store_true",
                        help="Actually push changes (default: dry run)")
    parser.add_argument("--phase", choices=list(PHASE_MAP.keys()),
                        help="Which phase to run (valentine/titles/tags/locs/category/all)")
    parser.add_argument("--limit", type=int,
                        help="Max number of videos to process")
    parser.add_argument("--only", choices=["title", "localizations", "category", "tags"],
                        help="Only push specific change type")
    parser.add_argument("--series", type=str,
                        help="Only push specific series (e.g. betty_boop)")
    args = parser.parse_args()
    push_changes(args)
