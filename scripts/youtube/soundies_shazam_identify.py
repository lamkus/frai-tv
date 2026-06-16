#!/usr/bin/env python3
"""
Soundies Shazam Identifier
Verwendet Shazam um alle Soundie-Videos automatisch zu identifizieren.

Workflow:
1. Extrahiert Audio von YouTube-Videos (30 Sekunden Sample)
2. Sendet an Shazam zur Erkennung
3. Speichert Artist + Track Info
"""

import asyncio
import json
import os
import subprocess
from pathlib import Path
from shazamio import Shazam

# Konfiguration
OUTPUT_DIR = Path("D:/remaike.TV/config/soundie_audio")
RESULTS_FILE = Path("D:/remaike.TV/config/soundies_shazam_results.json")

# Alle 21 Soundie Video-IDs
SOUNDIE_VIDEOS = [
    {"id": "mReDNz-Exdk", "title": "Lamp of Memory"},
    {"id": "GerP7_evS9o", "title": "Beyond the Blue Horizon"},
    {"id": "OvBqUlzTunI", "title": "Hollywood Boogie"},
    {"id": "D-LL4VuR5Pg", "title": "Lullaby of Broadway"},
    {"id": "w82vzaGBqwE", "title": "A Little Robin Told Me So"},
    {"id": "6XVj6G3qNYY", "title": "Jiveroo"},
    {"id": "NAk0QvvaT7M", "title": "Who's Yehudi"},
    {"id": "340C9lsoyYk", "title": "Tica Ti Tica Ta"},
    {"id": "oA7XcqVM1Vo", "title": "I Can't Give You Anything But Love"},
    {"id": "mDSdzFc572Y", "title": "What This Country Needs"},
    {"id": "LJp-M01OI-8", "title": "Chime Bells"},
    {"id": "rprpMDyTWRI", "title": "Zig Me Baby"},
    {"id": "Z2SxppvCWvE", "title": "Hawaiian Hula Song"},
    {"id": "2yGX3wy-4SQ", "title": "Havana Madrid Show"},
    {"id": "hAs6lunYl-E", "title": "A Jazz Etude"},
    {"id": "DHogGPBbzRI", "title": "Sweet Sue"},
    {"id": "A8LWgWF5f5k", "title": "The Hut-Sut Song"},
    {"id": "HvwtRYp43eU", "title": "Got to Be This or That"},
    {"id": "ukmrI7DlXkc", "title": "In a Shanty"},
    {"id": "1zKpqdriv70", "title": "Ten Pretty Girls"},
    {"id": "hIsTWWP-YkQ", "title": "Once in a While"},
]


def download_audio(video_id: str, output_path: Path) -> bool:
    """
    Lädt Audio von YouTube-Video herunter (30 Sekunden ab 0:10).
    Verwendet yt-dlp für beste Kompatibilität.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    output_file = output_path / f"{video_id}.mp3"
    
    if output_file.exists():
        print(f"  ✓ Audio bereits vorhanden: {video_id}")
        return True
    
    try:
        # yt-dlp: Extrahiere nur Audio, 30 Sekunden ab Sekunde 10
        cmd = [
            "yt-dlp",
            "-x",  # Extract audio
            "--audio-format", "mp3",
            "--audio-quality", "128K",
            "--download-sections", "*10-40",  # 30 Sekunden ab 0:10
            "-o", str(output_file),
            "--no-playlist",
            "--quiet",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and output_file.exists():
            print(f"  ✓ Audio heruntergeladen: {video_id}")
            return True
        else:
            # Fallback: Ganzes Audio herunterladen
            cmd_full = [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "128K",
                "-o", str(output_file),
                "--no-playlist",
                "--quiet",
                url
            ]
            result = subprocess.run(cmd_full, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"  ✓ Audio (vollständig) heruntergeladen: {video_id}")
                return True
            print(f"  ✗ Download fehlgeschlagen: {video_id}")
            print(f"    Error: {result.stderr[:200] if result.stderr else 'Unknown'}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ Timeout bei Download: {video_id}")
        return False
    except Exception as e:
        print(f"  ✗ Fehler bei Download: {video_id} - {e}")
        return False


async def identify_with_shazam(audio_path: Path) -> dict:
    """
    Identifiziert einen Song mit Shazam.
    """
    shazam = Shazam()
    
    try:
        result = await shazam.recognize(str(audio_path))
        
        if result and "track" in result:
            track = result["track"]
            return {
                "found": True,
                "title": track.get("title", "Unknown"),
                "artist": track.get("subtitle", "Unknown"),
                "album": track.get("sections", [{}])[0].get("metadata", [{}])[0].get("text", "") if track.get("sections") else "",
                "genre": track.get("genres", {}).get("primary", ""),
                "year": "",  # Shazam gibt oft kein Jahr zurück
                "shazam_key": track.get("key", ""),
                "apple_music_url": track.get("hub", {}).get("actions", [{}])[0].get("uri", "") if track.get("hub") else "",
            }
        else:
            return {"found": False, "error": "Kein Match gefunden"}
            
    except Exception as e:
        return {"found": False, "error": str(e)}


async def main():
    """Hauptfunktion: Download + Shazam für alle Soundies."""
    
    print("=" * 60)
    print("🎵 SOUNDIES SHAZAM IDENTIFIER")
    print("=" * 60)
    
    # Output-Verzeichnis erstellen
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {
        "meta": {
            "created": "2026-01-19",
            "method": "Shazam Audio Recognition",
            "total_videos": len(SOUNDIE_VIDEOS),
        },
        "results": []
    }
    
    identified_count = 0
    
    for i, video in enumerate(SOUNDIE_VIDEOS, 1):
        video_id = video["id"]
        current_title = video["title"]
        
        print(f"\n[{i}/{len(SOUNDIE_VIDEOS)}] {current_title} ({video_id})")
        
        # 1. Audio herunterladen
        audio_path = OUTPUT_DIR / f"{video_id}.mp3"
        if not download_audio(video_id, OUTPUT_DIR):
            results["results"].append({
                "video_id": video_id,
                "current_title": current_title,
                "shazam": {"found": False, "error": "Download failed"}
            })
            continue
        
        # 2. Mit Shazam identifizieren
        print(f"  🔍 Shazam-Analyse läuft...")
        shazam_result = await identify_with_shazam(audio_path)
        
        if shazam_result["found"]:
            identified_count += 1
            print(f"  ✅ GEFUNDEN: {shazam_result['artist']} - {shazam_result['title']}")
        else:
            print(f"  ❌ Nicht erkannt: {shazam_result.get('error', 'Unknown')}")
        
        results["results"].append({
            "video_id": video_id,
            "current_title": current_title,
            "shazam": shazam_result
        })
        
        # Kurze Pause um Rate-Limiting zu vermeiden
        await asyncio.sleep(1)
    
    # Ergebnisse speichern
    results["meta"]["identified"] = identified_count
    results["meta"]["not_found"] = len(SOUNDIE_VIDEOS) - identified_count
    
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"📊 ERGEBNIS: {identified_count}/{len(SOUNDIE_VIDEOS)} Songs erkannt")
    print(f"💾 Gespeichert in: {RESULTS_FILE}")
    print("=" * 60)
    
    # Zusammenfassung der gefundenen Songs
    print("\n📋 GEFUNDENE SONGS:")
    for r in results["results"]:
        if r["shazam"]["found"]:
            print(f"  ✅ {r['current_title']} → {r['shazam']['artist']}: {r['shazam']['title']}")
    
    print("\n❓ NICHT ERKANNT:")
    for r in results["results"]:
        if not r["shazam"]["found"]:
            print(f"  ❌ {r['current_title']}")


if __name__ == "__main__":
    asyncio.run(main())
