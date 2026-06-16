# -*- coding: utf-8 -*-
"""
apply_master_fix.py - Apply pre-computed YouTube video fixes from channel_master_fix.json
Uses YouTube Data API v3 with OAuth2 refresh token flow.
Respects quota limits (10,000 units/day = 200 updates max at 50 units each).
"""

import io
import sys
import json
import os
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ─── Configuration ───────────────────────────────────────────────────────────
BASE_DIR = r"D:\remaike.TV\config"
FIX_FILE = os.path.join(BASE_DIR, "channel_master_fix.json")
OAUTH_FILE = os.path.join(BASE_DIR, "youtube_oauth.json")
TODAY = datetime.now().strftime("%Y-%m-%d")
PROGRESS_FILE = os.path.join(BASE_DIR, f"master_fix_progress_{TODAY}.json")

# Quota tracking
QUOTA_PER_UPDATE = 50  # videos.update costs 50 units
QUOTA_PER_LIST = 1     # videos.list costs 1 unit
QUOTA_LIMIT = 10000
MAX_UPDATES_PER_RUN = 200  # safety limit
QUOTA_STOP_THRESHOLD = 9000  # stop if quota used exceeds this

# API endpoints
TOKEN_URL = "https://oauth2.googleapis.com/token"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# ─── Helper Functions ────────────────────────────────────────────────────────

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def refresh_access_token(oauth_config):
    """Refresh the OAuth2 access token using the refresh token."""
    data = urllib.parse.urlencode({
        'client_id': oauth_config['client_id'],
        'client_secret': oauth_config['client_secret'],
        'refresh_token': oauth_config['refresh_token'],
        'grant_type': 'refresh_token'
    }).encode('utf-8')

    req = urllib.request.Request(TOKEN_URL, data=data, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['access_token']
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"ERROR refreshing token: {e.code} - {error_body}")
        raise


def api_get(url, access_token):
    """Make an authenticated GET request."""
    req = urllib.request.Request(url)
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Accept', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"GET {url} failed: {e.code} - {error_body}")


def api_put(url, access_token, body):
    """Make an authenticated PUT request with JSON body."""
    json_body = json.dumps(body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=json_body, method='PUT')
    req.add_header('Authorization', f'Bearer {access_token}')
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    req.add_header('Accept', 'application/json')

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"PUT failed: {e.code} - {error_body}")


def fetch_videos_batch(video_ids, access_token):
    """Fetch video snippets for up to 50 IDs at once."""
    ids_str = ','.join(video_ids)
    url = f"{VIDEOS_URL}?part=snippet&id={ids_str}"
    return api_get(url, access_token)


def clean_title(title):
    """Remove @remAIke_IT from title."""
    title = title.replace(' | @remAIke_IT', '')
    title = title.replace(' @remAIke_IT', '')
    title = title.replace('@remAIke_IT', '')
    return title.strip()


def ensure_quality_tag_in_title(title):
    """Ensure '8K HQ (4K UHD)' is in the title."""
    if '8K HQ (4K UHD)' in title:
        return title
    # Replace existing partial quality tags
    if '| 8K HQ' in title and '(4K UHD)' not in title:
        title = title.replace('| 8K HQ', '| 8K HQ (4K UHD)')
    elif '| 8K' in title and 'HQ' not in title:
        title = title.replace('| 8K', '| 8K HQ (4K UHD)')
    elif '8K' not in title:
        title = title + ' | 8K HQ (4K UHD)'
    return title


def enforce_tag_limits(tags):
    """Ensure max 15 tags, max ~500 chars total."""
    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in tags:
        t_lower = t.lower()
        if t_lower not in seen:
            seen.add(t_lower)
            unique_tags.append(t)
    tags = unique_tags

    # Max 15 tags
    tags = tags[:15]

    # Ensure total chars <= 500
    total = sum(len(t) for t in tags)
    while total > 500 and len(tags) > 5:
        removed = tags.pop()
        total -= len(removed)

    return tags


def ensure_required_tags(tags):
    """Ensure 'Remastered' and '8K' are in tags."""
    tag_lower = [t.lower() for t in tags]
    if 'remastered' not in tag_lower:
        tags.append('Remastered')
    if '8k' not in tag_lower:
        tags.append('8K')
    return tags


def enforce_description_limits(desc):
    """Max 5000 chars, max 5 hashtags at end."""
    # Count hashtags at end
    lines = desc.split('\n')
    # Find hashtag line(s) at the end
    hashtag_count = 0
    for line in reversed(lines):
        stripped = line.strip()
        if stripped.startswith('#') or (stripped and all(w.startswith('#') for w in stripped.split())):
            tags_in_line = [w for w in stripped.split() if w.startswith('#')]
            hashtag_count += len(tags_in_line)
        elif stripped:
            break

    # If more than 5 hashtags, trim the last line
    if hashtag_count > 5:
        # Find the hashtag line and trim
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped and all(w.startswith('#') for w in stripped.split()):
                words = stripped.split()
                lines[i] = ' '.join(words[:5])
                break
        desc = '\n'.join(lines)

    # Max 5000 chars
    if len(desc) > 5000:
        desc = desc[:5000]

    return desc


def build_update_body(video_id, current_snippet, fix_entry=None):
    """
    Build the videos.update request body.
    Merges fix plan with current data, preserving all required fields.
    """
    snippet = {
        'title': current_snippet.get('title', ''),
        'description': current_snippet.get('description', ''),
        'tags': current_snippet.get('tags', []),
        'categoryId': current_snippet.get('categoryId', '22'),
        'defaultLanguage': current_snippet.get('defaultLanguage', 'de'),
        'defaultAudioLanguage': current_snippet.get('defaultAudioLanguage', 'de'),
    }

    # Apply fix plan if available
    if fix_entry:
        if fix_entry.get('new_title'):
            snippet['title'] = fix_entry['new_title']
        if fix_entry.get('new_tags'):
            snippet['tags'] = fix_entry['new_tags']
        if fix_entry.get('new_description'):
            snippet['description'] = fix_entry['new_description']

    # Apply universal fixes
    snippet['title'] = clean_title(snippet['title'])
    snippet['title'] = ensure_quality_tag_in_title(snippet['title'])
    snippet['defaultLanguage'] = 'de'
    snippet['defaultAudioLanguage'] = 'de'
    snippet['tags'] = ensure_required_tags(snippet['tags'])
    snippet['tags'] = enforce_tag_limits(snippet['tags'])
    snippet['description'] = enforce_description_limits(snippet['description'])

    return {
        'id': video_id,
        'snippet': snippet
    }


def load_progress():
    """Load existing progress file if it exists for today."""
    if os.path.exists(PROGRESS_FILE):
        return load_json(PROGRESS_FILE)
    return {
        'date': TODAY,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'completed_ids': [],
        'error_ids': [],
        'errors': [],
        'quota_used': 0,
        'success_count': 0,
        'error_count': 0,
        'skipped_count': 0,
        'status': 'in_progress'
    }


# ─── Main Execution ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"  YouTube Master Fix - {TODAY}")
    print("=" * 60)
    print()

    # Load fix plan
    print("[1/5] Loading fix plan...")
    fix_data = load_json(FIX_FILE)
    fix_map = {entry['id']: entry for entry in fix_data}
    print(f"  -> {len(fix_data)} videos in fix plan")

    # Load OAuth config
    print("[2/5] Refreshing OAuth token...")
    oauth_config = load_json(OAUTH_FILE)
    access_token = refresh_access_token(oauth_config)
    print("  -> Token refreshed successfully")

    # Load progress (resume if already started today)
    progress = load_progress()
    already_done = set(progress['completed_ids'] + progress['error_ids'])
    print(f"  -> Already processed today: {len(already_done)} videos")

    # Determine which videos to process
    # Priority: fix plan videos first, then remaining channel videos (for universal fixes)
    all_fix_ids = [entry['id'] for entry in fix_data if entry['id'] not in already_done]
    print(f"  -> Remaining to process: {len(all_fix_ids)} videos from fix plan")

    if not all_fix_ids:
        print("\n  ALL VIDEOS ALREADY PROCESSED TODAY. Nothing to do.")
        progress['status'] = 'completed'
        save_json(PROGRESS_FILE, progress)
        return

    # Process in batches of 50 (for fetching)
    print(f"\n[3/5] Processing videos (max {MAX_UPDATES_PER_RUN} per run)...")
    print(f"  Quota budget: {QUOTA_LIMIT} units | Stop threshold: {QUOTA_STOP_THRESHOLD}")
    print()

    updates_done = 0
    quota_used = progress['quota_used']

    # Process fix plan videos in batches of 50
    batch_size = 50
    for batch_start in range(0, len(all_fix_ids), batch_size):
        if updates_done >= MAX_UPDATES_PER_RUN:
            print(f"\n  STOP: Reached max updates per run ({MAX_UPDATES_PER_RUN})")
            break
        if quota_used >= QUOTA_STOP_THRESHOLD:
            print(f"\n  STOP: Quota threshold reached ({quota_used}/{QUOTA_LIMIT})")
            break

        batch_ids = all_fix_ids[batch_start:batch_start + batch_size]
        remaining_updates = MAX_UPDATES_PER_RUN - updates_done

        # Don't fetch more than we can update
        if len(batch_ids) > remaining_updates:
            batch_ids = batch_ids[:remaining_updates]

        # Fetch current state for this batch
        print(f"  Fetching batch {batch_start // batch_size + 1} ({len(batch_ids)} videos)...")
        try:
            response = fetch_videos_batch(batch_ids, access_token)
            quota_used += QUOTA_PER_LIST
        except Exception as e:
            print(f"  ERROR fetching batch: {e}")
            # Try to refresh token in case it expired
            try:
                access_token = refresh_access_token(oauth_config)
                response = fetch_videos_batch(batch_ids, access_token)
                quota_used += QUOTA_PER_LIST
            except Exception as e2:
                print(f"  FATAL: Cannot fetch batch even after token refresh: {e2}")
                break

        fetched_videos = {item['id']: item['snippet'] for item in response.get('items', [])}

        # Update each video in this batch
        for video_id in batch_ids:
            if updates_done >= MAX_UPDATES_PER_RUN or quota_used >= QUOTA_STOP_THRESHOLD:
                break

            if video_id not in fetched_videos:
                print(f"    SKIP {video_id}: not found in API response (deleted/private?)")
                progress['skipped_count'] += 1
                progress['error_ids'].append(video_id)
                progress['errors'].append({'id': video_id, 'error': 'not found in API response'})
                continue

            current_snippet = fetched_videos[video_id]
            fix_entry = fix_map.get(video_id)

            # Build update body
            update_body = build_update_body(video_id, current_snippet, fix_entry)

            # Check if anything actually changed
            title_changed = update_body['snippet']['title'] != current_snippet.get('title', '')
            tags_changed = update_body['snippet']['tags'] != current_snippet.get('tags', [])
            desc_changed = update_body['snippet']['description'] != current_snippet.get('description', '')
            lang_changed = (update_body['snippet']['defaultLanguage'] != current_snippet.get('defaultLanguage', '') or
                           update_body['snippet']['defaultAudioLanguage'] != current_snippet.get('defaultAudioLanguage', ''))

            if not (title_changed or tags_changed or desc_changed or lang_changed):
                print(f"    SKIP {video_id}: no changes needed")
                progress['skipped_count'] += 1
                progress['completed_ids'].append(video_id)
                continue

            # Execute the update
            update_url = f"{VIDEOS_URL}?part=snippet"
            try:
                result = api_put(update_url, access_token, update_body)
                quota_used += QUOTA_PER_UPDATE
                updates_done += 1
                progress['success_count'] += 1
                progress['completed_ids'].append(video_id)

                changes = []
                if title_changed:
                    changes.append('title')
                if tags_changed:
                    changes.append('tags')
                if desc_changed:
                    changes.append('desc')
                if lang_changed:
                    changes.append('lang')

                print(f"    OK   {video_id} [{','.join(changes)}] - \"{update_body['snippet']['title'][:50]}...\"")

                # Small delay to be respectful to API
                time.sleep(0.3)

            except Exception as e:
                error_msg = str(e)
                print(f"    ERR  {video_id}: {error_msg[:100]}")
                progress['error_count'] += 1
                progress['error_ids'].append(video_id)
                progress['errors'].append({'id': video_id, 'error': error_msg[:500]})

                # If we get a 401, refresh token
                if '401' in error_msg:
                    print("    -> Refreshing token...")
                    try:
                        access_token = refresh_access_token(oauth_config)
                    except:
                        print("    -> Token refresh failed. Stopping.")
                        break

                # If we get a 403 (quota exceeded), stop
                if '403' in error_msg and 'quota' in error_msg.lower():
                    print("    -> QUOTA EXCEEDED. Stopping.")
                    break

                time.sleep(1)  # longer delay after error

    # Save progress
    progress['quota_used'] = quota_used
    progress['finished_at'] = datetime.now(timezone.utc).isoformat()
    if len(progress['completed_ids']) + len(progress['error_ids']) >= len(all_fix_ids) + len(already_done):
        progress['status'] = 'completed'
    else:
        progress['status'] = 'partial'

    save_json(PROGRESS_FILE, progress)

    # Print summary
    print()
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Videos updated:    {progress['success_count']}")
    print(f"  Videos skipped:    {progress['skipped_count']}")
    print(f"  Errors:            {progress['error_count']}")
    print(f"  Quota used:        {quota_used} / {QUOTA_LIMIT}")
    print(f"  Quota remaining:   {QUOTA_LIMIT - quota_used}")
    print(f"  Status:            {progress['status']}")
    print(f"  Progress saved:    {PROGRESS_FILE}")
    print()

    remaining = len(all_fix_ids) - updates_done - progress['skipped_count'] - progress['error_count']
    if remaining > 0:
        days_needed = (remaining // MAX_UPDATES_PER_RUN) + 1
        print(f"  REMAINING: {remaining} videos still need updating.")
        print(f"  Run this script again tomorrow (~{days_needed} more day(s) needed).")
    else:
        print("  ALL FIX PLAN VIDEOS PROCESSED!")
    print("=" * 60)


if __name__ == '__main__':
    main()
