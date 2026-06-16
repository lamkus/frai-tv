#!/usr/bin/env python3
"""
🏷️ SMART TAG OPTIMIZER - Nur ergänzende Tags!
=============================================
Tags sollten NICHT wiederholen was in Title/Description steht.
Stattdessen: Schreibvarianten, Synonyme, Fremdsprachen.
"""

import json
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")
OUTPUT = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")

# =============================================================================
# SMART TAGS - Ergänzend, nicht doppelt!
# =============================================================================

# Basis-Tags (Schreibvarianten für "Wochenschau")
BASE_SPELLING_VARIANTS = [
    "Wochenschau",           # DE korrekt
    "Deutsche Wochenschau",  # Vollständig
    "German Newsreel",       # EN
    "newsreel",              # EN kurz
    "WWII newsreel",         # Kombination
    "WW2 footage",           # Alternative Schreibweise
    "World War 2",           # Ausgeschrieben
    "World War II",          # Römisch
]

# Synonyme für "Zweiter Weltkrieg" (verschiedene Sprachen/Schreibweisen)
WAR_SYNONYMS = [
    "Segunda Guerra Mundial",  # ES/PT
    "Seconde Guerre mondiale", # FR
    "Вторая мировая война",    # RU
    "第二次世界大戦",            # JA
    "二战",                    # ZH simplified
]

# Channel/Quality Tags (immer dabei)
CHANNEL_TAGS = [
    "remAIke",
    "8K upscale", 
    "AI enhanced",
    "restored footage",
    "public domain",
]

# Event-spezifische Synonym-Tags
EVENT_SYNONYMS = {
    "Pre-War Era": ["prewar", "Vorkriegszeit", "1939 Germany", "Nazi Germany 1939"],
    "Nazi-Soviet Pact": ["Molotov-Ribbentrop", "Hitler-Stalin Pact", "non-aggression pact", "Nichtangriffspakt"],
    "War Begins": ["September 1939", "Kriegsbeginn", "outbreak of war", "invasion of Poland"],
    "Poland Campaign": ["Fall Weiss", "Case White", "Polenfeldzug", "German invasion Poland"],
    "Fall of Warsaw": ["Warsaw 1939", "Warschau", "Polish surrender", "siege of Warsaw"],
    "Battle of Britain": ["Luftschlacht England", "RAF vs Luftwaffe", "Blitz London"],
    "Operation Barbarossa": ["Unternehmen Barbarossa", "invasion Soviet Union", "Ostfront", "Eastern Front"],
    "Stalingrad": ["Schlacht Stalingrad", "6th Army", "Paulus surrender"],
    "D-Day": ["Normandy invasion", "Operation Overlord", "6 June 1944", "Landung Normandie"],
    "Afrika Korps": ["North Africa campaign", "Rommel", "Desert Fox", "Afrikafeldzug"],
    "Pearl Harbor": ["December 1941", "Hawaii attack", "US enters war"],
    "Blitzkrieg": ["lightning war", "mobile warfare", "Panzer tactics"],
}

def get_smart_tags(video_data, title, description):
    """
    Generiere SMART Tags die Title/Description ERGÄNZEN.
    Keine Duplikate!
    """
    tags = []
    
    # 1. Basis Schreibvarianten (immer)
    tags.extend(BASE_SPELLING_VARIANTS[:5])  # Top 5
    
    # 2. Krieg-Synonyme in anderen Sprachen
    tags.extend(WAR_SYNONYMS[:3])  # Top 3
    
    # 3. Channel Tags
    tags.extend(CHANNEL_TAGS)
    
    # 4. Event-spezifische Synonyme
    event_en = video_data.get('event_en', '')
    if event_en in EVENT_SYNONYMS:
        # Nur Tags die NICHT schon im Title/Description sind
        for syn in EVENT_SYNONYMS[event_en]:
            if syn.lower() not in title.lower() and syn.lower() not in description.lower():
                tags.append(syn)
    
    # 5. Jahr als Tag (wenn nicht im Title)
    year = video_data.get('year', '')
    if year and str(year) not in title:
        tags.append(str(year))
        tags.append(f"{year} footage")
    
    # 6. Nummer-Varianten
    nr = video_data.get('nr', '')
    if nr:
        tags.append(f"Wochenschau {nr}")
        tags.append(f"Newsreel #{nr}")
    
    # Deduplizieren und limitieren
    seen = set()
    unique_tags = []
    for tag in tags:
        lower = tag.lower().strip()
        if lower not in seen and len(tag) >= 2:
            seen.add(lower)
            unique_tags.append(tag)
    
    # Max 20 Tags (YouTube Best Practice)
    return unique_tags[:20]

def main():
    print("=" * 70)
    print("🏷️  SMART TAG OPTIMIZER")
    print("    Tags die Title/Description ERGÄNZEN, nicht wiederholen!")
    print("=" * 70)
    
    # Laden
    with open(DATABASE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    stats = {
        "old_avg": 0,
        "new_avg": 0,
        "videos_updated": 0
    }
    
    old_total = 0
    new_total = 0
    
    for nr, video in db["videos"].items():
        old_tags = video.get('tags', [])
        old_total += len(old_tags)
        
        # Smart Tags generieren
        new_tags = get_smart_tags(
            video, 
            video.get('title', ''),
            video.get('description', '')
        )
        
        new_total += len(new_tags)
        
        # Update
        video['tags'] = new_tags
        video['tags_count'] = len(new_tags)
        stats["videos_updated"] += 1
    
    stats["old_avg"] = old_total / len(db["videos"])
    stats["new_avg"] = new_total / len(db["videos"])
    
    # Metadata updaten (falls vorhanden)
    if "metadata" not in db:
        db["metadata"] = {}
    db["metadata"]["tags_strategy"] = "smart_complementary"
    db["metadata"]["tags_updated"] = datetime.now().isoformat()
    db["metadata"]["avg_tags_count"] = round(stats["new_avg"], 1)
    
    # Speichern
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 ERGEBNIS:")
    print(f"   Videos aktualisiert: {stats['videos_updated']}")
    print(f"   Tags vorher: Ø {stats['old_avg']:.1f} pro Video")
    print(f"   Tags nachher: Ø {stats['new_avg']:.1f} pro Video")
    print(f"   Reduktion: -{100 - (stats['new_avg']/stats['old_avg']*100):.0f}%")
    print(f"\n✅ Gespeichert: {OUTPUT}")
    
    # Beispiel zeigen
    print(f"\n" + "=" * 70)
    print("📋 BEISPIEL (Nr. 459):")
    example = db["videos"]["459"]
    print(f"   Title: {example['title']}")
    print(f"   Tags ({len(example['tags'])}):")
    for tag in example['tags']:
        print(f"      • {tag}")

if __name__ == "__main__":
    main()
