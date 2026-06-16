"""
P0 Fix: Add 'remastered' + 'restored' Tags to 21 Videos
=========================================================

QUOTA: 21 × 51 = ~1,071 Units
BUG-FIX: NUR part='snippet' — NIEMALS 'status'!

Usage:
    python fix_remastered_tags.py --dry-run   # Preview
    python fix_remastered_tags.py --apply      # Execute
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# ── Config ──
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

# 21 Videos missing remastered/restored tags (6 DUPEs excluded)
TARGET_VIDEO_IDS = [
    "TLdsnAi8bWg",  # Skeleton Dance — 73,751 views!
    "tk3DHvp9CFs",  # Astronomer's Dream — 2,371 views
    "s_0yOzCKDa8",
    "hvJsq7z3sjg",
    "eX5cbYwNvnI",
    "Q_hgdk3UaJs",
    "eF81rBeXbzk",
    "ndAzCIUxo-c",
    "A8LWgWF5f5k",
    "TWodj8k8-zU",
    "sp1AzW-_rV0",
    "HGg-g6SwrrQ",
    "1O8sVLS-zfI",
    "D_kLmNFlbZI",
    "aKcgVrL3wvQ",
    "CKLYjy30fIw",
    "70Ni30lbXRc",
    "HCj_w3pBxlc",
    "u5poUF6KQfA",
    "5_Rx2lmeRfw",
    "U6CAhg95Izk",
]

# Tags to ensure exist
REQUIRED_TAGS = ["remastered", "restored", "AI enhanced", "upscaled", "classic"]

# Max 15 tags total (YouTube policy)
MAX_TAGS = 15


def get_oauth_credentials():
    """Load OAuth credentials for write operations."""
    token_path = Path(__file__).parent.parent.parent / "token.json"
    if not token_path.exists():
        print(f"ERROR: {token_path} not found!")
        sys.exit(1)

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = Credentials.from_authorized_user_file(str(token_path))
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json())
    return creds


def fetch_videos_public(video_ids: list[str]) -> list[dict]:
    """Fetch video snippets via Public API (1 Unit per 50 IDs)."""
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = requests.get(
            "https://youtube.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet",  # NUR snippet!
                "id": ",".join(batch),
                "key": API_KEY,
            }
        )
        if resp.status_code != 200:
            print(f"ERROR: videos.list returned {resp.status_code}: {resp.text[:200]}")
            return results
        data = resp.json()
        results.extend(data.get("items", []))
        print(f"  Fetched {len(data.get('items', []))} videos (batch {i//50+1})")
    return results


def fix_tags(video: dict) -> tuple[list[str], list[str], bool]:
    """
    Add required tags, respecting MAX_TAGS limit.
    Returns (new_tags, added_tags, changed).
    """
    snippet = video.get("snippet", {})
    current_tags = list(snippet.get("tags", []))
    current_lower = [t.lower() for t in current_tags]

    added = []
    for tag in REQUIRED_TAGS:
        if tag.lower() not in current_lower:
            if len(current_tags) < MAX_TAGS:
                current_tags.append(tag)
                added.append(tag)
            else:
                # Replace last tag if we're at limit
                # (lowest priority tag = last one)
                break

    return current_tags, added, len(added) > 0


def apply_update(creds, video_id: str, new_tags: list[str], snippet: dict) -> bool:
    """Apply tag update via OAuth. part='snippet' ONLY!"""
    from googleapiclient.discovery import build

    youtube = build("youtube", "v3", credentials=creds)

    snippet_copy = dict(snippet)
    snippet_copy["tags"] = new_tags
    # categoryId is REQUIRED in snippet update
    if "categoryId" not in snippet_copy:
        snippet_copy["categoryId"] = "1"

    try:
        youtube.videos().update(
            part="snippet",  # NUR snippet! NIEMALS status!
            body={
                "id": video_id,
                "snippet": snippet_copy,
            }
        ).execute()
        return True
    except Exception as e:
        print(f"  ERROR updating {video_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Add remastered/restored tags")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Usage: --dry-run or --apply")
        sys.exit(1)

    if not API_KEY:
        print("ERROR: YOUTUBE_API_KEY not set!")
        sys.exit(1)

    print(f"{'DRY RUN' if args.dry_run else 'APPLYING'}: Fix remastered tags on {len(TARGET_VIDEO_IDS)} videos")
    print(f"Required tags: {REQUIRED_TAGS}")
    print(f"Estimated quota: {len(TARGET_VIDEO_IDS) * 51} units\n")

    # Step 1: Fetch current state (Public API — 1 unit)
    print("Step 1: Fetching current video data...")
    videos = fetch_videos_public(TARGET_VIDEO_IDS)
    print(f"  Got {len(videos)} videos\n")

    if not videos:
        print("ERROR: No videos found!")
        sys.exit(1)

    # Step 2: Calculate changes
    changes = []
    for video in videos:
        vid = video["id"]
        title = video["snippet"]["title"][:60]
        current_tags = video["snippet"].get("tags", [])
        new_tags, added, changed = fix_tags(video)

        if changed:
            changes.append({
                "id": vid,
                "title": title,
                "current_count": len(current_tags),
                "new_count": len(new_tags),
                "added": added,
                "new_tags": new_tags,
                "snippet": video["snippet"],
            })
            print(f"  [{vid}] {title}")
            print(f"    Tags: {len(current_tags)} → {len(new_tags)} (+{len(added)})")
            print(f"    Added: {added}")
        else:
            print(f"  [{vid}] {title} — ALREADY OK")

    print(f"\n--- Summary ---")
    print(f"Videos to fix: {len(changes)}/{len(videos)}")
    print(f"Quota needed: {len(changes) * 50 + 1} units (1 list + {len(changes)} updates)")

    if args.dry_run:
        # Save preview
        out_path = Path(__file__).parent.parent.parent / "config" / "remastered_tags_preview.json"
        preview = [{
            "id": c["id"],
            "title": c["title"],
            "added_tags": c["added"],
            "tag_count": f"{c['current_count']}→{c['new_count']}",
        } for c in changes]
        out_path.write_text(json.dumps(preview, indent=2, ensure_ascii=False))
        print(f"\nPreview saved to: {out_path}")
        return

    # Step 3: Apply (OAuth)
    if not changes:
        print("Nothing to fix!")
        return

    print(f"\nStep 3: Applying {len(changes)} updates...")
    creds = get_oauth_credentials()

    success = 0
    errors = 0
    for i, change in enumerate(changes):
        result = apply_update(creds, change["id"], change["new_tags"], change["snippet"])
        if result:
            success += 1
            print(f"  [{i+1}/{len(changes)}] ✓ {change['id']} — +{change['added']}")
        else:
            errors += 1
            print(f"  [{i+1}/{len(changes)}] ✗ {change['id']} — FAILED")

        time.sleep(0.5)  # Rate limit

    print(f"\n--- Results ---")
    print(f"Success: {success}")
    print(f"Errors:  {errors}")
    print(f"Quota used: ~{success * 50 + 1} units")

    # Save result
    result_path = Path(__file__).parent.parent.parent / "config" / "remastered_tags_result.json"
    result_path.write_text(json.dumps({
        "date": datetime.now().isoformat(),
        "success": success,
        "errors": errors,
        "quota_used": success * 50 + 1,
        "changes": [{
            "id": c["id"],
            "title": c["title"],
            "added": c["added"],
        } for c in changes],
    }, indent=2, ensure_ascii=False))
    print(f"Result saved to: {result_path}")


if __name__ == "__main__":
    main()
