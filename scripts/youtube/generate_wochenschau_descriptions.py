#!/usr/bin/env python3
"""
Generate YouTube descriptions for ALL Wochenschau videos.
Uses verified historical events from wochenschau_events.json.
"""
import json
import re
from pathlib import Path
from datetime import datetime

# Load verified events from JSON
def load_events_db():
    """Load historical events from verified JSON."""
    event_file = Path('config/wochenschau_events.json')
    if event_file.exists():
        data = json.loads(event_file.read_text(encoding='utf-8'))
        return data.get('events', {})
    return {}

# Fallback events by month (only used if episode not in JSON)
HISTORICAL_EVENTS = {
    # 1939
    "1939-06": "Vorkriegszeit, Mobilmachung, Propaganda",
    "1939-08": "Molotow-Ribbentrop-Pakt, Kriegsvorbereitung",
    "1939-09": "Überfall auf Polen, Beginn des Zweiten Weltkriegs, Blitzkrieg",
    "1939-10": "Polen besetzt, Sitzkrieg im Westen",
    "1939-11": "Sitzkrieg, Wintervorbereitungen",
    "1939-12": "Winterkrieg Finnland-Sowjetunion, Weihnachten im Krieg",
    
    # 1940
    "1940-01": "Sitzkrieg, Winterkrieg Finnland",
    "1940-02": "Sitzkrieg, Propaganda, Heimatfront",
    "1940-03": "Vorbereitungen Westfeldzug, Ende Winterkrieg",
    "1940-04": "Invasion Dänemark und Norwegen (9. April)",
    "1940-05": "Westfeldzug beginnt (10. Mai), Invasion Belgien/Niederlande/Frankreich, Dünkirchen",
    "1940-06": "Fall von Paris (14. Juni), Kapitulation Frankreich (22. Juni), Siegesfeiern",
    "1940-07": "Luftschlacht um England beginnt, Siegesparaden, U-Boot-Krieg",
    "1940-08": "Luftschlacht um England (Battle of Britain), Luftangriffe",
    "1940-09": "Blitz auf London, Dreimächtepakt",
    "1940-10": "Luftschlacht um England, Achsenmächte",
    "1940-11": "Coventry-Bombardierung, Griechenland-Feldzug",
    "1940-12": "Nordafrika (Libyen), Weihnachten 1940",
    
    # 1941
    "1941-01": "Nordafrika-Feldzug, Tobruk",
    "1941-02": "Rommel in Nordafrika, Afrikakorps",
    "1941-03": "Balkanfeldzug-Vorbereitung, Lend-Lease USA",
    "1941-04": "Balkanfeldzug, Jugoslawien, Griechenland",
    "1941-05": "Kreta-Invasion (Fallschirmjäger), Rudolf Heß",
    "1941-06": "Unternehmen Barbarossa beginnt (22. Juni), Ostfront",
    "1941-07": "Vormarsch Ostfront, Kesselschlachten",
    "1941-08": "Ostfront Vormarsch, Smolensk, Ukraine",
    "1941-09": "Kiew eingenommen, Leningrad-Belagerung beginnt",
    "1941-10": "Operation Taifun (Moskau), Schlammperiode",
    "1941-11": "Vor Moskau, Wintereinbruch",
    "1941-12": "Moskau-Offensive gestoppt, Pearl Harbor (7. Dez), Kriegserklärung USA",
    
    # 1942
    "1942-01": "Winterkrise Ostfront, Wannsee-Konferenz",
    "1942-02": "Atlantikschlacht, U-Boot-Erfolge",
    "1942-03": "Frühjahrsoffensive-Vorbereitung",
    "1942-04": "Luftangriffe auf Deutschland beginnen",
    "1942-05": "Sewastopol, Charkow",
    "1942-06": "Sommeroffensive Süden, Tobruk fällt, Midway",
    "1942-07": "Stalingrad-Offensive beginnt, Kaukasus",
    "1942-08": "Stalingrad, Kaukasus-Ölfelder",
    "1942-09": "Stalingrad Häuserkampf",
    "1942-10": "El Alamein, Stalingrad",
    "1942-11": "Stalingrad eingekesselt, Torch-Landung Nordafrika",
    "1942-12": "Stalingrad-Kessel, Winterkämpfe",
    
    # 1943
    "1943-01": "Casablanca-Konferenz, Stalingrad-Kessel",
    "1943-02": "Kapitulation Stalingrad (2. Feb), totaler Krieg, Sportpalastrede",
    "1943-03": "Rückzüge Ostfront, Charkow zurückerobert",
    "1943-04": "Warschauer Ghetto, Tunesien",
    "1943-05": "Kapitulation Afrika-Korps (13. Mai)",
    "1943-06": "Bombardierungen, Heimatfront",
    "1943-07": "Kursk (größte Panzerschlacht), Sizilien-Landung",
    "1943-08": "Hamburg Feuersturm, Ostfront-Rückzüge",
    "1943-09": "Italien kapituliert, Badoglio, Mussolini befreit",
    "1943-10": "Ostfront-Rückzüge, Dnjepr",
    "1943-11": "Kiew verloren, Teheran-Konferenz",
    "1943-12": "Ostfront, Weihnachten im 5. Kriegsjahr",
    
    # 1944
    "1944-01": "Leningrad-Blockade durchbrochen",
    "1944-02": "Bombenkrieg, Big Week Luftangriffe",
    "1944-03": "Ungarn besetzt, Rückzüge",
    "1944-04": "Krim geräumt, Luftangriffe",
    "1944-05": "Monte Cassino, Invasionserwartung",
    "1944-06": "D-Day Normandie (6. Juni), V1-Raketen",
    "1944-07": "Stauffenberg-Attentat (20. Juli), Ostfront-Zusammenbruch",
    "1944-08": "Paris befreit, Rumänien wechselt Seiten",
    "1944-09": "V2-Raketen, Arnhem, Westwall",
    "1944-10": "Volkssturm, Aachen fällt",
    "1944-11": "Rückzüge, Endkampf-Propaganda",
    "1944-12": "Ardennenoffensive, letzte Offensive",
    
    # 1945
    "1945-01": "Ardennen-Rückzug, Weichsel-Oder-Offensive, Auschwitz befreit",
    "1945-02": "Jalta-Konferenz, Dresden, Oder-Front",
    "1945-03": "Rhein überquert, Endkampf (letzte Wochenschauen)"
}

def get_historical_content(date_str):
    """Get historical events for a date."""
    try:
        # Parse date from filename format YYYY-MM-DD
        year_month = date_str[:7]  # YYYY-MM
        return HISTORICAL_EVENTS.get(year_month, "Kriegsgeschehen, Heimatfront, Propaganda")
    except:
        return "Kriegsgeschehen, Heimatfront, Propaganda"

def translate_events(events_de):
    """Translate German events to English."""
    translations = {
        # Locations/Fronts
        "Ostfront": "Eastern Front",
        "Westfront": "Western Front", 
        "Heimatfront": "Home Front",
        "Nordafrika": "North Africa",
        "Kaukasus": "Caucasus",
        # Actions
        "Luftangriffe": "Air raids",
        "Rückzüge": "Retreats",
        "Kapitulation": "Surrender",
        "Vormarsch": "Advance",
        "Offensive": "Offensive",
        "Invasion": "Invasion",
        "Belagerung": "Siege",
        "Besetzt": "Occupied",
        "Eingenommen": "Captured",
        "Bombardierung": "Bombing",
        "Feuersturm": "Firestorm",
        # Events
        "Überfall auf Polen": "Invasion of Poland",
        "Beginn des Zweiten Weltkriegs": "Start of World War II",
        "Blitzkrieg": "Blitzkrieg",
        "Fall von Paris": "Fall of Paris",
        "Kapitulation Frankreich": "France surrenders",
        "Luftschlacht um England beginnt": "Battle of Britain begins",
        "Luftschlacht um England": "Battle of Britain",
        "Siegesparaden": "Victory parades",
        "Siegesfeiern": "Victory celebrations",
        "U-Boot-Krieg": "U-boat warfare",
        "Dreimächtepakt": "Tripartite Pact",
        "Unternehmen Barbarossa": "Operation Barbarossa",
        "Kesselschlachten": "Encirclement battles",
        "Wintereinbruch": "Winter onset",
        "Kriegserklärung USA": "US declares war",
        "Pearl Harbor": "Pearl Harbor",
        "Stalingrad-Kessel": "Stalingrad pocket",
        "Stalingrad eingekesselt": "Stalingrad encircled",
        "Kapitulation Stalingrad": "Stalingrad surrender",
        "Sportpalastrede": "Sportpalast speech",
        "totaler Krieg": "Total War",
        "Kursk": "Kursk",
        "größte Panzerschlacht": "largest tank battle",
        "Sizilien-Landung": "Sicily landing",
        "Italien kapituliert": "Italy surrenders",
        "Mussolini befreit": "Mussolini rescued",
        "D-Day Normandie": "D-Day Normandy",
        "V1-Raketen": "V1 rockets",
        "V2-Raketen": "V2 rockets",
        "Stauffenberg-Attentat": "Stauffenberg assassination attempt",
        "Paris befreit": "Paris liberated",
        "Volkssturm": "Volkssturm",
        "Ardennenoffensive": "Battle of the Bulge",
        "letzte Offensive": "last offensive",
        "Weichsel-Oder-Offensive": "Vistula-Oder Offensive",
        "Auschwitz befreit": "Auschwitz liberated",
        "Jalta-Konferenz": "Yalta Conference",
        "Dresden": "Dresden",
        "Rhein überquert": "Rhine crossed",
        "Endkampf": "Final battle",
        "Weihnachten": "Christmas",
        "Winterkrieg": "Winter War",
        "Sitzkrieg": "Phoney War",
        "Propaganda": "Propaganda",
        "Kriegsgeschehen": "War events",
        # Time periods
        "Vorkriegszeit": "Pre-war period",
        "Mobilmachung": "Mobilization",
        "Kriegsvorbereitung": "War preparations",
        "Molotow-Ribbentrop-Pakt": "Molotov-Ribbentrop Pact",
    }
    
    result = events_de
    for de, en in translations.items():
        result = result.replace(de, en)
    return result

# Global events database (loaded once)
EVENTS_DB = {}

def generate_description(nr, date_str, duration_min):
    """Generate multilingual YouTube description with verified event keywords."""
    global EVENTS_DB
    
    year = date_str[:4]
    date_formatted = f"{date_str[8:10]}.{date_str[5:7]}.{year}"
    
    # Get specific event from JSON if available
    event_info = EVENTS_DB.get(nr, {})
    event_de = event_info.get('event_de', '')
    event_en = event_info.get('event_en', '')
    event_note = event_info.get('note', '')
    
    # Build event-specific content for description
    if event_de and event_en:
        # Use specific verified event
        events_de = event_de
        events_en = event_en
        # Add note if significant
        if event_note and len(event_note) > 10:
            events_de = f"{event_de} – {event_note}"
    else:
        # Fallback to month-based events
        events_de = get_historical_content(date_str)
        events_en = translate_events(events_de)
    
    # Format EXACTLY like Nr. 516 (top performer)
    description = f"""🎬 Die Deutsche Wochenschau Nr. {nr} ({date_formatted}) | WWII German Newsreel | 8K

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🇩🇪 Wochenschau Nr. {nr} vom {date_formatted}. {events_de}. NS-Propaganda in 8K restauriert. Bundesarchiv-Material.

🇺🇸 Newsreel #{nr}, {date_formatted}. {events_en}. Nazi propaganda restored in 8K. Federal Archives footage.

🇪🇸 Noticiario #{nr} del {date_formatted}. {events_en}. Propaganda nazi restaurada en 8K.

🇫🇷 Actualités #{nr} du {date_formatted}. {events_en}. Propagande nazie restaurée en 8K.

🇵🇹 Noticiário #{nr} de {date_formatted}. {events_en}. Propaganda nazista restaurada em 8K.

🇮🇹 Cinegiornale #{nr} del {date_formatted}. {events_en}. Propaganda nazista in 8K.

🇳🇱 Journaal #{nr} van {date_formatted}. {events_en}. Nazi-propaganda in 8K.

🇵🇱 Kronika #{nr} z {date_formatted}. {events_en}. Propaganda nazistowska w 8K.

🇷🇺 Кинохроника #{nr} от {date_formatted}. {events_en}. Нацистская пропаганда в 8K.

🇯🇵 週報 #{nr} {date_formatted}。{events_en}。ナチス宣伝8K復元。

🇨🇳 新闻片 #{nr} {date_formatted}。{events_en}。纳粹宣传8K修复。

🇰🇷 주간뉴스 #{nr} {date_formatted}. {events_en}. 나치 선전 8K 복원.

🇹🇷 Haber #{nr} {date_formatted}. {events_en}. Nazi propagandası 8K.

🇸🇦 الأخبار #{nr} {date_formatted}. {events_en}. دعاية نازية 8K.

🇮🇳 न्यूज़रील #{nr} {date_formatted}। {events_en}। नाज़ी प्रचार 8K।

🇹🇭 ข่าว #{nr} {date_formatted}. {events_en}. โฆษณานาซี 8K.

🇻🇳 Tin #{nr} {date_formatted}. {events_en}. Tuyên truyền 8K.

🇮🇩 Berita #{nr} {date_formatted}. {events_en}. Propaganda Nazi 8K.

🇸🇪 Veckojournal #{nr} {date_formatted}. {events_en}. Nazipropaganda 8K.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 PRIMARY SOURCE | BUNDESARCHIV FOOTAGE
🎬 LIKE for historical archives! 🔔 SUBSCRIBE @remAIke_IT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 https://frai.tv | @remAIke_IT

#Wochenschau #GermanNewsreel #WWII #WW2 #WorldWar2 #SecondWorldWar #NaziGermany #ThirdReich #Wehrmacht #Goebbels #Propaganda #EasternFront #WesternFront #DDay #Normandy #Stalingrad #Berlin{year} #HistoricalFootage #PrimarySource #Bundesarchiv #Archives #Documentary #8K #Restored #remAIke"""
    
    return description

def generate_tags(nr, date_str):
    """Generate optimal tags with event-specific keywords."""
    global EVENTS_DB
    year = date_str[:4]
    
    # Base tags
    tags = [
        f"{year} News",
        "8K Newsreel",
        "Archival Material",
        "Die Deutsche Wochenschau",
        "Film Restoration",
        "German Propaganda",
        "Historical Documentary",
        "Historical Footage",
        "Military History",
        "Nazi Germany",
        "News Reel",
        "Second World War",
        "Vintage Film",
        "WWII Germany",
        "War Archives",
        "World War II",
        "Bundesarchiv",
        "remAIke",
        "8K"
    ]
    
    # Add event-specific tag if available
    event_info = EVENTS_DB.get(nr, {})
    event_en = event_info.get('event_en', '')
    if event_en and len(event_en) > 3:
        tags.insert(0, event_en)  # Add event as first tag
    
    return tags[:19]  # Max 19 tags

def parse_filename(filename):
    """Parse Wochenschau filename to extract info."""
    # Format: Deutsche_Wochenschau_Nr516_1940-07-24_20min.mp4
    match = re.match(r'Deutsche_Wochenschau_Nr(\d+)_(\d{4}-\d{2}-\d{2})_(\d+)min\.mp4', filename)
    if match:
        return {
            'nr': match.group(1),
            'date': match.group(2),
            'duration': int(match.group(3))
        }
    return None

def main():
    global EVENTS_DB
    
    # Read filenames from terminal output (saved)
    source_dir = Path("V:/OriginalSources/German_Historical/Wochenschau_Certified")
    
    # Get files via command
    import subprocess
    result = subprocess.run(
        ['powershell', '-Command', f'Get-ChildItem -Path "{source_dir}" -Name'],
        capture_output=True, text=True
    )
    
    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    
    print(f"📁 Gefunden: {len(files)} Wochenschau-Dateien")
    print("=" * 80)
    
    all_data = []
    
    # Load event mapping into GLOBAL variable for use in generate_description/tags
    event_file = Path('config/wochenschau_events.json')
    events = {}
    if event_file.exists():
        events_data = json.loads(event_file.read_text(encoding='utf-8'))
        events = events_data.get('events', {})
        EVENTS_DB = events  # Set global!
        print(f"📅 Loaded {len(events)} historical events into EVENTS_DB")
    
    for filename in sorted(files):
        info = parse_filename(filename)
        if not info:
            print(f"⚠️ Konnte nicht parsen: {filename}")
            continue
        
        nr = info['nr']
        date = info['date']
        duration = info['duration']
        
        # Check if this episode has a major event
        event_info = events.get(nr, {})
        event_keyword = event_info.get('event_en', '')
        
        # Generate title - with event keyword if available
        year = date[:4]
        if event_keyword and len(event_keyword) > 0:
            # Event-based title: [Event] – Wochenschau Nr. XXX (YYYY)
            # Max 100 chars YouTube, aim for ~70 chars for best display
            title = f"{event_keyword} – Wochenschau Nr. {nr} ({year}) | 8K HQ | @remAIke_IT"
        else:
            # Standard title with full date
            date_formatted = f"{date[8:10]}.{date[5:7]}.{year}"
            title = f"Deutsche Wochenschau Nr. {nr} ({date_formatted}) | 8K HQ | @remAIke_IT"
        
        # Generate description
        description = generate_description(nr, date, duration)
        
        # Generate tags
        tags = generate_tags(nr, date)
        
        entry = {
            'filename': filename,
            'video_nr': nr,
            'date': date,
            'duration_min': duration,
            'title': title,
            'description': description,
            'tags': tags,
            'category': '27',  # Education
            'privacy': 'public'
        }
        
        all_data.append(entry)
        print(f"✅ Nr. {nr} ({date}) - {duration}min")
    
    # Save to JSON
    output_file = Path('config/wochenschau_upload_data.json')
    output_file.write_text(
        json.dumps(all_data, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    print()
    print("=" * 80)
    print(f"💾 Gespeichert: {output_file}")
    print(f"📊 {len(all_data)} Videos vorbereitet")
    
    # Show sample
    print()
    print("=" * 80)
    print("📋 BEISPIEL (Nr. 516):")
    print("=" * 80)
    sample = next((d for d in all_data if d['video_nr'] == '516'), all_data[0])
    print(f"TITLE: {sample['title']}")
    print(f"LENGTH: {len(sample['title'])} chars")
    print()
    print("DESCRIPTION:")
    print(sample['description'][:1000])
    print("...")

if __name__ == '__main__':
    main()
