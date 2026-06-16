#!/usr/bin/env python3
"""
COMPLETE Wochenschau Update - Format A with Individual Historical Content
- Title: "Wochenschau Nr. XXX: [Event] (YYYY) | 8K | @remAIke_IT"
- Description: Individual historical context + locations
- Tags: Specific to each episode's event
"""
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'

# Load events database
with open('config/wochenschau_events.json', 'r', encoding='utf-8') as f:
    events_data = json.load(f)
    EVENTS = events_data.get('events', {})

# Individual video data with historical details and locations
VIDEO_DATA = {
    # 1939
    "477": {
        "video_id": "iRzeiRoAsj4",
        "event_en": "Poland Occupied",
        "event_de": "Polen besetzt", 
        "year": 1939,
        "date": "1939-10-04",
        "locations": ["Warsaw", "Krakow", "Danzig", "Posen", "Lodz", "Poland"],
        "locations_de": ["Warschau", "Krakau", "Danzig", "Posen", "Lodz", "Polen"],
        "context_en": "German forces complete the occupation of Poland after the September 1939 invasion. The Wehrmacht parades through conquered Polish cities while the civilian population faces the beginning of Nazi occupation.",
        "context_de": "Deutsche Truppen vollenden die Besetzung Polens nach dem Überfall im September 1939. Die Wehrmacht paradiert durch eroberte polnische Städte.",
        "tags_specific": ["Poland 1939", "Warsaw", "Invasion of Poland", "September Campaign", "Polish Campaign"]
    },
    "480": {
        "video_id": "jeLWajro1As",
        "event_en": "Bürgerbräu Bombing",
        "event_de": "Bürgerbräu-Attentat",
        "year": 1939,
        "date": "1939-11-08",
        "locations": ["Munich", "Bürgerbräukeller", "Bavaria", "Germany"],
        "locations_de": ["München", "Bürgerbräukeller", "Bayern", "Deutschland"],
        "context_en": "Georg Elser's assassination attempt on Hitler at the Bürgerbräukeller in Munich. The bomb exploded 13 minutes after Hitler left, killing 8 and injuring 62. Nazi propaganda portrayed it as divine protection.",
        "context_de": "Georg Elsers Attentatsversuch auf Hitler im Bürgerbräukeller München. Die Bombe explodierte 13 Minuten nach Hitlers Abgang.",
        "tags_specific": ["Georg Elser", "Bürgerbräukeller", "Munich 1939", "Assassination Attempt", "November 8 1939"]
    },
    "482": {
        "video_id": "N7WPQUjFJjA",
        "event_en": "Winter War Begins",
        "event_de": "Winterkrieg beginnt",
        "year": 1939,
        "date": "1939-11-30",
        "locations": ["Finland", "Helsinki", "Karelia", "Mannerheim Line", "Soviet Union"],
        "locations_de": ["Finnland", "Helsinki", "Karelien", "Mannerheim-Linie", "Sowjetunion"],
        "context_en": "Soviet Union invades Finland, beginning the Winter War. Despite massive numerical superiority, the Red Army faces fierce Finnish resistance at the Mannerheim Line. Germany remains officially neutral but sympathetic to Finland.",
        "context_de": "Die Sowjetunion greift Finnland an - Beginn des Winterkriegs. Trotz Übermacht stößt die Rote Armee auf erbitterten finnischen Widerstand.",
        "tags_specific": ["Winter War", "Finland 1939", "Soviet Invasion", "Mannerheim Line", "Talvisota"]
    },
    "483": {
        "video_id": "cHxmbbT6EaM",
        "event_en": "Winter War",
        "event_de": "Winterkrieg",
        "year": 1939,
        "date": "1939-12-06",
        "locations": ["Finland", "Karelia", "Suomussalmi", "Soviet Union", "Arctic"],
        "locations_de": ["Finnland", "Karelien", "Suomussalmi", "Sowjetunion", "Arktis"],
        "context_en": "Continued coverage of the Russo-Finnish Winter War. Finnish ski troops inflict heavy casualties on Soviet forces in the frozen forests of Karelia using guerrilla tactics.",
        "context_de": "Fortsetzung der Berichterstattung zum Winterkrieg. Finnische Skitruppen fügen sowjetischen Einheiten schwere Verluste zu.",
        "tags_specific": ["Winter War", "Finnish Ski Troops", "Karelia", "Suomussalmi", "White Death"]
    },
    "488": {
        "video_id": "8sF9hLlPsQw",
        "event_en": "Phoney War",
        "event_de": "Sitzkrieg",
        "year": 1940,
        "date": "1940-01-10",
        "locations": ["Western Front", "Maginot Line", "Siegfried Line", "France", "Germany"],
        "locations_de": ["Westfront", "Maginot-Linie", "Siegfried-Linie", "Frankreich", "Deutschland"],
        "context_en": "The 'Phoney War' or 'Sitzkrieg' continues on the Western Front. French and German troops face each other across fortified lines with minimal combat, as both sides prepare for the coming spring offensive.",
        "context_de": "Der 'Sitzkrieg' an der Westfront geht weiter. Französische und deutsche Truppen stehen sich an befestigten Linien gegenüber.",
        "tags_specific": ["Phoney War", "Sitzkrieg", "Maginot Line", "Siegfried Line", "Drôle de guerre"]
    },
    # 1940
    "508": {
        "video_id": "fC0MlizsAQQ",
        "event_en": "Dunkirk Pocket",
        "event_de": "Kessel von Dünkirchen",
        "year": 1940,
        "date": "1940-05-29",
        "locations": ["Dunkirk", "Calais", "English Channel", "Belgium", "France", "Flanders"],
        "locations_de": ["Dünkirchen", "Calais", "Ärmelkanal", "Belgien", "Frankreich", "Flandern"],
        "context_en": "German forces encircle Allied troops at Dunkirk. Over 300,000 British and French soldiers are trapped against the sea as the Wehrmacht closes in. Operation Dynamo evacuation begins.",
        "context_de": "Deutsche Truppen kesseln alliierte Streitkräfte bei Dünkirchen ein. Über 300.000 Soldaten sind am Meer eingeschlossen.",
        "tags_specific": ["Dunkirk 1940", "Operation Dynamo", "BEF", "Dunkirk Evacuation", "Fall Gelb"]
    },
    "509": {
        "video_id": "2uHl4LYN8O8",
        "event_en": "Dunkirk Evacuation",
        "event_de": "Evakuierung Dünkirchen",
        "year": 1940,
        "date": "1940-06-05",
        "locations": ["Dunkirk", "English Channel", "Dover", "Calais", "France", "England"],
        "locations_de": ["Dünkirchen", "Ärmelkanal", "Dover", "Calais", "Frankreich", "England"],
        "context_en": "German propaganda shows the aftermath of Dunkirk evacuation. Abandoned Allied equipment litters the beaches while the Wehrmacht claims total victory, despite 338,000 troops escaping to Britain.",
        "context_de": "Deutsche Propaganda zeigt die Nachwirkungen der Evakuierung. Verlassene alliierte Ausrüstung an den Stränden.",
        "tags_specific": ["Dunkirk Beaches", "Little Ships", "Operation Dynamo", "Miracle of Dunkirk", "BEF Evacuation"]
    },
    "511": {
        "video_id": "3rB80OGKzrg",
        "event_en": "Paris Falls",
        "event_de": "Paris fällt",
        "year": 1940,
        "date": "1940-06-14",
        "locations": ["Paris", "Champs-Élysées", "Arc de Triomphe", "Eiffel Tower", "France"],
        "locations_de": ["Paris", "Champs-Élysées", "Arc de Triomphe", "Eiffelturm", "Frankreich"],
        "context_en": "German troops march into Paris on June 14, 1940. The Wehrmacht parades down the Champs-Élysées as the swastika flies over the Arc de Triomphe. France's capital falls without resistance.",
        "context_de": "Deutsche Truppen marschieren am 14. Juni 1940 in Paris ein. Die Wehrmacht paradiert über die Champs-Élysées.",
        "tags_specific": ["Paris 1940", "Fall of France", "Champs-Élysées", "Arc de Triomphe", "German Occupation Paris"]
    },
    "512": {
        "video_id": "xblc6reUMr0",
        "event_en": "French Armistice",
        "event_de": "Französischer Waffenstillstand",
        "year": 1940,
        "date": "1940-06-22",
        "locations": ["Compiègne", "Rethondes", "France", "Railway Carriage", "Forest of Compiègne"],
        "locations_de": ["Compiègne", "Rethondes", "Frankreich", "Eisenbahnwaggon", "Wald von Compiègne"],
        "context_en": "France signs the armistice in the same railway carriage where Germany surrendered in 1918. Hitler's revenge is complete as France is divided into occupied and Vichy zones.",
        "context_de": "Frankreich unterzeichnet den Waffenstillstand im selben Eisenbahnwaggon, in dem Deutschland 1918 kapitulierte.",
        "tags_specific": ["Armistice 1940", "Compiègne", "Vichy France", "French Surrender", "Railway Carriage"]
    },
    "513": {
        "video_id": "Q1xfUV7qHFc",
        "event_en": "Channel Islands",
        "event_de": "Kanalinseln besetzt",
        "year": 1940,
        "date": "1940-06-30",
        "locations": ["Jersey", "Guernsey", "Channel Islands", "English Channel", "Britain"],
        "locations_de": ["Jersey", "Guernsey", "Kanalinseln", "Ärmelkanal", "Großbritannien"],
        "context_en": "German forces occupy the Channel Islands - the only British territory occupied during WWII. Jersey and Guernsey fall without resistance after British demilitarization.",
        "context_de": "Deutsche Truppen besetzen die Kanalinseln - das einzige während des WWII besetzte britische Territorium.",
        "tags_specific": ["Channel Islands", "Jersey 1940", "Guernsey", "British Territory", "German Occupation"]
    },
    "516": {
        "video_id": "T-EsdXGhqog",
        "event_en": "Battle of Britain",
        "event_de": "Luftschlacht um England",
        "year": 1940,
        "date": "1940-07-24",
        "locations": ["England", "London", "Dover", "English Channel", "RAF Bases", "Kent"],
        "locations_de": ["England", "London", "Dover", "Ärmelkanal", "RAF-Stützpunkte", "Kent"],
        "context_en": "The Battle of Britain begins as the Luftwaffe attacks British convoys and coastal targets. German propaganda shows confident pilots preparing for the aerial campaign against Britain.",
        "context_de": "Die Luftschlacht um England beginnt. Die Luftwaffe greift britische Konvois und Küstenziele an.",
        "tags_specific": ["Battle of Britain", "Luftwaffe", "RAF", "Adlertag", "Kanalkampf", "Spitfire"]
    },
    "521": {
        "video_id": "4raY-jvtci4",
        "event_en": "London Bombed",
        "event_de": "London bombardiert",
        "year": 1940,
        "date": "1940-09-07",
        "locations": ["London", "East End", "Docklands", "Thames", "England"],
        "locations_de": ["London", "East End", "Docklands", "Themse", "England"],
        "context_en": "The Blitz begins as the Luftwaffe shifts from RAF bases to bombing London. September 7, 1940 marks 'Black Saturday' with massive raids on London's East End and Docklands.",
        "context_de": "Der Blitz beginnt - die Luftwaffe wechselt von RAF-Stützpunkten zu Bombardierung Londons. Der 7. September 1940 ist der 'Schwarze Samstag'.",
        "tags_specific": ["London Blitz", "Black Saturday", "East End", "Docklands", "September 7 1940"]
    },
    "522": {
        "video_id": "S31f7FuEvXw",
        "event_en": "Berlin Retaliation",
        "event_de": "Vergeltung Berlin",
        "year": 1940,
        "date": "1940-09-11",
        "locations": ["Berlin", "Germany", "London", "England"],
        "locations_de": ["Berlin", "Deutschland", "London", "England"],
        "context_en": "Nazi propaganda responds to RAF bombing raids on Berlin. Hitler promises to 'erase' British cities in retaliation. The escalating bombing war continues.",
        "context_de": "Nazi-Propaganda reagiert auf RAF-Bombenangriffe auf Berlin. Hitler verspricht, britische Städte 'auszuradieren'.",
        "tags_specific": ["RAF Berlin", "Retaliation", "Bombing War", "Hitler Speech", "Sportpalast"]
    },
    "523": {
        "video_id": "fNCZYqnK3Cc",
        "event_en": "London Blitz",
        "event_de": "Londoner Blitz",
        "year": 1940,
        "date": "1940-09-18",
        "locations": ["London", "Buckingham Palace", "St. Paul's Cathedral", "Coventry", "England"],
        "locations_de": ["London", "Buckingham Palace", "St. Paul's Cathedral", "Coventry", "England"],
        "context_en": "Continued Blitz coverage shows London under nightly bombardment. St. Paul's Cathedral stands defiant amid the flames. The British 'spirit of the Blitz' emerges.",
        "context_de": "Fortsetzung der Blitz-Berichterstattung zeigt London unter nächtlicher Bombardierung. St. Paul's Cathedral trotzt den Flammen.",
        "tags_specific": ["Blitz Spirit", "St Paul's Cathedral", "London Fire", "Coventry Blitz", "Night Raids"]
    },
    "524": {
        "video_id": "RzT_RJKjHzE",
        "event_en": "Sea Lion Postponed",
        "event_de": "Seelöwe verschoben",
        "year": 1940,
        "date": "1940-09-25",
        "locations": ["English Channel", "France", "England", "Invasion Barges"],
        "locations_de": ["Ärmelkanal", "Frankreich", "England", "Invasionsboote"],
        "context_en": "Operation Sea Lion (invasion of Britain) is indefinitely postponed as the Luftwaffe fails to achieve air superiority. German propaganda shifts focus away from the failed invasion plans.",
        "context_de": "Operation Seelöwe (Invasion Britanniens) wird auf unbestimmte Zeit verschoben, da die Luftwaffe keine Lufthoheit erringen kann.",
        "tags_specific": ["Operation Sea Lion", "Unternehmen Seelöwe", "Invasion Britain", "Luftwaffe Defeat", "Channel Ports"]
    },
    # 1943
    "652": {
        "video_id": "0sO7jVL43yQ",
        "event_en": "Kharkov Retaken",
        "event_de": "Charkow zurückerobert",
        "year": 1943,
        "date": "1943-03-15",
        "locations": ["Kharkov", "Kharkiv", "Ukraine", "Eastern Front", "Donbass"],
        "locations_de": ["Charkow", "Charkiw", "Ukraine", "Ostfront", "Donbass"],
        "context_en": "Third Battle of Kharkov - SS Panzer Corps retakes the city after the Stalingrad disaster. Manstein's 'backhand blow' stabilizes the Eastern Front temporarily.",
        "context_de": "Dritte Schlacht um Charkow - SS-Panzerkorps erobert die Stadt nach der Stalingrad-Katastrophe zurück. Mansteins 'Schlag aus der Nachhand'.",
        "tags_specific": ["Kharkov 1943", "Third Battle Kharkov", "Manstein", "SS Panzer Corps", "Eastern Front 1943"]
    },
    "654": {
        "video_id": "dYBzf5V1TjI",
        "event_en": "Tunisia Battles",
        "event_de": "Kämpfe in Tunesien",
        "year": 1943,
        "date": "1943-03-29",
        "locations": ["Tunisia", "Kasserine", "Mareth Line", "North Africa", "Rommel"],
        "locations_de": ["Tunesien", "Kasserine", "Mareth-Linie", "Nordafrika", "Rommel"],
        "context_en": "Fighting continues in Tunisia as Axis forces make their last stand in North Africa. The Afrika Korps and Italian forces face overwhelming Allied pressure.",
        "context_de": "Kämpfe in Tunesien - Achsenmächte leisten letzten Widerstand in Nordafrika. Das Afrikakorps steht unter alliiertem Druck.",
        "tags_specific": ["Tunisia 1943", "Afrika Korps", "Mareth Line", "Kasserine Pass", "North Africa Campaign"]
    },
    # 1944
    "720": {
        "video_id": "6K-MuUu6L44",
        "event_en": "V1 Attacks",
        "event_de": "V1-Angriffe",
        "year": 1944,
        "date": "1944-06-16",
        "locations": ["London", "England", "Pas-de-Calais", "France", "Peenemünde"],
        "locations_de": ["London", "England", "Pas-de-Calais", "Frankreich", "Peenemünde"],
        "context_en": "V1 flying bombs ('Vergeltungswaffe 1') begin striking London. Nazi propaganda celebrates the 'wonder weapon' as retaliation for Allied bombing of German cities.",
        "context_de": "V1 Flugbomben ('Vergeltungswaffe 1') beginnen London zu treffen. Nazi-Propaganda feiert die 'Wunderwaffe'.",
        "tags_specific": ["V1", "Vergeltungswaffe", "Flying Bomb", "Buzz Bomb", "Doodlebug", "Wonder Weapon"]
    },
    "721": {
        "video_id": "W-UcQleew8Y",
        "event_en": "Bagration Begins",
        "event_de": "Bagration beginnt",
        "year": 1944,
        "date": "1944-06-23",
        "locations": ["Belarus", "Minsk", "Vitebsk", "Mogilev", "Eastern Front"],
        "locations_de": ["Weißrussland", "Minsk", "Witebsk", "Mogiljow", "Ostfront"],
        "context_en": "Operation Bagration - the massive Soviet summer offensive begins, destroying German Army Group Centre. The greatest German military defeat of the war unfolds.",
        "context_de": "Operation Bagration - die massive sowjetische Sommeroffensive beginnt und vernichtet die Heeresgruppe Mitte.",
        "tags_specific": ["Operation Bagration", "Belarus 1944", "Army Group Centre", "Minsk", "Soviet Offensive"]
    },
    "722": {
        "video_id": "bZkUPQHqyfg",
        "event_en": "Bagration",
        "event_de": "Bagration",
        "year": 1944,
        "date": "1944-06-30",
        "locations": ["Minsk", "Belarus", "Bobruisk", "Eastern Front", "Soviet Union"],
        "locations_de": ["Minsk", "Weißrussland", "Bobruisk", "Ostfront", "Sowjetunion"],
        "context_en": "Continued coverage of Operation Bagration. Soviet forces liberate Minsk as German Army Group Centre collapses. 300,000 German soldiers killed or captured.",
        "context_de": "Fortsetzung Operation Bagration. Sowjetische Truppen befreien Minsk, Heeresgruppe Mitte bricht zusammen.",
        "tags_specific": ["Minsk Liberation", "Bagration", "Army Group Centre Destruction", "Bobruisk Pocket", "June 1944"]
    },
    "746": {
        "video_id": "jGz1kC1Z69A",
        "event_en": "Ardennes Offensive",
        "event_de": "Ardennenoffensive",
        "year": 1944,
        "date": "1944-12-16",
        "locations": ["Ardennes", "Belgium", "Bastogne", "Luxembourg", "Western Front"],
        "locations_de": ["Ardennen", "Belgien", "Bastogne", "Luxemburg", "Westfront"],
        "context_en": "Battle of the Bulge begins - Hitler's last major offensive in the West. German forces achieve initial surprise but the offensive ultimately fails at Bastogne.",
        "context_de": "Die Ardennenoffensive beginnt - Hitlers letzte große Offensive im Westen. Deutsche Truppen erreichen anfängliche Überraschung.",
        "tags_specific": ["Battle of the Bulge", "Ardennes 1944", "Bastogne", "Wacht am Rhein", "Winter 1944"]
    },
    # 1945
    "750": {
        "video_id": "w2UvksMOs3c",
        "event_en": "Vistula Offensive",
        "event_de": "Weichsel-Oder-Operation",
        "year": 1945,
        "date": "1945-01-12",
        "locations": ["Vistula", "Warsaw", "Poland", "Oder River", "Eastern Front"],
        "locations_de": ["Weichsel", "Warschau", "Polen", "Oder", "Ostfront"],
        "context_en": "Vistula-Oder Offensive - Soviet forces launch massive attack from the Vistula to the Oder. Warsaw is liberated as the Red Army advances 500km in three weeks.",
        "context_de": "Weichsel-Oder-Operation - Sowjetische Truppen starten Großoffensive. Warschau wird befreit, die Rote Armee rückt 500km vor.",
        "tags_specific": ["Vistula-Oder", "Warsaw Liberation", "January 1945", "Zhukov", "Eastern Front 1945"]
    },
    "751": {
        "video_id": "6YLPpJLgVXk",
        "event_en": "Eastern Collapse",
        "event_de": "Zusammenbruch im Osten",
        "year": 1945,
        "date": "1945-01-19",
        "locations": ["East Prussia", "Silesia", "Königsberg", "Breslau", "Germany"],
        "locations_de": ["Ostpreußen", "Schlesien", "Königsberg", "Breslau", "Deutschland"],
        "context_en": "Eastern Front collapses as Soviet forces enter German territory. Millions of German civilians flee westward in the largest refugee crisis in European history.",
        "context_de": "Ostfront bricht zusammen, sowjetische Truppen erreichen deutsches Territorium. Millionen fliehen nach Westen.",
        "tags_specific": ["East Prussia 1945", "German Refugees", "Königsberg", "Silesia", "Flight and Expulsion"]
    },
    "753": {
        "video_id": "iEEvt-s1XhQ",
        "event_en": "Yalta Conference",
        "event_de": "Konferenz von Jalta",
        "year": 1945,
        "date": "1945-02-04",
        "locations": ["Yalta", "Crimea", "Soviet Union", "Livadia Palace"],
        "locations_de": ["Jalta", "Krim", "Sowjetunion", "Liwadija-Palast"],
        "context_en": "Coverage of the Yalta Conference where Roosevelt, Churchill, and Stalin meet to discuss post-war Europe. Nazi propaganda portrays it as the 'enemy conspiracy'.",
        "context_de": "Berichterstattung zur Konferenz von Jalta. Roosevelt, Churchill und Stalin diskutieren das Nachkriegseuropa.",
        "tags_specific": ["Yalta Conference", "Big Three", "Roosevelt", "Churchill", "Stalin", "February 1945"]
    },
    "754": {
        "video_id": "H_n_mS-eKps",
        "event_en": "Dresden Bombed",
        "event_de": "Dresden bombardiert",
        "year": 1945,
        "date": "1945-02-13",
        "locations": ["Dresden", "Saxony", "Elbe River", "Germany"],
        "locations_de": ["Dresden", "Sachsen", "Elbe", "Deutschland"],
        "context_en": "Allied firebombing of Dresden kills tens of thousands. Nazi propaganda uses the destruction of the 'Florence of the Elbe' for propaganda purposes.",
        "context_de": "Alliierte Brandbomben auf Dresden töten Zehntausende. Nazi-Propaganda nutzt die Zerstörung des 'Elb-Florenz'.",
        "tags_specific": ["Dresden Bombing", "February 1945", "Firebombing", "Florence of the Elbe", "RAF Bomber Command"]
    }
}

def get_youtube():
    with open(OAUTH_FILE, 'r') as f:
        td = json.load(f)
    creds = Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    )
    return build('youtube', 'v3', credentials=creds)

def generate_title(nr, data):
    """Generate Format A title: Wochenschau Nr. XXX: Event (YYYY) | 8K | @remAIke_IT"""
    return f"Wochenschau Nr. {nr}: {data['event_en']} ({data['year']}) | 8K | @remAIke_IT"

def generate_description(nr, data):
    """Generate individual historical description with locations"""
    locations_str = ", ".join(data['locations'][:5])
    locations_de_str = ", ".join(data['locations_de'][:5])
    
    return f"""🎬 Die Deutsche Wochenschau Nr. {nr} ({data['date']}) | {data['event_en']} | 8K

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🗺️ LOCATIONS: {locations_str}
📍 ORTE: {locations_de_str}

🇩🇪 {data['event_de']}
{data['context_de']}
Original NS-Propaganda aus dem Bundesarchiv in 8K restauriert.

🇺🇸 {data['event_en']}
{data['context_en']}
Nazi propaganda from German Federal Archives, restored in stunning 8K quality.

📅 Date: {data['date']} | Wochenschau Nr. {nr}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you found this historically valuable!
💬 COMMENT: What do you know about this event?
🔔 SUBSCRIBE @remAIke_IT for complete WWII archives!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at https://frai.tv | @remAIke_IT

#Wochenschau #WWII #WW2 #{data['event_en'].replace(' ', '')} #{data['year']} #8K #HistoricalFootage"""

def generate_tags(nr, data):
    """Generate individual tags for each video"""
    base_tags = [
        "Wochenschau",
        "Deutsche Wochenschau",
        f"Wochenschau Nr {nr}",
        f"Wochenschau {nr}",
        data['event_en'],
        data['event_de'],
    ]
    
    # Add location tags
    location_tags = data['locations'][:3]
    
    # Add specific tags
    specific_tags = data.get('tags_specific', [])
    
    # Add year and common tags
    common_tags = [
        str(data['year']),
        "WWII",
        "World War 2",
        "Nazi Germany",
        "German Newsreel",
        "8K",
        "Historical Documentary",
        "Bundesarchiv",
        "Third Reich"
    ]
    
    # Combine all, remove duplicates, limit to 15
    all_tags = base_tags + location_tags + specific_tags + common_tags
    seen = set()
    unique_tags = []
    for tag in all_tags:
        if tag.lower() not in seen and len(unique_tags) < 15:
            seen.add(tag.lower())
            unique_tags.append(tag)
    
    return unique_tags

def main():
    apply_mode = '--apply' in sys.argv
    
    print("=" * 70)
    print("WOCHENSCHAU COMPLETE UPDATE - FORMAT A")
    print("Individual Historical Content for Each Video")
    print("=" * 70)
    
    updates = []
    
    for nr, data in sorted(VIDEO_DATA.items(), key=lambda x: int(x[0])):
        title = generate_title(nr, data)
        description = generate_description(nr, data)
        tags = generate_tags(nr, data)
        
        updates.append({
            'nr': nr,
            'video_id': data['video_id'],
            'title': title,
            'description': description,
            'tags': tags,
            'locations': data['locations']
        })
        
        print(f"\n{'='*60}")
        print(f"Nr. {nr}: {data['event_en']}")
        print(f"{'='*60}")
        print(f"Video ID: {data['video_id']}")
        print(f"\nTITLE ({len(title)} chars):")
        print(f"  {title}")
        print(f"\nLOCATIONS: {', '.join(data['locations'][:4])}")
        print(f"\nTAGS ({len(tags)}):")
        print(f"  {tags[:8]}...")
        print(f"\nDESCRIPTION (first 300 chars):")
        print(f"  {description[:300]}...")
    
    print(f"\n{'='*70}")
    print(f"TOTAL: {len(updates)} videos to update")
    print(f"{'='*70}")
    
    if not apply_mode:
        print("\n⚠️ DRY RUN - run with --apply to update all videos")
        
        # Save update plan
        with open('config/wochenschau_update_plan.json', 'w', encoding='utf-8') as f:
            json.dump(updates, f, indent=2, ensure_ascii=False)
        print(f"✅ Update plan saved to config/wochenschau_update_plan.json")
        return
    
    # Apply updates
    print("\n🚀 APPLYING UPDATES...")
    yt = get_youtube()
    
    success = 0
    failed = 0
    
    for update in updates:
        print(f"\n📝 Updating Nr. {update['nr']}...")
        
        try:
            # Get current category
            current = yt.videos().list(part='snippet', id=update['video_id']).execute()
            if not current['items']:
                print(f"   ❌ Video not found!")
                failed += 1
                continue
            
            category_id = current['items'][0]['snippet']['categoryId']
            
            # Update video
            response = yt.videos().update(
                part='snippet',
                body={
                    'id': update['video_id'],
                    'snippet': {
                        'title': update['title'],
                        'description': update['description'],
                        'tags': update['tags'],
                        'categoryId': category_id
                    }
                }
            ).execute()
            
            print(f"   ✅ Updated: {response['snippet']['title'][:50]}...")
            success += 1
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            failed += 1
    
    print(f"\n{'='*70}")
    print(f"COMPLETE!")
    print(f"  ✅ Success: {success}")
    print(f"  ❌ Failed: {failed}")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
