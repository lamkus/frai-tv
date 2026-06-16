#!/usr/bin/env python3
"""
Wochenschau Extra-Quellen Download
===================================
Downloads newly discovered episodes from:
- Indonesian subtitled uploads (alifrafikkhan@gmail.com)
- YouTube reuploads archived on Archive.org (GermanWWIIArchive, xxhistoryfootage)
- Individual uploads with non-standard identifiers

Discovered through manual research on 2026-02-08.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# Zielordner
DEST_DIR = r"V:\OriginalSources\German_Historical\Wochenschau_Certified\Todo"

# Log
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                        "logs", "wochenschau_download_extra.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ============================================================================
# CONFIRMED SOURCES (manually verified metadata)
# ============================================================================

EXTRA_SOURCES = [
    {
        "nr": 549,
        "identifier": "die-deutsche-wochenschau-berita-mingguan-jerman-no.-549-12-maret-1941",
        "filename": "Die Deutsche Wochenschau (Berita Mingguan Jerman) No. 549 - 12 Maret 1941.mp4",
        "format": "mp4",
        "size_mb": 497,
        "resolution": "1920x1080",
        "duration_min": 28,
        "source": "Indonesian subtitle upload (alifrafikkhan)",
        "note": "Full episode with Indonesian subtitles, 1080p"
    },
    {
        "nr": 580,
        "identifier": "die-deutsche-wochenschau-berita-mingguan-jerman-no.-580-15-oktober-1941-teks-indonesia",
        "filename": "Die Deutsche Wochenschau (Berita Mingguan Jerman) No. 580 - 15 Oktober 1941 (teks Indonesia).mp4",
        "format": "mp4",
        "size_mb": 987,
        "resolution": "1920x1080",
        "duration_min": 31,
        "source": "Indonesian subtitle upload (alifrafikkhan)",
        "note": "Full episode with Indonesian subtitles, 1080p"
    },
    {
        "nr": 563,
        "identifier": "youtube-gsmozf3JQOI",
        "filename": "gsmozf3JQOI.webm",
        "format": "webm",
        "size_mb": 367,
        "resolution": "1920x1440",
        "duration_min": 25,
        "source": "YouTube reupload (GermanWWIIArchive)",
        "note": "Full episode with English subtitles, 1440p WebM"
    },
    {
        "nr": 603,
        "identifier": "youtube-316Vg0U71Ok",
        "filename": "316Vg0U71Ok.webm",
        "format": "webm",
        "size_mb": 301,
        "resolution": "1920x1080",
        "duration_min": 24,
        "source": "YouTube reupload (xxhistoryfootage)",
        "note": "Full episode with English subtitles, 1080p WebM"
    },
    {
        "nr": 587,
        "identifier": "1941-12-03-Die-Deutsche-Wochenschau-587",
        "filename": "1941-12-03-DieDeutscheWochenschauNr.58710m08s640x480.mkv",
        "format": "mkv",
        "size_mb": 50,
        "resolution": "640x480",
        "duration_min": 10,
        "source": "Individual upload (peter_hansen)",
        "note": "EXCERPT ONLY - 10 min, Moelders funeral + Antikominternpakt"
    }
]


def download_file(url, dest_path, expected_size_mb=0):
    """Download mit Fortschrittsanzeige und Retry"""
    for attempt in range(1, 4):
        try:
            log(f"  📥 Download: {os.path.basename(dest_path)} (Versuch {attempt})")
            log(f"     URL: {url}")
            
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) remAIke-Archiver/1.0'
            })
            
            response = urllib.request.urlopen(req, timeout=300)
            total_size = int(response.headers.get('content-length', 0))
            
            block_size = 1024 * 1024  # 1 MB
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    f.write(block)
                    downloaded += len(block)
                    if total_size > 0:
                        pct = (downloaded / total_size) * 100
                        print(f"    {pct:.1f}% ({downloaded / 1024 / 1024:.1f}/{total_size / 1024 / 1024:.1f} MB)", 
                              end='\r', flush=True)
            
            print()  # Newline nach Fortschritt
            actual_size_mb = os.path.getsize(dest_path) / 1024 / 1024
            log(f"  ✅ Fertig: {actual_size_mb:.1f} MB")
            return True
            
        except Exception as e:
            log(f"  ❌ Fehler (Versuch {attempt}): {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            if attempt < 3:
                wait = attempt * 10
                log(f"     Warte {wait}s vor erneutem Versuch...")
                time.sleep(wait)
    
    return False


def main():
    log("=" * 70)
    log("🎬 WOCHENSCHAU EXTRA-QUELLEN DOWNLOAD")
    log(f"   Neue Quellen: {len(EXTRA_SOURCES)}")
    log(f"   Zielordner: {DEST_DIR}")
    log("=" * 70)
    
    os.makedirs(DEST_DIR, exist_ok=True)
    
    results = {
        "downloaded": [],
        "skipped": [],
        "failed": [],
        "excerpts": []
    }
    
    total_downloaded_mb = 0
    
    for i, source in enumerate(EXTRA_SOURCES, 1):
        nr = source["nr"]
        identifier = source["identifier"]
        filename = source["filename"]
        fmt = source["format"]
        
        log(f"\n{'='*50}")
        log(f"[{i}/{len(EXTRA_SOURCES)}] Nr. {nr} — {source['source']}")
        log(f"   Größe: ~{source['size_mb']} MB | {source['resolution']} | {source['duration_min']} min")
        log(f"   {source['note']}")
        
        # Zieldatei
        dest_filename = f"Wochenschau_Nr{nr}.{fmt}"
        dest_path = os.path.join(DEST_DIR, dest_filename)
        
        # Check ob schon vorhanden
        if os.path.exists(dest_path):
            existing_size = os.path.getsize(dest_path) / 1024 / 1024
            log(f"  ⏭️ Übersprungen (existiert: {existing_size:.1f} MB): {dest_filename}")
            results["skipped"].append({"nr": nr, "size_mb": existing_size})
            continue
        
        # Auch andere Formate checken
        for ext in ["mp4", "mkv", "webm"]:
            alt_path = os.path.join(DEST_DIR, f"Wochenschau_Nr{nr}.{ext}")
            if os.path.exists(alt_path):
                existing_size = os.path.getsize(alt_path) / 1024 / 1024
                log(f"  ⏭️ Übersprungen (existiert als .{ext}: {existing_size:.1f} MB)")
                results["skipped"].append({"nr": nr, "size_mb": existing_size, "format": ext})
                break
        else:
            # Download URL konstruieren
            encoded_filename = urllib.parse.quote(filename)
            url = f"https://archive.org/download/{identifier}/{encoded_filename}"
            
            success = download_file(url, dest_path, source["size_mb"])
            
            if success:
                actual_size = os.path.getsize(dest_path) / 1024 / 1024
                total_downloaded_mb += actual_size
                
                if source["duration_min"] < 15:
                    results["excerpts"].append({
                        "nr": nr, "size_mb": actual_size, "duration_min": source["duration_min"],
                        "note": source["note"]
                    })
                    log(f"  ⚠️ AUSZUG: Nur {source['duration_min']} min, nicht vollständig!")
                else:
                    results["downloaded"].append({
                        "nr": nr, "size_mb": actual_size, "format": fmt,
                        "resolution": source["resolution"], "source": source["source"]
                    })
            else:
                results["failed"].append({"nr": nr, "error": "Download fehlgeschlagen nach 3 Versuchen"})
        
        # Rate limiting
        time.sleep(2)
    
    # Zusammenfassung
    log("\n" + "=" * 70)
    log("📊 ZUSAMMENFASSUNG")
    log("=" * 70)
    log(f"  ✅ Heruntergeladen: {len(results['downloaded'])} Episoden")
    for d in results["downloaded"]:
        log(f"     Nr. {d['nr']}: {d['size_mb']:.1f} MB ({d['resolution']}, {d['source']})")
    
    if results["excerpts"]:
        log(f"  ⚠️ Auszüge: {len(results['excerpts'])} (nicht vollständig!)")
        for e in results["excerpts"]:
            log(f"     Nr. {e['nr']}: {e['size_mb']:.1f} MB, nur {e['duration_min']} min — {e['note']}")
    
    if results["skipped"]:
        log(f"  ⏭️ Übersprungen: {len(results['skipped'])} (bereits vorhanden)")
        for s in results["skipped"]:
            log(f"     Nr. {s['nr']}: {s['size_mb']:.1f} MB")
    
    if results["failed"]:
        log(f"  ❌ Fehlgeschlagen: {len(results['failed'])}")
        for f in results["failed"]:
            log(f"     Nr. {f['nr']}: {f['error']}")
    
    log(f"\n  📦 Gesamt heruntergeladen: {total_downloaded_mb:.1f} MB")
    
    # Ergebnis-JSON
    result_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                               "config", "wochenschau_extra_download_result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_sources": len(EXTRA_SOURCES),
            "results": results,
            "total_downloaded_mb": round(total_downloaded_mb, 1),
            "remaining_missing": sorted(list(set([460, 461, 462, 463, 464, 465, 466, 467, 469, 475, 476, 
                478, 479, 481, 484, 485, 486, 487, 489, 490, 494, 495, 498, 500, 501, 503, 
                535, 540, 541, 551, 558, 559, 560, 591, 597, 626, 636]) - 
                set(d["nr"] for d in results["downloaded"])))
        }, f, indent=2, ensure_ascii=False)
    
    log(f"\n  📄 Report: {result_path}")
    log("\n🏁 FERTIG!")


if __name__ == "__main__":
    main()
