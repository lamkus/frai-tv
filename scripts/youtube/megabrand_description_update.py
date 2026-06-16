"""
MEGA-BRAND Description Updater — frai.tv + remaike.IT + @remAIke_IT
====================================================================

Adds mega-brand cross-promotion to ALL YouTube video descriptions:
  - frai.tv/watch/<ID> deep link (per-video!)
  - www.remaike.IT website link
  - @remAIke_IT YouTube channel link
  - CTA block (Like/Comment/Subscribe)

Wochenschau videos get PREMIUM positioning:
  - "Full WWII Newsreel Archive" link to frai.tv
  - Multilingual search terms block
  - Historical context framing

QUOTA:
  Phase 1 (AUDIT): ~8 Public API calls = 8 units (FREE read)
  Phase 2 (UPDATE): N × 50 units per video that needs changes

Usage:
    python megabrand_description_update.py --audit          # Phase 1: Scan + Report
    python megabrand_description_update.py --dry-run        # Phase 2: Preview changes
    python megabrand_description_update.py --apply          # Phase 2: Apply changes
    python megabrand_description_update.py --apply --limit 10  # Apply first 10 only
"""

import os
import sys
import json
import re
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ──
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PLAYLIST = "UUVFv6Egpl0LDvigpFbQXNeQ"

FRAI_TV_BASE = "https://frai.tv/watch"
REMAIKE_URL = "www.remaike.IT"
YT_CHANNEL_URL = "https://www.youtube.com/@remAIke_IT"

# ── Category Detection (from title patterns) ──
CATEGORY_PATTERNS = {
    "wochenschau": [r"wochenschau", r"newsreel", r"WS \d{3}"],
    "betty_boop": [r"betty boop"],
    "alfred_kwak": [r"alfred.*kwak", r"alfred.*quack"],
    "superman": [r"superman.*fleischer", r"fleischer.*superman"],
    "felix": [r"felix.*cat", r"felix the cat"],
    "soundie": [r"soundie"],
    "looney_tunes": [r"looney tunes", r"merrie melodies", r"bugs bunny", r"daffy duck"],
    "popeye": [r"popeye"],
    "casper": [r"casper"],
    "maulwurf": [r"maulwurf", r"krtek", r"little mole"],
    "ken_block": [r"ken block", r"gymkhana"],
    "bravestarr": [r"bravestarr"],
    "christmas": [r"christmas", r"xmas", r"holiday special"],
    "der_7_sinn": [r"7\. sinn", r"7th sense", r"der 7"],
}

# ── Mega-Brand Block Templates ──

MEGA_BRAND_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 Watch in our curated collection: {frai_link}
🌐 {remaike_url}
📺 {yt_channel_url}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

CTA_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

WOCHENSCHAU_EXTRA = """📖 Full WWII Newsreel Archive: https://frai.tv/#wochenschau
🌍 Deutsche Wochenschau — Historical Document for educational purposes."""

SEPARATOR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"


def detect_category(title: str) -> str:
    """Detect video category from title."""
    title_lower = title.lower()
    for cat, patterns in CATEGORY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, title_lower):
                return cat
    return "other"


def has_frai_link(desc: str) -> bool:
    return "frai.tv" in desc.lower()


def has_remaike_link(desc: str) -> bool:
    return "remaike.it" in desc.lower()


def has_yt_channel_link(desc: str) -> bool:
    return "@remaike_it" in desc.lower() or "youtube.com/@remAIke_IT" in desc


def has_cta_block(desc: str) -> bool:
    """Check if CTA block (LIKE/SUBSCRIBE) exists."""
    lower = desc.lower()
    return ("like" in lower and "subscribe" in lower) or "🔔" in desc


def has_mega_brand_block(desc: str) -> bool:
    """Check if the full mega-brand block is already present."""
    return has_frai_link(desc) and has_remaike_link(desc) and has_yt_channel_link(desc)


# ── PUBLIC API: Read all video IDs from uploads playlist ──

def _get_api_client():
    """Get API client — tries Public API key first, falls back to OAuth."""
    if API_KEY:
        return None  # Use requests + API_KEY
    # Use OAuth service
    return get_youtube_service()


def fetch_all_upload_ids() -> list[str]:
    """Fetch all video IDs from the upload playlist."""
    ids = []
    page_token = None
    youtube = _get_api_client()

    while True:
        if youtube:
            # OAuth path
            kwargs = {
                "part": "contentDetails",
                "playlistId": UPLOAD_PLAYLIST,
                "maxResults": 50,
            }
            if page_token:
                kwargs["pageToken"] = page_token
            resp = youtube.playlistItems().list(**kwargs).execute()
            data = resp
        else:
            # Public API path
            params = {
                "part": "contentDetails",
                "playlistId": UPLOAD_PLAYLIST,
                "maxResults": 50,
                "key": API_KEY,
            }
            if page_token:
                params["pageToken"] = page_token
            resp = requests.get(
                "https://youtube.googleapis.com/youtube/v3/playlistItems",
                params=params,
            )
            data = resp.json()

        if "error" in data:
            print(f"  [API ERROR] {data['error']['message']}")
            break
        for item in data.get("items", []):
            vid_id = item["contentDetails"]["videoId"]
            ids.append(vid_id)
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    return ids


def fetch_video_details(video_ids: list[str]) -> list[dict]:
    """Fetch video details in batches of 50 (1 unit per call)."""
    results = []
    youtube = _get_api_client()

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        if youtube:
            # OAuth path
            resp = youtube.videos().list(
                part="snippet,status",
                id=",".join(batch),
            ).execute()
            data = resp
        else:
            # Public API path
            resp = requests.get(
                "https://youtube.googleapis.com/youtube/v3/videos",
                params={
                    "part": "snippet,status",
                    "id": ",".join(batch),
                    "key": API_KEY,
                },
            )
            data = resp.json()

        if "error" in data:
            print(f"  [API ERROR] {data['error']['message']}")
            break
        results.extend(data.get("items", []))
    return results


# ── AUDIT ──

def run_audit():
    """Phase 1: Audit all video descriptions for mega-brand links."""
    print("=" * 60)
    print("MEGA-BRAND AUDIT — Phase 1 (Public API)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # Step 1: Get all upload IDs
    print("\n🔍 Fetching all upload IDs...")
    all_ids = fetch_all_upload_ids()
    print(f"   Found {len(all_ids)} videos in upload playlist")

    # Step 2: Fetch details
    print("\n🔍 Fetching video details (Public API)...")
    videos = fetch_video_details(all_ids)
    print(f"   Retrieved {len(videos)} video details")

    # Step 3: Analyze
    audit = {
        "total": len(videos),
        "has_frai": 0,
        "has_remaike": 0,
        "has_yt_link": 0,
        "has_cta": 0,
        "has_full_megabrand": 0,
        "missing_frai": [],
        "missing_remaike": [],
        "missing_cta": [],
        "missing_any": [],
        "by_category": {},
        "public_count": 0,
        "private_count": 0,
    }

    for vid in videos:
        vid_id = vid["id"]
        snippet = vid["snippet"]
        title = snippet["title"]
        desc = snippet.get("description", "")
        status = vid.get("status", {}).get("privacyStatus", "unknown")
        cat = detect_category(title)

        is_public = status == "public"
        if is_public:
            audit["public_count"] += 1
        else:
            audit["private_count"] += 1

        # Category stats
        if cat not in audit["by_category"]:
            audit["by_category"][cat] = {
                "total": 0, "has_frai": 0, "has_remaike": 0,
                "has_cta": 0, "has_full": 0, "missing": []
            }
        audit["by_category"][cat]["total"] += 1

        f = has_frai_link(desc)
        r = has_remaike_link(desc)
        y = has_yt_channel_link(desc)
        c = has_cta_block(desc)
        full = f and r and y

        if f:
            audit["has_frai"] += 1
            audit["by_category"][cat]["has_frai"] += 1
        if r:
            audit["has_remaike"] += 1
            audit["by_category"][cat]["has_remaike"] += 1
        if c:
            audit["has_cta"] += 1
            audit["by_category"][cat]["has_cta"] += 1
        if full:
            audit["has_full_megabrand"] += 1
            audit["by_category"][cat]["has_full"] += 1

        entry = {
            "id": vid_id,
            "title": title,
            "category": cat,
            "status": status,
            "has_frai": f,
            "has_remaike": r,
            "has_yt_link": y,
            "has_cta": c,
            "desc_length": len(desc),
        }

        if not f:
            audit["missing_frai"].append(entry)
        if not r:
            audit["missing_remaike"].append(entry)
        if not c:
            audit["missing_cta"].append(entry)
        if not full:
            audit["missing_any"].append(entry)
            audit["by_category"][cat]["missing"].append(vid_id)

    # Print report
    print(f"\n{'='*60}")
    print(f"MEGA-BRAND AUDIT REPORT")
    print(f"{'='*60}")
    print(f"Total Videos:       {audit['total']}")
    print(f"Public:             {audit['public_count']}")
    print(f"Private:            {audit['private_count']}")
    print(f"")
    print(f"Has frai.tv:        {audit['has_frai']}/{audit['total']} ({100*audit['has_frai']//max(1,audit['total'])}%)")
    print(f"Has remaike.IT:     {audit['has_remaike']}/{audit['total']} ({100*audit['has_remaike']//max(1,audit['total'])}%)")
    print(f"Has @remAIke_IT:    {audit['has_yt_link']}/{audit['total']}")
    print(f"Has CTA block:      {audit['has_cta']}/{audit['total']}")
    print(f"FULL mega-brand:    {audit['has_full_megabrand']}/{audit['total']}")
    print(f"")
    print(f"MISSING frai.tv:    {len(audit['missing_frai'])} videos")
    print(f"MISSING remaike.IT: {len(audit['missing_remaike'])} videos")
    print(f"MISSING CTA:        {len(audit['missing_cta'])} videos")
    print(f"MISSING ANY link:   {len(audit['missing_any'])} videos")

    print(f"\n── By Category ──")
    for cat, stats in sorted(audit["by_category"].items(), key=lambda x: -x[1]["total"]):
        total = stats["total"]
        missing = total - stats["has_full"]
        print(f"  {cat:20s}: {total:3d} total | {stats['has_frai']:3d} frai | "
              f"{stats['has_remaike']:3d} remaike | {missing:3d} need fix")

    # Save audit report
    report_path = Path(__file__).resolve().parent.parent.parent / "config" / \
        f"megabrand_audit_{datetime.now().strftime('%Y_%m_%d')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Report saved: {report_path}")

    # Quota summary
    quota = len(all_ids) // 50 + 1 + len(videos) // 50 + 1
    print(f"\n📊 Quota used (read-only): ~{quota} units")
    print(f"📊 Quota needed for update: {len(audit['missing_any'])} × 50 = {len(audit['missing_any'])*50} units")

    return audit


# ── UPDATE ──

def get_youtube_service():
    """Get authenticated YouTube service for write operations."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build as api_build

    token_path = Path(__file__).resolve().parent.parent.parent / "token.json"
    with open(token_path, "r") as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", ["https://www.googleapis.com/auth/youtube.force-ssl"]),
    )
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        token_data["token"] = creds.token
        token_data["expiry"] = creds.expiry.isoformat() if creds.expiry else None
        with open(token_path, "w") as f:
            json.dump(token_data, f, indent=2)

    return api_build("youtube", "v3", credentials=creds)


def build_mega_brand_block(video_id: str, category: str) -> str:
    """Build the mega-brand footer block for a video description."""
    frai_link = f"{FRAI_TV_BASE}/{video_id}"

    parts = []

    # CTA block
    parts.append(SEPARATOR)
    parts.append("👆 LIKE if you enjoyed this!")
    parts.append("💬 COMMENT your thoughts!")
    parts.append("🔔 SUBSCRIBE for more restored classics!")
    parts.append(SEPARATOR)

    # Wochenschau premium block
    if category == "wochenschau":
        parts.append("📖 Full WWII Newsreel Archive: https://frai.tv/#wochenschau")
        parts.append("🌍 Deutsche Wochenschau — Historical educational document.")
        parts.append("")

    # Mega-brand links
    parts.append(f"📺 Watch in our curated collection: {frai_link}")
    parts.append(f"🌐 {REMAIKE_URL}")
    parts.append(f"📺 {YT_CHANNEL_URL}")

    return "\n".join(parts)


def clean_existing_brand_blocks(desc: str) -> str:
    """Remove existing brand/CTA blocks to avoid duplication.
    
    Strategy: Remove SPECIFIC known blocks, not everything between separators.
    Preserves: multilingual search terms, source credits, hashtags, etc.
    """
    lines = desc.split("\n")
    cleaned = []
    i = 0
    
    while i < len(lines):
        stripped = lines[i].strip()
        
        # Detect CTA block: separator → LIKE → COMMENT → SUBSCRIBE → separator
        if stripped == SEPARATOR:
            # Look ahead: is this a CTA block?
            block_lines = [i]
            j = i + 1
            is_cta_block = False
            is_link_block = False
            
            while j < len(lines) and j < i + 8:  # Look up to 8 lines ahead
                s = lines[j].strip()
                if s == SEPARATOR:
                    block_lines.append(j)
                    # Check what was between the separators
                    between = [lines[k].strip() for k in range(i+1, j)]
                    between_text = " ".join(between).lower()
                    
                    if "like" in between_text and ("subscribe" in between_text or "comment" in between_text):
                        is_cta_block = True
                    if "remaike.it" in between_text or "frai.tv" in between_text or "@remaike_it" in between_text.lower():
                        is_link_block = True
                    break
                j += 1
            
            if is_cta_block or is_link_block:
                # Skip the entire block (sep → content → sep)
                i = block_lines[-1] + 1
                continue
            else:
                # Not a brand block — just an empty separator pair, keep it
                # But check if it's a lone separator followed by links
                next_lines = []
                for k in range(i+1, min(i+5, len(lines))):
                    next_lines.append(lines[k].strip())
                next_text = " ".join(next_lines).lower()
                
                if ("remaike.it" in next_text or "frai.tv" in next_text) and \
                   not any(c in next_text for c in ["wochenschau", "newsreel", "🎬"]):
                    # This separator starts a trailing link section
                    i += 1
                    continue
                
                cleaned.append(lines[i])
                i += 1
                continue
        
        # Remove standalone old brand lines (not between separators)
        if stripped in [
            f"🌐 {REMAIKE_URL}",
            "🌐 www.remaike.IT",
            f"📺 {YT_CHANNEL_URL}",
            "📺 https://www.youtube.com/@remAIke_IT",
        ]:
            i += 1
            continue
        
        # Remove old CTA lines (standalone, not in separator block)
        if stripped in [
            "👆 LIKE if you found this valuable!",
            "👆 LIKE if you enjoyed this!",
            "💬 COMMENT your thoughts!",
            "🔔 SUBSCRIBE for more vintage content!",
            "🔔 SUBSCRIBE for more vintage content in 8K!",
            "🔔 SUBSCRIBE for more restored classics!",
        ]:
            i += 1
            continue
        
        # Remove old frai.tv promo lines
        if re.match(r"^📺 Watch.*frai\.tv", stripped):
            i += 1
            continue
        if re.match(r"^📖 Full WWII.*frai\.tv", stripped):
            i += 1
            continue
        if stripped == "🌍 Deutsche Wochenschau — Historical educational document.":
            i += 1
            continue
        
        cleaned.append(lines[i])
        i += 1

    # Remove trailing empty lines
    while cleaned and cleaned[-1].strip() == "":
        cleaned.pop()

    return "\n".join(cleaned)


def update_description(current_desc: str, video_id: str, category: str) -> str:
    """Build the new description with mega-brand block appended."""
    # First, clean any existing partial brand blocks
    cleaned = clean_existing_brand_blocks(current_desc)

    # Build new mega-brand footer
    brand_block = build_mega_brand_block(video_id, category)

    # Combine
    if not cleaned.endswith("\n"):
        cleaned += "\n"

    return cleaned + "\n" + brand_block


def run_update(dry_run: bool, limit: int = 0):
    """Phase 2: Update video descriptions with mega-brand block."""
    mode = "DRY RUN" if dry_run else "APPLYING"
    print("=" * 60)
    print(f"MEGA-BRAND UPDATE — Phase 2 ({mode})")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    if limit:
        print(f"Limit: {limit} videos")
    print("=" * 60)

    # Load audit report if available
    audit_path = Path(__file__).resolve().parent.parent.parent / "config" / \
        f"megabrand_audit_{datetime.now().strftime('%Y_%m_%d')}.json"
    
    if audit_path.exists():
        with open(audit_path, "r", encoding="utf-8") as f:
            audit = json.load(f)
        missing = audit.get("missing_any", [])
        print(f"\n📄 Loaded audit: {len(missing)} videos need mega-brand")
    else:
        print("\n⚠️  No audit report found. Running audit first...")
        audit = run_audit()
        missing = audit.get("missing_any", [])

    if not missing:
        print("\n✅ All videos already have mega-brand! Nothing to do.")
        return

    # Priority sort: Wochenschau first, then high-value categories
    PRIORITY_ORDER = {
        "wochenschau": 0,   # History = highest value
        "felix": 1,         # 3,252 avg views
        "ken_block": 2,     # 2,213 avg views
        "superman": 3,      # 1,890 avg views (in "other")
        "christmas": 4,     # 941 avg views
        "popeye": 5,        # 887 avg views
        "looney_tunes": 6,  # 461 avg views
        "other": 7,         # Mixed — includes Superman, high-view films
        "betty_boop": 8,    # 149 avg views
        "alfred_kwak": 9,   # 71 avg views
        "soundie": 10,      # 7 avg views
        "casper": 11,
        "maulwurf": 12,
        "der_7_sinn": 13,
        "bravestarr": 14,
    }
    missing.sort(key=lambda v: PRIORITY_ORDER.get(v.get("category", "other"), 99))
    missing_ids = [v["id"] for v in missing]

    # Show priority breakdown
    from collections import Counter
    cat_counts = Counter(v.get("category", "other") for v in missing)
    print("\n── Priority Queue ──")
    for cat, _ in sorted(cat_counts.items(), key=lambda x: PRIORITY_ORDER.get(x[0], 99)):
        count = cat_counts[cat]
        prio = PRIORITY_ORDER.get(cat, 99)
        print(f"  P{prio}: {cat:20s} → {count} videos")

    if limit:
        missing_ids = missing_ids[:limit]
        print(f"\n   Processing first {limit} videos (priority-sorted)")

    # Get YouTube service for writes
    youtube = get_youtube_service()

    results = []
    quota_used = 0
    errors = 0
    updated = 0

    # Process in batches of 50 for reading
    for batch_start in range(0, len(missing_ids), 50):
        batch_ids = missing_ids[batch_start:batch_start + 50]

        # Read current state via OAuth (need snippet for update)
        try:
            resp = youtube.videos().list(
                part="snippet",
                id=",".join(batch_ids),
            ).execute()
        except Exception as e:
            print(f"\n[API ERROR] Reading batch {batch_start}: {e}")
            break

        for item in resp.get("items", []):
            vid_id = item["id"]
            snippet = item["snippet"]
            title = snippet["title"]
            current_desc = snippet.get("description", "")
            current_tags = snippet.get("tags", [])
            cat_id = snippet["categoryId"]

            # Skip private videos
            # (we can't detect from snippet alone, but we'll try anyway)

            category = detect_category(title)

            # Check if already has full mega-brand (in case audit is stale)
            if has_mega_brand_block(current_desc):
                print(f"  [SKIP] {vid_id}: Already has mega-brand — {title[:50]}")
                continue

            # Build new description
            new_desc = update_description(current_desc, vid_id, category)

            # Check desc length (YouTube max: 5000 chars)
            if len(new_desc) > 5000:
                print(f"  [WARN] {vid_id}: Desc too long ({len(new_desc)} chars), trimming content")
                # Truncate old content to make room
                excess = len(new_desc) - 4900  # Leave 100 char margin
                cleaned = clean_existing_brand_blocks(current_desc)
                cleaned = cleaned[:len(cleaned) - excess]
                new_desc = update_description(cleaned, vid_id, category)

            if dry_run:
                # Show preview
                brand_preview = build_mega_brand_block(vid_id, category)
                print(f"  [DRY] {vid_id}: {title[:55]}")
                print(f"         Cat: {category} | Desc: {len(current_desc)}→{len(new_desc)} chars")
                if category == "wochenschau":
                    print(f"         + PREMIUM Wochenschau block")
                results.append({
                    "id": vid_id,
                    "title": title,
                    "category": category,
                    "old_len": len(current_desc),
                    "new_len": len(new_desc),
                    "status": "dry_run",
                })
            else:
                # APPLY
                body = {
                    "id": vid_id,
                    "snippet": {
                        "title": title,
                        "description": new_desc,
                        "tags": current_tags,
                        "categoryId": cat_id,
                    },
                }
                try:
                    youtube.videos().update(part="snippet", body=body).execute()
                    updated += 1
                    quota_used += 50
                    cat_label = f" [PREMIUM]" if category == "wochenschau" else ""
                    print(f"  [OK] {vid_id}: {title[:50]}{cat_label}")
                    results.append({
                        "id": vid_id,
                        "title": title,
                        "category": category,
                        "status": "success",
                    })
                    # Rate limit: 1 request per second
                    time.sleep(0.5)
                except Exception as e:
                    error_msg = str(e)
                    print(f"  [ERR] {vid_id}: {error_msg[:80]}")
                    results.append({
                        "id": vid_id,
                        "title": title,
                        "category": category,
                        "status": "error",
                        "error": error_msg,
                    })
                    errors += 1
                    if "quotaExceeded" in error_msg:
                        print("\n🛑 QUOTA EXCEEDED! Stopping immediately.")
                        break

    # Summary
    success = sum(1 for r in results if r["status"] in ("success", "dry_run"))
    ws_count = sum(1 for r in results if r.get("category") == "wochenschau")

    print(f"\n{'='*60}")
    print(f"MEGA-BRAND UPDATE SUMMARY")
    print(f"{'='*60}")
    print(f"Total processed:    {len(results)}")
    print(f"Success:            {success}")
    print(f"Errors:             {errors}")
    print(f"Wochenschau:        {ws_count} (with premium block)")
    print(f"Quota used:         {quota_used} units")

    # Save report
    report = {
        "date": datetime.now().isoformat(),
        "mode": "dry_run" if dry_run else "applied",
        "total": len(results),
        "success": success,
        "errors": errors,
        "wochenschau_premium": ws_count,
        "quota_used": quota_used,
        "results": results,
    }

    suffix = "dryrun" if dry_run else "applied"
    report_path = Path(__file__).resolve().parent.parent.parent / "config" / \
        f"megabrand_update_{suffix}_{datetime.now().strftime('%Y_%m_%d')}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n📄 Report: {report_path}")

    if dry_run:
        total_quota = len(results) * 50
        print(f"\n📊 Estimated quota for --apply: {total_quota} units")
        print(f"🔄 To apply: python {sys.argv[0]} --apply")
        if total_quota > 8000:
            batches = (len(results) // 160) + 1
            print(f"⚠️  Quota > 8000! Split into {batches} days with --limit 160")


def main():
    parser = argparse.ArgumentParser(description="Mega-Brand Description Updater")
    parser.add_argument("--audit", action="store_true", help="Phase 1: Audit only (Public API)")
    parser.add_argument("--dry-run", action="store_true", help="Phase 2: Preview changes")
    parser.add_argument("--apply", action="store_true", help="Phase 2: Apply changes (OAuth)")
    parser.add_argument("--limit", type=int, default=0, help="Max videos to update")
    args = parser.parse_args()

    if not API_KEY:
        # Check if OAuth token exists as fallback
        token_path = Path(__file__).resolve().parent.parent.parent / "token.json"
        if not token_path.exists():
            print("❌ Neither YOUTUBE_API_KEY nor token.json found!")
            sys.exit(1)
        print("ℹ️  Using OAuth (token.json) — no Public API key set")

    if args.audit:
        run_audit()
    elif args.dry_run or args.apply:
        run_update(dry_run=not args.apply, limit=args.limit)
    else:
        print("Usage:")
        print("  python megabrand_description_update.py --audit       # Scan all videos")
        print("  python megabrand_description_update.py --dry-run     # Preview changes")
        print("  python megabrand_description_update.py --apply       # Apply changes")
        print("  python megabrand_description_update.py --apply --limit 10")


if __name__ == "__main__":
    main()
