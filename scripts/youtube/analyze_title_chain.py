#!/usr/bin/env python3
"""
TITEL-KETTEN-ANALYSE: Prüft ob alle Namensgebungen konsistent und international optimiert sind
"""

import json

def analyze_titles():
    print("=" * 80)
    print("🔍 TITEL-KETTEN-ANALYSE: Wochenschau SEO")
    print("=" * 80)
    
    # Lade FIXED Daten
    with open('config/wochenschau_upload_data_FIXED.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data if isinstance(data, list) else data.get('videos', [])
    print(f"\n📊 {len(videos)} Videos in Datenbank\n")
    
    # Analysiere Titel-Struktur
    print("=" * 80)
    print("📋 AKTUELLE TITEL-STRUKTUR (Sample)")
    print("=" * 80)
    
    lengths = []
    issues = []
    
    for v in videos[:15]:
        title = v.get('title', '')
        nr = v.get('video_nr', '?')
        date = v.get('date', '?')
        lengths.append(len(title))
        
        # Prüfe auf Probleme
        problems = []
        if len(title) > 60:
            problems.append(f"⚠️ {len(title)} chars (>60)")
        if len(title) > 70:
            problems.append("🔴 ABGESCHNITTEN auf Mobile!")
        if "8K HQ" not in title:
            problems.append("❌ 8K HQ fehlt")
        if "@remAIke_IT" not in title:
            problems.append("❌ Brand fehlt")
        if "Germany WWII Newsreel" not in title and "German Newsreel" not in title:
            problems.append("❌ EN Keyword fehlt")
        
        status = " | ".join(problems) if problems else "✅ OK"
        print(f"Nr.{nr:>4} | {len(title):>2}c | {title[:55]}...")
        if problems:
            print(f"         └── {status}")
            issues.append((nr, problems))
    
    print()
    print("=" * 80)
    print("📊 STATISTIK")
    print("=" * 80)
    print(f"   Kürzester Titel: {min(lengths)} Zeichen")
    print(f"   Längster Titel:  {max(lengths)} Zeichen")
    print(f"   Durchschnitt:    {sum(lengths)/len(lengths):.0f} Zeichen")
    print(f"   YouTube Max:     60 Zeichen (empfohlen)")
    print()
    
    over_60 = sum(1 for l in lengths if l > 60)
    over_70 = sum(1 for l in lengths if l > 70)
    print(f"   ⚠️  Videos > 60 Zeichen: {over_60}/{len(lengths)} ({over_60/len(lengths)*100:.0f}%)")
    print(f"   🔴 Videos > 70 Zeichen: {over_70}/{len(lengths)} ({over_70/len(lengths)*100:.0f}%)")
    
    # Zeige aktuellen Titel-Aufbau
    print()
    print("=" * 80)
    print("🏗️ AKTUELLER TITEL-AUFBAU")
    print("=" * 80)
    sample = videos[0]['title']
    print(f"\n   AKTUELL: {sample}")
    print(f"   LÄNGE:   {len(sample)} Zeichen")
    print()
    
    # Zerlege Titel in Komponenten
    parts = sample.split(" | ")
    print("   KOMPONENTEN:")
    for i, part in enumerate(parts, 1):
        print(f"     {i}. {part} ({len(part)} chars)")
    
    print()
    print("=" * 80)
    print("🌍 INTERNATIONALE TITEL-ALTERNATIVEN")
    print("=" * 80)
    
    # Zeige alternative Formate
    nr = videos[0].get('video_nr', '459')
    date = videos[0].get('date', '1939-06-21')
    date_parts = date.split('-')
    date_de = f"{date_parts[2]}.{date_parts[1]}.{date_parts[0]}"
    year = date_parts[0]
    
    alternatives = [
        # Aktuell
        (f"Die Deutsche Wochenschau Nr. {nr} | {date_de} | Germany WWII Newsreel | 8K HQ | @remAIke_IT", "AKTUELL"),
        
        # Kürzer - Keyword First
        (f"Wochenschau {nr} ({date_de}) | WWII German Newsreel 8K | @remAIke_IT", "Option A: Keyword First"),
        
        # Noch kürzer
        (f"Wochenschau Nr. {nr} | {date_de} | 8K HQ | @remAIke_IT", "Option B: Kompakt"),
        
        # International Focus
        (f"German Newsreel {nr} ({year}) | Deutsche Wochenschau 8K | @remAIke_IT", "Option C: EN First"),
        
        # Ultra-kurz für Mobile
        (f"Wochenschau {nr} ({date_de}) | 8K @remAIke_IT", "Option D: Ultra-Kompakt"),
        
        # Mit Event (wenn bekannt)
        (f"Wochenschau: Pre-War Era ({date_de}) | WWII 8K | @remAIke_IT", "Option E: Event-Based"),
    ]
    
    print()
    for title, label in alternatives:
        status = "✅" if len(title) <= 60 else ("⚠️" if len(title) <= 70 else "🔴")
        print(f"   {status} {len(title):>2}c | {label}")
        print(f"        {title}")
        print()
    
    print("=" * 80)
    print("📝 EMPFEHLUNG")
    print("=" * 80)
    print("""
    PROBLEM: Aktuelle Titel sind 80+ Zeichen = werden auf Mobile abgeschnitten!
    
    LÖSUNG - Priorisierte Reihenfolge:
    
    1. KEYWORD FIRST: "Wochenschau" oder "German Newsreel" am ANFANG
       → 90% der Top-Videos haben Keyword vorne (ahrefs Study)
    
    2. UNIQUE IDENTIFIER: Nr. + Datum
       → Für Archiv-Content essentiell
    
    3. QUALITY BADGE: "8K" 
       → Differentiator zu anderen Channels
    
    4. BRAND: "@remAIke_IT"
       → Am Ende ist OK
    
    EMPFOHLENES FORMAT (55-60 chars):
    ┌────────────────────────────────────────────────────────────┐
    │ Wochenschau Nr. XXX (DD.MM.YYYY) | 8K HQ | @remAIke_IT    │
    └────────────────────────────────────────────────────────────┘
    
    BEISPIEL:
    "Wochenschau Nr. 459 (21.06.1939) | 8K HQ | @remAIke_IT"
    = 53 Zeichen ✅
    
    ALTERNATIV für International (EN First):
    "German Newsreel 459 (1939) | Deutsche Wochenschau 8K | @remAIke"
    = 63 Zeichen ⚠️ (knapp)
""")

if __name__ == "__main__":
    analyze_titles()
