#!/usr/bin/env python3
"""
MASTER WOCHENSCHAU TITLE GENERATOR
===================================
Generiert SEO-optimierte Titel für ALLE 252 Wochenschau-Ausgaben (Nr. 459-755)

Wikipedia bestätigt:
- Nr. 459 (Juni 1939) = Erste erhaltene (Ufa-Tonwoche)
- Nr. 511 (Juni 1940) = Erste "Deutsche Wochenschau" (Einheitstitel)
- Nr. 755 (22. März 1945) = Letzte Ausgabe

Format: "Wochenschau [NR]: [Event] ([Mon YYYY]) | 8K"
Target: 50-55 chars (max 60)
"""

import json
import os
from datetime import datetime

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_FILE = os.path.join(BASE_DIR, "config", "wochenschau_events.json")
UPLOAD_DATA = os.path.join(BASE_DIR, "config", "wochenschau_upload_data_FIXED.json")
MASTER_OUTPUT = os.path.join(BASE_DIR, "config", "wochenschau_master_titles.json")

# Monatsnamen EN für kompakte Titel
MONTHS_EN = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
}

def load_events():
    """Lade Event-Daten"""
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('events', {})

def load_upload_data():
    """Lade Upload-Daten"""
    with open(UPLOAD_DATA, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_date_short(date_str):
    """Konvertiere YYYY-MM-DD zu 'Mon YYYY'"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{MONTHS_EN[dt.month]} {dt.year}"
    except:
        return ""

def create_optimized_title(nr, event_en, date_str):
    """
    Erstelle optimierten Titel
    Target: 50-55 chars
    """
    short_date = format_date_short(date_str)
    title = f"Wochenschau {nr}: {event_en} ({short_date}) | 8K"
    
    # Falls zu lang, kürze Event
    if len(title) > 60:
        # Häufige Kürzungen
        replacements = {
            " of ": " ",
            " Continues": "",
            " Offensive": " Off.",
            " Campaign": "",
            " Operation": " Op.",
            "Preparations": "Prep",
        }
        for old, new in replacements.items():
            if old in event_en:
                event_en = event_en.replace(old, new)
                title = f"Wochenschau {nr}: {event_en} ({short_date}) | 8K"
                if len(title) <= 60:
                    break
    
    return title

def generate_master_titles():
    """Generiere Master-Titel-Datei"""
    events = load_events()
    upload_data = load_upload_data()
    
    print("=" * 70)
    print("🎬 MASTER WOCHENSCHAU TITLE GENERATOR")
    print("=" * 70)
    
    # Build upload data lookup by video_nr
    upload_lookup = {v['video_nr']: v for v in upload_data}
    
    master = {
        "_meta": {
            "description": "Master SEO-optimierte Titel für alle Deutsche Wochenschau Ausgaben",
            "format": "Wochenschau [NR]: [Event] ([Mon YYYY]) | 8K",
            "target_length": "50-55 chars (max 60)",
            "total_episodes": "Nr. 459 (Juni 1939) bis Nr. 755 (März 1945)",
            "source": "Wikipedia: https://de.wikipedia.org/wiki/Die_Deutsche_Wochenschau",
            "notes": {
                "ufa_tonwoche": "Nr. 459-510 waren ursprünglich 'Ufa-Tonwoche'",
                "deutsche_wochenschau": "Ab Nr. 511 (Juni 1940) Einheitstitel",
                "last_episode": "Nr. 755 (22.03.1945) - Hitlers letzter öffentlicher Auftritt"
            },
            "created": datetime.now().isoformat(),
            "created_by": "Copilot für remAIke_IT"
        },
        "titles": {}
    }
    
    stats = {
        "total": 0,
        "under_50": 0,
        "under_55": 0,
        "under_60": 0,
        "over_60": 0,
        "with_historical_events": 0,
        "lengths": []
    }
    
    # Iteriere über alle Event-Nummern
    for nr_str, event_data in sorted(events.items(), key=lambda x: int(x[0])):
        nr = int(nr_str)
        date_str = event_data.get('date', '')
        event_en = event_data.get('event_en', 'WWII Germany')
        event_de = event_data.get('event_de', '')
        note = event_data.get('note', '')
        
        # Hole zusätzliche Daten aus Upload-File wenn vorhanden
        upload_info = upload_lookup.get(nr_str, {})
        
        # Generiere optimierten Titel
        new_title = create_optimized_title(nr, event_en, date_str)
        title_len = len(new_title)
        
        stats["total"] += 1
        stats["lengths"].append(title_len)
        
        if title_len <= 50:
            stats["under_50"] += 1
        if title_len <= 55:
            stats["under_55"] += 1
        if title_len <= 60:
            stats["under_60"] += 1
        else:
            stats["over_60"] += 1
        
        # Zähle "wichtige" historische Events
        important_events = ["Battle", "Falls", "Invasion", "Blitz", "Victory", 
                          "Barbarossa", "Stalingrad", "D-Day", "Surrender"]
        if any(e in event_en for e in important_events):
            stats["with_historical_events"] += 1
        
        master["titles"][nr_str] = {
            "number": nr,
            "date": date_str,
            "date_short": format_date_short(date_str),
            "event_de": event_de,
            "event_en": event_en,
            "historical_note": note,
            "is_ufa_tonwoche": nr < 511,
            "optimized_title": new_title,
            "title_length": title_len,
            "old_title": upload_info.get('title', ''),
            "youtube_id": upload_info.get('youtube_id', ''),
            "filename": upload_info.get('filename', '')
        }
    
    # Statistiken
    avg_len = sum(stats["lengths"]) / len(stats["lengths"]) if stats["lengths"] else 0
    master["_meta"]["statistics"] = {
        "total_episodes": stats["total"],
        "avg_title_length": round(avg_len, 1),
        "under_50_chars": stats["under_50"],
        "under_55_chars": stats["under_55"],
        "under_60_chars": stats["under_60"],
        "over_60_chars": stats["over_60"],
        "with_major_events": stats["with_historical_events"],
        "ufa_tonwoche_count": sum(1 for t in master["titles"].values() if t["is_ufa_tonwoche"]),
        "deutsche_wochenschau_count": sum(1 for t in master["titles"].values() if not t["is_ufa_tonwoche"])
    }
    
    # Speichern
    with open(MASTER_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(master, f, indent=2, ensure_ascii=False)
    
    # Ausgabe
    print(f"\n📊 STATISTIK:")
    print(f"   Episoden total:        {stats['total']}")
    print(f"   Ufa-Tonwoche (vor 511): {master['_meta']['statistics']['ufa_tonwoche_count']}")
    print(f"   Deutsche Wochenschau:   {master['_meta']['statistics']['deutsche_wochenschau_count']}")
    print(f"\n📏 TITEL-LÄNGEN:")
    print(f"   Durchschnitt:          {avg_len:.1f} chars")
    print(f"   Unter 50 chars:        {stats['under_50']} ({stats['under_50']/stats['total']*100:.1f}%)")
    print(f"   Unter 55 chars:        {stats['under_55']} ({stats['under_55']/stats['total']*100:.1f}%)")
    print(f"   Unter 60 chars:        {stats['under_60']} ({stats['under_60']/stats['total']*100:.1f}%)")
    print(f"   Über 60 chars:         {stats['over_60']}")
    print(f"\n🎯 WICHTIGE EVENTS:")
    print(f"   Mit Major Events:      {stats['with_historical_events']}")
    
    # Beispiele
    print(f"\n📝 BEISPIEL-TITEL (chronologisch):")
    print("-" * 70)
    
    highlights = ["459", "470", "508", "511", "515", "523", "570", "609", "700", "755"]
    for nr in highlights:
        if nr in master["titles"]:
            t = master["titles"][nr]
            status = "🔵 Ufa-Tonwoche" if t["is_ufa_tonwoche"] else "🟢 Dt. Wochenschau"
            print(f"\n   Nr. {nr} ({t['date_short']}) {status}")
            print(f"   → {t['optimized_title']}")
            print(f"   📖 {t['historical_note']}")
    
    print(f"\n" + "=" * 70)
    print(f"✅ MASTER-DATEI ERSTELLT: {MASTER_OUTPUT}")
    print(f"   {stats['total']} Titel für die komplette Wochenschau-Geschichte!")
    print("=" * 70)
    
    return master

if __name__ == "__main__":
    generate_master_titles()
