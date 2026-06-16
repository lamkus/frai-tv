#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final YouTube optimization run for @remAIke_IT
Tasks:
  1. Fix remaining Wochenschau category (27 -> 1)
  2. Add "Full Movie" to feature-length titles (>45min)
  3. Update NASA/Skylab descriptions for Artemis 2
  4. Verification scan of all public videos

Quota-efficient: fetches uploads once, uses that for all tasks.
No search endpoint (saves 200 quota).
"""

import sys, io, json, time, urllib.request, urllib.parse, urllib.error, re, os
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ── Config ──────────────────────────────────────────────────────────────
OAUTH_PATH = r"D:\remaike.TV\config\youtube_oauth.json"
REPORT_PATH = r"D:\remaike.TV\config\finalization_report_2026_04_15.json"
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOADS_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"

quota_used = 0
report = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "tasks": {},
    "verification": {},
    "quota_used": 0
}

# ── OAuth ───────────────────────────────────────────────────────────────
def load_oauth():
    with open(OAUTH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def refresh_access_token(oauth):
    data = urllib.parse.urlencode({
        "client_id": oauth["client_id"],
        "client_secret": oauth["client_secret"],
        "refresh_token": oauth["refresh_token"],
        "grant_type": "refresh_token"
    }).encode("utf-8")
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    token = result["access_token"]
    oauth["token"] = token
    with open(OAUTH_PATH, "w", encoding="utf-8") as f:
        json.dump(oauth, f, indent=2, ensure_ascii=False)
    print("[AUTH] Token refreshed successfully")
    return token

# ── API helpers ─────────────────────────────────────────────────────────
class QuotaExceeded(Exception):
    pass

def api_get(url, token):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        if e.code == 403 and "quota" in body.lower():
            print(f"[QUOTA EXCEEDED] Cannot continue - daily quota exhausted.")
            raise QuotaExceeded(body[:300])
        print(f"[API ERROR] GET {e.code}: {body[:300]}")
        raise

def api_put(url, token, body):
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8") if e.fp else ""
        if e.code == 403 and "quota" in body_err.lower():
            print(f"[QUOTA EXCEEDED] Cannot continue - daily quota exhausted.")
            raise QuotaExceeded(body_err[:300])
        print(f"[API ERROR] PUT {e.code}: {body_err[:500]}")
        raise

def get_video_details(token, video_ids, parts="snippet,contentDetails,status,localizations"):
    """Get video details in batches of 50. ~1 quota per batch."""
    global quota_used
    results = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        ids_str = ",".join(batch)
        url = (f"https://www.googleapis.com/youtube/v3/videos"
               f"?part={urllib.parse.quote(parts)}&id={ids_str}")
        quota_used += 1
        data = api_get(url, token)
        results.extend(data.get("items", []))
    return results

def update_video(token, video_id, snippet=None, status=None, localizations=None):
    """Update video. Costs 50 quota."""
    global quota_used
    url = "https://www.googleapis.com/youtube/v3/videos?part="
    parts_list = []
    body = {"id": video_id}
    if snippet:
        parts_list.append("snippet")
        body["snippet"] = snippet
    if status:
        parts_list.append("status")
        body["status"] = status
    if localizations:
        parts_list.append("localizations")
        body["localizations"] = localizations
    url += ",".join(parts_list)
    quota_used += 50
    result = api_put(url, token, body)
    time.sleep(0.25)
    return result

def get_all_uploads(token):
    """Get ALL video IDs from the uploads playlist. ~1 quota per page."""
    global quota_used
    all_ids = []
    url = (f"https://www.googleapis.com/youtube/v3/playlistItems"
           f"?part=contentDetails&playlistId={UPLOADS_PLAYLIST}&maxResults=50")
    while url:
        quota_used += 1
        data = api_get(url, token)
        for item in data.get("items", []):
            all_ids.append(item["contentDetails"]["videoId"])
        npt = data.get("nextPageToken")
        if npt:
            url = (f"https://www.googleapis.com/youtube/v3/playlistItems"
                   f"?part=contentDetails&playlistId={UPLOADS_PLAYLIST}"
                   f"&maxResults=50&pageToken={npt}")
        else:
            url = None
    print(f"[UPLOADS] Found {len(all_ids)} videos in uploads playlist")
    return all_ids

def parse_duration_seconds(iso_dur):
    """Parse ISO 8601 duration like PT1H23M45S to seconds."""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_dur or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)

# ── TASK 1: Wochenschau category fix ───────────────────────────────────
def task1_wochenschau_category(token, all_details):
    print("\n" + "=" * 60)
    print("TASK 1: Fix Wochenschau category (27 -> 1)")
    print("=" * 60)

    # Find Wochenschau videos with wrong category from the already-fetched data
    wrong_cat = []
    for v in all_details:
        title = v["snippet"]["title"]
        cat = v["snippet"].get("categoryId", "")
        if "Wochenschau" in title and cat == "27":
            wrong_cat.append(v)

    print(f"  {len(wrong_cat)} Wochenschau videos still have categoryId=27")

    fixed = []
    for v in wrong_cat:
        vid = v["id"]
        snippet = v["snippet"]
        title = snippet["title"]
        snippet["categoryId"] = "1"
        print(f"  Fixing: {title}")
        try:
            update_video(token, vid, snippet=snippet)
            fixed.append({"id": vid, "title": title})
        except QuotaExceeded:
            raise
        except Exception as e:
            print(f"  ERROR fixing {vid}: {e}")

    report["tasks"]["task1_category_fix"] = {
        "found": len(wrong_cat),
        "fixed": len(fixed),
        "videos": fixed
    }
    print(f"  Task 1 done: {len(fixed)}/{len(wrong_cat)} fixed")
    return len(fixed)

# ── TASK 2: Add "Full Movie" to long titles ───────────────────────────
def task2_full_movie_titles(token, all_details):
    print("\n" + "=" * 60)
    print("TASK 2: Add 'Full Movie' to feature-length titles (>45min)")
    print("=" * 60)

    # Filter: public, >45 min, no "Full Movie" in title
    candidates = []
    for v in all_details:
        if v.get("status", {}).get("privacyStatus") != "public":
            continue
        dur = parse_duration_seconds(v.get("contentDetails", {}).get("duration", ""))
        if dur < 45 * 60:
            continue
        if "Full Movie" in v["snippet"]["title"]:
            continue
        candidates.append(v)

    print(f"  Found {len(candidates)} public videos >45min without 'Full Movie'")

    updated = []
    for v in candidates:
        vid = v["id"]
        snippet = v["snippet"]
        old_title = snippet["title"]

        # Insert "| Full Movie" before the quality tag
        new_title = old_title
        if "| 8K HQ (4K UHD)" in old_title:
            new_title = old_title.replace("| 8K HQ (4K UHD)", "| Full Movie | 8K HQ (4K UHD)")
        elif "[8K]" in old_title:
            new_title = old_title.replace("[8K]", "| Full Movie [8K]")
        else:
            new_title = old_title + " | Full Movie"

        # Enforce 100-char limit by dropping middle segments
        if len(new_title) > 100:
            parts = new_title.split(" | ")
            if len(parts) >= 4:
                quality = parts[-1]
                middle = [p for p in parts[1:-1] if p != "Full Movie"]
                while len(" | ".join([parts[0]] + middle + ["Full Movie", quality])) > 100 and middle:
                    middle.pop()
                new_title = " | ".join([parts[0]] + middle + ["Full Movie", quality])
            if len(new_title) > 100:
                new_title = new_title[:97] + "..."

        if new_title == old_title:
            continue

        dur = parse_duration_seconds(v.get("contentDetails", {}).get("duration", ""))
        print(f"  [{len(new_title)}c] ({dur // 60}min) {old_title}")
        print(f"       -> {new_title}")

        snippet["title"] = new_title
        try:
            update_video(token, vid, snippet=snippet)
            updated.append({"id": vid, "old": old_title, "new": new_title})
        except QuotaExceeded:
            raise
        except Exception as e:
            print(f"  ERROR updating {vid}: {e}")

    report["tasks"]["task2_full_movie"] = {
        "candidates": len(candidates),
        "updated": len(updated),
        "videos": updated
    }
    print(f"  Task 2 done: {len(updated)}/{len(candidates)} updated")
    return len(updated)

# ── TASK 3: NASA/Skylab Artemis 2 update ──────────────────────────────
def task3_skylab_artemis(token, all_details):
    print("\n" + "=" * 60)
    print("TASK 3: Update NASA/Skylab videos for Artemis 2")
    print("=" * 60)

    ARTEMIS_PREFIX = (
        "\U0001f680 Artemis II returned humans to the Moon in April 2026! "
        "Relive the missions that made it possible \u2014 restored in stunning 8K.\n\n"
        "\u2501" * 35 + "\n"
    )
    ARTEMIS_TAGS = ["Artemis 2", "Artemis II", "NASA 2026", "Moon landing", "space history", "8K space"]

    # Find Skylab videos from the already-fetched data
    skylab_videos = [v for v in all_details
                     if "Skylab" in v["snippet"].get("title", "")
                     or "skylab" in v["snippet"].get("title", "").lower()]
    print(f"  Found {len(skylab_videos)} Skylab videos")

    updated = []
    skipped = []

    for v in skylab_videos:
        vid = v["id"]
        snippet = v["snippet"]
        title = snippet["title"]
        desc = snippet.get("description", "")

        if "Artemis" in desc:
            print(f"  SKIP (already has Artemis): {title}")
            skipped.append({"id": vid, "title": title, "reason": "already has Artemis"})
            continue

        snippet["description"] = ARTEMIS_PREFIX + desc

        existing_tags = snippet.get("tags", [])
        new_tags = list(existing_tags)
        for tag in ARTEMIS_TAGS:
            if tag not in new_tags:
                new_tags.append(tag)
        if len(new_tags) > 15:
            new_tags = new_tags[:15]
        snippet["tags"] = new_tags

        print(f"  Updating: {title}")
        print(f"    Tags: {len(existing_tags)} -> {len(new_tags)}")
        try:
            update_video(token, vid, snippet=snippet)
            updated.append({"id": vid, "title": title, "tags_added": len(new_tags) - len(existing_tags)})
        except QuotaExceeded:
            raise
        except Exception as e:
            print(f"  ERROR updating {vid}: {e}")

    report["tasks"]["task3_skylab_artemis"] = {
        "found": len(skylab_videos),
        "updated": len(updated),
        "skipped": len(skipped),
        "videos_updated": updated,
        "videos_skipped": skipped
    }
    print(f"  Task 3 done: {len(updated)} updated, {len(skipped)} skipped")
    return len(updated)

# ── TASK 4: Verification (uses same data, re-fetches for post-update accuracy) ──
def task4_verification(token, all_ids):
    print("\n" + "=" * 60)
    print("TASK 4: Final verification scan (re-fetching for accuracy)")
    print("=" * 60)

    all_details = get_video_details(token, all_ids,
                                     parts="snippet,contentDetails,status,localizations")

    public = [v for v in all_details if v.get("status", {}).get("privacyStatus") == "public"]
    print(f"  {len(public)} public videos out of {len(all_details)} total")

    # Category distribution
    cat_dist = {}
    for v in public:
        cat = v["snippet"].get("categoryId", "?")
        cat_dist[cat] = cat_dist.get(cat, 0) + 1

    cat_names = {"1": "Film & Animation", "27": "Education", "22": "People & Blogs",
                 "10": "Music", "24": "Entertainment", "25": "News & Politics"}
    print("\n  Category distribution:")
    for cat_id, count in sorted(cat_dist.items(), key=lambda x: -x[1]):
        name = cat_names.get(cat_id, f"Category {cat_id}")
        print(f"    {cat_id} ({name}): {count}")

    # Title format
    title_8k_hq = sum(1 for v in public if "8K HQ (4K UHD)" in v["snippet"]["title"])
    title_8k_bracket = sum(1 for v in public if "[8K]" in v["snippet"]["title"] and "8K HQ" not in v["snippet"]["title"])
    title_other = len(public) - title_8k_hq - title_8k_bracket

    print(f"\n  Title format:")
    print(f"    '8K HQ (4K UHD)': {title_8k_hq}")
    print(f"    '[8K]': {title_8k_bracket}")
    print(f"    other: {title_other}")

    # Full Movie for long videos
    long_videos = [v for v in public
                   if parse_duration_seconds(v.get("contentDetails", {}).get("duration", "")) >= 45 * 60]
    with_fm = [v for v in long_videos if "Full Movie" in v["snippet"]["title"]]
    without_fm = [v for v in long_videos if "Full Movie" not in v["snippet"]["title"]]

    print(f"\n  Feature-length videos (>45min): {len(long_videos)}")
    print(f"    With 'Full Movie': {len(with_fm)}")
    print(f"    Without 'Full Movie': {len(without_fm)}")
    for v in without_fm:
        dur = parse_duration_seconds(v["contentDetails"].get("duration", ""))
        print(f"      - {v['snippet']['title']} ({dur // 60}min)")

    # Localizations
    loc_8plus = sum(1 for v in public if len(v.get("localizations", {})) >= 8)
    loc_under8 = sum(1 for v in public if 0 < len(v.get("localizations", {})) < 8)
    loc_none = sum(1 for v in public if len(v.get("localizations", {})) == 0)

    print(f"\n  Localizations:")
    print(f"    8+ languages: {loc_8plus}")
    print(f"    1-7 languages: {loc_under8}")
    print(f"    None: {loc_none}")

    report["verification"] = {
        "total_public": len(public),
        "total_all": len(all_details),
        "category_distribution": {f"{k} ({cat_names.get(k, '?')})": v for k, v in cat_dist.items()},
        "title_format": {
            "8K_HQ_4K_UHD": title_8k_hq,
            "bracket_8K": title_8k_bracket,
            "other": title_other
        },
        "feature_length": {
            "total_45plus_min": len(long_videos),
            "with_full_movie": len(with_fm),
            "without_full_movie": len(without_fm),
            "missing_titles": [v["snippet"]["title"] for v in without_fm]
        },
        "localizations": {
            "8plus_languages": loc_8plus,
            "1to7_languages": loc_under8,
            "none": loc_none
        }
    }

# ── Main ────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("remAIke.TV - FINAL YouTube Optimization Run")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    oauth = load_oauth()
    token = refresh_access_token(oauth)

    # Step 1: Fetch all upload IDs once (~10 quota for ~450 videos)
    all_ids = get_all_uploads(token)

    # Step 2: Fetch full details for ALL videos once (~10 quota)
    print("\n[FETCH] Loading full details for all videos...")
    all_details = get_video_details(token, all_ids,
                                     parts="snippet,contentDetails,status,localizations")
    print(f"[FETCH] Got details for {len(all_details)} videos")

    try:
        # Tasks 1-3 use the pre-fetched data for filtering, only call API for updates
        task1_wochenschau_category(token, all_details)
        task2_full_movie_titles(token, all_details)
        task3_skylab_artemis(token, all_details)

        # Task 4: Re-fetch for post-update verification
        task4_verification(token, all_ids)

    except QuotaExceeded:
        print("\n[FATAL] Quota exceeded mid-run. Saving partial report.")
        report["error"] = "Quota exceeded before all tasks completed"

    # Save report
    report["quota_used"] = quota_used
    report["completed"] = datetime.now(timezone.utc).isoformat()

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"ALL TASKS COMPLETE")
    print(f"Quota used: ~{quota_used} units")
    print(f"Report saved: {REPORT_PATH}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    try:
        main()
    except QuotaExceeded:
        print("\n[FATAL] YouTube API quota exceeded. Quota resets at 09:00 MESZ (07:00 UTC).")
        print("Re-run this script after quota reset.")
        report["error"] = "Quota exceeded - could not start. Re-run after reset."
        report["quota_used"] = quota_used
        report["completed"] = datetime.now(timezone.utc).isoformat()
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        sys.exit(1)
