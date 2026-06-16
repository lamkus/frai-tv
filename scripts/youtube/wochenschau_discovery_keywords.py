"""
wochenschau_discovery_keywords.py — Add History/Documentary/Discovery Keywords
==============================================================================
Adds high-volume discovery keywords to all Wochenschau videos:
- Tags: "history documentary", "war documentary", "WWII documentary",
        "history channel", "discovery", "full documentary", "war footage"
- Description line 1: Keyword-rich hook with documentary/history terms

Cost: 51 Units per video (1 read + 50 write)
~42 Wochenschau videos × 51 = ~2,142 Units

Usage:
  python scripts/youtube/wochenschau_discovery_keywords.py --scan         # Scan only
  python scripts/youtube/wochenschau_discovery_keywords.py --apply        # Apply fixes
  python scripts/youtube/wochenschau_discovery_keywords.py --apply --max 10  # Limit batch
"""

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

TOKEN_FILE = ROOT / "token.json"
REPORT_FILE = ROOT / "reports" / "wochenschau_keyword_update.json"
LOCATIONS_FILE = ROOT / "config" / "wochenschau_complete_locations.json"

# ── Discovery Keywords to ADD ─────────────────────────────────────────────────
# These are HIGH-VOLUME search terms that viewers actually search for
MUST_HAVE_TAGS = [
    "history documentary",
    "war documentary",
    "WWII documentary",
    "world war 2 documentary",
    "history channel",
    "discovery",
    "war footage",
    "original footage",
    "vintage footage",
    "full documentary",
    "AI enhanced",
    "remastered",
    "restored",
]

# Tags that should be on every Wochenschau video
BASE_TAGS = [
    "wochenschau", "deutsche wochenschau",
    "wwii", "world war 2", "ww2",
    "newsreel", "historical footage",
    "history", "documentary", "education",
    "public domain", "8K", "4K UHD",
    "history documentary", "war documentary", "WWII documentary",
    "world war 2 documentary",
    "history channel", "discovery",
    "war footage", "original footage", "vintage footage",
    "full documentary",
    "AI enhanced", "remastered", "restored",
]


def get_youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE))
    return build("youtube", "v3", credentials=creds)


def get_all_wochenschau_ids(yt) -> list[dict]:
    """Get all Wochenschau videos from channel uploads."""
    videos = []
    page_token = None
    
    while True:
        params = {
            "part": "contentDetails,snippet",
            "playlistId": "UUVFv6Egpl0LDvigpFbQXNeQ",  # Uploads playlist
            "maxResults": 50,
        }
        if page_token:
            params["pageToken"] = page_token
            
        resp = yt.playlistItems().list(**params).execute()
        
        for item in resp.get("items", []):
            title = item["snippet"]["title"]
            vid = item["contentDetails"]["videoId"]
            # Match Wochenschau videos (but not the livestream)
            if "ochenschau" in title and vid != "lm4EcKHQ45o":
                videos.append({"id": vid, "title": title})
        
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    
    return videos


def check_missing_keywords(tags: list[str]) -> list[str]:
    """Check which discovery keywords are missing from current tags."""
    tags_lower = {t.lower() for t in tags}
    missing = []
    for kw in MUST_HAVE_TAGS:
        if kw.lower() not in tags_lower:
            missing.append(kw)
    return missing


def build_description_with_keywords(desc: str, title: str) -> str:
    """Ensure the description has discovery keywords in the visible portion."""
    lines = desc.split("\n")
    
    # Check if first visible lines already have documentary/history keywords
    first_5 = "\n".join(lines[:5]).lower()
    has_documentary = "documentary" in first_5 or "war documentary" in first_5
    has_history_ref = "history channel" in first_5 or "discovery" in first_5
    
    if has_documentary and has_history_ref:
        return None  # Already good
    
    # Find the line after the disclaimer block to insert keywords
    # Look for the "This footage is a primary source..." line
    insert_idx = None
    for i, line in enumerate(lines):
        if "primary source" in line.lower() or "contents do not reflect" in line.lower():
            insert_idx = i + 1
            break
    
    if insert_idx is None:
        # Look for first empty line after emoji block
        for i, line in enumerate(lines):
            if i > 2 and line.strip() == "":
                insert_idx = i + 1
                break
    
    if insert_idx is None:
        insert_idx = min(3, len(lines))
    
    # Build keyword-rich insert block
    keyword_block = [
        "",
        "🎞️ A real WWII history documentary source — original Deutsche Wochenschau newsreel.",
        "Like History Channel & Discovery documentaries? This is the REAL uncut war footage,",
        "AI remastered and restored in stunning quality. No re-enactments. Pure history.",
        "",
    ]
    
    # Check if this block already exists (avoid duplicates)
    if "Like History Channel" in desc:
        return None
    
    new_lines = lines[:insert_idx] + keyword_block + lines[insert_idx:]
    return "\n".join(new_lines)


def scan_videos(yt, wochenschau_videos: list[dict]) -> list[dict]:
    """Scan all Wochenschau videos and find which need keyword updates."""
    results = []
    
    # Process in batches of 50 (1 Unit per videos.list call)
    batch_size = 50
    for i in range(0, len(wochenschau_videos), batch_size):
        batch = wochenschau_videos[i:i+batch_size]
        ids = ",".join(v["id"] for v in batch)
        
        resp = yt.videos().list(part="snippet,status", id=ids).execute()
        
        for item in resp.get("items", []):
            vid = item["id"]
            snippet = item["snippet"]
            title = snippet["title"]
            tags = snippet.get("tags", [])
            desc = snippet["description"]
            privacy = item["status"]["privacyStatus"]
            
            # Skip private/unlisted
            if privacy != "public":
                continue
            
            # Skip DUPE videos
            if "DUPE" in title:
                continue
            
            missing_tags = check_missing_keywords(tags)
            new_desc = build_description_with_keywords(desc, title)
            
            needs_update = bool(missing_tags) or new_desc is not None
            
            results.append({
                "id": vid,
                "title": title,
                "current_tags": len(tags),
                "missing_tags": missing_tags,
                "needs_desc_update": new_desc is not None,
                "needs_update": needs_update,
            })
    
    return results


def apply_updates(yt, wochenschau_videos: list[dict], max_updates: int = 999) -> dict:
    """Apply keyword updates to Wochenschau videos."""
    updated = 0
    failed = 0
    skipped = 0
    details = []
    
    # Get full video data first
    all_ids = [v["id"] for v in wochenschau_videos]
    video_data = {}
    
    for i in range(0, len(all_ids), 50):
        batch_ids = ",".join(all_ids[i:i+50])
        resp = yt.videos().list(part="snippet,status", id=batch_ids).execute()
        for item in resp.get("items", []):
            video_data[item["id"]] = item
    
    for vid_info in wochenschau_videos:
        if updated >= max_updates:
            break
            
        vid = vid_info["id"]
        if vid not in video_data:
            continue
            
        item = video_data[vid]
        snippet = item["snippet"]
        title = snippet["title"]
        privacy = item["status"]["privacyStatus"]
        
        if privacy != "public" or "DUPE" in title:
            skipped += 1
            continue
        
        tags = snippet.get("tags", [])
        desc = snippet["description"]
        
        # Check what needs updating
        missing_tags = check_missing_keywords(tags)
        new_desc = build_description_with_keywords(desc, title)
        
        if not missing_tags and new_desc is None:
            skipped += 1
            continue
        
        # Build new tags (merge existing + missing, cap at 30)
        new_tags = list(tags)  # Keep existing
        tags_lower = {t.lower() for t in new_tags}
        for kw in MUST_HAVE_TAGS:
            if kw.lower() not in tags_lower:
                new_tags.append(kw)
                tags_lower.add(kw.lower())
        
        # Cap at 30 tags
        if len(new_tags) > 30:
            new_tags = new_tags[:30]
        
        # Prepare update
        update_snippet = {
            "title": title,
            "description": new_desc if new_desc else desc,
            "tags": new_tags,
            "categoryId": snippet["categoryId"],
        }
        
        try:
            yt.videos().update(
                part="snippet",
                body={"id": vid, "snippet": update_snippet}
            ).execute()
            
            updated += 1
            added = len(new_tags) - len(tags)
            print(f"  ✅ [{updated}] {title[:60]} (+{added} tags, desc={'YES' if new_desc else 'no'})")
            details.append({"id": vid, "title": title, "status": "updated", "tags_added": added})
            
            # Rate limit: 1 update per second
            time.sleep(1)
            
        except Exception as exc:
            failed += 1
            print(f"  ❌ {title[:60]}: {exc}")
            details.append({"id": vid, "title": title, "status": "failed", "error": str(exc)})
    
    return {
        "updated": updated,
        "failed": failed,
        "skipped": skipped,
        "details": details,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add History/Documentary/Discovery keywords to Wochenschau videos")
    parser.add_argument("--scan", action="store_true", help="Scan only, show what needs updating")
    parser.add_argument("--apply", action="store_true", help="Apply keyword updates")
    parser.add_argument("--max", type=int, default=999, help="Max videos to update")
    args = parser.parse_args()
    
    if not args.scan and not args.apply:
        parser.print_help()
        return
    
    yt = get_youtube()
    
    print("\n📡 Scanning channel for Wochenschau videos...")
    wochenschau = get_all_wochenschau_ids(yt)
    print(f"   Found {len(wochenschau)} Wochenschau videos\n")
    
    if args.scan:
        results = scan_videos(yt, wochenschau)
        needs_update = [r for r in results if r["needs_update"]]
        
        print(f"\n{'='*70}")
        print(f"  WOCHENSCHAU KEYWORD SCAN RESULTS")
        print(f"{'='*70}")
        print(f"  Total Wochenschau videos:  {len(results)}")
        print(f"  Need keyword updates:      {len(needs_update)}")
        print(f"  Already optimized:         {len(results) - len(needs_update)}")
        print(f"  Estimated quota cost:      {len(needs_update) * 51} Units")
        print()
        
        if needs_update:
            print("  MISSING KEYWORDS SUMMARY:")
            from collections import Counter
            all_missing = Counter()
            for r in needs_update:
                for tag in r["missing_tags"]:
                    all_missing[tag] += 1
            
            for tag, count in all_missing.most_common(15):
                print(f"    {tag:40s} missing on {count} videos")
            
            print(f"\n  Videos needing description update: {sum(1 for r in needs_update if r['needs_desc_update'])}")
        
        # Save report
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_FILE.open("w", encoding="utf-8") as f:
            json.dump({"scan_date": time.strftime("%Y-%m-%d"), "results": results}, f, indent=2)
        print(f"\n  Report saved: {REPORT_FILE}")
    
    elif args.apply:
        print(f"  Applying keyword updates (max {args.max})...")
        print(f"  Estimated quota: {min(len(wochenschau), args.max) * 51} Units\n")
        
        result = apply_updates(yt, wochenschau, max_updates=args.max)
        
        print(f"\n{'='*70}")
        print(f"  UPDATE RESULTS")
        print(f"{'='*70}")
        print(f"  Updated:  {result['updated']}")
        print(f"  Failed:   {result['failed']}")
        print(f"  Skipped:  {result['skipped']}")
        print(f"  Quota:    ~{result['updated'] * 51 + len(wochenschau)} Units")
        
        # Save report
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_FILE.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Report saved: {REPORT_FILE}")


if __name__ == "__main__":
    main()
