#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical fix script: revert [8K] titles, fix Wochenschau categories, add Full Movie.
Uses urllib only. UTF-8 everywhere.
"""
import json
import re
import time
import urllib.request
import urllib.parse
import urllib.error
import sys
import os
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
OAUTH_PATH   = r"D:\remaike.TV\config\youtube_oauth.json"
VIDEOS_PATH  = r"D:\remaike.TV\config\all_videos_raw.json"
REPORT_PATH  = r"D:\remaike.TV\config\critical_title_fix_2026_04_14.json"

# ── Auth helpers ────────────────────────────────────────────────────────────
def load_oauth():
    with open(OAUTH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def refresh_access_token(oauth):
    """Refresh the OAuth2 access token."""
    data = urllib.parse.urlencode({
        "client_id":     oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "refresh_token": oauth["refresh_token"],
        "grant_type":    "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    oauth["token"] = result["access_token"]
    # persist refreshed token
    with open(OAUTH_PATH, "w", encoding="utf-8") as f:
        json.dump(oauth, f, indent=2, ensure_ascii=False)
    print(f"[AUTH] Token refreshed successfully.")
    return oauth

def get_token(oauth):
    return oauth["token"]

# ── YouTube API helpers ─────────────────────────────────────────────────────
def yt_update_video(token, video_id, snippet_patch, category_id=None):
    """
    PUT to videos.update with part=snippet.
    snippet_patch = dict with keys to set (title, categoryId, etc.)
    We must send the full snippet minus thumbnails.
    """
    # First fetch the current snippet to preserve all fields
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    if not data.get("items"):
        return {"error": f"Video {video_id} not found"}

    item = data["items"][0]
    snippet = item["snippet"]

    # Apply patches
    for k, v in snippet_patch.items():
        snippet[k] = v
    if category_id:
        snippet["categoryId"] = category_id

    # Remove thumbnails (can't send them in update)
    snippet.pop("thumbnails", None)

    # Build the update body
    body = {
        "id": video_id,
        "snippet": snippet
    }

    body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet"
    req = urllib.request.Request(url, data=body_bytes, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        return {"error": f"HTTP {e.code}", "detail": err_body}

# ── Duration helper ─────────────────────────────────────────────────────────
def duration_seconds(iso_dur):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_dur or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("CRITICAL FIX SCRIPT - Title Revert, Category Fix, Full Movie Add")
    print("=" * 70)

    # Load data
    oauth = load_oauth()
    oauth = refresh_access_token(oauth)
    token = get_token(oauth)

    with open(VIDEOS_PATH, "r", encoding="utf-8") as f:
        all_videos = json.load(f)

    print(f"Loaded {len(all_videos)} videos from cache.")

    # ── TASK 1: Find [8K] bracket titles ────────────────────────────────────
    bracket_videos = [v for v in all_videos if "[8K]" in v["snippet"]["title"]]
    print(f"\nTASK 1: Found {len(bracket_videos)} videos with [8K] in title.")

    # ── TASK 2: Find Wochenschau in category 27 ────────────────────────────
    ws27_videos = [v for v in all_videos if "ochenschau" in v["snippet"]["title"].lower() and v["snippet"]["categoryId"] == "27"]
    print(f"TASK 2: Found {len(ws27_videos)} Wochenschau videos in category 27.")

    # ── TASK 3: Find long videos without Full Movie ────────────────────────
    long_no_fm = []
    for v in all_videos:
        dur = duration_seconds(v["contentDetails"]["duration"])
        title = v["snippet"]["title"]
        if dur >= 2700 and "full movie" not in title.lower() and "ganzer film" not in title.lower():
            long_no_fm.append(v)
    print(f"TASK 3: Found {len(long_no_fm)} videos >45min without 'Full Movie'/'Ganzer Film'.")

    # ── Build update plan ───────────────────────────────────────────────────
    # Each entry: {video_id, old_title, new_title, old_cat, new_cat, tasks}
    updates = {}  # keyed by video_id

    # Task 1: Fix [8K] -> | 8K HQ (4K UHD)
    for v in bracket_videos:
        vid = v["id"]
        old_title = v["snippet"]["title"]
        new_title = old_title.replace("[8K]", "| 8K HQ (4K UHD)").strip()
        # Clean up any double spaces
        new_title = re.sub(r"\s{2,}", " ", new_title)
        updates[vid] = {
            "video_id": vid,
            "old_title": old_title,
            "new_title": new_title,
            "old_cat": v["snippet"]["categoryId"],
            "new_cat": None,
            "tasks": ["revert_8k_title"],
        }

    # Task 2: Fix Wochenschau category 27 -> 1
    for v in ws27_videos:
        vid = v["id"]
        if vid in updates:
            updates[vid]["new_cat"] = "1"
            updates[vid]["tasks"].append("fix_wochenschau_category")
        else:
            updates[vid] = {
                "video_id": vid,
                "old_title": v["snippet"]["title"],
                "new_title": None,  # no title change
                "old_cat": "27",
                "new_cat": "1",
                "tasks": ["fix_wochenschau_category"],
            }

    # Task 3: Add "Full Movie" before quality tag
    for v in long_no_fm:
        vid = v["id"]
        title = updates[vid]["new_title"] if vid in updates and updates[vid]["new_title"] else v["snippet"]["title"]

        # Insert "Full Movie" before the quality tag
        # Quality tag patterns: "| 8K HQ (4K UHD)", "| 8K (4K UHD)", "[8K]" (already handled)
        # We look for the last "|" before the 8K tag and insert before it
        # Pattern: find "| 8K" or "| 8K HQ" at end
        quality_pattern = r"\|\s*8K\s*(HQ\s*)?\(4K\s*UHD\)\s*$"
        m = re.search(quality_pattern, title)
        if m:
            insert_pos = m.start()
            new_title = title[:insert_pos] + "| Full Movie " + title[insert_pos:]
            new_title = re.sub(r"\s{2,}", " ", new_title).strip()
        else:
            # No quality tag found, just append
            new_title = title + " | Full Movie"

        if vid in updates:
            updates[vid]["new_title"] = new_title
            updates[vid]["tasks"].append("add_full_movie")
        else:
            updates[vid] = {
                "video_id": vid,
                "old_title": v["snippet"]["title"],
                "new_title": new_title,
                "old_cat": v["snippet"]["categoryId"],
                "new_cat": None,
                "tasks": ["add_full_movie"],
            }

    total = len(updates)
    quota_needed = total * 50
    print(f"\nTotal unique videos to update: {total}")
    print(f"Estimated quota: {quota_needed} units")

    if quota_needed > 10000:
        print(f"WARNING: Exceeds 10,000 quota budget! Aborting.")
        return

    # ── Execute updates ─────────────────────────────────────────────────────
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_planned": total,
            "task1_revert_8k": len(bracket_videos),
            "task2_fix_category": len(ws27_videos),
            "task3_add_full_movie": len(long_no_fm),
            "quota_estimated": quota_needed,
        },
        "results": [],
        "errors": [],
    }

    success_count = 0
    error_count = 0
    quota_used = 0

    # Sort: bracket title fixes first, then category fixes, then full movie
    sorted_updates = sorted(updates.values(), key=lambda u: (
        0 if "revert_8k_title" in u["tasks"] else 1,
        0 if "fix_wochenschau_category" in u["tasks"] else 1,
    ))

    for i, upd in enumerate(sorted_updates):
        vid = upd["video_id"]
        snippet_patch = {}
        cat_id = None

        if upd["new_title"]:
            snippet_patch["title"] = upd["new_title"]
        if upd["new_cat"]:
            cat_id = upd["new_cat"]

        # If nothing to change, skip
        if not snippet_patch and not cat_id:
            print(f"[{i+1}/{total}] SKIP {vid} - nothing to change")
            continue

        tasks_str = "+".join(upd["tasks"])
        title_info = f'"{upd["old_title"]}"'
        if upd["new_title"]:
            title_info += f' -> "{upd["new_title"]}"'
        cat_info = ""
        if cat_id:
            cat_info = f" cat:{upd['old_cat']}->{cat_id}"

        print(f"[{i+1}/{total}] {tasks_str} | {vid} | {title_info}{cat_info}")

        try:
            result = yt_update_video(token, vid, snippet_patch, cat_id)
            if "error" in result:
                error_detail = result.get("detail", "")
                # Check for auth error and retry once
                if "401" in str(result.get("error", "")):
                    print("  -> Token expired, refreshing...")
                    oauth = refresh_access_token(oauth)
                    token = get_token(oauth)
                    result = yt_update_video(token, vid, snippet_patch, cat_id)

                if "error" in result:
                    print(f"  -> ERROR: {result['error']}")
                    report["errors"].append({
                        "video_id": vid,
                        "tasks": upd["tasks"],
                        "error": str(result),
                    })
                    error_count += 1
                    continue

            new_title_actual = result.get("snippet", {}).get("title", "?")
            new_cat_actual = result.get("snippet", {}).get("categoryId", "?")
            print(f"  -> OK: title=\"{new_title_actual}\" cat={new_cat_actual}")

            report["results"].append({
                "video_id": vid,
                "tasks": upd["tasks"],
                "old_title": upd["old_title"],
                "new_title": new_title_actual,
                "old_category": upd["old_cat"],
                "new_category": new_cat_actual,
                "status": "success",
            })
            success_count += 1
            quota_used += 50  # read costs 1, update costs 50

        except Exception as e:
            print(f"  -> EXCEPTION: {e}")
            report["errors"].append({
                "video_id": vid,
                "tasks": upd["tasks"],
                "error": str(e),
            })
            error_count += 1

        # Small delay to be nice to the API
        if (i + 1) % 10 == 0:
            time.sleep(1)

    # ── Save report ─────────────────────────────────────────────────────────
    report["summary"]["success"] = success_count
    report["summary"]["errors"] = error_count
    report["summary"]["quota_used"] = quota_used

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 70}")
    print(f"DONE: {success_count} success, {error_count} errors, ~{quota_used} quota used")
    print(f"Report saved to: {REPORT_PATH}")
    print(f"{'=' * 70}")

if __name__ == "__main__":
    main()
