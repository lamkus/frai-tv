#!/usr/bin/env python3
"""
🎬 WOCHENSCHAU COMPLETE UPLOAD DATABASE GENERATOR
==================================================
Generiert ALLE Informationen für jeden Upload:
- Optimierter Titel (SEO 2026)
- Multilingual Description (14 Sprachen)
- International Tags (nach YouTube User Base)
- Kategorie, Playlist-Zuordnung, etc.

Basiert auf:
- wochenschau_events.json (historische Events)
- WOCHENSCHAU_MULTILINGUAL_SEO.md (Templates)
- YouTube SEO Best Practices 2026
"""

import json
import os
from datetime import datetime

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EVENTS_FILE = os.path.join(BASE_DIR, "config", "wochenschau_events.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")

# Monatsnamen
MONTHS_EN = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
             7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
MONTHS_DE = {1: "Januar", 2: "Februar", 3: "März", 4: "April", 5: "Mai", 6: "Juni",
             7: "Juli", 8: "August", 9: "September", 10: "Oktober", 11: "November", 12: "Dezember"}

# ============================================================================
# MULTILINGUAL TRANSLATIONS (14 Sprachen nach YouTube User Base 2025)
# ============================================================================

# WWII Translations für Description
WWII_TRANSLATIONS = {
    "de": {"wwii": "Zweiter Weltkrieg", "newsreel": "Wochenschau", "history": "Geschichte"},
    "en": {"wwii": "World War II", "newsreel": "Newsreel", "history": "History"},
    "es": {"wwii": "Segunda Guerra Mundial", "newsreel": "Noticiero", "history": "Historia"},
    "pt": {"wwii": "Segunda Guerra Mundial", "newsreel": "Cinejornal", "history": "História"},
    "fr": {"wwii": "Seconde Guerre mondiale", "newsreel": "Actualités", "history": "Histoire"},
    "ru": {"wwii": "Вторая мировая война", "newsreel": "Кинохроника", "history": "История"},
    "ja": {"wwii": "第二次世界大戦", "newsreel": "ニュース映画", "history": "歴史"},
    "hi": {"wwii": "द्वितीय विश्व युद्ध", "newsreel": "न्यूज़रील", "history": "इतिहास"},
    "zh": {"wwii": "二战", "newsreel": "新闻片", "history": "历史"},
    "ar": {"wwii": "الحرب العالمية الثانية", "newsreel": "النشرة الإخبارية", "history": "تاريخ"},
    "id": {"wwii": "Perang Dunia II", "newsreel": "Berita Film", "history": "Sejarah"},
    "vi": {"wwii": "Thế chiến thứ hai", "newsreel": "Tin tức phim", "history": "Lịch sử"},
    "tr": {"wwii": "İkinci Dünya Savaşı", "newsreel": "Haber Filmi", "history": "Tarih"},
    "ko": {"wwii": "제2차 세계대전", "newsreel": "뉴스릴", "history": "역사"},
}

# Core Tags (immer dabei)
CORE_TAGS = [
    "remAIke", "remAIke_IT", "8K", "8K HQ", "UHD",
    "Wochenschau", "Deutsche Wochenschau", "German newsreel",
    "WWII", "World War II", "WW2", "history", "documentary",
    "public domain", "archival footage", "historical footage",
]

# Multilingual Tags (nach YouTube User Base - wichtigste zuerst!)
MULTILINGUAL_TAGS = {
    # 🇮🇳 Hindi (500M - LARGEST!)
    "hi": ["द्वितीय विश्व युद्ध", "जर्मन न्यूज़रील", "इतिहास"],
    # 🇺🇸🇬🇧 English (309.5M)
    "en": ["World War 2", "German news", "WWII documentary", "war footage"],
    # 🇮🇩 Indonesian (151M - 3rd largest!)
    "id": ["Perang Dunia II", "berita Jerman", "sejarah", "dokumenter"],
    # 🇧🇷 Portuguese (150M)
    "pt": ["Segunda Guerra Mundial", "cinejornal alemão", "história"],
    # 🇪🇸🇲🇽 Spanish (124M)
    "es": ["Segunda Guerra Mundial", "noticiero alemán", "historia", "documental"],
    # 🇯🇵 Japanese (78.5M)
    "ja": ["第二次世界大戦", "ドイツニュース", "歴史", "ドキュメンタリー"],
    # 🇩🇪 German (64.7M)
    "de": ["Zweiter Weltkrieg", "Kriegswochenschau", "Geschichte", "Dokumentation"],
    # 🇻🇳 Vietnamese (62.1M)
    "vi": ["Thế chiến thứ hai", "tin tức Đức", "lịch sử"],
    # 🇹🇷 Turkish (57.9M)
    "tr": ["İkinci Dünya Savaşı", "Alman haber filmi", "tarih"],
    # 🇫🇷 French (51.5M)
    "fr": ["Seconde Guerre mondiale", "actualités allemandes", "histoire"],
    # 🇸🇦🇪🇬 Arabic (49.3M)
    "ar": ["الحرب العالمية الثانية", "التاريخ"],
    # 🇰🇷 Korean (42.9M)
    "ko": ["제2차 세계대전", "독일 뉴스릴", "역사"],
    # 🇷🇺 Russian (growing)
    "ru": ["Вторая мировая война", "немецкая кинохроника"],
    # 🇨🇳 Chinese (diaspora)
    "zh": ["二战", "德国新闻片", "历史纪录片"],
}

# Event-spezifische Übersetzungen
EVENT_TRANSLATIONS = {
    "Battle of Britain": {"de": "Luftschlacht um England", "es": "Batalla de Inglaterra", 
                         "fr": "Bataille d'Angleterre", "ja": "バトル・オブ・ブリテン",
                         "ru": "Битва за Британию", "zh": "不列颠之战"},
    "Barbarossa": {"de": "Unternehmen Barbarossa", "es": "Operación Barbarroja",
                  "ru": "Операция Барбаросса", "ja": "バルバロッサ作戦", "zh": "巴巴罗萨行动"},
    "Stalingrad": {"de": "Schlacht von Stalingrad", "es": "Batalla de Stalingrado",
                  "ru": "Сталинградская битва", "ja": "スターリングラード", "zh": "斯大林格勒战役"},
    "Dunkirk": {"de": "Dünkirchen", "es": "Dunkerque", "fr": "Dunkerque",
               "ja": "ダンケルク", "zh": "敦刻尔克"},
    "Paris Falls": {"de": "Fall von Paris", "es": "Caída de París", 
                   "fr": "Chute de Paris", "ja": "パリ陥落", "zh": "巴黎沦陷"},
    "Poland": {"de": "Polenfeldzug", "es": "Invasión de Polonia",
              "ru": "Вторжение в Польшу", "ja": "ポーランド侵攻"},
    "Normandy": {"de": "Normandie", "es": "Normandía", "fr": "Normandie",
                "ja": "ノルマンディー", "zh": "诺曼底"},
    "Africa": {"de": "Afrikafeldzug", "es": "Campaña de África",
              "ja": "北アフリカ戦線", "zh": "北非战场"},
}

# ============================================================================
# DESCRIPTION TEMPLATE
# ============================================================================

def generate_description(nr, date_str, event_de, event_en, note, is_ufa):
    """Generiere SEO-optimierte multilingual Description"""
    
    # Datum parsen
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_de = f"{dt.day:02d}.{dt.month:02d}.{dt.year}"
        date_en = f"{MONTHS_EN[dt.month]} {dt.day}, {dt.year}"
        year = dt.year
    except:
        date_de = date_str
        date_en = date_str
        year = "1940"
    
    # Ufa-Tonwoche Hinweis
    ufa_note = ""
    if is_ufa:
        ufa_note = """
📜 HISTORISCHER HINWEIS / HISTORICAL NOTE / NOTA HISTÓRICA:
🇩🇪 Diese Ausgabe wurde ursprünglich als "Ufa-Tonwoche" veröffentlicht.
    Die Bezeichnung "Deutsche Wochenschau" wurde erst ab Juni 1940 (Nr. 511) verwendet.
🇬🇧 This edition was originally released as "Ufa-Tonwoche" (Ufa Sound Weekly).
    The title "Deutsche Wochenschau" was only used from June 1940 onwards.
🇪🇸 Esta edición fue publicada originalmente como "Ufa-Tonwoche".

"""
    
    description = f"""🎬 WOCHENSCHAU {nr} | {date_de} | {event_en}
{event_de} | German WWII Newsreel | 8K Restored
{ufa_note}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇩🇪 DEUTSCH:
Die Deutsche Wochenschau Nr. {nr} vom {date_de}.
{note if note else f"Originale Kino-Wochenschau mit zeitgenössischem Bild- und Tonmaterial."}
⚠️ Historisches Archivmaterial - dient der Dokumentation und Bildung.

🇬🇧 ENGLISH:
German Weekly Newsreel No. {nr}, dated {date_en}.
Original theatrical newsreel with contemporary footage and audio.
⚠️ Historical archive material - for documentation and educational purposes.

🇪🇸 ESPAÑOL:
Noticiero Semanal Alemán Nr. {nr}, del {date_de}.
Material de archivo cinematográfico original de la época.
⚠️ Material de archivo histórico - con fines documentales y educativos.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 8K HQ Edition:
• AI-Stabilized archival source
• Enhanced clarity for modern displays
• Original visual and audio character preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg, {event_de}
🇬🇧 German Newsreel, World War II, WWII, {event_en}
🇪🇸 Noticiero alemán, Segunda Guerra Mundial
🇫🇷 Actualités allemandes, Seconde Guerre mondiale
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial
🇷🇺 Немецкая кинохроника, Вторая мировая война
🇯🇵 ドイツニュース映画, 第二次世界大戦
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध
🇨🇳 德国新闻片, 二战
🇸🇦 النشرة الإخبارية الألمانية
🇮🇩 Berita Jerman, Perang Dunia II
🇻🇳 Tin tức Đức, Thế chiến thứ hai
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı
🇰🇷 독일 뉴스릴, 제2차 세계대전
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More at: https://frai.tv | @remAIke_IT
🎬 Full Playlist: https://www.youtube.com/playlist?list=PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg

📜 Source: Public Domain (Bundesarchiv / German Federal Archives)

#Wochenschau #WWII #WW2 #8K #History #WorldWarII #DeutscheWochenschau #GermanNewsreel #{year} #PublicDomain #ArchiveFootage #remAIke
"""
    return description.strip()

# ============================================================================
# TAG GENERATION
# ============================================================================

def generate_tags(nr, year, event_en, event_de):
    """Generiere internationale Tags (max ~500 chars)"""
    
    tags = CORE_TAGS.copy()
    
    # Episodenspezifisch
    tags.extend([f"Wochenschau {nr}", f"Wochenschau Nr {nr}", str(year), f"{year}s"])
    
    # Event-spezifisch
    if event_en:
        tags.append(event_en)
        # Event-Übersetzungen hinzufügen
        for key, translations in EVENT_TRANSLATIONS.items():
            if key.lower() in event_en.lower():
                tags.extend(translations.values())
                break
    
    if event_de and event_de not in tags:
        tags.append(event_de)
    
    # Multilingual Tags (nach Priorität - größte Märkte zuerst)
    priority_langs = ["hi", "en", "id", "pt", "es", "ja", "de", "fr", "ar", "tr", "ru"]
    for lang in priority_langs:
        if lang in MULTILINGUAL_TAGS:
            # Nur erste 2 pro Sprache um Limit nicht zu sprengen
            tags.extend(MULTILINGUAL_TAGS[lang][:2])
    
    # Deduplizieren und Limit prüfen
    seen = set()
    unique_tags = []
    total_chars = 0
    for tag in tags:
        if tag.lower() not in seen and total_chars + len(tag) < 480:
            seen.add(tag.lower())
            unique_tags.append(tag)
            total_chars += len(tag) + 1  # +1 für Komma
    
    return unique_tags

# ============================================================================
# TITLE GENERATION
# ============================================================================

def generate_title(nr, event_en, date_str):
    """Generiere SEO-optimierten Titel (max 60 chars)"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        short_date = f"{MONTHS_EN[dt.month]} {dt.year}"
    except:
        short_date = date_str[:7] if date_str else ""
    
    title = f"Wochenschau {nr}: {event_en} ({short_date}) | 8K"
    
    # Kürzen wenn nötig
    if len(title) > 60:
        replacements = {" of ": " ", " Continues": "", " Offensive": " Off.",
                       " Campaign": "", " Operation": " Op.", "Preparations": "Prep"}
        for old, new in replacements.items():
            if old in event_en:
                event_en = event_en.replace(old, new)
                title = f"Wochenschau {nr}: {event_en} ({short_date}) | 8K"
                if len(title) <= 60:
                    break
    
    return title

# ============================================================================
# MAIN GENERATOR
# ============================================================================

def generate_complete_database():
    """Generiere komplette Upload-Datenbank"""
    
    print("=" * 70)
    print("🎬 WOCHENSCHAU COMPLETE UPLOAD DATABASE GENERATOR")
    print("=" * 70)
    
    # Lade Events
    with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
        events_data = json.load(f)
    events = events_data.get('events', {})
    
    database = {
        "_meta": {
            "description": "Komplette Upload-Datenbank für alle Deutsche Wochenschau Ausgaben",
            "version": "2.0",
            "seo_standard": "YouTube Algorithm 2026",
            "languages": "14 (DE, EN, ES, PT, FR, RU, JA, HI, ZH, AR, ID, VI, TR, KO)",
            "total_episodes": len(events),
            "number_range": "Nr. 459 (Juni 1939) bis Nr. 755 (März 1945)",
            "created": datetime.now().isoformat(),
            "created_by": "Copilot für remAIke_IT",
            "usage": "Direkt für YouTube Upload verwenden - alle Felder sind fertig!",
            "category_id": "25",  # News & Politics
            "privacy_status": "private",  # NIEMALS auto-publish!
            "playlist_id": "PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg"
        },
        "videos": {}
    }
    
    stats = {"total": 0, "ufa_tonwoche": 0, "deutsche_wochenschau": 0}
    
    for nr_str, event_data in sorted(events.items(), key=lambda x: int(x[0])):
        nr = int(nr_str)
        date_str = event_data.get('date', '')
        event_en = event_data.get('event_en', 'WWII Germany')
        event_de = event_data.get('event_de', '')
        note = event_data.get('note', '')
        is_ufa = nr < 511
        
        # Jahr extrahieren
        try:
            year = int(date_str[:4])
        except:
            year = 1940
        
        # Alle Daten generieren
        title = generate_title(nr, event_en, date_str)
        description = generate_description(nr, date_str, event_de, event_en, note, is_ufa)
        tags = generate_tags(nr, year, event_en, event_de)
        
        database["videos"][nr_str] = {
            "number": nr,
            "date": date_str,
            "year": year,
            "event_de": event_de,
            "event_en": event_en,
            "historical_note": note,
            "is_ufa_tonwoche": is_ufa,
            
            # YouTube Upload Fields - READY TO USE!
            "title": title,
            "title_length": len(title),
            "description": description,
            "description_length": len(description),
            "tags": tags,
            "tags_count": len(tags),
            "tags_total_chars": sum(len(t) for t in tags),
            
            # YouTube Settings
            "category_id": "25",  # News & Politics
            "default_language": "de",
            "privacy_status": "private",  # User publishes manually!
            "made_for_kids": False,
            "embeddable": True,
            "license": "creativeCommon",
            
            # Filename pattern
            "expected_filename": f"Deutsche_Wochenschau_Nr{nr}_{date_str}_8K.mp4"
        }
        
        stats["total"] += 1
        if is_ufa:
            stats["ufa_tonwoche"] += 1
        else:
            stats["deutsche_wochenschau"] += 1
    
    # Speichern
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    # Statistik
    print(f"\n📊 STATISTIK:")
    print(f"   Videos total:           {stats['total']}")
    print(f"   Ufa-Tonwoche (<511):    {stats['ufa_tonwoche']}")
    print(f"   Deutsche Wochenschau:   {stats['deutsche_wochenschau']}")
    
    # Beispiel ausgeben
    print(f"\n📝 BEISPIEL (Nr. 523 - London Blitz):")
    print("-" * 70)
    sample = database["videos"].get("523", {})
    print(f"   Title ({sample.get('title_length')} chars):")
    print(f"   {sample.get('title')}")
    print(f"\n   Tags ({sample.get('tags_count')} tags, {sample.get('tags_total_chars')} chars):")
    print(f"   {', '.join(sample.get('tags', [])[:10])}...")
    print(f"\n   Description ({sample.get('description_length')} chars):")
    print(f"   {sample.get('description', '')[:300]}...")
    
    print(f"\n" + "=" * 70)
    print(f"✅ COMPLETE DATABASE SAVED: {OUTPUT_FILE}")
    print(f"   {stats['total']} Videos mit ALLEN Upload-Daten!")
    print(f"   → Titel, Description, Tags, Settings - ALULAR FERTIG!")
    print("=" * 70)
    
    return database

if __name__ == "__main__":
    generate_complete_database()
