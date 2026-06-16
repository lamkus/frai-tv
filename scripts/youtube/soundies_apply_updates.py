#!/usr/bin/env python3
"""
Soundies YouTube Title Updater
Aktualisiert Titel für HIGH und MEDIUM confidence Soundies.

STOP-GATE: Nur Titel-Updates, keine Privacy-Änderungen!
"""

import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Konfiguration
CONFIG_DIR = Path("D:/remaike.TV/config")
OAUTH_FILE = CONFIG_DIR / "youtube_oauth.json"
UPDATES_FILE = CONFIG_DIR / "soundies_final_updates_v2.json"
RESULTS_FILE = CONFIG_DIR / "soundies_apply_results.json"


def load_oauth_credentials():
    """Lädt OAuth Credentials aus JSON."""
    with open(OAUTH_FILE, "r") as f:
        token_data = json.load(f)
    
    return Credentials(
        token=token_data["access_token"],
        refresh_token=token_data["refresh_token"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
    )


def update_video_title(youtube, video_id: str, new_title: str) -> dict:
    """
    Aktualisiert den Titel eines YouTube-Videos.
    Behält alle anderen Metadaten (Description, Tags, Category) bei.
    """
    try:
        # 1. Aktuellen Video-Status abrufen
        video_response = youtube.videos().list(
            part="snippet,status",
            id=video_id
        ).execute()
        
        if not video_response.get("items"):
            return {"success": False, "error": f"Video {video_id} nicht gefunden"}
        
        video = video_response["items"][0]
        snippet = video["snippet"]
        old_title = snippet["title"]
        
        # 2. Nur Titel ändern, Rest beibehalten
        snippet["title"] = new_title
        
        # 3. Update durchführen
        update_response = youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        ).execute()
        
        return {
            "success": True,
            "video_id": video_id,
            "old_title": old_title,
            "new_title": new_title
        }
        
    except Exception as e:
        return {
            "success": False,
            "video_id": video_id,
            "error": str(e)
        }


def main():
    print("=" * 70)
    print("🎬 SOUNDIES YOUTUBE TITLE UPDATER")
    print("=" * 70)
    
    # 1. Updates laden
    with open(UPDATES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updates = data["updates"]
    
    # 2. Nur HIGH und MEDIUM filtern
    to_update = [
        u for u in updates 
        if u["confidence"] in ["HIGH", "MEDIUM"] and u.get("apply", True)
    ]
    
    print(f"\n📋 {len(to_update)} Videos zu aktualisieren (HIGH + MEDIUM)")
    print("-" * 70)
    
    for u in to_update:
        conf_icon = "✅" if u["confidence"] == "HIGH" else "⚠️"
        print(f"  {conf_icon} [{u['confidence']}] {u['song']}")
        print(f"     → {u['artist']}")
    
    print("-" * 70)
    input("\n⏸️  ENTER drücken um fortzufahren (Ctrl+C zum Abbrechen)...")
    
    # 3. OAuth laden
    print("\n🔐 Lade OAuth Credentials...")
    credentials = load_oauth_credentials()
    youtube = build("youtube", "v3", credentials=credentials)
    
    # 4. Updates durchführen
    results = {
        "meta": {
            "date": "2026-01-19",
            "total": len(to_update),
            "success": 0,
            "failed": 0
        },
        "updates": []
    }
    
    for i, update in enumerate(to_update, 1):
        video_id = update["id"]
        new_title = update["new_title"]
        
        print(f"\n[{i}/{len(to_update)}] {update['song']}")
        print(f"  🎯 Neuer Titel: {new_title[:60]}...")
        
        result = update_video_title(youtube, video_id, new_title)
        results["updates"].append(result)
        
        if result["success"]:
            results["meta"]["success"] += 1
            print(f"  ✅ Erfolgreich aktualisiert!")
        else:
            results["meta"]["failed"] += 1
            print(f"  ❌ Fehler: {result.get('error', 'Unknown')}")
    
    # 5. Ergebnisse speichern
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print(f"📊 ERGEBNIS: {results['meta']['success']}/{len(to_update)} erfolgreich")
    print(f"💾 Details in: {RESULTS_FILE}")
    print("=" * 70)
    
    # Erfolgreiche Updates anzeigen
    if results["meta"]["success"] > 0:
        print("\n✅ AKTUALISIERTE VIDEOS:")
        for r in results["updates"]:
            if r["success"]:
                print(f"  • {r['new_title'][:65]}...")


if __name__ == "__main__":
    main()
