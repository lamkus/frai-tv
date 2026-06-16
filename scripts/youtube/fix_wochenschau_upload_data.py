#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 FIX WOCHENSCHAU UPLOAD DATA - NACH ALLEN SEO REGELN
═══════════════════════════════════════════════════════════════════════════════

REGELN (aus Templates):
1. TITEL: Die Deutsche Wochenschau Nr. [NR] | [DD.MM.YYYY] | Germany WWII Newsreel | 8K HQ | @remAIke_IT
2. UFA-TONWOCHE: Videos VOR Juni 1940 (Nr. < 512) brauchen historischen Hinweis
3. DESCRIPTION: Trilingual DE/EN/ES + Historischer Kontext + CTA
4. TAGS: Multilingual (14 Sprachen)

HISTORISCHE FAKTEN:
- Bis Juni 1940: "Ufa-Tonwoche" (und Tobis-Wochenschau, Deulig-Woche etc.)
- Ab Juni 1940: "Die Deutsche Wochenschau" (Zusammenlegung)
- Nr. 512 = erste "Deutsche Wochenschau" (21.06.1940)
"""

import json
import os
from datetime import datetime

INPUT_FILE = "config/wochenschau_upload_data.json"
OUTPUT_FILE = "config/wochenschau_upload_data_FIXED.json"

# Erste "Deutsche Wochenschau" war Nr. 512 vom 21.06.1940
FIRST_DW_NR = 512

# ═══════════════════════════════════════════════════════════════════════════════
# HISTORISCHER HINWEIS FÜR UFA-TONWOCHE (vor Juni 1940)
# ═══════════════════════════════════════════════════════════════════════════════
UFA_TONWOCHE_NOTE = """
📜 HISTORISCHER HINWEIS / HISTORICAL NOTE / NOTA HISTÓRICA:
🇩🇪 Diese Ausgabe wurde ursprünglich als "Ufa-Tonwoche" veröffentlicht.
    Die Bezeichnung "Deutsche Wochenschau" wurde erst ab Juni 1940 (Nr. 512) verwendet,
    als alle deutschen Wochenschauen zur zentralen Propaganda-Wochenschau zusammengelegt wurden.
🇬🇧 This edition was originally released as "Ufa-Tonwoche" (Ufa Sound Weekly).
    The title "Deutsche Wochenschau" was only used from June 1940 (No. 512) onwards,
    when all German newsreels were merged into one centralized propaganda newsreel.
🇪🇸 Esta edición fue publicada originalmente como "Ufa-Tonwoche".
    El título "Deutsche Wochenschau" solo se usó a partir de junio de 1940.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# TITEL-TEMPLATE NACH SEO_TEMPLATE.md
# ═══════════════════════════════════════════════════════════════════════════════
def build_title(nr, date_str):
    """
    Format: Die Deutsche Wochenschau Nr. [NR] | [DD.MM.YYYY] | Germany WWII Newsreel | 8K HQ | @remAIke_IT
    """
    # Datum umformatieren: YYYY-MM-DD → DD.MM.YYYY
    parts = date_str.split("-")
    formatted_date = f"{parts[2]}.{parts[1]}.{parts[0]}"
    
    return f"Die Deutsche Wochenschau Nr. {nr} | {formatted_date} | Germany WWII Newsreel | 8K HQ | @remAIke_IT"

# ═══════════════════════════════════════════════════════════════════════════════
# DESCRIPTION-TEMPLATE NACH REGELN
# ═══════════════════════════════════════════════════════════════════════════════
def build_description(nr, date_str, is_pre_1940=False):
    """
    Baut vollständige Description nach Template:
    - Header mit Emoji
    - Trilingual DE/EN/ES
    - Historischer Hinweis für Ufa-Tonwoche
    - CTA Block
    - Hashtags
    """
    # Datum formatieren
    parts = date_str.split("-")
    date_de = f"{parts[2]}.{parts[1]}.{parts[0]}"
    date_en = f"{parts[1]}/{parts[2]}/{parts[0]}"  # MM/DD/YYYY
    year = parts[0]
    
    # Header
    desc = f"""🎬 Die Deutsche Wochenschau Nr. {nr} | {date_de} | WWII German Newsreel | 8K
"""
    
    # Ufa-Tonwoche Hinweis für frühe Ausgaben
    if is_pre_1940:
        desc += UFA_TONWOCHE_NOTE
    
    # Haupttext trilingual
    desc += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇩🇪 DEUTSCH:
Die Deutsche Wochenschau Nr. {nr} vom {date_de}.
Originale Kino-Wochenschau aus Deutschland mit zeitgenössischem Bild- und Tonmaterial.
⚠️ Historisches Archivmaterial - dient der Dokumentation und Bildung.

🇬🇧 ENGLISH:
German Weekly Newsreel No. {nr}, dated {date_en}.
Original theatrical newsreel footage with contemporary image and sound material.
⚠️ Historical archive material - for documentation and educational purposes.

🇪🇸 ESPAÑOL:
Noticiero Semanal Alemán Nr. {nr}, del {date_de}.
Material de archivo cinematográfico original con imágenes y sonido de la época.
⚠️ Material de archivo histórico - con fines documentales y educativos.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 8K HQ Edition:
• Stabilized archival source
• Enhanced clarity for modern displays  
• Original visual and audio character preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More at: https://frai.tv | @remAIke_IT
🎬 Full Playlist: https://www.youtube.com/playlist?list=PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg

📜 Source: Public Domain (Bundesarchiv / German Federal Archives)

#Wochenschau #GermanNewsreel #WWIIHistory #{year} #ArchiveFootage #HistoricalFilm 
#Zeitgeschichte #WorldHistory #Europe{year} #8K #remAIke #WWII #WW2
"""
    return desc

# ═══════════════════════════════════════════════════════════════════════════════
# TAGS NACH 14-SPRACHEN TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════════
def build_tags(nr, date_str):
    """Baut multilingual Tags für 14+ Sprachen"""
    year = date_str.split("-")[0]
    
    tags = [
        # Brand
        "remAIke", "remAIke_IT", "8K", "8K HQ", "UHD",
        
        # Serie
        "Wochenschau", "Deutsche Wochenschau", f"Wochenschau {nr}", "German newsreel",
        
        # Historisch Core
        "WWII", "WW2", "World War II", "World War 2", "history", "documentary",
        "public domain", "archival footage", "historical footage",
        f"{year}", "1940s" if int(year) >= 1940 else "1930s",
        
        # German
        "Zweiter Weltkrieg", "Geschichte", "Dokumentation", "Zeitgeschichte",
        "Kino Wochenschau", "Third Reich", "Drittes Reich",
        
        # Spanish (124M users)
        "Segunda Guerra Mundial", "noticiero alemán", "historia", "documental",
        
        # Portuguese (150M users)  
        "Segunda Guerra", "cinejornal alemão", "história",
        
        # French
        "Seconde Guerre mondiale", "actualités allemandes",
        
        # Japanese (78.5M)
        "第二次世界大戦", "ドイツニュース映画", "歴史",
        
        # Hindi (500M - largest!)
        "द्वितीय विश्व युद्ध", "जर्मन न्यूज़रील",
        
        # Russian
        "Вторая мировая война", "немецкая кинохроника",
        
        # Chinese
        "二战", "德国新闻片",
        
        # Arabic
        "الحرب العالمية الثانية",
        
        # Indonesian (151M)
        "Perang Dunia II", "berita Jerman",
        
        # Korean
        "제2차 세계대전",
        
        # Turkish
        "İkinci Dünya Savaşı",
        
        # Vietnamese
        "Thế chiến thứ hai",
    ]
    
    return tags

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FIX FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 70)
    print("🔧 WOCHENSCHAU UPLOAD DATA FIX - NACH ALLEN REGELN")
    print("=" * 70)
    print()
    print("📋 REGELN:")
    print("  1. Titel: Die Deutsche Wochenschau Nr. X | DD.MM.YYYY | Germany WWII Newsreel | 8K HQ | @remAIke_IT")
    print("  2. Ufa-Tonwoche Hinweis für Nr. < 512 (vor Juni 1940)")
    print("  3. Trilingual Description (DE/EN/ES)")
    print("  4. 14-Sprachen Tags")
    print("  5. CTA Block (LIKE/COMMENT/SUBSCRIBE)")
    print()
    
    # Lade existierende Daten
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    videos = data.get("videos", data) if isinstance(data, dict) else data
    print(f"📊 {len(videos)} Videos geladen")
    
    fixed_count = 0
    ufa_tonwoche_count = 0
    
    for video in videos:
        nr = int(video.get("video_nr", video.get("nr", 0)))
        date_str = video.get("date", "")
        
        if not nr or not date_str:
            continue
        
        # Ist es eine Ufa-Tonwoche (vor Juni 1940)?
        is_pre_1940 = nr < FIRST_DW_NR
        if is_pre_1940:
            ufa_tonwoche_count += 1
        
        # Fix Title
        old_title = video.get("title", "")
        new_title = build_title(nr, date_str)
        
        # Fix Description
        new_desc = build_description(nr, date_str, is_pre_1940)
        
        # Fix Tags
        new_tags = build_tags(nr, date_str)
        
        # Update
        video["title"] = new_title
        video["description"] = new_desc
        video["tags"] = new_tags
        video["category"] = "27"  # Education
        
        fixed_count += 1
    
    # Speichere gefixte Daten
    output_data = {"videos": videos} if isinstance(data, dict) else videos
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print()
    print("=" * 70)
    print(f"✅ {fixed_count} Videos gefixt!")
    print(f"📜 {ufa_tonwoche_count} Videos mit Ufa-Tonwoche Hinweis (vor Juni 1940)")
    print(f"📁 Gespeichert: {OUTPUT_FILE}")
    print("=" * 70)
    
    # Zeige Beispiel
    print()
    print("📺 BEISPIEL (Nr. 459 - Ufa-Tonwoche 1939):")
    print("-" * 70)
    sample = [v for v in videos if int(v.get("video_nr", v.get("nr", 0))) == 459]
    if sample:
        print(f"TITEL: {sample[0]['title']}")
        print()
        print("DESCRIPTION (erste 500 Zeichen):")
        print(sample[0]['description'][:500])
        print("...")

if __name__ == "__main__":
    main()
