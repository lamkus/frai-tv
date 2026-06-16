"""
WOCHENSCHAU BULK DOWNLOADER
============================
Lädt ALLE verfügbaren fehlenden Episoden von Archive.org herunter.
Sucht automatisch nach alternativen Quellen für noch fehlende Nummern.

Erstellt: 2026-02-08
"""
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime

# ============================================================================
# KONFIGURATION
# ============================================================================
DOWNLOAD_DIR = r"V:\OriginalSources\German_Historical\Wochenschau_Certified\Todo"
FALLBACK_DIR = r"D:\remaike.TV\downloads\wochenschau"  # Falls V: nicht verfügbar
LOG_FILE = r"D:\remaike.TV\logs\wochenschau_download.log"

# 47 fehlende Episoden
MISSING_EPISODES = [
    460, 461, 462, 463, 464, 465, 466, 467, 469,  # 1939 Vorkrieg
    475, 476, 478, 479, 481, 484, 485, 486, 487, 489, 490,  # 1939-40 Sitzkrieg
    494, 495, 498, 500, 501, 503,
    535, 540, 541, 546, 549, 551, 558, 559, 560,  # 1940-41
    563, 580, 587, 591, 597, 603,  # 1941-42
    626, 636, 643, 646, 664, 678  # 1942-43
]

# ============================================================================
# BEKANNTE DOWNLOAD-QUELLEN (aus Recherche 2026-02-08)
# ============================================================================
KNOWN_SOURCES = {
    # --- EINZELDATEIEN ---
    546: {
        "identifier": "19410219DieDeutscheWochenschauNr.54623m14s640x480",
        "files": [None],  # None = Hauptdatei automatisch finden
        "quality": "640x480",
        "note": "Einzeldatei, 23:14"
    },
    
    # --- KOMPILATION Nr. 642-668 (1943 Part 1) ---
    643: {
        "identifier": "diedeutschewochenschau646.2",
        "files": [
            "die deutsche wochenschau 643.mp4",
            "die deutsche wochenschau 643.2.mp4"
        ],
        "quality": "Standard",
        "note": "In Kompilation 642-668"
    },
    646: {
        "identifier": "diedeutschewochenschau646.2",
        "files": ["die deutsche wochenschau 646.mp4"],
        "quality": "Standard",
        "note": "In Kompilation 642-668"
    },
    664: {
        "identifier": "diedeutschewochenschau646.2",
        "files": ["die deutsche wochenschau 664.mp4"],
        "quality": "Standard",
        "note": "In Kompilation 642-668"
    },
    
    # --- KOMPILATION Nr. 669-695 (1943 Part 2) ---
    678: {
        "identifier": "diedeutschewochenschau674_201907",
        "files": ["die deutsche wochenschau 678.mp4"],
        "quality": "Standard",
        "note": "In Kompilation 669-695"
    },
}

# ============================================================================
# ARCHIVE.ORG IDENTIFIER-PATTERNS ZUM SUCHEN
# ============================================================================
SEARCH_PATTERNS = [
    # Pattern 1: Offizielle Uploads mit Datum
    lambda nr: f"https://archive.org/metadata/{_date_identifier(nr)}",
    # Pattern 2: DieDeutscheWochenschauNr.XXX
    lambda nr: f"https://archive.org/metadata/DieDeutscheWochenschauNr.{nr}",
    lambda nr: f"https://archive.org/metadata/DieDeutscheWochenschauNr{nr}",
    # Pattern 3: UfA-Tonwoche mit Datum (für Nr < 511)
    lambda nr: f"https://archive.org/metadata/UfA-Tonwoche-Nr.{nr}" if nr < 511 else None,
    lambda nr: f"https://archive.org/metadata/UfATonwocheNr{nr}" if nr < 511 else None,
    # Pattern 4: DWS-Date Format (RGAKFD)
    lambda nr: f"https://archive.org/metadata/dws-{_date_dws(nr)}" if _date_dws(nr) else None,
    # Pattern 5: diedeutschewochenschaunr
    lambda nr: f"https://archive.org/metadata/diedeutschewochenschaunr{nr}",
    # Pattern 6: ufa-tonwoche-XXX
    lambda nr: f"https://archive.org/metadata/ufa-tonwoche-{nr}" if nr < 511 else None,
    # Pattern 7: Alternative Schreibweisen
    lambda nr: f"https://archive.org/metadata/die-deutsche-wochenschau-{nr}",
    lambda nr: f"https://archive.org/metadata/DeutscheWochenschau{nr}",
    lambda nr: f"https://archive.org/metadata/deutsche-wochenschau-nr-{nr}",
    # Pattern 8: NPC (NARA Naval Photographic Center)
    lambda nr: f"https://archive.org/metadata/NPC-{nr}",
]

# Geschätzte Daten für fehlende Nummern
EPISODE_DATES = {
    460: "1939-06-28", 461: "1939-07-05", 462: "1939-07-12", 463: "1939-07-19",
    464: "1939-07-26", 465: "1939-08-02", 466: "1939-08-09", 467: "1939-08-16",
    469: "1939-08-30", 475: "1939-10-11", 476: "1939-10-18", 478: "1939-11-01",
    479: "1939-11-08", 481: "1939-11-22", 484: "1939-12-13", 485: "1939-12-20",
    486: "1939-12-27", 487: "1940-01-03", 489: "1940-01-17", 490: "1940-01-24",
    494: "1940-02-21", 495: "1940-02-28", 498: "1940-03-20", 500: "1940-04-03",
    501: "1940-04-10", 503: "1940-04-24", 535: "1940-12-04", 540: "1941-01-08",
    541: "1941-01-15", 546: "1941-02-19", 549: "1941-03-12", 551: "1941-03-26",
    558: "1941-05-14", 559: "1941-05-21", 560: "1941-05-28", 563: "1941-06-18",
    580: "1941-10-15", 587: "1941-12-03", 591: "1942-01-07", 597: "1942-02-18",
    603: "1942-04-01", 626: "1942-09-16", 636: "1942-11-25", 643: "1943-01-13",
    646: "1943-02-03", 664: "1943-06-16", 678: "1943-09-22"
}

def _date_identifier(nr):
    """Erstellt möglichen Identifier mit Datum"""
    d = EPISODE_DATES.get(nr, "")
    if not d:
        return f"DieDeutscheWochenschauNr{nr}"
    parts = d.split("-")
    return f"{parts[0]}{parts[1]}{parts[2]}DieDeutscheWochenschauNr.{nr}"

def _date_dws(nr):
    """Erstellt DWS-Datumsformat (z.B. dws-14.3.40)"""
    d = EPISODE_DATES.get(nr, "")
    if not d:
        return None
    parts = d.split("-")
    day = str(int(parts[2]))
    month = str(int(parts[1]))
    year = parts[0][2:]  # 39, 40, 41...
    return f"{day}.{month}.{year}"


def log(msg):
    """Logging in Datei und Console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def get_download_dir():
    """Prüft ob V: verfügbar ist, sonst Fallback"""
    if os.path.exists(os.path.dirname(DOWNLOAD_DIR)):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        return DOWNLOAD_DIR
    else:
        os.makedirs(FALLBACK_DIR, exist_ok=True)
        log(f"⚠️ V: nicht verfügbar, nutze Fallback: {FALLBACK_DIR}")
        return FALLBACK_DIR


def check_archive_identifier(identifier):
    """Prüft ob ein Archive.org Identifier existiert und gibt Dateiliste zurück"""
    url = f"https://archive.org/metadata/{identifier}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "files" in data:
                mp4_files = [
                    f for f in data["files"]
                    if f.get("format", "").upper() in ("MPEG4", "H.264", "MP4")
                    or f.get("name", "").lower().endswith(".mp4")
                ]
                return {
                    "exists": True,
                    "identifier": identifier,
                    "title": data.get("metadata", {}).get("title", "Unknown"),
                    "files": mp4_files,
                    "all_files": data.get("files", [])
                }
    except (urllib.error.HTTPError, urllib.error.URLError):
        pass
    except Exception as e:
        log(f"  ⚠️ Fehler bei {identifier}: {e}")
    return {"exists": False}


def download_file(url, dest_path, max_retries=3):
    """Lädt eine Datei herunter mit Fortschrittsanzeige"""
    if os.path.exists(dest_path):
        existing_size = os.path.getsize(dest_path)
        if existing_size > 1_000_000:  # > 1MB = wahrscheinlich komplett
            log(f"  ⏭️ Übersprungen (existiert: {existing_size/1024/1024:.1f} MB): {os.path.basename(dest_path)}")
            return True
    
    for attempt in range(max_retries):
        try:
            log(f"  📥 Download: {os.path.basename(dest_path)} (Versuch {attempt+1})")
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            with urllib.request.urlopen(req, timeout=300) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                
                with open(dest_path, "wb") as f:
                    while True:
                        chunk = resp.read(8192 * 16)  # 128KB chunks
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total > 0:
                            pct = downloaded / total * 100
                            mb = downloaded / 1024 / 1024
                            total_mb = total / 1024 / 1024
                            if downloaded % (8192 * 128) < 8192 * 16:  # Alle ~16MB Status
                                print(f"\r    {pct:.1f}% ({mb:.1f}/{total_mb:.1f} MB)", end="", flush=True)
                
                print()  # Newline
                final_size = os.path.getsize(dest_path)
                log(f"  ✅ Fertig: {final_size/1024/1024:.1f} MB")
                return True
                
        except Exception as e:
            log(f"  ❌ Fehler (Versuch {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    
    return False


def search_episode_on_archive(nr):
    """Sucht eine Episode mit verschiedenen Identifier-Patterns"""
    log(f"🔍 Suche Nr. {nr} auf Archive.org...")
    
    for i, pattern_fn in enumerate(SEARCH_PATTERNS):
        try:
            url = pattern_fn(nr)
            if url is None:
                continue
            
            # Identifier aus URL extrahieren
            identifier = url.split("/metadata/")[-1]
            result = check_archive_identifier(identifier)
            
            if result["exists"] and result.get("files"):
                log(f"  🎉 GEFUNDEN via Pattern {i+1}: {identifier}")
                log(f"     Titel: {result.get('title', 'N/A')}")
                log(f"     MP4-Dateien: {len(result['files'])}")
                return result
        except Exception as e:
            pass
    
    # API-Suche als Fallback
    series = "UfA-Tonwoche" if nr < 511 else "Deutsche Wochenschau"
    search_queries = [
        f'title:("{series}" AND "{nr}")',
        f'description:("Nr. {nr}" AND ("Wochenschau" OR "Tonwoche"))',
        f'("{series}" AND "Nr. {nr}")',
        f'(wochenschau AND {nr})',
    ]
    
    for query in search_queries:
        try:
            api_url = (
                f"https://archive.org/advancedsearch.php?"
                f"q={urllib.parse.quote(query)}+AND+mediatype:movies"
                f"&fl=identifier,title&rows=5&output=json"
            )
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("response", {}).get("docs", [])
                
                for doc in docs:
                    ident = doc.get("identifier", "")
                    title = doc.get("title", "")
                    # Prüfe ob Nummer im Titel/Identifier vorkommt
                    if str(nr) in title or str(nr) in ident:
                        check = check_archive_identifier(ident)
                        if check["exists"] and check.get("files"):
                            log(f"  🎉 GEFUNDEN via API-Suche: {ident}")
                            return check
            time.sleep(0.5)  # Rate limiting
        except Exception:
            pass
    
    log(f"  ❌ Nr. {nr} nicht auf Archive.org gefunden")
    return None


def download_known_episodes(dest_dir):
    """Lädt die 5 bekannten freien Episoden herunter"""
    log("=" * 70)
    log("📥 PHASE 1: Bekannte freie Episoden herunterladen")
    log("=" * 70)
    
    results = {"success": [], "failed": [], "skipped": []}
    
    for nr, info in KNOWN_SOURCES.items():
        identifier = info["identifier"]
        log(f"\n--- Nr. {nr} ({info['note']}) ---")
        
        if info["files"] == [None]:
            # Einzeldatei - automatisch MP4 finden
            meta = check_archive_identifier(identifier)
            if meta["exists"] and meta.get("files"):
                for f in meta["files"]:
                    fname = f.get("name", "")
                    if fname.lower().endswith(".mp4"):
                        url = f"https://archive.org/download/{identifier}/{urllib.parse.quote(fname)}"
                        dest = os.path.join(dest_dir, f"Wochenschau_Nr{nr}.mp4")
                        if download_file(url, dest):
                            results["success"].append(nr)
                        else:
                            results["failed"].append(nr)
                        break
            else:
                # Direkt-Download versuchen
                url = f"https://archive.org/download/{identifier}/"
                log(f"  ⚠️ Metadata nicht abrufbar, versuche Direkt-Download...")
                # Versuche gängige Dateinamen
                for ext_name in [
                    f"19410219DieDeutscheWochenschauNr.54623m14s640x480.mp4",
                    f"19410219%20Die%20Deutsche%20Wochenschau%20Nr.%20546%20%2823m%2014s%2C%20640x480%29.mp4"
                ]:
                    try:
                        dest = os.path.join(dest_dir, f"Wochenschau_Nr{nr}.mp4")
                        dl_url = f"https://archive.org/download/{identifier}/{ext_name}"
                        if download_file(dl_url, dest):
                            results["success"].append(nr)
                            break
                    except:
                        continue
                else:
                    results["failed"].append(nr)
        else:
            # Spezifische Dateien aus Kompilation
            for fname in info["files"]:
                encoded = urllib.parse.quote(fname)
                url = f"https://archive.org/download/{identifier}/{encoded}"
                safe_name = fname.replace(" ", "_").replace(".", "_")
                dest = os.path.join(dest_dir, f"Wochenschau_Nr{nr}_{safe_name}.mp4")
                if download_file(url, dest):
                    if nr not in results["success"]:
                        results["success"].append(nr)
                else:
                    if nr not in results["failed"]:
                        results["failed"].append(nr)
    
    return results


def search_and_download_missing(dest_dir, already_found):
    """Sucht und lädt alle noch fehlenden Episoden"""
    log("\n" + "=" * 70)
    log("🔍 PHASE 2: Fehlende Episoden suchen auf Archive.org")
    log("=" * 70)
    
    still_missing = [nr for nr in MISSING_EPISODES if nr not in already_found]
    results = {"found": [], "downloaded": [], "not_found": []}
    
    for i, nr in enumerate(still_missing):
        log(f"\n[{i+1}/{len(still_missing)}] Suche Nr. {nr}...")
        
        found = search_episode_on_archive(nr)
        
        if found and found.get("files"):
            results["found"].append(nr)
            
            # Download versuchen
            for f in found["files"]:
                fname = f.get("name", "")
                if not fname.lower().endswith(".mp4"):
                    continue
                    
                url = f"https://archive.org/download/{found['identifier']}/{urllib.parse.quote(fname)}"
                dest = os.path.join(dest_dir, f"Wochenschau_Nr{nr}_{fname.replace(' ', '_')}")
                if not dest.lower().endswith(".mp4"):
                    dest += ".mp4"
                    
                if download_file(url, dest):
                    results["downloaded"].append(nr)
                    break
        else:
            results["not_found"].append(nr)
        
        # Rate limiting: 1 Sekunde zwischen Suchen
        time.sleep(1)
    
    return results


def search_compilations_for_missing(dest_dir, still_missing):
    """Durchsucht Archive.org Kompilationen nach fehlenden Episoden"""
    log("\n" + "=" * 70)
    log("📦 PHASE 3: Kompilationen durchsuchen")
    log("=" * 70)
    
    # Bekannte Kompilationen und ihre Bereiche
    compilations = [
        {
            "identifier": "diedeutschewochenschau646.2",
            "range": (642, 668),
            "title": "1943 Part 1"
        },
        {
            "identifier": "diedeutschewochenschau674_201907",
            "range": (669, 695),
            "title": "1943 Part 2"
        },
        {
            "identifier": "DieDeutscheWochenschauNr747",
            "range": (696, 746),
            "title": "1944"
        },
        {
            "identifier": "DieDeutscheWochenschauNr748January111945",
            "range": (748, 755),
            "title": "1945"
        },
        {
            "identifier": "diedeutschewochenschau_202011",
            "range": None,
            "title": "Unknown compilation 2020"
        },
        {
            "identifier": "diedeutschewochenschaudasostfront_201910",
            "range": None,
            "title": "Ostfront compilation"
        },
        {
            "identifier": "diedeutschewochenschaudasostfront_20191024",
            "range": None,
            "title": "Ostfront compilation 2"
        },
    ]
    
    results = {"found_in_compilations": []}
    
    for comp in compilations:
        # Prüfe ob fehlende Nummern im Bereich liegen
        relevant = []
        if comp["range"]:
            relevant = [nr for nr in still_missing 
                       if comp["range"][0] <= nr <= comp["range"][1]]
        
        if not relevant and comp["range"]:
            continue
            
        log(f"\n📦 Prüfe: {comp['identifier']} ({comp['title']})")
        
        meta = check_archive_identifier(comp["identifier"])
        if not meta["exists"]:
            log(f"  ❌ Nicht erreichbar")
            continue
        
        # Alle Dateien durchgehen und nach Nummern suchen
        all_files = meta.get("all_files", [])
        mp4_files = [f for f in all_files 
                    if f.get("name", "").lower().endswith(".mp4")]
        
        log(f"  📁 {len(mp4_files)} MP4-Dateien gefunden")
        
        for f in mp4_files:
            fname = f.get("name", "")
            # Episodennummer aus Dateiname extrahieren
            for nr in still_missing:
                nr_str = str(nr)
                # Verschiedene Namensmuster prüfen
                if (f"wochenschau {nr_str}" in fname.lower() or
                    f"wochenschau_{nr_str}" in fname.lower() or
                    f"nr.{nr_str}" in fname.lower() or
                    f"nr{nr_str}" in fname.lower() or
                    f"nr. {nr_str}" in fname.lower() or
                    fname.lower().strip() == f"{nr_str}.mp4"):
                    
                    log(f"  🎉 Nr. {nr} gefunden: {fname}")
                    results["found_in_compilations"].append({
                        "nr": nr,
                        "identifier": comp["identifier"],
                        "filename": fname,
                        "size": f.get("size", "unknown")
                    })
                    
                    # Sofort herunterladen
                    url = f"https://archive.org/download/{comp['identifier']}/{urllib.parse.quote(fname)}"
                    dest = os.path.join(dest_dir, f"Wochenschau_Nr{nr}.mp4")
                    download_file(url, dest)
        
        time.sleep(1)
    
    return results


def search_nara_ushmm(still_missing):
    """Sucht auf NARA und USHMM nach fehlenden Episoden"""
    log("\n" + "=" * 70)
    log("🏛️ PHASE 4: NARA/USHMM Archive durchsuchen")  
    log("=" * 70)
    
    results = {"nara_found": [], "ushmm_found": []}
    
    # NARA Record Group 242 Suche über Archive.org
    for nr in still_missing[:10]:  # Erste 10 testen
        series = "UfA Tonwoche" if nr < 511 else "Deutsche Wochenschau"
        query = f'("Record Group 242" OR "RG 242" OR "NARA") AND ("{series}" OR "Wochenschau") AND "{nr}"'
        
        try:
            api_url = (
                f"https://archive.org/advancedsearch.php?"
                f"q={urllib.parse.quote(query)}+AND+mediatype:movies"
                f"&fl=identifier,title,description&rows=5&output=json"
            )
            req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    for doc in docs:
                        log(f"  🏛️ NARA/USHMM Treffer für Nr. {nr}: {doc.get('title', 'N/A')}")
                        results["nara_found"].append({
                            "nr": nr,
                            "identifier": doc.get("identifier"),
                            "title": doc.get("title")
                        })
        except Exception:
            pass
        time.sleep(0.5)
    
    return results


def generate_report(dest_dir, all_results):
    """Erstellt Abschlussbericht"""
    log("\n" + "=" * 70)
    log("📊 ABSCHLUSSBERICHT")
    log("=" * 70)
    
    # Sammle alle erfolgreichen Downloads
    downloaded = set()
    if "known" in all_results:
        downloaded.update(all_results["known"].get("success", []))
    if "search" in all_results:
        downloaded.update(all_results["search"].get("downloaded", []))
    
    found_not_dl = set()
    if "search" in all_results:
        found_not_dl.update(all_results["search"].get("found", []))
        found_not_dl -= downloaded
    
    not_found = set(MISSING_EPISODES) - downloaded - found_not_dl
    
    log(f"\n📊 ERGEBNIS:")
    log(f"   ✅ Heruntergeladen:  {len(downloaded)}")
    log(f"   🟡 Gefunden/pending: {len(found_not_dl)}")
    log(f"   ❌ Nicht gefunden:   {len(not_found)}")
    log(f"   📁 Zielordner:      {dest_dir}")
    
    if downloaded:
        log(f"\n   ✅ Erfolgreiche Downloads: {sorted(downloaded)}")
    if not_found:
        log(f"\n   ❌ Noch fehlend: {sorted(not_found)}")
    
    # Dateien im Zielordner auflisten
    log(f"\n📁 Dateien in {dest_dir}:")
    if os.path.exists(dest_dir):
        new_files = [f for f in os.listdir(dest_dir) if "Wochenschau_Nr" in f]
        for f in sorted(new_files):
            size = os.path.getsize(os.path.join(dest_dir, f))
            log(f"   {f} ({size/1024/1024:.1f} MB)")
    
    # Report als JSON speichern
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_missing": len(MISSING_EPISODES),
        "downloaded": sorted(downloaded),
        "found_not_downloaded": sorted(found_not_dl),
        "not_found": sorted(not_found),
        "download_dir": dest_dir,
        "details": all_results
    }
    
    report_path = os.path.join(os.path.dirname(LOG_FILE), "..", "config", "wochenschau_download_result.json")
    report_path = os.path.normpath(report_path)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    log(f"\n📄 Report gespeichert: {report_path}")
    
    return report


def main():
    log("🎬 WOCHENSCHAU BULK DOWNLOADER gestartet")
    log(f"   Fehlende Episoden: {len(MISSING_EPISODES)}")
    log(f"   Bekannte Quellen: {len(KNOWN_SOURCES)}")
    
    dest_dir = get_download_dir()
    log(f"   Zielordner: {dest_dir}")
    
    all_results = {}
    
    # Phase 1: Bekannte freie Episoden herunterladen
    all_results["known"] = download_known_episodes(dest_dir)
    
    already_found = set(all_results["known"].get("success", []))
    
    # Phase 2: Kompilationen durchsuchen
    still_missing = [nr for nr in MISSING_EPISODES if nr not in already_found]
    all_results["compilations"] = search_compilations_for_missing(dest_dir, still_missing)
    
    # Update already_found
    for item in all_results["compilations"].get("found_in_compilations", []):
        already_found.add(item["nr"])
    
    # Phase 3: Einzeln suchen
    still_missing = [nr for nr in MISSING_EPISODES if nr not in already_found]
    if still_missing:
        all_results["search"] = search_and_download_missing(dest_dir, already_found)
        for nr in all_results["search"].get("downloaded", []):
            already_found.add(nr)
    
    # Phase 4: NARA/USHMM
    still_missing = [nr for nr in MISSING_EPISODES if nr not in already_found]
    if still_missing:
        all_results["nara"] = search_nara_ushmm(still_missing)
    
    # Abschlussbericht
    report = generate_report(dest_dir, all_results)
    
    log("\n🏁 FERTIG!")
    return report


if __name__ == "__main__":
    main()
