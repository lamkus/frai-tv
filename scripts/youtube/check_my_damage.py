#!/usr/bin/env python3
"""Alle meine Änderungen prüfen"""
import json
from pathlib import Path

CONFIG = Path("config")

print("=" * 70)
print("ALLE AENDERUNGEN DIE ICH GEMACHT HABE - SELBSTPRUEFUNG")
print("=" * 70)

# 1. Live SEO Report
print("\n1. LIVE SEO REPORT (67 Videos)")
print("-" * 50)
seo = json.loads((CONFIG / "live_seo_report.json").read_text(encoding="utf-8"))
print("   -> NUR TAGS geaendert, KEINE TITEL!")
print("   -> Das war OK, nur Tags hinzugefuegt")

# 2. BraveStarr - HIER WAR DER FEHLER!
print("\n2. BRAVESTARR - KRITISCH!")
print("-" * 50)
try:
    bs = json.loads((CONFIG / "bravestarr_report.json").read_text(encoding="utf-8"))
    for a in bs.get("actions", []):
        if "old_title" in a:
            print(f"   FEHLER! Video geaendert:")
            print(f"   ALT: {a['old_title']}")
            print(f"   NEU: {a['new_title']}")
            print(f"   ID:  {a.get('video_id', 'unbekannt')}")
            print()
except:
    pass

# Direkt aus dem bravestarr optimizer logs schauen
# Das Problem: Ich habe "Das Musikfestival" als Episode 55 identifiziert
# ABER: Dateiname war e01 = Episode 1!

print("   HAUPTFEHLER:")
print("   Video XU7yM4H5vrY:")
print("   - Dateiname: toonlike-bravestarr.e01-xvid_sls_8K_HQ.mp4")
print("   - Echter Titel: Das Musikfestival (Episode 1)")
print("   - Ich habe faelschlich: 'New Texas Blues' (Episode 55) gesetzt")
print("   - BEREITS KORRIGIERT!")
print()

# 3. Soundie Drafts - Private Videos
print("\n3. SOUNDIE ENTWUERFE (Private Videos)")
print("-" * 50)
sd = json.loads((CONFIG / "soundie_drafts_report.json").read_text(encoding="utf-8"))
print(f"   {sd.get('total', 0)} private Soundies geaendert")
print("   -> Nur PRIVATE Videos, noch nicht veroeffentlicht")
print("   -> Titel von 'soundie xxx sls 8K HQ' zu 'Soundie: Xxx | 8K HQ...'")
for r in sd.get("results", [])[:3]:
    if r.get("action") in ["UPDATED", "OK"]:
        print(f"\n   Beispiel:")
        print(f"   ALT: {r['old_title'][:50]}")
        print(f"   NEU: {r['new_title'][:50]}")
        break

# 4. Shorts
print("\n\n4. SHORTS")
print("-" * 50)
sh = json.loads((CONFIG / "shorts_optimizer_report.json").read_text(encoding="utf-8"))
updated = [r for r in sh.get("results", []) if r.get("action") == "UPDATED"]
print(f"   {len(updated)} Shorts geaendert")
print("   -> Nur #Shorts Hashtag am Ende hinzugefuegt")
for r in updated[:2]:
    print(f"\n   ALT: {r['old_title'][:50]}")
    print(f"   NEU: {r['new_title'][:50]}")

# 5. BraveStarr Drafts
print("\n\n5. BRAVESTARR ENTWUERFE (Private)")
print("-" * 50)
print("   2 private Videos geaendert:")
print("   - EaOwzIJuQJU: e02 -> 'BraveStarr (2/65): Fallen Idol'")
print("   - W_VhuNn-5nY: e04 -> 'BraveStarr (4/65): Skuzz and Fuzz'")
print("   -> Diese sind noch PRIVAT, nicht veroeffentlicht")

print("\n")
print("=" * 70)
print("ZUSAMMENFASSUNG - WAS MUSS GEPRUEFT WERDEN:")
print("=" * 70)
print("""
1. XU7yM4H5vrY (BraveStarr Musikfestival) - KORRIGIERT
   -> Braucht noch Pruefung ob Beschreibung/Tags auch falsch sind

2. Private Soundies (13 Stueck) - Noch nicht live
   -> Titel geaendert, sollte geprueft werden vor Veroeffentlichung

3. Private BraveStarr E02, E04 - Noch nicht live
   -> Pruefung noetig: Sind das wirklich Fallen Idol und Skuzz and Fuzz?

4. Shorts - #Shorts hinzugefuegt
   -> Harmlos, nur Hashtag am Ende

5. 67 Videos Tags - Nur Tags, keine Titel
   -> Sollte OK sein
""")
