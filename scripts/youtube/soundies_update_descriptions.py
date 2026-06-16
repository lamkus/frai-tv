#!/usr/bin/env python3
"""
Soundies SEO Description Updater
Aktualisiert Descriptions für alle Soundies mit Music-optimiertem SEO.
"""

import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CONFIG_DIR = Path("D:/remaike.TV/config")
OAUTH_FILE = CONFIG_DIR / "youtube_oauth.json"
UPDATES_FILE = CONFIG_DIR / "soundies_final_updates_v2.json"
RESULTS_FILE = CONFIG_DIR / "soundies_description_results.json"


def generate_seo_description(artist: str, song: str, year: str, featuring: str = None) -> str:
    """Generiert SEO-optimierte Description für Soundies."""
    
    year_text = f" ({year})" if year and year != "1940s" else ""
    feat_text = f"\n🎹 Featuring: {featuring}" if featuring else ""
    
    description = f"""🎬 {artist}: {song}{year_text}

A rare vintage Soundie from the golden age of jukebox music films! Soundies were 3-minute musical films produced between 1940-1947 for coin-operated film jukeboxes called Panorams.
{feat_text}
🎵 Artist: {artist}
🎼 Song: {song}
📅 Era: 1940s
🎞️ Format: Soundie (Musical Short Film)
✨ Quality: 8K AI-Enhanced

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you love vintage music!
💬 COMMENT your favorite classic songs!
🔔 SUBSCRIBE for more rare musical gems!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More vintage music: https://frai.tv
🎬 Channel: @remAIke_IT

#Soundie #VintageMusic #1940s #Jazz #Swing #ClassicMusic #JukeboxMusic #BigBand #PublicDomain #8K #Retro #GoldenAge #MusicalShort #Panoram #{artist.replace(" ", "").replace("&", "").replace(",", "")}
"""
    return description


def main():
    print("=" * 70)
    print("🎵 SOUNDIES SEO DESCRIPTION UPDATER")
    print("=" * 70)
    
    # Load updates
    with open(UPDATES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updates = data["updates"]
    # Alle mit identifizierten Artists (HIGH + MEDIUM)
    to_update = [u for u in updates if u["confidence"] in ["HIGH", "MEDIUM"] and u.get("apply", True)]
    
    print(f"\n📋 {len(to_update)} Descriptions zu aktualisieren\n")
    
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
        artist = update["artist"]
        song = update["song"]
        year = update.get("year", "1940s")
        featuring = update.get("featuring")
        
        print(f"[{i}/{len(to_update)}] {artist}: {song}")
        
        try:
            # Get current video
            video_response = youtube.videos().list(part="snippet", id=video_id).execute()
            
            if not video_response.get("items"):
                print(f"    ❌ Video nicht gefunden")
                results["updates"].append({"success": False, "video_id": video_id, "error": "Not found"})
                results["meta"]["failed"] += 1
                continue
            
            video = video_response["items"][0]
            snippet = video["snippet"]
            old_description = snippet.get("description", "")
            
            # Generate new SEO description
            new_description = generate_seo_description(artist, song, year, featuring)
            
            # Update description
            snippet["description"] = new_description
            
            # Also add tags if missing
            existing_tags = snippet.get("tags", [])
            seo_tags = [
                "Soundie", "Soundies", "vintage music", "1940s", "jazz", "swing",
                "big band", "classic music", "jukebox", "panoram", "musical short",
                "public domain", "8K", "retro", artist, song
            ]
            # Merge without duplicates
            all_tags = list(set(existing_tags + seo_tags))[:15]  # Max 15 tags
            snippet["tags"] = all_tags
            
            update_response = youtube.videos().update(
                part="snippet",
                body={"id": video_id, "snippet": snippet}
            ).execute()
            
            print(f"    ✅ Description + Tags aktualisiert")
            results["updates"].append({
                "success": True,
                "video_id": video_id,
                "artist": artist,
                "song": song,
                "tags_added": len(all_tags)
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


if __name__ == "__main__":
    main()
