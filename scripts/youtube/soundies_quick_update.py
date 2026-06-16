#!/usr/bin/env python3
"""Quick Soundies updater - no input required."""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CONFIG_DIR = Path("D:/remaike.TV/config")
OAUTH_FILE = CONFIG_DIR / "youtube_oauth.json"
UPDATES_FILE = CONFIG_DIR / "soundies_final_updates_v2.json"
RESULTS_FILE = CONFIG_DIR / "soundies_apply_results.json"

# Load updates
with open(UPDATES_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

updates = data["updates"]
to_update = [u for u in updates if u["confidence"] in ["HIGH", "MEDIUM"] and u.get("apply", True)]

print("=" * 70)
print("🎬 SOUNDIES YOUTUBE TITLE UPDATER")
print("=" * 70)
print(f"\n📋 {len(to_update)} Videos zu aktualisieren (HIGH + MEDIUM)\n")

# Load OAuth
with open(OAUTH_FILE, "r") as f:
    token_data = json.load(f)

credentials = Credentials(
    token=token_data["token"],
    refresh_token=token_data["refresh_token"],
    token_uri=token_data["token_uri"],
    client_id=token_data["client_id"],
    client_secret=token_data["client_secret"],
)

youtube = build("youtube", "v3", credentials=credentials)

results = {
    "meta": {"date": "2026-01-19", "total": len(to_update), "success": 0, "failed": 0},
    "updates": []
}

for i, update in enumerate(to_update, 1):
    video_id = update["id"]
    new_title = update["new_title"]
    song = update["song"]
    artist = update["artist"]
    
    print(f"[{i}/{len(to_update)}] {song}")
    print(f"    Artist: {artist}")
    
    try:
        # Get current video
        video_response = youtube.videos().list(part="snippet,status", id=video_id).execute()
        
        if not video_response.get("items"):
            print(f"    ❌ Video nicht gefunden")
            results["updates"].append({"success": False, "video_id": video_id, "error": "Not found"})
            results["meta"]["failed"] += 1
            continue
        
        video = video_response["items"][0]
        snippet = video["snippet"]
        old_title = snippet["title"]
        
        # Update title only
        snippet["title"] = new_title
        
        update_response = youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": snippet}
        ).execute()
        
        print(f"    ✅ {new_title[:55]}...")
        results["updates"].append({
            "success": True,
            "video_id": video_id,
            "old_title": old_title,
            "new_title": new_title
        })
        results["meta"]["success"] += 1
        
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"    ❌ Fehler: {error_msg}")
        results["updates"].append({"success": False, "video_id": video_id, "error": error_msg})
        results["meta"]["failed"] += 1

# Save results
with open(RESULTS_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("\n" + "=" * 70)
print(f"📊 ERGEBNIS: {results['meta']['success']}/{len(to_update)} erfolgreich")
if results["meta"]["failed"] > 0:
    print(f"❌ FEHLGESCHLAGEN: {results['meta']['failed']}")
print(f"💾 Details: {RESULTS_FILE}")
print("=" * 70)
