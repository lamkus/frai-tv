#!/usr/bin/env python3
"""
Wochenschau Title Optimization - YouTube SEO 2026
=================================================
Problem: Alle 252 Titel sind 91 Zeichen (sollten <60 sein!)
Lösung: Neue Kurzformat mit Event-Keywords

AKTUELLES FORMAT (91 chars):
"Die Deutsche Wochenschau Nr. 459 | 21.06.1939 | Germany WWII Newsreel | 8K HQ | @remAIke_IT"

NEUES FORMAT (~50-55 chars):
"Wochenschau 459: Pre-War Era (June 1939) | 8K"

Warum:
- YouTube truncates bei 60-70 chars
- @remAIke_IT erscheint sowieso als Channel-Name
- "Germany WWII Newsreel" → im Description besser aufgehoben
- "HQ" → redundant bei 8K
- Event-Keyword → SEO + Clickbait!
"""

import json
import os
from datetime import datetime

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_FILE = os.path.join(BASE_DIR, "config", "wochenschau_events.json")
UPLOAD_DATA = os.path.join(BASE_DIR, "config", "wochenschau_upload_data_FIXED.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "config", "wochenschau_titles_optimized.json")

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
    
    Format: "Wochenschau [NR]: [Event] ([Mon YYYY]) | 8K"
    Target: 50-55 chars
    """
    short_date = format_date_short(date_str)
    
    # Basis-Titel
    title = f"Wochenschau {nr}: {event_en} ({short_date}) | 8K"
    
    # Falls zu lang (>60), kürze Event
    if len(title) > 60:
        # Versuche kürzere Event-Variante
        if " of " in event_en:
            event_short = event_en.replace(" of ", " ")
            title = f"Wochenschau {nr}: {event_short} ({short_date}) | 8K"
        elif " Continues" in event_en:
            event_short = event_en.replace(" Continues", "")
            title = f"Wochenschau {nr}: {event_short} ({short_date}) | 8K"
    
    return title

def analyze_and_optimize():
    """Hauptanalyse und Optimierung"""
    events = load_events()
    upload_data = load_upload_data()
    
    print("=" * 70)
    print("🎬 WOCHENSCHAU TITLE OPTIMIZATION - YouTube SEO 2026")
    print("=" * 70)
    
    results = {
        "meta": {
            "created": datetime.now().isoformat(),
            "purpose": "Optimized titles for YouTube SEO 2026",
            "target_length": "50-55 chars (max 60)",
            "format": "Wochenschau [NR]: [Event] ([Mon YYYY]) | 8K"
        },
        "statistics": {},
        "titles": {}
    }
    
    total = 0
    with_events = 0
    under_60 = 0
    under_55 = 0
    
    for video in upload_data:
        nr = video.get('video_nr', '')
        if not nr:
            continue
            
        total += 1
        current_title = video.get('title', '')
        date_str = video.get('date', '')
        
        # Hole Event wenn vorhanden
        event_data = events.get(str(nr), {})
        event_en = event_data.get('event_en', 'WWII Germany')
        
        if event_data:
            with_events += 1
        
        # Erstelle optimierten Titel
        new_title = create_optimized_title(nr, event_en, date_str)
        new_len = len(new_title)
        
        if new_len <= 60:
            under_60 += 1
        if new_len <= 55:
            under_55 += 1
        
        results["titles"][str(nr)] = {
            "current_title": current_title,
            "current_length": len(current_title),
            "new_title": new_title,
            "new_length": new_len,
            "event_en": event_en,
            "date": date_str,
            "savings": len(current_title) - new_len
        }
    
    # Statistiken
    avg_new = 0
    if results["titles"]:
        avg_new = sum(t["new_length"] for t in results["titles"].values()) / len(results["titles"])
    
    results["statistics"] = {
        "total_videos": total,
        "videos_with_events": with_events,
        "videos_without_events": total - with_events,
        "new_titles_under_60": under_60,
        "new_titles_under_55": under_55,
        "avg_current_length": 91,  # Alle sind 91
        "avg_new_length": avg_new
    }
    
    # Speichern
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Ausgabe
    print(f"\n📊 STATISTIK:")
    print(f"   Videos total:          {total}")
    print(f"   Mit Event-Daten:       {with_events} ({with_events/total*100:.1f}%)")
    print(f"   Ohne Event-Daten:      {total - with_events}")
    print(f"\n📏 TITEL-LÄNGEN:")
    print(f"   Aktuelle Länge:        91 chars (ALLE!)")
    print(f"   Neue Länge (Ø):        {results['statistics']['avg_new_length']:.1f} chars")
    print(f"   Unter 60 chars:        {under_60} ({under_60/total*100:.1f}%)")
    print(f"   Unter 55 chars:        {under_55} ({under_55/total*100:.1f}%)")
    print(f"   Ersparnis:             ~{91 - results['statistics']['avg_new_length']:.0f} chars pro Titel!")
    
    # Beispiele zeigen
    print(f"\n📝 BEISPIELE (Vorher → Nachher):")
    print("-" * 70)
    
    sample_nrs = ["459", "470", "473", "508", "511", "515", "523", "553"]
    for nr in sample_nrs:
        if nr in results["titles"]:
            t = results["titles"][nr]
            print(f"\n   Nr. {nr}:")
            print(f"   VORHER ({t['current_length']} chars):")
            print(f"   {t['current_title'][:70]}...")
            print(f"   NACHHER ({t['new_length']} chars):")
            print(f"   {t['new_title']}")
            print(f"   Event: {t['event_en']}")
    
    print(f"\n✅ Ergebnis gespeichert: {OUTPUT_FILE}")
    
    return results

if __name__ == "__main__":
    analyze_and_optimize()
