#!/usr/bin/env python3
"""Alfred Playlist Ordner - Stellt korrekte Episoden-Reihenfolge her.

Findet oder erstellt Alfred-Playlist und ordnet Videos chronologisch.

REGELN:
- Keine Deletes per API (Playlist manuell in Studio leeren falls nötig)
- Nur Inserts (50 Units pro Video)
- Stop bei quotaExceeded

Usage:
  python scripts/youtube/alfred_playlist_ordner.py --check     # Prüft Playlist-Status
  python scripts/youtube/alfred_playlist_ordner.py --create    # Erstellt/Befüllt Playlist
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
OAUTH_FILE = CONFIG / "youtube_oauth.json"
VIDEOS_CACHE = CONFIG / "videos.json"
OUT_REPORT = CONFIG / "alfred_playlist_report.json"

CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"

# Playlist-Konfiguration
ALFRED_PLAYLIST_TITLE = "🦆 Alfred J. Kwak / Quack - Complete Series | Deutsch | 8K"
ALFRED_PLAYLIST_DESC = """Die KOMPLETTE Alfred J. Kwak / Jodokus Quack Serie auf Deutsch!

Perfekt zum Durchschauen - chronologisch von Episode 1 bis 52.
8K AI Restored by remAIke.

▶️ Autoplay an - Binge Alfred!

Keywords: Alfred J. Kwak, Alfred Jodokus Quack, Kwak, Quack, Deutsch, German, Zeichentrick, 80er, 90er

#AlfredJKwak #AlfredJodokusQuack #Kwak #Quack #Zeichentrick #Deutsch #remAIke"""


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_youtube_client():
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
        creds.refresh(Request())
        creds_data["token"] = creds.token
        save_json(OAUTH_FILE, creds_data)
    
    return build("youtube", "v3", credentials=creds)


def get_episode(title: str) -> int:
    m = re.search(r'\((\d+)/(\d+)\)', title)
    if m:
        return int(m.group(1))
    return 999


def get_alfred_videos() -> List[Dict]:
    """Lädt Alfred-Videos aus Cache, sortiert nach Episode."""
    cache = load_json(VIDEOS_CACHE)
    videos = cache.get("videos", [])
    
    alfreds = [v for v in videos 
               if "alfred" in v.get("title", "").lower() 
               and ("kwak" in v.get("title","").lower() or "quack" in v.get("title","").lower())]
    
    # Deduplizieren
    seen = set()
    unique = []
    for v in sorted(alfreds, key=lambda x: get_episode(x.get("title", ""))):
        if v["id"] not in seen:
            seen.add(v["id"])
            unique.append(v)
    
    return unique


def find_alfred_playlist(youtube) -> Optional[str]:
    """Sucht existierende Alfred-Playlist."""
    playlists = youtube.playlists().list(
        part="snippet",
        channelId=CHANNEL_ID,
        maxResults=50
    ).execute()
    
    for pl in playlists.get("items", []):
        title = pl["snippet"]["title"].lower()
        if "alfred" in title and ("kwak" in title or "quack" in title):
            return pl["id"]
    
    return None


def get_playlist_items(youtube, playlist_id: str) -> List[str]:
    """Holt aktuelle Videos in Playlist."""
    items = []
    next_page = None
    
    while True:
        resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in resp.get("items", []):
            items.append(item["contentDetails"]["videoId"])
        
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
    
    return items


def create_playlist(youtube) -> str:
    """Erstellt neue Alfred-Playlist."""
    resp = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": ALFRED_PLAYLIST_TITLE,
                "description": ALFRED_PLAYLIST_DESC,
            },
            "status": {
                "privacyStatus": "public"
            }
        }
    ).execute()
    
    return resp["id"]


def add_to_playlist(youtube, playlist_id: str, video_id: str, position: int) -> bool:
    """Fügt Video zur Playlist hinzu."""
    try:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    },
                    "position": position
                }
            }
        ).execute()
        return True
    except HttpError as e:
        if "quotaExceeded" in str(e):
            raise
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Prüft Playlist-Status")
    parser.add_argument("--create", action="store_true", help="Erstellt/Befüllt Playlist")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🦆 ALFRED PLAYLIST ORDNER")
    print("=" * 60)
    
    youtube = get_youtube_client()
    alfred_videos = get_alfred_videos()
    
    print(f"\n📊 Alfred-Videos im Cache: {len(alfred_videos)}")
    
    # Playlist suchen
    playlist_id = find_alfred_playlist(youtube)
    
    if playlist_id:
        print(f"✅ Alfred-Playlist gefunden: {playlist_id}")
        current_items = get_playlist_items(youtube, playlist_id)
        print(f"   Aktuelle Videos in Playlist: {len(current_items)}")
    else:
        print("❌ Keine Alfred-Playlist gefunden")
        current_items = []
    
    # Welche fehlen?
    alfred_ids = [v["id"] for v in alfred_videos]
    missing = [vid for vid in alfred_ids if vid not in current_items]
    
    print(f"\n📋 Status:")
    print(f"   Soll: {len(alfred_ids)} Videos")
    print(f"   Ist:  {len(current_items)} Videos")
    print(f"   Fehlen: {len(missing)} Videos")
    
    if args.check or (not args.create):
        print(f"\n⚠️  CHECK MODE - keine Änderungen. Mit --create ausführen.")
        
        if missing:
            print(f"\n📝 Fehlende Videos:")
            for vid in missing[:10]:
                v = next((x for x in alfred_videos if x["id"] == vid), {})
                print(f"   • {vid}: {v.get('title', '')[:50]}")
            if len(missing) > 10:
                print(f"   ... und {len(missing) - 10} weitere")
        return
    
    # CREATE MODE
    print(f"\n🚀 CREATING/UPDATING PLAYLIST...")
    
    if not playlist_id:
        print("   Creating new playlist...")
        playlist_id = create_playlist(youtube)
        print(f"   ✅ Created: {playlist_id}")
    
    # Videos hinzufügen (nur fehlende, in richtiger Position)
    added = 0
    failed = 0
    errors = []
    
    # Für korrekte Reihenfolge: alle Videos in Order durchgehen
    for pos, video in enumerate(alfred_videos):
        vid = video["id"]
        
        if vid in current_items:
            continue  # Bereits vorhanden
        
        try:
            if add_to_playlist(youtube, playlist_id, vid, pos):
                added += 1
                ep = get_episode(video.get("title", ""))
                print(f"   ✅ Pos {pos+1}: Ep {ep} - {vid}")
                time.sleep(0.3)
            else:
                failed += 1
                errors.append(f"{vid}: insert failed")
        except HttpError as e:
            if "quotaExceeded" in str(e):
                print(f"\n❌ QUOTA EXCEEDED! Stopping.")
                errors.append("quotaExceeded")
                break
            failed += 1
            errors.append(f"{vid}: {str(e)[:50]}")
    
    # Report
    report = {
        "updated_at": datetime.now().isoformat(),
        "playlist_id": playlist_id,
        "total_alfred_videos": len(alfred_videos),
        "previously_in_playlist": len(current_items),
        "added": added,
        "failed": failed,
        "errors": errors[:20],
        "estimated_quota_used": added * 50,
    }
    save_json(OUT_REPORT, report)
    
    print(f"\n{'=' * 60}")
    print(f"✅ DONE: {added} added, {failed} failed")
    print(f"   Quota used: ~{added * 50} units")
    print(f"📄 Report: {OUT_REPORT}")


if __name__ == "__main__":
    main()
