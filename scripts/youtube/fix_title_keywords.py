#!/usr/bin/env python3
"""
fix_title_keywords.py — P1: Add "Classic", "Full Movie", "Full Episode", "Ganzer Film" to titles

Keyword impact (proven channel data):
  "Classic" = +724% avg view lift
  "Full Movie" = Top YouTube search term (0 videos have it!)
  "Full Episode" = Standard query for TV content (0 videos have it!)

29 videos × 51 Units = ~1,479 quota
Run AFTER P0 scripts (fix_remastered_tags.py + fix_desc_line1.py)

Usage:
    python fix_title_keywords.py --dry-run   # Fetch current titles, show changes
    python fix_title_keywords.py --apply     # Apply title changes
    python fix_title_keywords.py --verify    # Verify char counts only (offline)
"""

import os
import sys
import json
import time

# ═══════════════════════════════════════════════════════════════════════
# TITLE UPDATES — video_id → target title (all verified ≤70 chars)
# ═══════════════════════════════════════════════════════════════════════

TITLE_UPDATES = {
    # ── GROUP A: Classic + Full Movie (both keywords new) ─────────────
    "8lLtNb11NKU": "Metropolis (1927) Full Movie | Sci-Fi Classic | 8K HQ (4K UHD)",          # 62
    "PSdJJaxI4gM": "Charade (1953) Full Movie | Classic Mystery | 8K HQ (4K UHD)",            # 60
    "JhJmasQ8N-8": "Great Expectations (1946) Full Movie | Classic | 8K HQ (4K UHD)",         # 63
    "exukLdxugy8": "Häxan (1922) Full Movie | Occult Classic | 8K HQ (4K UHD)",               # 58
    "_aUNgDJoWoU": "Scarlet Street (1945) Full Movie | Classic Noir | 8K HQ (4K UHD)",        # 66

    # ── GROUP B: Classic only (short/medium length, no Full Movie) ────
    "5WVJHELSD7A": "The Cabinet of Dr. Caligari (1920) | Horror Classic | 8K HQ (4K UHD)",    # 68
    "hPQN992PMUY": "Frankenstein (1910) | Horror Classic | 8K HQ (4K UHD)",                   # 54
    "z8FqTSpp6Kg": "Dinner for One (1963) | Classic Comedy | 8K HQ (4K UHD)",                 # 55
    "b4cqLlJ7t4M": "Phantom of the Opera (1925) | Horror Classic | 8K HQ (4K UHD)",          # 63

    # ── GROUP C: Full Movie added (already have Classic) ──────────────
    "Nzi6aRKDoEs": "Nosferatu (1922) Full Movie | Silent Horror Classic | 8K HQ (4K UHD)",    # 68
    "d8Ak1R_eOlY": "White Zombie (1932) Full Movie | Horror Classic | 8K HQ (4K UHD)",       # 64

    # ── GROUP D: Full Movie only ──────────────────────────────────────
    "LEM6FkBTDNs": "20,000 Leagues Under the Sea (1916) Full Movie | 8K HQ (4K UHD)",        # 63
    "dpF2uQVgCsM": "The Fast and the Furious (1954) Full Movie | 8K HQ (4K UHD)",            # 59
    "pqrCPhUCpxE": "Voyage to Prehistoric Women (1968) Full Movie | 8K HQ (4K UHD)",         # 62
    "9dQKLUfKfgU": "Planet Outlaws (1953) Full Movie | Sci-Fi | 8K HQ (4K UHD)",             # 59
    "YbC2JynVCRA": "A Bill of Divorcement (1932) Full Movie | 8K HQ (4K UHD)",               # 57
    "Fjb-aAUetX0": "Teaserama (1955) Full Movie | Burlesque | 8K HQ (4K UHD)",               # 57
    "cCNm8nNHing": "Tarzan's Revenge (1938) Full Movie | 8K HQ (4K UHD)",                    # 52
    "FG-vqRH5Cg4": "Charlie Chaplin Film Festival (1920) Full Movie | 8K HQ (4K UHD)",       # 64

    # ── GROUP E: Full Episode (series) ────────────────────────────────
    "gx6eICiEYLo": "Alfred J. Kwak (1): Hurra, er ist da! | Full Episode | 8K HQ (4K UHD)",  # 69
    "UAUBOJoTjgc": "Alfred J. Kwak E50: Das Casino | Full Episode | 8K HQ (4K UHD)",         # 63
    "m4M6Hr_mxSk": "Alfred J. Kwak E15: Die Explosion | Full Episode | 8K HQ (4K UHD)",     # 66
    "10UZiHJh060": "Alfred J. Kwak E32: Atlantis | Full Episode | 8K HQ (4K UHD)",           # 61
    "2Jxj04DqPq0": "Alfred J. Kwak E35: Michael Duckson | Full Episode | 8K HQ (4K UHD)",   # 68
    "lNcvMYyLPVU": "Astro Boy (1): Astro Boys Geburt | Full Episode | 8K HQ (4K UHD)",      # 66
    "Ukabxz6LK0c": "Astro Boy (2): Astro gegen Atlas | Full Episode | 8K HQ (4K UHD)",      # 66
    "xzZ9yB5lJ9s": "Ferdy: Rettung Bambini | Full Episode Deutsch | 8K HQ (4K UHD)",        # 62

    # ── GROUP F: Ganzer Film (German language) ────────────────────────
    "5Bj9cvKO3P8": "Asterix der Gallier (1967) Ganzer Film | 8K HQ (4K UHD)",                # 55
    "jPzc1XtrMds": "Asterix: Sieg über Cäsar (1985) Ganzer Film | 8K HQ (4K UHD)",           # 60
}

# Group metadata for reporting
GROUPS = {
    "A": {"name": "Classic + Full Movie", "ids": ["8lLtNb11NKU", "PSdJJaxI4gM", "JhJmasQ8N-8", "exukLdxugy8", "_aUNgDJoWoU"]},
    "B": {"name": "Classic only", "ids": ["5WVJHELSD7A", "hPQN992PMUY", "z8FqTSpp6Kg", "b4cqLlJ7t4M"]},
    "C": {"name": "Full Movie (has Classic)", "ids": ["Nzi6aRKDoEs", "d8Ak1R_eOlY"]},
    "D": {"name": "Full Movie only", "ids": ["LEM6FkBTDNs", "dpF2uQVgCsM", "pqrCPhUCpxE", "9dQKLUfKfgU", "YbC2JynVCRA", "Fjb-aAUetX0", "cCNm8nNHing", "FG-vqRH5Cg4"]},
    "E": {"name": "Full Episode", "ids": ["gx6eICiEYLo", "UAUBOJoTjgc", "m4M6Hr_mxSk", "10UZiHJh060", "2Jxj04DqPq0", "lNcvMYyLPVU", "Ukabxz6LK0c", "xzZ9yB5lJ9s"]},
    "F": {"name": "Ganzer Film (DE)", "ids": ["5Bj9cvKO3P8", "jPzc1XtrMds"]},
}

MAX_TITLE_LEN = 70


def verify_titles():
    """Offline check: verify all target titles are ≤70 chars."""
    print("=" * 70)
    print("TITLE LENGTH VERIFICATION")
    print("=" * 70)
    errors = 0
    for group_key, group in GROUPS.items():
        print(f"\n── Group {group_key}: {group['name']} ──")
        for vid in group["ids"]:
            title = TITLE_UPDATES[vid]
            length = len(title)
            status = "✅" if length <= MAX_TITLE_LEN else "❌ TOO LONG!"
            if length > MAX_TITLE_LEN:
                errors += 1
            print(f"  {vid}  [{length:2d}] {status}  {title}")

    print(f"\n{'=' * 70}")
    print(f"Total: {len(TITLE_UPDATES)} videos")
    if errors:
        print(f"❌ {errors} titles exceed {MAX_TITLE_LEN} chars!")
    else:
        print(f"✅ All titles ≤ {MAX_TITLE_LEN} chars")
    
    # Keyword summary
    classic_count = sum(1 for t in TITLE_UPDATES.values() if "Classic" in t or "classic" in t.lower())
    full_movie = sum(1 for t in TITLE_UPDATES.values() if "Full Movie" in t)
    full_ep = sum(1 for t in TITLE_UPDATES.values() if "Full Episode" in t)
    ganzer = sum(1 for t in TITLE_UPDATES.values() if "Ganzer Film" in t)
    print(f"\nKeywords: Classic={classic_count}, Full Movie={full_movie}, Full Episode={full_ep}, Ganzer Film={ganzer}")
    print(f"Estimated quota: {len(TITLE_UPDATES)} × 51 = {len(TITLE_UPDATES) * 51} units")
    return errors == 0


def get_youtube_service():
    """Build YouTube API service with OAuth credentials."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    token_path = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
    token_path = os.path.normpath(token_path)

    if not os.path.exists(token_path):
        print(f"❌ token.json not found at {token_path}")
        sys.exit(1)

    creds = Credentials.from_authorized_user_file(token_path)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())
        print("🔄 Token refreshed")

    return build("youtube", "v3", credentials=creds)


def fetch_videos(youtube, video_ids):
    """Fetch video snippets in batches of 50. Uses part='snippet' ONLY."""
    videos = {}
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        ids_str = ",".join(batch)
        # ⚠️ CRITICAL: part="snippet" ONLY — NEVER add "status"!
        response = youtube.videos().list(
            part="snippet",
            id=ids_str
        ).execute()

        for item in response.get("items", []):
            videos[item["id"]] = item
        
        api_calls = i // 50 + 1
        print(f"  📡 Batch {api_calls}: fetched {len(response.get('items', []))} videos (1 quota unit)")
        time.sleep(0.5)

    return videos


def dry_run(youtube):
    """Fetch current titles and show what would change."""
    print("=" * 70)
    print("DRY RUN — Title Keyword Additions")
    print("=" * 70)

    video_ids = list(TITLE_UPDATES.keys())
    print(f"\n📡 Fetching {len(video_ids)} videos from YouTube API...")
    videos = fetch_videos(youtube, video_ids)

    changes = []
    skipped = []
    missing = []

    for group_key, group in GROUPS.items():
        print(f"\n── Group {group_key}: {group['name']} ──")
        for vid in group["ids"]:
            target = TITLE_UPDATES[vid]
            if vid not in videos:
                print(f"  ❓ {vid} — NOT FOUND (deleted/private?)")
                missing.append(vid)
                continue

            current = videos[vid]["snippet"]["title"]
            if current == target:
                print(f"  ⏭️  {vid} — Already correct")
                skipped.append(vid)
            else:
                print(f"  🔄 {vid}")
                print(f"      NOW:  [{len(current):2d}] {current}")
                print(f"      NEW:  [{len(target):2d}] {target}")
                changes.append(vid)

    print(f"\n{'=' * 70}")
    print(f"SUMMARY")
    print(f"  To update:  {len(changes)} videos")
    print(f"  Skipped:    {len(skipped)} (already correct)")
    print(f"  Missing:    {len(missing)} (not found)")
    print(f"  Quota:      {len(changes)} × 51 = ~{len(changes) * 51} units")
    print(f"\nRun with --apply to execute these changes.")
    return changes


def apply_changes(youtube):
    """Apply title changes to YouTube."""
    print("=" * 70)
    print("APPLYING Title Keyword Changes")
    print("=" * 70)

    video_ids = list(TITLE_UPDATES.keys())
    print(f"\n📡 Fetching {len(video_ids)} videos...")
    videos = fetch_videos(youtube, video_ids)

    updated = 0
    skipped = 0
    errors = 0
    quota_used = len(videos)  # list calls

    for group_key, group in GROUPS.items():
        print(f"\n── Group {group_key}: {group['name']} ──")
        for vid in group["ids"]:
            target = TITLE_UPDATES[vid]
            if vid not in videos:
                print(f"  ❓ {vid} — NOT FOUND, skipping")
                continue

            snippet = videos[vid]["snippet"]
            current = snippet["title"]

            if current == target:
                print(f"  ⏭️  {vid} — Already correct: {current[:50]}...")
                skipped += 1
                continue

            # Build update body — preserve ALL snippet fields
            snippet["title"] = target

            try:
                # ⚠️ CRITICAL: part="snippet" ONLY!
                youtube.videos().update(
                    part="snippet",
                    body={
                        "id": vid,
                        "snippet": {
                            "title": target,
                            "description": snippet["description"],
                            "tags": snippet.get("tags", []),
                            "categoryId": snippet["categoryId"],
                        }
                    }
                ).execute()
                
                quota_used += 50
                updated += 1
                print(f"  ✅ {vid} [{len(target)}] {target}")
                time.sleep(1)  # Rate limit

            except Exception as e:
                error_msg = str(e)
                errors += 1
                print(f"  ❌ {vid} — ERROR: {error_msg[:100]}")
                if "quotaExceeded" in error_msg or "403" in error_msg:
                    print("\n🛑 QUOTA EXHAUSTED! Stopping immediately.")
                    break
        else:
            continue
        break  # Break outer loop if inner broke

    print(f"\n{'=' * 70}")
    print(f"RESULTS")
    print(f"  ✅ Updated:  {updated}")
    print(f"  ⏭️  Skipped:  {skipped}")
    print(f"  ❌ Errors:   {errors}")
    print(f"  💰 Quota:    ~{quota_used} units")

    # Save report
    report = {
        "date": time.strftime("%Y-%m-%d %H:%M"),
        "script": "fix_title_keywords.py",
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "quota_used": quota_used,
    }
    report_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "title_keywords_report.json")
    report_path = os.path.normpath(report_path)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Report saved: {report_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fix_title_keywords.py --verify    # Offline char count check")
        print("  python fix_title_keywords.py --dry-run   # Fetch + compare (API read)")
        print("  python fix_title_keywords.py --apply     # Apply changes (API write)")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "--verify":
        verify_titles()
    elif mode == "--dry-run":
        youtube = get_youtube_service()
        dry_run(youtube)
    elif mode == "--apply":
        youtube = get_youtube_service()
        apply_changes(youtube)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
