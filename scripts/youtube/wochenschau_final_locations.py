#!/usr/bin/env python3
"""
FINALES VOLLSTÄNDIGES Location-Mapping für ALLE 252 Wochenschau-Episoden
Jedes Event hat eine historisch korrekte Geo-Location
"""

import json

# Lade existierendes Mapping
with open('config/wochenschau_complete_upload_database.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

videos = db['videos']

# 100% VOLLSTÄNDIGES EVENT → LOCATION MAPPING
# Alphabetisch sortiert für einfache Wartung
EVENT_LOCATIONS = {
    # A
    '1000 Bombers Cologne': {'lat': 50.9375, 'lng': 6.9603, 'desc': 'Cologne, Germany'},
    '900 Days Leningrad': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad (St. Petersburg), Russia'},
    'Aachen Battle': {'lat': 50.7753, 'lng': 6.0839, 'desc': 'Aachen, Germany'},
    'Aachen Falls': {'lat': 50.7753, 'lng': 6.0839, 'desc': 'Aachen, Germany'},
    'Africa Campaign': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Corps': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Defeat': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunis, Tunisia'},
    'Africa Offensive': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Retreat': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Africa Surrender': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunis, Tunisia'},
    'After Stalingrad': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad (Volgograd), Russia'},
    'Air Supremacy Lost': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Altmark Incident': {'lat': 58.9690, 'lng': 5.7331, 'desc': 'Jøssingfjord, Norway'},
    'Anzio Landing': {'lat': 41.4475, 'lng': 12.6323, 'desc': 'Anzio, Italy'},
    'Ardennes Fails': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    'Ardennes Offensive': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    'Ardennes Peak': {'lat': 50.0833, 'lng': 5.7833, 'desc': 'Bastogne, Belgium'},
    'Ardennes Planning': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Ardennes Ready': {'lat': 50.2, 'lng': 5.8, 'desc': 'Ardennes, Belgium'},
    'Arnhem Victory': {'lat': 51.9851, 'lng': 5.8987, 'desc': 'Arnhem, Netherlands'},
    'Athens Occupied': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Athens, Greece'},
    'Atlantic Charter': {'lat': 47.5615, 'lng': -52.7126, 'desc': 'Newfoundland, Canada'},
    'Atlantic Naval War': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    'Atlantic Wall': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Auschwitz Liberated': {'lat': 50.0343, 'lng': 19.1783, 'desc': 'Auschwitz, Poland'},
    'Autumn Mud': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Eastern Front, Russia'},
    
    # B
    'Baedeker Raids': {'lat': 52.6269, 'lng': 1.2993, 'desc': 'Norwich, England'},
    'Bagration': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Minsk, Belarus'},
    'Bagration Begins': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Belarus'},
    'Balkans Campaign': {'lat': 42.0, 'lng': 22.0, 'desc': 'Balkans'},
    'Barbarossa Order': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Battle Peak': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Battle of Britain': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Battle of Narvik': {'lat': 68.4385, 'lng': 17.4272, 'desc': 'Narvik, Norway'},
    'Belgrade Coup': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
    'Belgrade Falls': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
    'Berlin Bombed': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Berlin Parade': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Berlin Retaliation': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Big Week': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Bismarck Sails': {'lat': 54.37, 'lng': 10.13, 'desc': 'Kiel, Germany'},
    'Bismarck Sunk': {'lat': 48.1, 'lng': -16.2, 'desc': 'Atlantic Ocean'},
    'Blitz Continues': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Bombs on Germany': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Budapest Encircled': {'lat': 47.4979, 'lng': 19.0402, 'desc': 'Budapest, Hungary'},
    'Bulgaria Joins Axis': {'lat': 42.6977, 'lng': 23.3219, 'desc': 'Sofia, Bulgaria'},
    'Bürgerbräu Bomb': {'lat': 48.1351, 'lng': 11.582, 'desc': 'Munich, Germany'},
    
    # C
    'Casablanca Summit': {'lat': 33.5731, 'lng': -7.5898, 'desc': 'Casablanca, Morocco'},
    'Case Blue': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Southern Russia'},
    'Cassino Bombed': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Cassino Falls': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Cassino Final': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Cassino III': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Caucasus Advance': {'lat': 43.2567, 'lng': 42.4348, 'desc': 'Caucasus Mountains'},
    'Caucasus Elbrus': {'lat': 43.3499, 'lng': 42.4453, 'desc': 'Mount Elbrus, Caucasus'},
    'Cerberus Success': {'lat': 50.9, 'lng': 1.4, 'desc': 'English Channel'},
    'Channel Battles': {'lat': 50.9, 'lng': 1.4, 'desc': 'English Channel'},
    'Channel Islands': {'lat': 49.4657, 'lng': -2.5853, 'desc': 'Channel Islands'},
    'Christmas 1940': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Christmas 1943': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Christmas Stalingrad': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Churchill-Stalin': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Citadel Planning': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Coventry Destroyed': {'lat': 52.4068, 'lng': -1.5197, 'desc': 'Coventry, England'},
    'Coventry Raid': {'lat': 52.4068, 'lng': -1.5197, 'desc': 'Coventry, England'},
    'Crete Captured': {'lat': 35.2401, 'lng': 24.8093, 'desc': 'Crete, Greece'},
    'Crimea Defense': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    'Crimea Evacuation': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    'Crimea Lost': {'lat': 44.9521, 'lng': 34.1024, 'desc': 'Crimea'},
    
    # D
    'D-Day': {'lat': 49.3385, 'lng': -0.8638, 'desc': 'Omaha Beach, Normandy'},
    'Dambuster Attack': {'lat': 51.4, 'lng': 8.3, 'desc': 'Möhne Dam, Germany'},
    'Dambuster Raid': {'lat': 51.4, 'lng': 8.3, 'desc': 'Möhne Dam, Germany'},
    'Demyansk Pocket': {'lat': 57.6378, 'lng': 32.4661, 'desc': 'Demyansk, Russia'},
    'Dieppe Raid': {'lat': 49.9242, 'lng': 1.0800, 'desc': 'Dieppe, France'},
    'Dnepr Battles': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Dnieper River, Ukraine'},
    'Dresden Bombed': {'lat': 51.0504, 'lng': 13.7373, 'desc': 'Dresden, Germany'},
    'Dunkirk Evacuation': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    'Dunkirk Pocket': {'lat': 51.0343, 'lng': 2.3768, 'desc': 'Dunkirk, France'},
    
    # E
    'Eagle Day': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'England'},
    'Eagle Day Planning': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'East Front Holds': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'East Prussia': {'lat': 54.3520, 'lng': 18.6466, 'desc': 'East Prussia'},
    'East Prussia Defense': {'lat': 54.3520, 'lng': 18.6466, 'desc': 'East Prussia'},
    'Eastern Advance': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Collapse': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Eastern Retreats': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Situation': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Spring': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Eastern Summer': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'El Alamein': {'lat': 30.8333, 'lng': 28.95, 'desc': 'El Alamein, Egypt'},
    'El Alamein Defeat': {'lat': 30.8333, 'lng': 28.95, 'desc': 'El Alamein, Egypt'},
    'El Alamein II': {'lat': 30.8333, 'lng': 28.95, 'desc': 'El Alamein, Egypt'},
    
    # F
    'Factory Battle': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Falaise Pocket': {'lat': 48.8955, 'lng': -0.1944, 'desc': 'Falaise, France'},
    'Fall of Warsaw': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Final Newsreel': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Finland Front': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    'Finland Surrenders': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Helsinki, Finland'},
    'France Collapsing': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'France Retreat': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'France'},
    'French Armistice': {'lat': 49.4272, 'lng': 2.8322, 'desc': 'Compiègne, France'},
    'Frost Hits': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    
    # G
    'Greece Victory': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Athens, Greece'},
    'Greece War': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Greece'},
    'Greek Disaster': {'lat': 37.9838, 'lng': 23.7275, 'desc': 'Greece'},
    'Gustav Line': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    
    # H
    'Hamburg Bombing': {'lat': 53.5511, 'lng': 9.9937, 'desc': 'Hamburg, Germany'},
    'Hamburg Firestorm': {'lat': 53.5511, 'lng': 9.9937, 'desc': 'Hamburg, Germany'},
    'Hendaye Meeting': {'lat': 43.3619, 'lng': -1.7740, 'desc': 'Hendaye, France'},
    'Heydrich Death': {'lat': 50.0755, 'lng': 14.4378, 'desc': 'Prague, Czechoslovakia'},
    'Heydrich Killed': {'lat': 50.0755, 'lng': 14.4378, 'desc': 'Prague, Czechoslovakia'},
    'Hitler Speech': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Hungary Joins Axis': {'lat': 47.4979, 'lng': 19.0402, 'desc': 'Budapest, Hungary'},
    'Hungary Occupied': {'lat': 47.4979, 'lng': 19.0402, 'desc': 'Budapest, Hungary'},
    
    # I
    'Invasion Expected': {'lat': 49.1829, 'lng': -0.3707, 'desc': 'Normandy, France'},
    'Italy Front': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'Italy Retreat': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Italy'},
    'Italy Surrenders': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    
    # J
    'July 20 Plot': {'lat': 54.0833, 'lng': 21.1167, 'desc': "Wolf's Lair, East Prussia"},
    
    # K
    'Katyn Discovery': {'lat': 54.7756, 'lng': 31.7919, 'desc': 'Katyn, Russia'},
    'Katyn Propaganda': {'lat': 54.7756, 'lng': 31.7919, 'desc': 'Katyn, Russia'},
    'Kharkov III': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Offensive': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Pocket': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Recaptured': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kharkov Victory': {'lat': 49.9935, 'lng': 36.2304, 'desc': 'Kharkov, Ukraine'},
    'Kiev Advance': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Battle': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Encirclement': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Liberated': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Kiev Surrender': {'lat': 50.4501, 'lng': 30.5234, 'desc': 'Kyiv, Ukraine'},
    'Korsun Pocket': {'lat': 49.1786, 'lng': 31.2513, 'desc': 'Korsun, Ukraine'},
    'Kursk Battle': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    'Kursk Buildup': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    'Kursk Cancelled': {'lat': 51.7373, 'lng': 36.1874, 'desc': 'Kursk, Russia'},
    
    # L
    'Last Offensive': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Lend-Lease Act': {'lat': 38.9072, 'lng': -77.0369, 'desc': 'Washington D.C., USA'},
    'Leningrad Encircled': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad Freed': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad Prep': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad Relief': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'Leningrad Siege': {'lat': 59.9343, 'lng': 30.3351, 'desc': 'Leningrad, Russia'},
    'London Blitz': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'London Bombed': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Lubeck Bombed': {'lat': 53.8655, 'lng': 10.6866, 'desc': 'Lübeck, Germany'},
    
    # M
    'Market Garden': {'lat': 51.9851, 'lng': 5.8987, 'desc': 'Arnhem, Netherlands'},
    'Midway Battle': {'lat': 28.2072, 'lng': -177.3735, 'desc': 'Midway Atoll, Pacific'},
    'Minsk Falls': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Minsk, Belarus'},
    'Minsk Liberated': {'lat': 53.9045, 'lng': 27.5615, 'desc': 'Minsk, Belarus'},
    'Molotov in Berlin': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Monte Cassino': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Monte Cassino II': {'lat': 41.4905, 'lng': 13.8134, 'desc': 'Monte Cassino, Italy'},
    'Moscow Advance': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Moscow Counterattack': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Moscow in Danger': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Mussolini Falls': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    'Mussolini Rescue': {'lat': 42.4605, 'lng': 13.5628, 'desc': 'Gran Sasso, Italy'},
    
    # N
    'Nazi-Soviet Pact': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'New Year 1941': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'New Year 1944': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'North Africa': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Northwind Offensive': {'lat': 48.8, 'lng': 7.8, 'desc': 'Alsace, France'},
    'Norway Invasion': {'lat': 59.9139, 'lng': 10.7522, 'desc': 'Oslo, Norway'},
    
    # O
    'Operation Barbarossa': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Soviet Union'},
    
    # P
    'Paris Falls': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'Paris Liberated': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'Paris Threatened': {'lat': 48.8566, 'lng': 2.3522, 'desc': 'Paris, France'},
    'Pearl Harbor': {'lat': 21.3647, 'lng': -157.9507, 'desc': 'Pearl Harbor, Hawaii'},
    'Phoney War': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Poland Campaign': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Poland Occupied': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Poland'},
    'Pre-War Era': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    
    # R
    'Reich Border': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Ring Operation': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Romania Surrenders': {'lat': 44.4268, 'lng': 26.1025, 'desc': 'Bucharest, Romania'},
    'Rome Falls': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    'Rome Offensive': {'lat': 41.9028, 'lng': 12.4964, 'desc': 'Rome, Italy'},
    'Rommel Arrives': {'lat': 32.9, 'lng': 13.18, 'desc': 'Tripoli, Libya'},
    'Rommel Offensive': {'lat': 32.0853, 'lng': 20.0, 'desc': 'North Africa'},
    'Rommel in Egypt': {'lat': 30.8333, 'lng': 28.95, 'desc': 'El Alamein, Egypt'},
    'Rostov Captured': {'lat': 47.2357, 'lng': 39.7015, 'desc': 'Rostov-on-Don, Russia'},
    'Rostov Falls Again': {'lat': 47.2357, 'lng': 39.7015, 'desc': 'Rostov-on-Don, Russia'},
    'Rotterdam Blitz': {'lat': 51.9244, 'lng': 4.4777, 'desc': 'Rotterdam, Netherlands'},
    'Ruhr Bombing': {'lat': 51.4556, 'lng': 7.0116, 'desc': 'Essen, Germany'},
    
    # S
    'Salerno Landing': {'lat': 40.6824, 'lng': 14.7681, 'desc': 'Salerno, Italy'},
    'Sea Lion Cancelled': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Sea Lion Postponed': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Sedan Advance': {'lat': 49.7017, 'lng': 4.9403, 'desc': 'Sedan, France'},
    'Sevastopol Falls': {'lat': 44.6167, 'lng': 33.5254, 'desc': 'Sevastopol, Crimea'},
    'Sicily Invasion': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Sicily Lost': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Sicily Preparation': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Sicily Retreat': {'lat': 37.5994, 'lng': 14.0154, 'desc': 'Sicily, Italy'},
    'Singapore Battle': {'lat': 1.3521, 'lng': 103.8198, 'desc': 'Singapore'},
    'Singapore Falls': {'lat': 1.3521, 'lng': 103.8198, 'desc': 'Singapore'},
    'Smolensk Falls': {'lat': 54.7826, 'lng': 32.0453, 'desc': 'Smolensk, Russia'},
    'Smolensk Freed': {'lat': 54.7826, 'lng': 32.0453, 'desc': 'Smolensk, Russia'},
    'Smolensk Pocket': {'lat': 54.7826, 'lng': 32.0453, 'desc': 'Smolensk, Russia'},
    'Soviet Counter': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Spring Offensive': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Southern Russia'},
    'Stalingrad Advance': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Agony': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Encircled': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Factories': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Hill': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Peak': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Pocket': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Reached': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Streets': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Stalingrad Surrender': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Strasbourg Liberated': {'lat': 48.5734, 'lng': 7.7521, 'desc': 'Strasbourg, France'},
    
    # T
    'Tehran Conference': {'lat': 35.6892, 'lng': 51.3890, 'desc': 'Tehran, Iran'},
    'Tikhvin Falls': {'lat': 59.6433, 'lng': 33.5309, 'desc': 'Tikhvin, Russia'},
    'Tobruk Battles': {'lat': 32.0833, 'lng': 23.95, 'desc': 'Tobruk, Libya'},
    'Tobruk Captured': {'lat': 32.0833, 'lng': 23.95, 'desc': 'Tobruk, Libya'},
    'Tobruk Falls': {'lat': 32.0833, 'lng': 23.95, 'desc': 'Tobruk, Libya'},
    'Torch Landing': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'North Africa'},
    'Total War': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Tripartite Pact': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Tunisia Battles': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunisia'},
    'Tunisia Final': {'lat': 36.8065, 'lng': 10.1815, 'desc': 'Tunisia'},
    'Typhoon Begins': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    
    # U
    'U-Boat Victories': {'lat': 54.3233, 'lng': 10.1228, 'desc': 'Kiel, Germany'},
    'U-Boat War': {'lat': 45.0, 'lng': -30.0, 'desc': 'Atlantic Ocean'},
    'US Enters War': {'lat': 38.9072, 'lng': -77.0369, 'desc': 'Washington D.C., USA'},
    
    # V
    'V1 Attacks': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'V2 Attacks': {'lat': 51.5074, 'lng': -0.1278, 'desc': 'London, England'},
    'Vistula Offensive': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Vistula River, Poland'},
    'Volkssturm': {'lat': 52.52, 'lng': 13.405, 'desc': 'Germany'},
    'Vyazma Pocket': {'lat': 55.2106, 'lng': 34.2816, 'desc': 'Vyazma, Russia'},
    
    # W
    'Wannsee Conference': {'lat': 52.4293, 'lng': 13.1658, 'desc': 'Berlin-Wannsee, Germany'},
    'War Begins': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'War Preparations': {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'},
    'Warsaw Encircled': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Warsaw Uprising': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Warsaw Victory': {'lat': 52.2297, 'lng': 21.0122, 'desc': 'Warsaw, Poland'},
    'Western Campaign': {'lat': 50.8503, 'lng': 4.3517, 'desc': 'Belgium'},
    'Winter Battles': {'lat': 55.0, 'lng': 30.0, 'desc': 'Eastern Front'},
    'Winter Crisis': {'lat': 55.7558, 'lng': 37.6173, 'desc': 'Moscow, Russia'},
    'Winter Storm': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Winter Storm Fails': {'lat': 48.708, 'lng': 44.5133, 'desc': 'Stalingrad, Russia'},
    'Winter War': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    'Winter War Begins': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Finland'},
    'Winter War Ends': {'lat': 60.1699, 'lng': 24.9384, 'desc': 'Helsinki, Finland'},
    
    # Y
    'Yalta Conference': {'lat': 44.4952, 'lng': 34.1615, 'desc': 'Yalta, Crimea'},
    'Yugoslavia Crisis': {'lat': 44.7866, 'lng': 20.4489, 'desc': 'Belgrade, Yugoslavia'},
}

# Erstelle vollständiges Mapping
complete_mapping = {}
unmapped_events = set()
mapped_count = 0
default_count = 0

DEFAULT_LOCATION = {'lat': 52.52, 'lng': 13.405, 'desc': 'Berlin, Germany'}

for nr, v in videos.items():
    event = v.get('event_en', '')
    
    if event in EVENT_LOCATIONS:
        loc = EVENT_LOCATIONS[event]
        mapped_count += 1
    else:
        loc = DEFAULT_LOCATION
        unmapped_events.add(event)
        default_count += 1
    
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
print("✅ WOCHENSCHAU LOCATIONS - FINALES MAPPING")
print("=" * 70)
print(f"\n📍 Explizit gemapped: {mapped_count} von {len(videos)}")
print(f"📍 Default (Berlin):  {default_count}")
print(f"📍 Coverage:          {(mapped_count/len(videos)*100):.1f}%")

if unmapped_events:
    print(f"\n❓ Noch mit Default-Location ({len(unmapped_events)} Events):")
    for evt in sorted(unmapped_events):
        print(f"      - '{evt}'")

print(f"\n💾 Gespeichert: config/wochenschau_complete_locations.json")

# Statistik nach Jahr
print("\n📅 LOCATIONS NACH JAHR:")
year_stats = {}
for nr, v in complete_mapping.items():
    year = v['date'][:4]
    loc_desc = v['location']['desc']
    if year not in year_stats:
        year_stats[year] = {'count': 0, 'locations': set()}
    year_stats[year]['count'] += 1
    year_stats[year]['locations'].add(loc_desc.split(',')[0])

for year in sorted(year_stats.keys()):
    locs = year_stats[year]['locations']
    print(f"   {year}: {year_stats[year]['count']} Episoden | {len(locs)} unique locations")
