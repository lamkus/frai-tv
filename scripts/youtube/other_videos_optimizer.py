#!/usr/bin/env python3
"""Other Videos Tag Optimizer - Session 13.01.2026

Ziel: Alle Videos der "Other"-Kategorie mit <10 Tags optimieren.
Das sind Videos die NICHT zu den bekannten Serien gehören.

Ausschluss-Liste (bereits optimiert):
- Alfred, Kwak, Quack
- Betty Boop
- Popeye
- Porky Pig
- Casper
- Superman
- Felix the Cat
- Chaplin, Keaton
- Soundie, Wochenschau
- Hitchcock
- Asterix
- Dinner for One
- Color Classic

REGELN:
- OAuth für alles (wir haben es)
- Keine Deletes
- Stop bei quotaExceeded

Usage:
  python scripts/youtube/other_videos_optimizer.py                    # Dry-run
  python scripts/youtube/other_videos_optimizer.py --apply            # Alle anwenden
  python scripts/youtube/other_videos_optimizer.py --apply --limit 10 # Nur 10 Videos
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
OAUTH_FILE = CONFIG / "youtube_oauth.json"
VIDEOS_CACHE = CONFIG / "videos.json"
TAGS_PLAN = CONFIG / "tags_plan.json"
OUT_REPORT = CONFIG / "other_videos_report.json"

CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

# ═══════════════════════════════════════════════════════════════════════════
# EXCLUSION PATTERNS - Videos die NICHT "Other" sind
# ═══════════════════════════════════════════════════════════════════════════

EXCLUDE_PATTERNS = [
    r'alfred',
    r'kwak',
    r'quack',
    r'jodokus',
    r'jodocus',
    r'betty\s*boop',
    r'popeye',
    r'porky',
    r'casper',
    r'superman',
    r'felix',
    r'chaplin',
    r'keaton',
    r'soundie',
    r'wochenschau',
    r'hitchcock',
    r'asterix',
    r'dinner\s*for\s*one',
    r'color\s*classic',
    r'fleischer',
    r'#short',  # Shorts ausschließen
]

# Standard-Tags für "Other" Videos
BASE_TAGS = [
    "8K",
    "4K UHD",
    "restored",
    "remastered",
    "AI upscaled",
    "AI restoration",
    "best online version",
    "remAIke",
    "@remAIke_IT",
    "reAImastered",
    "FRai.TV",
    "vintage",
    "classic",
    "public domain",
]


@dataclass
class Video:
    id: str
    title: str
    description: str
    tags: List[str]
    category_id: str


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_youtube_client():
    """OAuth Client."""
    if not OAUTH_FILE.exists():
        raise SystemExit(f"Missing: {OAUTH_FILE}")
    
    creds_data = load_json(OAUTH_FILE)
    creds = Credentials(
        token=creds_data.get("token"),
        refresh_token=creds_data.get("refresh_token"),
        token_uri=creds_data.get("token_uri"),
        client_id=creds_data.get("client_id"),
        client_secret=creds_data.get("client_secret"),
        scopes=creds_data.get("scopes"),
    )
    
    if creds.expired and creds.refresh_token:
        print("[OAuth] Refreshing token...")
        creds.refresh(Request())
        creds_data["token"] = creds.token
        save_json(OAUTH_FILE, creds_data)
    
    return build("youtube", "v3", credentials=creds)


def is_excluded(title: str) -> bool:
    """Prüft ob ein Video zu einer bekannten Serie gehört."""
    t = title.lower()
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            return True
    return False


def dedupe_tags(tags: List[str]) -> List[str]:
    """Entfernt Duplikate, behält Reihenfolge."""
    seen = set()
    result = []
    for tag in tags:
        tag = str(tag or "").strip().lstrip("#")
        if not tag:
            continue
        key = tag.casefold()
        if key not in seen:
            seen.add(key)
            result.append(tag)
    return result


def limit_tags_500_chars(tags: List[str], min_tags: int = 20, max_tags: int = 30) -> List[str]:
    """Begrenzt Tags auf YouTube-Limit (500 Zeichen)."""
    tags = dedupe_tags(tags)
    kept = []
    
    for tag in tags:
        candidate = kept + [tag]
        if len(",".join(candidate)) <= 500:
            kept = candidate
        if len(kept) >= max_tags:
            break
    
    # Auffüllen mit Base-Tags wenn nötig
    if len(kept) < min_tags:
        for filler in BASE_TAGS:
            if filler.casefold() in {t.casefold() for t in kept}:
                continue
            candidate = kept + [filler]
            if len(",".join(candidate)) <= 500:
                kept = candidate
            if len(kept) >= min_tags:
                break
    
    return kept


def extract_title_keywords(title: str) -> List[str]:
    """Extrahiert sinnvolle Keywords aus dem Titel."""
    # Entferne technische Marker
    clean = re.sub(r'\|.*$', '', title)  # Alles nach |
    clean = re.sub(r'@\w+', '', clean)   # @mentions
    clean = re.sub(r'\b(8K|4K|UHD|HQ|HD)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'\(\d{4}\)', '', clean)  # (1933)
    clean = re.sub(r'[^\w\s\-]', ' ', clean)  # Sonderzeichen
    
    words = clean.split()
    # Nur Wörter mit 3+ Buchstaben
    keywords = [w for w in words if len(w) >= 3 and not w.isdigit()]
    return keywords[:10]  # Max 10 Keywords aus Titel


def generate_tags_for_video(video: Video) -> List[str]:
    """Generiert optimale Tags für ein Video."""
    tags = list(video.tags) if video.tags else []
    
    # Keywords aus Titel
    title_keywords = extract_title_keywords(video.title)
    tags.extend(title_keywords)
    
    # Jahr extrahieren falls vorhanden
    year_match = re.search(r'\((\d{4})\)', video.title)
    if year_match:
        year = year_match.group(1)
        tags.append(year)
        tags.append(f"{year}s")
    
    # Base-Tags hinzufügen
    tags.extend(BASE_TAGS)
    
    # Spezifische Genre-Tags basierend auf Titel-Hinweisen
    title_lower = video.title.lower()
    
    if any(x in title_lower for x in ["skeleton", "spooky", "ghost", "halloween"]):
        tags.extend(["Halloween", "spooky", "skeleton dance", "horror"])
    
    if any(x in title_lower for x in ["zombie", "horror"]):
        tags.extend(["horror", "zombie", "classic horror", "monster movie"])
    
    if any(x in title_lower for x in ["car", "racing", "porsche", "getaway", "ken block"]):
        tags.extend(["car", "racing", "automotive", "street racing", "car culture"])
    
    if any(x in title_lower for x in ["three stooges", "stooges"]):
        tags.extend(["Three Stooges", "comedy", "slapstick", "classic comedy"])
    
    if any(x in title_lower for x in ["animation", "cartoon", "animated"]):
        tags.extend(["animation", "cartoon", "animated", "classic animation"])
    
    return limit_tags_500_chars(tags)


def fetch_all_videos(youtube) -> List[Video]:
    """Holt alle Videos vom Channel."""
    print(f"[Fetch] Getting all videos from channel...")
    
    ch_resp = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID
    ).execute()
    
    if not ch_resp.get("items"):
        raise SystemExit("Channel not found")
    
    uploads_playlist = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    video_ids = []
    next_page = None
    
    while True:
        pl_resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in pl_resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        
        next_page = pl_resp.get("nextPageToken")
        if not next_page:
            break
    
    print(f"   Found {len(video_ids)} video IDs")
    
    # Video-Details holen
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = youtube.videos().list(
            part="snippet",
            id=",".join(batch)
        ).execute()
        
        for item in resp.get("items", []):
            snippet = item["snippet"]
            videos.append(Video(
                id=item["id"],
                title=snippet.get("title", ""),
                description=snippet.get("description", ""),
                tags=snippet.get("tags", []),
                category_id=snippet.get("categoryId", "")
            ))
    
    print(f"   Got details for {len(videos)} videos")
    return videos


def filter_other_videos(videos: List[Video], max_tags: int = 10) -> List[Video]:
    """Filtert nur 'Other' Videos mit wenigen Tags."""
    other = []
    for v in videos:
        # Skip bekannte Serien
        if is_excluded(v.title):
            continue
        
        # Skip Videos mit genug Tags
        tag_count = len(v.tags) if v.tags else 0
        if tag_count >= max_tags:
            continue
        
        other.append(v)
    
    # Nach Tag-Count sortieren (wenigste zuerst)
    other.sort(key=lambda x: len(x.tags) if x.tags else 0)
    return other


def apply_tags(youtube, video: Video, new_tags: List[str], dry_run: bool) -> tuple[bool, str]:
    """Wendet neue Tags auf ein Video an."""
    if dry_run:
        return True, "DRY-RUN"
    
    try:
        # Aktuelles Snippet holen
        resp = youtube.videos().list(part="snippet", id=video.id).execute()
        if not resp.get("items"):
            return False, "Video not found"
        
        snippet = resp["items"][0]["snippet"]
        old_count = len(snippet.get("tags", []))
        snippet["tags"] = new_tags
        
        # Update
        youtube.videos().update(
            part="snippet",
            body={"id": video.id, "snippet": snippet}
        ).execute()
        
        return True, f"Tags: {old_count} -> {len(new_tags)}"
    
    except HttpError as e:
        if "quotaExceeded" in str(e):
            return False, "QUOTA_EXCEEDED"
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Other Videos Tag Optimizer")
    parser.add_argument("--apply", action="store_true", help="Änderungen anwenden")
    parser.add_argument("--limit", type=int, default=0, help="Max Anzahl Videos")
    args = parser.parse_args()
    
    print("=" * 60)
    print("OTHER VIDEOS TAG OPTIMIZER")
    print("=" * 60)
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    if args.limit:
        print(f"Limit: {args.limit} videos")
    print()
    
    youtube = get_youtube_client()
    
    # Videos holen
    all_videos = fetch_all_videos(youtube)
    
    # Nur "Other" mit <10 Tags
    other_videos = filter_other_videos(all_videos, max_tags=10)
    print(f"\n[Filter] 'Other' videos with <10 tags: {len(other_videos)}")
    
    if not other_videos:
        print("[OK] No videos need optimization!")
        return
    
    # Limit anwenden
    if args.limit and args.limit < len(other_videos):
        other_videos = other_videos[:args.limit]
        print(f"   Limited to: {len(other_videos)} videos")
    
    # Quota-Schätzung
    estimated_quota = len(other_videos) * 50
    print(f"\n[Quota] Estimated cost: ~{estimated_quota} units ({len(other_videos)} x 50)")
    
    # Vorschau
    print(f"\n[Preview] First 5 videos:")
    for v in other_videos[:5]:
        tag_count = len(v.tags) if v.tags else 0
        print(f"   * [{tag_count} tags] {v.title[:55]}...")
    
    if not args.apply:
        print("\n[DRY-RUN] No changes made. Use --apply to update.")
        
        # Report speichern
        report = {
            "timestamp": datetime.now().isoformat(),
            "mode": "dry-run",
            "total_other_videos": len(other_videos),
            "estimated_quota": estimated_quota,
            "videos": [
                {
                    "id": v.id,
                    "title": v.title,
                    "current_tags": len(v.tags) if v.tags else 0,
                    "suggested_tags": generate_tags_for_video(v)
                }
                for v in other_videos
            ]
        }
        save_json(OUT_REPORT, report)
        print(f"\n[Saved] Report: {OUT_REPORT}")
        return
    
    # APPLY MODE
    print(f"\n[APPLY] Processing {len(other_videos)} videos...")
    
    results = {
        "success": [],
        "failed": [],
        "quota_stop": False
    }
    
    for i, video in enumerate(other_videos, 1):
        new_tags = generate_tags_for_video(video)
        old_count = len(video.tags) if video.tags else 0
        
        print(f"   [{i}/{len(other_videos)}] {video.title[:45]}...")
        
        success, msg = apply_tags(youtube, video, new_tags, dry_run=False)
        
        if success:
            results["success"].append({
                "id": video.id,
                "title": video.title,
                "old_tags": old_count,
                "new_tags": len(new_tags)
            })
            print(f"      OK: {old_count} -> {len(new_tags)} tags")
        else:
            if "QUOTA" in msg:
                print(f"      [STOP] Quota exceeded!")
                results["quota_stop"] = True
                break
            results["failed"].append({
                "id": video.id,
                "title": video.title,
                "error": msg
            })
            print(f"      FAIL: {msg}")
        
        # Rate limit
        time.sleep(0.5)
    
    # Report
    print(f"\n[Results]")
    print(f"   Success: {len(results['success'])}")
    print(f"   Failed: {len(results['failed'])}")
    print(f"   Quota used: ~{len(results['success']) * 50} units")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": "apply",
        "results": results
    }
    save_json(OUT_REPORT, report)
    print(f"\n[Saved] Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
