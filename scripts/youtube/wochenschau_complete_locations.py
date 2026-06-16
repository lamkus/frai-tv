#!/usr/bin/env python3
"""
Erweitertes Location-Mapping für ALLE 252 Wochenschau-Episoden
Basierend auf historischen Events
"""

import json

# Lade existierendes Mapping
with open('config/wochenschau_complete_upload_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

videos = db['videos']

# VOLLSTÄNDIGES EVENT → LOCATION MAPPING
# Jedes Event bekommt einen historisch korrekten Ort
EVENT_LOCATIONS = {
    # === VORKRIEG (1939) ===
    'Pre-War Era': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Nazi-Soviet Pact': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    
    # === POLEN (Sep 1939) ===
    'War Begins': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Poland Campaign': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Warsaw Encircled': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Fall of Warsaw': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Warsaw Victory': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Poland Occupied': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    
    # === SITZKRIEG / PHONEY WAR (Winter 1939/40) ===
    'Bürgerbräu Bomb': {'lat': 48.1351, 'lng': 11.582, 'desc': 'Munich, Germany'},
    'Winter War Begins': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Helsinki, Finland'},
    'Winter War': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    'Phoney War': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Altmark Incident': {'lat': 58.9690, 'lng': 5.7331, 'desc': 'Jøssingfjord, Norway'},
    'Finland Front': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    'Winter War Ends': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Atlantic Naval War': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    'War Preparations': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # === NORWEGEN (Apr-Jun 1940) ===
    'Norway Invasion': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Oslo, Norway'},
    'Battle of Narvik': {'lat': 68.4385, 'lng': 17.4272, 'desc': 'Narvik, Norway'},
    'Norway Campaign': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Norway'},
    'Norway Victory': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Norway'},
    
    # === WESTFELDZUG (Mai-Jun 1940) ===
    'Western Campaign': {'lat': 50.8503, 'lng': 4.3517, 'desc': 'Belgium'},
    'Rotterdam Blitz': {'lat': 51.9244, 'lng': 4.4777, 'desc': 'Rotterdam, Netherlands'},
    'Holland Falls': {'lat': 52.0907, 'lng': 5.1214, 'desc': 'Netherlands'},
    'Belgium Falls': {'lat': 50.8503, 'lng': 4.3517, 'desc': 'Brussels, Belgium'},
    'Sedan Advance': {'lat': 49.7017, 'lng': 4.9403, 'desc': 'Sedan, France'},
    'Ardennes Breakthrough': {'lat': 49.7017, 'lng': 4.9403, 'desc': 'Ardennes, France'},
    'Dunkirk Pocket': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    'Dunkirk Evacuation': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    'France Collapsing': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'Paris Falls': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'French Armistice': {'lat': 49.4272, 'lng': 2.8322, 'desc': 'Compiègne, France'},
    'Channel Islands': {'lat': 49.4657, 'lng': -2.5853, 'desc': 'Channel Islands'},
    'Berlin Parade': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # === LUFTSCHLACHT UM ENGLAND (Jul-Okt 1940) ===
    'Battle of Britain': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Channel Battles': {'lat': 50.9, 'lng': 1.4, 'desc': 'English Channel'},
    'Eagle Day': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'England'},
    'Eagle Day Planning': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'England'},
    'Battle Peak': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'England'},
    'London Blitz': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'London Bombed': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Blitz Continues': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Berlin Retaliation': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Sea Lion Postponed': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Sea Lion Cancelled': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    
    # === ATLANTIK & U-BOOT-KRIEG ===
    'U-Boat Victories': {'lat': 54.3233, 'lng': 10.1228, 'desc': 'Kiel, Germany'},
    'U-Boat War': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    'Convoy Battles': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    
    # === DIPLOMATIE (1940) ===
    'Tripartite Pact': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Hendaye Meeting': {'lat': 43.3619, 'lng': -1.7740, 'desc': 'Hendaye, France'},
    'Vienna Award': {'lat': 48.2082, 'lng': 16.3738, 'desc': 'Vienna, Austria'},
    
    # === BALKAN (1940-1941) ===
    'Greece War': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Athens, Greece'},
    'Greece Campaign': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Greece'},
    'Greece Falls': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Athens, Greece'},
    'Yugoslavia Crisis': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
    'Yugoslavia Campaign': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Yugoslavia'},
    'Belgrade Falls': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
    'Balkans Campaign': {'lat': 42.0, 'lng': 22.0, 'desc': 'Balkans'},
    'Crete Invasion': {'lat': 35.2401, 'lng': 24.8093, 'desc': 'Crete, Greece'},
    'Crete Victory': {'lat': 35.2401, 'lng': 24.8093, 'desc': 'Crete, Greece'},
    'Bulgaria Joins Axis': {'lat': 42.6977, 'lng': 23.3219, 'desc': 'Sofia, Bulgaria'},
    'Romania Alliance': {'lat': 44.4268, 'lng': 26.1025, 'desc': 'Bucharest, Romania'},
    'Hungary Alliance': {'lat': 47.4979, 'lng': 19.0402, 'desc': 'Budapest, Hungary'},
    
    # === AFRIKA (1941-1943) ===
    'Africa Campaign': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Corps': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Offensive': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Rommel Arrives': {'lat': 32.9, 'lng': 13.18, 'desc': 'Tripoli, Libya'},
    'Tobruk Falls': {'lat': 32.0833, 'lng': 23.95, 'desc': 'Tobruk, Libya'},
    'Tobruk Siege': {'lat': 32.0833, 'lng': 23.95, 'desc': 'Tobruk, Libya'},
    'El Alamein': {'lat': 30.8333, 'lng': 28.95, 'desc': 'El Alamein, Egypt'},
    'Tunisia Battles': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunisia'},
    'Africa Retreat': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Defeat': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunisia'},
    
    # === OSTFRONT (1941) ===
    'Barbarossa': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Eastern Front'},
    'Barbarossa Begins': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Soviet Invasion': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Soviet Union'},
    'Minsk Battle': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Minsk, Belarus'},
    'Smolensk Battle': {'lat': 54.7826, 'lng': 32.0453, 'desc': 'Smolensk, Russia'},
    'Kiev Encirclement': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Battle': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Falls': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Leningrad Siege': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Moscow Offensive': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Moscow Battle': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Winter Crisis': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Eastern Front'},
    
    # === OSTFRONT (1942) ===
    'Spring Offensive': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Southern Russia'},
    'Crimea Campaign': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    'Sevastopol Siege': {'lat': 44.6167, 'lng': 33.5254, 'desc': 'Sevastopol, Crimea'},
    'Sevastopol Falls': {'lat': 44.6167, 'lng': 33.5254, 'desc': 'Sevastopol, Crimea'},
    'Kharkov': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Battle': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Victory': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Caucasus Advance': {'lat': 43.2567, 'lng': 42.4348, 'desc': 'Caucasus Mountains'},
    'Stalingrad': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Battle': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Encircled': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Disaster': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    
    # === OSTFRONT (1943) ===
    'Kharkov III': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kursk': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    'Kursk Battle': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    'Kursk Aftermath': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    'Eastern Retreat': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Ukraine'},
    'Dnieper Line': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Dnieper River, Ukraine'},
    'Ukraine Retreat': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Ukraine'},
    
    # === ITALIEN (1943-1944) ===
    'Sicily Invasion': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Italy Campaign': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'Mussolini Rescued': {'lat': 42.4605, 'lng': 13.5628, 'desc': 'Gran Sasso, Italy'},
    'Salerno': {'lat': 40.6824, 'lng': 14.7681, 'desc': 'Salerno, Italy'},
    'Anzio': {'lat': 41.4475, 'lng': 12.6323, 'desc': 'Anzio, Italy'},
    'Monte Cassino': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Rome Falls': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    'Gothic Line': {'lat': 44.0, 'lng': 11.5, 'desc': 'Northern Italy'},
    
    # === OSTFRONT (1944) ===
    'Bagration': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Belarus'},
    'Bagration Begins': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Belarus'},
    'Belarus Liberated': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Minsk, Belarus'},
    'Baltic States': {'lat': 56.9496, 'lng': 24.1052, 'desc': 'Riga, Latvia'},
    'Eastern Collapse': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Vistula Offensive': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Warsaw Uprising': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    
    # === D-DAY & WESTFRONT (1944) ===
    'D-Day': {'lat': 49.3385, 'lng': -0.8638, 'desc': 'Omaha Beach, Normandy'},
    'Normandy': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Normandy Battles': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'V1 Attacks': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'V2 Attacks': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    '20 July Plot': {'lat': 54.0833, 'lng': 21.1167, 'desc': "Wolf's Lair, East Prussia"},
    'Paris Liberated': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'Arnhem': {'lat': 51.9851, 'lng': 5.8987, 'desc': 'Arnhem, Netherlands'},
    'Ardennes Offensive': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    'Battle of Bulge': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    
    # === ENDPHASE (1945) ===
    'Yalta Conference': {'lat': 44.4952, 'lng': 34.1615, 'desc': 'Yalta, Crimea'},
    'Dresden Bombed': {'lat': 51.0504, 'lng': 13.7373, 'desc': 'Dresden, Germany'},
    'Oder Offensive': {'lat': 52.52, 'lng': 13.405, 'desc': 'Oder River, Germany'},
    'Final Defense': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Final Days': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Final Newsreel': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Last Newsreel': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # === HEIMATFRONT & ALLGEMEIN ===
    'Home Front': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'War Industry': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Total War': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Volkssturm': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'New Year': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Christmas': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Hitler Speech': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # === WEITERE EVENTS (aus Fehlerliste) ===
    # Luftangriffe
    '1000 Bombers Cologne': {'lat': 50.9375, 'lng': 6.9603, 'desc': 'Cologne, Germany'},
    'Berlin Bombed': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Big Week': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},  # Allied bombing week
    'Baedeker Raids': {'lat': 54.3233, 'lng': 10.1228, 'desc': 'Lübeck, Germany'},
    'Hamburg Firestorm': {'lat': 53.5511, 'lng': 9.9937, 'desc': 'Hamburg, Germany'},
    
    # Aachen
    'Aachen Battle': {'lat': 50.7753, 'lng': 6.0839, 'desc': 'Aachen, Germany'},
    'Aachen Falls': {'lat': 50.7753, 'lng': 6.0839, 'desc': 'Aachen, Germany'},
    
    # Afrika
    'Africa Surrender': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunis, Tunisia'},
    
    # Luft
    'Air Supremacy Lost': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    
    # Ardennen
    'Ardennes Fails': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    'Ardennes Peak': {'lat': 50.0833, 'lng': 5.7833, 'desc': 'Bastogne, Belgium'},
    'Ardennes Planning': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Ardennes Ready': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    
    # Griechenland
    'Athens Occupied': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Athens, Greece'},
    
    # Diplomatie/Konferenzen
    'Atlantic Charter': {'lat': 47.5615, 'lng': -52.7126, 'desc': 'Newfoundland, Canada'},
    'Atlantic Wall': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Auschwitz Liberated': {'lat': 50.0343, 'lng': 19.1783, 'desc': 'Auschwitz, Poland'},
    
    # Wetter/Gelände
    'Autumn Mud': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Eastern Front'},
    'Summer Campaign': {'lat': 50.0, 'lng': 36.0, 'desc': 'Eastern Front'},
    
    # Jugoslawien
    'Belgrade Coup': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
    
    # Marine
    'Bismarck Sails': {'lat': 54.37, 'lng': 10.13, 'desc': 'Kiel/Gdynia, Germany'},
    'Bismarck Sunk': {'lat': 48.1, 'lng': -16.2, 'desc': 'Atlantic Ocean'},
    'Graf Spee': {'lat': -34.8941, 'lng': -56.1866, 'desc': 'Montevideo, Uruguay'},
    'Tirpitz': {'lat': 69.7, 'lng': 19.0, 'desc': 'Tromsø, Norway'},
    
    # Verschiedene Schlachten
    'Brusilov Offensive': {'lat': 50.0, 'lng': 36.0, 'desc': 'Eastern Front'},
    'Budapest Siege': {'lat': 47.4979, 'lng': 19.0402, 'desc': 'Budapest, Hungary'},
    'Budenny Encircled': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Cassino Bombing': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    
    # Ostfront
    'Collapse East': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Eastern Front'},
    'Crimea Cleared': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    'Crimea Lost': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    
    # D-Day und Folgen
    'D-Day Aftermath': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'D-Day Response': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    
    # Diplomatie
    'Danzig Crisis': {'lat': 54.352, 'lng': 18.6466, 'desc': 'Danzig (Gdańsk), Poland'},
    'Declaration of War': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # Dnieper
    'Dnieper Battles': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Dnieper River, Ukraine'},
    'Dnieper Crossing': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Dnieper River, Ukraine'},
    
    # Donbass
    'Donbass': {'lat': 48.0, 'lng': 37.8, 'desc': 'Donbass, Ukraine'},
    'Don Advance': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Don River, Russia'},
    
    # Weitere Ostfront
    'East Offensive': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'East Stabilizing': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Defense': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Stalemate': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    
    # Endphase
    'End Nearing': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # Frankreich
    'France Advance': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'France Retreat': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'France Battles': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    
    # Gustav-Linie
    'Gustav Line': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    
    # Heimatfront
    'Goebbels Speech': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Harvest Time': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    
    # Italien
    'Italy Surrenders': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    'Italy Invasion': {'lat': 40.6824, 'lng': 14.7681, 'desc': 'Salerno, Italy'},
    'Italy Defense': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'Italy Front': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'Italy Stalemate': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    
    # Japan
    'Japan War': {'lat': 35.6762, 'lng': 139.6503, 'desc': 'Tokyo, Japan'},
    
    # Kaukasus
    'Caucasus Retreat': {'lat': 43.2567, 'lng': 42.4348, 'desc': 'Caucasus Mountains'},
    
    # Kerch
    'Kerch Victory': {'lat': 45.3531, 'lng': 36.4689, 'desc': 'Kerch, Crimea'},
    
    # Kiew
    'Kyiv Recaptured': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    
    # Leningrad
    'Leningrad Relief': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad Freed': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    
    # Mittelmeer
    'Malta Siege': {'lat': 35.8989, 'lng': 14.5146, 'desc': 'Malta'},
    'Mediterranean War': {'lat': 35.8989, 'lng': 14.5146, 'desc': 'Mediterranean Sea'},
    
    # Moskau
    'Moscow Stalled': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Moscow Winter': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    
    # Niederlande
    'Netherlands Falls': {'lat': 52.0907, 'lng': 5.1214, 'desc': 'Netherlands'},
    
    # Normandie
    'Normandy Collapse': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Normandy Defense': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Normandy Landing': {'lat': 49.3385, 'lng': -0.8638, 'desc': 'Omaha Beach, Normandy'},
    
    # Pearl Harbor
    'Pearl Harbor': {'lat': 21.3647, 'lng': -157.9507, 'desc': 'Pearl Harbor, Hawaii'},
    
    # Pazifik
    'Pacific War': {'lat': 35.6762, 'lng': 139.6503, 'desc': 'Pacific Ocean'},
    
    # Propaganda
    'Propaganda': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Propaganda Reel': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # Reich
    'Reich Contracts': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Reich Defense': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Reich Interior': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    
    # Rhein
    'Rhine Crossed': {'lat': 50.9375, 'lng': 6.9603, 'desc': 'Rhine River, Germany'},
    'Rhine Defense': {'lat': 50.9375, 'lng': 6.9603, 'desc': 'Rhine River, Germany'},
    
    # Rostov
    'Rostov': {'lat': 47.2357, 'lng': 39.7015, 'desc': 'Rostov-on-Don, Russia'},
    'Rostov Lost': {'lat': 47.2357, 'lng': 39.7015, 'desc': 'Rostov-on-Don, Russia'},
    'Rostov Retaken': {'lat': 47.2357, 'lng': 39.7015, 'desc': 'Rostov-on-Don, Russia'},
    
    # Rückzug
    'Retreat Continues': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Retreat East': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Retreat West': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Western Front'},
    
    # Russland
    'Russia Winter': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    
    # Seeblockade
    'Sea Blockade': {'lat': 54.3233, 'lng': 10.1228, 'desc': 'North Sea'},
    
    # Sewastopol
    'Sevastopol Lost': {'lat': 44.6167, 'lng': 33.5254, 'desc': 'Sevastopol, Crimea'},
    
    # Sizilien
    'Sicily Battles': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Sicily Defense': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Sicily Falls': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    
    # Skandinavien
    'Scandinavia': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Scandinavia'},
    
    # Somme
    'Somme Battle': {'lat': 49.9088, 'lng': 2.2973, 'desc': 'Somme, France'},
    
    # Sowjetunion
    'Soviet Counterattack': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    'Soviet Defense': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    'Soviet Offensive': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Soviet Resistance': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    'Soviet Summer': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Soviet Winter': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Russia'},
    
    # Stalingrad
    'Stalingrad Begins': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Continues': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Ends': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Hell': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Lost': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Peak': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Pocket': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Siege': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Street': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Supplies': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Surrender': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    
    # Strategisch
    'Strategic Bombing': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Strategic Retreat': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    
    # Sommer/Winter Kampagnen
    'Summer Battles': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Summer Offensive': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Winter Battles': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Winter Defense': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Winter Line': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Italy'},
    'Winter Offensive': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    
    # Totaler Krieg
    'Total War Declared': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # Verschiedene 1944-45
    'Two Fronts': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'US Entry': {'lat': 38.9072, 'lng': -77.0369, 'desc': 'Washington D.C., USA'},
    'US Enters War': {'lat': 38.9072, 'lng': -77.0369, 'desc': 'Washington D.C., USA'},
    
    # V-Waffen
    'V1 Launch': {'lat': 49.3, 'lng': 4.0, 'desc': 'Northern France'},
    'V2 Launch': {'lat': 53.9, 'lng': 12.5, 'desc': 'Peenemünde, Germany'},
    'V-Weapons': {'lat': 53.9, 'lng': 12.5, 'desc': 'Peenemünde, Germany'},
    
    # Verschiedene Siege
    'Victory Claims': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # Weichsel
    'Vistula Defense': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Vistula River, Poland'},
    'Vistula Front': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Vistula River, Poland'},
    
    # Wehrmacht
    'Wehrmacht': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Wehrmacht Advance': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Wehrmacht Retreat': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    
    # Westfront
    'West Front': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Western Front'},
    'West Retreat': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Western Front'},
    'Western Defense': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Western Front'},
    'Western Retreat': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Western Front'},
}

# Fallback für alle nicht gemappten Events: Berlin (Produktionsort)
DEFAULT_LOCATION = {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'}

# Erstelle vollständiges Mapping
complete_mapping = {}
unmapped_events = set()

for nr, v in videos.items():
    event = v.get('event_en', '')
    
    if event in EVENT_LOCATIONS:
        loc = EVENT_LOCATIONS[event]
    else:
        # Versuche partial match
        matched = False
        for key, loc_data in EVENT_LOCATIONS.items():
            if key.lower() in event.lower() or event.lower() in key.lower():
                loc = loc_data
                matched = True
                break
        
        if not matched:
            loc = DEFAULT_LOCATION
            unmapped_events.add(event)
    
    complete_mapping[nr] = {
        'number': int(nr),
        'date': v['date'],
        'event_en': event,
        'event_de': v.get('event_de', ''),
        'location': loc,
        'historical_note': v.get('historical_note', '')
    }

# Speichere
with open('config/wochenschau_complete_locations.json', 'w', encoding='utf-8') as f:
    json.dump(complete_mapping, f, indent=2, ensure_ascii=False)

print("=" * 70)
print("✅ WOCHENSCHAU LOCATIONS KOMPLETT")
print("=" * 70)
print(f"\n📍 Gemapped: {len(complete_mapping)} von {len(videos)} (100%)")
print(f"\n❓ Events mit Default-Location (Berlin): {len(unmapped_events)}")

if unmapped_events:
    print("\n   Nicht explizit gemappte Events:")
    for evt in sorted(unmapped_events)[:20]:
        print(f"      - {evt}")
    if len(unmapped_events) > 20:
        print(f"      ... und {len(unmapped_events)-20} weitere")

print(f"\n💾 Gespeichert: config/wochenschau_complete_locations.json")
