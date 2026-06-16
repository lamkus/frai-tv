#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Apply YouTube video fixes from video_master_db_v3.json.
Priority: top-performing videos first (by views).
Budget: 10,000 quota units.

Step 1: Re-authenticate (refresh token or interactive OAuth)
Step 2: Apply fixes from database

Each videos.update call costs ~50 quota (snippet part).
GET costs 1 quota unit per video.
"""

import json
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
import os
from datetime import datetime, timezone

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CONFIG_DIR, "video_master_db_v3.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
OAUTH_PATH = os.path.join(CONFIG_DIR, "youtube_oauth.json")
CLIENT_SECRET_PATH = os.path.join(CONFIG_DIR, "client_secret.json")
REPORT_PATH = os.path.join(CONFIG_DIR, "proper_fix_2026_04_02.json")

QUOTA_BUDGET = 10000
QUOTA_PER_GET = 1
QUOTA_PER_UPDATE = 50
QUOTA_PER_VIDEO = QUOTA_PER_GET + QUOTA_PER_UPDATE  # 51

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_valid_credentials():
    """Get valid OAuth credentials, re-authenticating if needed."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None

    # Try loading existing credentials from youtube_oauth.json
    if os.path.exists(OAUTH_PATH):
        try:
            oauth_data = load_json(OAUTH_PATH)
            creds = Credentials(
                token=oauth_data.get("token"),
                refresh_token=oauth_data.get("refresh_token"),
                token_uri=oauth_data.get("token_uri", "https://oauth2.googleapis.com/token"),
                client_id=oauth_data.get("client_id"),
                client_secret=oauth_data.get("client_secret"),
                scopes=oauth_data.get("scopes", SCOPES)
            )
        except Exception as e:
            print(f"Could not load {OAUTH_PATH}: {e}")

    # Try loading from token.json format
    if creds is None and os.path.exists(TOKEN_PATH):
        try:
            token_data = load_json(TOKEN_PATH)
            client_data = load_json(CLIENT_SECRET_PATH)
            client = client_data.get("installed", client_data.get("web", {}))
            creds = Credentials(
                token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client["client_id"],
                client_secret=client["client_secret"],
                scopes=SCOPES
            )
        except Exception as e:
            print(f"Could not load {TOKEN_PATH}: {e}")

    # Try to refresh if we have credentials
    if creds and creds.refresh_token:
        try:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            print("Token refreshed successfully!")
            # Save refreshed token
            _save_creds(creds)
            return creds
        except Exception as e:
            print(f"Token refresh failed: {e}")
            creds = None

    # Interactive OAuth flow
    if creds is None or not creds.valid:
        print("\n" + "=" * 50)
        print("INTERACTIVE OAUTH AUTHENTICATION REQUIRED")
        print("=" * 50)
        print("Browser will open for Google sign-in.")
        print("Select the remAIke_IT / FRai.TV account!")
        print()

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH, SCOPES
        )
        creds = flow.run_local_server(
            port=0,
            prompt='consent',
            access_type='offline'
        )
        _save_creds(creds)
        print("New token saved!")

    return creds

def _save_creds(creds):
    """Save credentials to both token files."""
    # Save to youtube_oauth.json format
    oauth_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else SCOPES,
        "universe_domain": "googleapis.com",
        "account": "",
        "expiry": creds.expiry.isoformat() + "Z" if creds.expiry else ""
    }
    save_json(OAUTH_PATH, oauth_data)

    # Save to token.json format too
    token_data = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "scope": " ".join(SCOPES),
        "token_type": "Bearer",
        "expiry_date": int(creds.expiry.timestamp() * 1000) if creds.expiry else 0
    }
    save_json(TOKEN_PATH, token_data)

def api_request(url, access_token, method='GET', body=None):
    """Make an authenticated API request using urllib."""
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Accept', 'application/json')

    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        req.data = data

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8')), resp.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            err = json.loads(error_body)
        except:
            err = {"message": error_body}
        return {"error": err}, e.code

def get_video(video_id, access_token):
    """GET a video's snippet and localizations from YouTube API."""
    params = urllib.parse.urlencode({
        "part": "snippet,localizations",
        "id": video_id
    })
    url = f"https://www.googleapis.com/youtube/v3/videos?{params}"
    return api_request(url, access_token)

def update_video(video_id, snippet, localizations, access_token):
    """PUT update a video's snippet and localizations."""
    params = urllib.parse.urlencode({
        "part": "snippet,localizations"
    })
    url = f"https://www.googleapis.com/youtube/v3/videos?{params}"
    body = {
        "id": video_id,
        "snippet": snippet,
        "localizations": localizations
    }
    return api_request(url, access_token, method='PUT', body=body)

def main():
    print("=" * 60)
    print("YouTube Video Fix Script - Database-Driven")
    print(f"Budget: {QUOTA_BUDGET} quota units")
    print("=" * 60)

    # Step 1: Authentication
    print("\n--- Step 1: Authentication ---")
    creds = get_valid_credentials()
    access_token = creds.token

    # Verify with a test call
    test_result, test_status = get_video("TLdsnAi8bWg", access_token)
    if test_status != 200:
        print(f"API test failed: {test_result}")
        sys.exit(1)
    print(f"API test OK: {test_result['items'][0]['snippet']['title'][:50]}")

    # Step 2: Load database
    print("\n--- Step 2: Loading database ---")
    db = load_json(DB_PATH)

    # Get videos that need changes, sorted by views (descending)
    videos_to_fix = []
    for vid_id, v in db["videos"].items():
        if v.get("has_changes"):
            views = v.get("metrics", {}).get("views", 0)
            videos_to_fix.append((vid_id, v, views))

    videos_to_fix.sort(key=lambda x: x[2], reverse=True)
    print(f"Total videos with changes: {len(videos_to_fix)}")

    # Calculate how many we can do (subtract 1 for test call)
    max_videos = (QUOTA_BUDGET - 1) // QUOTA_PER_VIDEO
    videos_to_fix = videos_to_fix[:max_videos]
    print(f"Will fix top {len(videos_to_fix)} videos (by views)")

    # Step 3: Apply fixes
    print("\n--- Step 3: Applying fixes ---")

    report = {
        "run_date": datetime.now(timezone.utc).isoformat(),
        "budget": QUOTA_BUDGET,
        "quota_per_video": QUOTA_PER_VIDEO,
        "total_attempted": 0,
        "total_success": 0,
        "total_failed": 0,
        "total_skipped": 0,
        "quota_used": 1,  # test call
        "results": []
    }

    quota_used = 1  # test call
    success_count = 0
    fail_count = 0
    skip_count = 0

    for idx, (vid_id, db_entry, views) in enumerate(videos_to_fix):
        if quota_used + QUOTA_PER_VIDEO > QUOTA_BUDGET:
            print(f"\n[BUDGET] Quota budget reached at video {idx}. Stopping.")
            break

        change_types = db_entry.get("change_types", [])
        ideal = db_entry.get("ideal", {})
        current_title = db_entry["current"]["title"]

        print(f"\n[{idx+1}/{len(videos_to_fix)}] {vid_id} ({views} views) [{db_entry.get('series','')}]")
        print(f"  Current: {current_title[:70]}")

        # GET current state from YouTube
        result, status = get_video(vid_id, access_token)
        quota_used += QUOTA_PER_GET

        if status == 401:
            # Token expired mid-run, refresh
            print("  Token expired, refreshing...")
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            access_token = creds.token
            _save_creds(creds)
            result, status = get_video(vid_id, access_token)
            quota_used += QUOTA_PER_GET

        if status != 200 or "error" in result:
            print(f"  ERROR getting video: {str(result.get('error', {}))[:100]}")
            fail_count += 1
            report["results"].append({
                "id": vid_id, "status": "get_failed",
                "error": str(result)[:200], "views": views,
                "series": db_entry.get("series")
            })
            continue

        items = result.get("items", [])
        if not items:
            print(f"  SKIP: Video not found")
            skip_count += 1
            report["results"].append({
                "id": vid_id, "status": "not_found", "views": views,
                "series": db_entry.get("series")
            })
            continue

        yt_video = items[0]
        yt_snippet = yt_video.get("snippet", {})
        yt_localizations = yt_video.get("localizations", {})

        # Build updated snippet - keep all existing fields
        new_snippet = {
            "categoryId": yt_snippet.get("categoryId"),
            "title": yt_snippet.get("title"),
            "description": yt_snippet.get("description", ""),
            "tags": yt_snippet.get("tags", []),
            "defaultLanguage": yt_snippet.get("defaultLanguage") or "en",
            "defaultAudioLanguage": yt_snippet.get("defaultAudioLanguage") or "en",
        }

        changes_applied = []

        # Apply title change
        if "title" in change_types and ideal.get("title"):
            old_title = new_snippet["title"]
            new_title = ideal["title"]
            if old_title != new_title:
                new_snippet["title"] = new_title
                changes_applied.append(f"title: removed suffix")
                print(f"  -> {new_title[:70]}")

        # Apply category change
        if "category" in change_types and ideal.get("categoryId"):
            old_cat = new_snippet["categoryId"]
            new_cat = ideal["categoryId"]
            if old_cat != new_cat:
                new_snippet["categoryId"] = new_cat
                changes_applied.append(f"category: {old_cat}->{new_cat}")
                print(f"  Category: {old_cat} -> {new_cat}")

        # Apply localization changes
        new_localizations = dict(yt_localizations)
        loc_changes = 0

        if "localizations" in change_types and ideal.get("localizations"):
            ideal_locs = ideal["localizations"]
            for lang, ideal_title in ideal_locs.items():
                if lang in new_localizations:
                    old_loc_title = new_localizations[lang].get("title", "")
                    if old_loc_title != ideal_title:
                        new_localizations[lang] = dict(new_localizations[lang])
                        new_localizations[lang]["title"] = ideal_title
                        loc_changes += 1
                else:
                    # New localization
                    new_localizations[lang] = {
                        "title": ideal_title,
                        "description": yt_snippet.get("description", "")
                    }
                    loc_changes += 1

            if loc_changes > 0:
                changes_applied.append(f"localizations: {loc_changes} langs")
                print(f"  Localizations: {loc_changes} updated")

        if not changes_applied:
            print(f"  SKIP: Already up to date")
            skip_count += 1
            report["results"].append({
                "id": vid_id, "status": "already_current", "views": views,
                "series": db_entry.get("series")
            })
            continue

        # PUT update
        result, status = update_video(vid_id, new_snippet, new_localizations, access_token)
        quota_used += QUOTA_PER_UPDATE

        if status == 200 and "error" not in result:
            success_count += 1
            print(f"  OK ({', '.join(changes_applied)})")
            report["results"].append({
                "id": vid_id, "status": "success", "views": views,
                "series": db_entry.get("series"),
                "changes": changes_applied
            })
        else:
            fail_count += 1
            error_msg = str(result.get("error", {}))[:200]
            print(f"  FAILED: {error_msg}")
            report["results"].append({
                "id": vid_id, "status": "update_failed", "views": views,
                "series": db_entry.get("series"),
                "error": error_msg,
                "changes_attempted": changes_applied
            })

            # Handle token expiry
            if status == 401:
                print("  Refreshing token and retrying...")
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                access_token = creds.token
                _save_creds(creds)
                result, status = update_video(vid_id, new_snippet, new_localizations, access_token)
                quota_used += QUOTA_PER_UPDATE
                if status == 200 and "error" not in result:
                    success_count += 1
                    fail_count -= 1
                    report["results"][-1]["status"] = "success_after_retry"
                    print(f"  RETRY OK")

        # Rate limit
        time.sleep(0.3)

    # Final report
    report["total_attempted"] = success_count + fail_count + skip_count
    report["total_success"] = success_count
    report["total_failed"] = fail_count
    report["total_skipped"] = skip_count
    report["quota_used"] = quota_used

    save_json(REPORT_PATH, report)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Attempted: {report['total_attempted']}")
    print(f"Success:   {success_count}")
    print(f"Failed:    {fail_count}")
    print(f"Skipped:   {skip_count}")
    print(f"Quota used: ~{quota_used}")
    print(f"Report:    {REPORT_PATH}")

if __name__ == "__main__":
    main()
