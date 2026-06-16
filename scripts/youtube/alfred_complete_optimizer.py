#!/usr/bin/env python3
"""Alfred Complete Optimizer - Zuverlässig, keine Fragen.

Macht alles in einem Rutsch:
1. Holt ALLE Videos vom Channel via OAuth (wir haben OAuth, nutzen wir es)
2. Filtert Alfred-Videos
3. Generiert optimierte Tags/Description
4. Wendet an (mit --apply)

REGELN:
- OAuth für alles (wir haben es, Public API Key ist nicht konfiguriert)
- Keine Deletes
- Stop bei quotaExceeded

Usage:
  python scripts/youtube/alfred_complete_optimizer.py           # Dry-run
  python scripts/youtube/alfred_complete_optimizer.py --apply   # Anwenden
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
OAUTH_FILE = CONFIG / "youtube_oauth.json"
VIDEOS_CACHE = CONFIG / "videos.json"
TAGS_PLAN = CONFIG / "tags_plan.json"
OUT_PLAN = CONFIG / "alfred_seo_plan.json"
OUT_REPORT = CONFIG / "alfred_seo_apply_report.json"

CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

# ═══════════════════════════════════════════════════════════════════════════
# ALFRED SEO CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

ALFRED_TAGS_BASE = [
    "Alfred J. Kwak",
    "Alfred Jodokus Quack", 
    "Alfred Jodokus Kwak",
    "Alfred Jodocus Kwak",
    "Alfred Jodocus Quack",
    "Kwak",
    "Quack",
    "Alfred der kleine Rabe",
    "Herman van Veen",
    "Harald Siepermann",
    "Zeichentrick",
    "Zeichentrickserie",
    "Kinderserie",
    "Deutsch",
    "German",
    "80er",
    "90er",
    "Nostalgie",
    "Classic Animation",
    "remAIke",
    "8K",
    "4K UHD",
    "remastered",
    "restored",
]

ALFRED_DESCRIPTION_BLOCK = """

🇩🇪 Alfred J. Kwak / Quack (Alfred Jodokus Quack) – Deutsche Zeichentrickserie (80er/90er).
🇬🇧 Alfred J. Kwak / Quack (Alfred Jodokus Quack) – Classic animated series.

Keywords: Alfred J. Kwak, Alfred Jodokus Quack, Alfred Jodocus Kwak, Kwak, Quack, Deutsch, German.

#AlfredJKwak #AlfredJodokusQuack #Kwak #Quack #Zeichentrick #Deutsch #remAIke"""


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
    """OAuth Client - wir haben Token, also nutzen wir es."""
    if not OAUTH_FILE.exists():
        raise SystemExit(f"❌ Missing: {OAUTH_FILE}")
    
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
        print("🔄 Refreshing OAuth token...")
        creds.refresh(Request())
        creds_data["token"] = creds.token
        save_json(OAUTH_FILE, creds_data)
    
    return build("youtube", "v3", credentials=creds)


def fetch_all_channel_videos(youtube) -> List[Video]:
    """Holt ALLE Videos vom Channel. Quota: ~3-5 Units."""
    print(f"📥 Fetching all videos from channel {CHANNEL_ID}...")
    
    # Erst Uploads-Playlist ID holen
    ch_resp = youtube.channels().list(
        part="contentDetails",
        id=CHANNEL_ID
    ).execute()
    
    if not ch_resp.get("items"):
        raise SystemExit("❌ Channel not found")
    
    uploads_playlist = ch_resp["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"   Uploads playlist: {uploads_playlist}")
    
    # Alle Video-IDs sammeln
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
    
    # Video-Details holen (in Batches von 50)
    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        v_resp = youtube.videos().list(
            part="snippet",
            id=",".join(batch)
        ).execute()
        
        for item in v_resp.get("items", []):
            sn = item["snippet"]
            videos.append(Video(
                id=item["id"],
                title=sn.get("title", ""),
                description=sn.get("description", ""),
                tags=sn.get("tags", []),
                category_id=sn.get("categoryId", "24"),
            ))
    
    print(f"   Fetched details for {len(videos)} videos")
    return videos


def is_alfred(title: str) -> bool:
    t = (title or "").lower()
    return "alfred" in t and ("kwak" in t or "quack" in t)


def build_alfred_tags(existing_tags: List[str]) -> List[str]:
    """Baut optimierte Tags für Alfred. Max 500 Zeichen."""
    # Basis-Tags zuerst
    tags = list(ALFRED_TAGS_BASE)
    
    # Existierende Tags hinzufügen (wenn nicht doppelt)
    seen = {t.lower() for t in tags}
    for t in existing_tags:
        if t.lower() not in seen and t.strip():
            tags.append(t)
            seen.add(t.lower())
    
    # Auf 500 Zeichen begrenzen
    while tags and len(",".join(tags)) > 500:
        tags = tags[:-1]
    
    return tags


def enhance_description(desc: str) -> str:
    """Fügt SEO-Block zur Description hinzu wenn nicht vorhanden."""
    if "Keywords: Alfred J. Kwak" in desc:
        return desc
    return desc.rstrip() + ALFRED_DESCRIPTION_BLOCK


def main():
    parser = argparse.ArgumentParser(description="Alfred Complete Optimizer")
    parser.add_argument("--apply", action="store_true", help="Änderungen anwenden")
    parser.add_argument("--limit", type=int, default=0, help="Max Videos zu ändern")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🦆 ALFRED COMPLETE OPTIMIZER")
    print("=" * 60)
    
    youtube = get_youtube_client()
    
    # 1. Alle Videos holen
    all_videos = fetch_all_channel_videos(youtube)
    
    # 2. Cache aktualisieren
    cache_data = {
        "updated_at": datetime.now().isoformat(),
        "channel_id": CHANNEL_ID,
        "total_videos": len(all_videos),
        "videos": [asdict(v) for v in all_videos]
    }
    save_json(VIDEOS_CACHE, cache_data)
    print(f"💾 Cache updated: {VIDEOS_CACHE}")
    
    # 3. Alfred-Videos filtern
    alfred_videos = [v for v in all_videos if is_alfred(v.title)]
    print(f"\n🦆 Found {len(alfred_videos)} Alfred videos")
    
    if not alfred_videos:
        print("❌ No Alfred videos found!")
        return
    
    # 4. Plan erstellen
    plan_items = []
    for v in alfred_videos:
        new_tags = build_alfred_tags(v.tags)
        new_desc = enhance_description(v.description)
        
        changes = {
            "tags_changed": new_tags != v.tags,
            "desc_changed": new_desc != v.description,
            "old_tags_count": len(v.tags),
            "new_tags_count": len(new_tags),
            "new_tags_chars": len(",".join(new_tags)),
        }
        
        plan_items.append({
            "id": v.id,
            "title": v.title,
            "category_id": v.category_id,
            "new_tags": new_tags,
            "new_description": new_desc,
            "changes": changes,
        })
    
    # Plan speichern
    plan = {
        "generated_at": datetime.now().isoformat(),
        "total_alfred_videos": len(alfred_videos),
        "estimated_quota": len(alfred_videos) * 50,
        "items": plan_items,
    }
    save_json(OUT_PLAN, plan)
    print(f"📋 Plan saved: {OUT_PLAN}")
    print(f"   Estimated quota for apply: ~{len(alfred_videos) * 50} units")
    
    # 5. Statistiken
    needs_update = sum(1 for p in plan_items if p["changes"]["tags_changed"] or p["changes"]["desc_changed"])
    print(f"\n📊 Statistics:")
    print(f"   Videos needing update: {needs_update}/{len(alfred_videos)}")
    
    for p in plan_items[:5]:
        print(f"   • {p['title'][:50]}...")
        print(f"     Tags: {p['changes']['old_tags_count']} → {p['changes']['new_tags_count']} ({p['changes']['new_tags_chars']} chars)")
    
    if not args.apply:
        print(f"\n⚠️  DRY-RUN - keine Änderungen. Mit --apply ausführen.")
        return
    
    # 6. APPLY
    print(f"\n🚀 APPLYING CHANGES...")
    
    limit = args.limit if args.limit > 0 else len(plan_items)
    applied = 0
    failed = 0
    errors = []
    
    for item in plan_items[:limit]:
        vid = item["id"]
        
        body = {
            "id": vid,
            "snippet": {
                "title": item["title"],  # Titel nicht ändern
                "description": item["new_description"],
                "tags": item["new_tags"],
                "categoryId": item["category_id"],
            }
        }
        
        try:
            youtube.videos().update(part="snippet", body=body).execute()
            applied += 1
            print(f"   ✅ {vid}: {item['title'][:40]}...")
            time.sleep(0.5)  # Rate limiting
            
        except HttpError as e:
            error_msg = str(e)
            if "quotaExceeded" in error_msg:
                print(f"\n❌ QUOTA EXCEEDED! Stopping.")
                errors.append("quotaExceeded - stopped")
                break
            failed += 1
            errors.append(f"{vid}: {error_msg[:100]}")
            print(f"   ❌ {vid}: {error_msg[:50]}")
    
    # Report speichern
    report = {
        "applied_at": datetime.now().isoformat(),
        "total_planned": len(plan_items),
        "applied": applied,
        "failed": failed,
        "errors": errors[:20],
    }
    save_json(OUT_REPORT, report)
    
    print(f"\n{'=' * 60}")
    print(f"✅ DONE: {applied} applied, {failed} failed")
    print(f"📄 Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
