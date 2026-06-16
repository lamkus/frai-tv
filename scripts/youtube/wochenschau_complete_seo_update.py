#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 WOCHENSCHAU COMPLETE SEO UPDATE - NACH REGELN UND 2026 RESEARCH
═══════════════════════════════════════════════════════════════════════════════

TEAM-DEBATTE (gemäß Agents.md):
────────────────────────────────────────────────────────────────────────────────
│ Rolle             │ Gewicht │ Position                                     │
├───────────────────┼─────────┼──────────────────────────────────────────────┤
│ Lead Architect    │   15    │ Keyword-First für Ranking                    │
│ SEO/Marketing     │   10    │ Datum im Titel, keine "Nr." - spart Zeichen  │
│ UX Design         │    3    │ Lesbarkeit: Event macht Titel interessanter  │
│ i18n              │    2    │ Multilingual Descriptions sind Pflicht       │
│ Data Engineering  │    7    │ Locations in Description für Local SEO       │
│ Documentation     │    3    │ Historische Korrektheit prüfen               │
└───────────────────┴─────────┴──────────────────────────────────────────────┘

ENTSCHEIDUNG: Titel-Formel (40 Punkte Gewicht)
────────────────────────────────────────────────────────────────────────────────
Wochenschau [NR]: [Event EN] ([DD.MM.YYYY]) | 8K | @remAIke_IT

Beispiel: Wochenschau 516: Battle of Britain (24.07.1940) | 8K | @remAIke_IT
          ^^^^^^^^^^                          ^^^^^^^^^^
          Position 0 (max SEO)                Datum inkludiert!

EXTERNE RESEARCH (ahrefs.com/blog/youtube-seo):
────────────────────────────────────────────────────────────────────────────────
1. "Use your keyword in the title" - Position 0-15 = 100% weight
2. "Keep titles under 60 characters" - Wichtig für mobile truncation
3. "90% of top ranking videos included target keyword in title"
4. Tags = MINIMAL role (YouTube official 2026)
5. Description first 160 chars = In search sichtbar
6. Chapters/Timestamps = Ranking signal seit 2021 Update

═══════════════════════════════════════════════════════════════════════════════
"""

import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'
EVENTS_FILE = 'config/wochenschau_events.json'

# ═══════════════════════════════════════════════════════════════════════════════
# MULTILINGUAL KEYWORDS - Wie suchen internationale User nach WWII Content?
# ═══════════════════════════════════════════════════════════════════════════════
# 
# RESEARCH FINDINGS (YouTube International SEO):
# - Tags in MULTIPLE LANGUAGES erhöhen Global Reach
# - Hindi: द्वितीय विश्व युद्ध (WWII), समाचार (newsreel)
# - Japanese: 第二次世界大戦, ニュース映画 (newsreel), ドイツ軍
# - Spanish: Segunda Guerra Mundial, noticiero alemán
# - Portuguese: Segunda Guerra, cinejornal alemão
# - Russian: Вторая мировая, немецкая кинохроника
# - Arabic: الحرب العالمية الثانية, ألمانيا النازية
# - Chinese: 二战, 德国新闻片
#
# ═══════════════════════════════════════════════════════════════════════════════

# Global search terms for WWII content by language
GLOBAL_WWII_TAGS = {
    'core': ['WWII', 'WW2', 'World War 2', 'World War II'],
    'german': ['Zweiter Weltkrieg', 'Deutsche Wochenschau', 'Drittes Reich', 'Nazi Deutschland'],
    'spanish': ['Segunda Guerra Mundial', 'noticiero alemán', 'Alemania Nazi'],
    'portuguese': ['Segunda Guerra', 'cinejornal', 'Alemanha nazista'],
    'french': ['Seconde Guerre mondiale', 'actualités allemandes', 'Troisième Reich'],
    'japanese': ['第二次世界大戦', 'ドイツ軍', 'ナチス'],  # Dai-ni-ji sekai taisen
    'russian': ['Вторая мировая война', 'немецкая кинохроника'],
    'hindi': ['द्वितीय विश्व युद्ध', 'नाज़ी जर्मनी'],
    'chinese': ['二战', '德国新闻', '纳粹德国'],
    'arabic': ['الحرب العالمية الثانية'],
}

# Event-specific translations for global reach
EVENT_TRANSLATIONS = {
    'Battle of Britain': {
        'de': 'Luftschlacht um England',
        'es': 'Batalla de Inglaterra',
        'pt': 'Batalha da Grã-Bretanha',
        'fr': 'Bataille d\'Angleterre',
        'ja': 'バトル・オブ・ブリテン',
        'ru': 'Битва за Британию',
    },
    'Fall of Paris': {
        'de': 'Fall von Paris',
        'es': 'Caída de París',
        'pt': 'Queda de Paris',
        'fr': 'Chute de Paris',
        'ja': 'パリ陥落',
        'ru': 'Падение Парижа',
    },
    'Dunkirk': {
        'de': 'Dünkirchen',
        'es': 'Dunkerque',
        'pt': 'Dunquerque',
        'fr': 'Dunkerque',
        'ja': 'ダンケルク',
        'ru': 'Дюнкерк',
    },
    'Dresden': {
        'de': 'Dresden',
        'es': 'Bombardeo de Dresde',
        'pt': 'Bombardeio de Dresden',
        'ja': 'ドレスデン爆撃',
        'ru': 'Бомбардировка Дрездена',
    },
    'Ardennes': {
        'de': 'Ardennenoffensive',
        'es': 'Batalla de las Ardenas',
        'pt': 'Batalha do Bulge',
        'ja': 'バルジの戦い',
        'ru': 'Арденнская операция',
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# WOCHENSCHAU HISTORICAL DATA - INDIVIDUELL PRO EPISODE + MULTILINGUAL
# ═══════════════════════════════════════════════════════════════════════════════

WOCHENSCHAU_DATA = {
    477: {
        'date': '11.10.1939',
        'event_en': 'Poland Occupied',
        'event_de': 'Polen besetzt',
        'locations': ['Warsaw', 'Kraków', 'Danzig', 'Poland', 'Warschau', 'Krakau', 'Polen'],
        'context_de': 'Nach dem Überfall am 01.09.1939 zeigt diese Ausgabe die vollständige Besetzung Polens. Deutsche Truppen in Warschau, Siegesparaden.',
        'context_en': 'Following the invasion on Sept 1, 1939, this newsreel shows the complete occupation of Poland. German troops in Warsaw, victory parades.',
        'tags': ['Poland 1939', 'Warsaw', 'Invasion of Poland', 'September Campaign', 'Fall Weiss', 'Warschau 1939'],
        # MULTILINGUAL: How do Indians, Japanese, Brazilians search for this?
        'tags_intl': ['Invasión de Polonia', 'Invasão da Polônia', 'ポーランド侵攻', 'पोलैंड पर आक्रमण', '波兰战役', 'Вторжение в Польшу']
    },
    480: {
        'date': '08.11.1939',
        'event_en': 'Bürgerbräukeller Bomb',
        'event_de': 'Bürgerbräu-Attentat',
        'locations': ['Munich', 'Bürgerbräukeller', 'München', 'Bavaria', 'Bayern'],
        'context_de': 'Berichterstattung über das Attentat auf Hitler durch Georg Elser am 08.11.1939 im Münchner Bürgerbräukeller. Hitler verließ 13 Minuten vor der Explosion.',
        'context_en': 'Coverage of Georg Elser\'s assassination attempt on Hitler at Munich\'s Bürgerbräukeller on Nov 8, 1939. Hitler left 13 minutes before the explosion.',
        'tags': ['Georg Elser', 'Munich 1939', 'Assassination attempt', 'Bürgerbräukeller', 'Hitler'],
        'tags_intl': ['Atentado contra Hitler', 'ヒトラー暗殺未遂', 'Покушение на Гитлера', 'Tentativa de assassinato']
    },
    482: {
        'date': '30.11.1939',
        'event_en': 'Winter War Begins',
        'event_de': 'Winterkrieg beginnt',
        'locations': ['Finland', 'Soviet Union', 'Karelia', 'Helsinki', 'Finnland', 'Sowjetunion', 'Karelien'],
        'context_de': 'Sowjetischer Angriff auf Finnland am 30.11.1939. Der Winterkrieg beginnt. Deutsche Sympathie für Finnland.',
        'context_en': 'Soviet attack on Finland on Nov 30, 1939. The Winter War begins. German sympathy for Finland shown.',
        'tags': ['Winter War', 'Finland 1939', 'Soviet invasion', 'Talvisota', 'Mannerheim Line'],
        'tags_intl': ['Guerra de Invierno', '冬戦争', 'Зимняя война', 'Guerra de Inverno', 'सर्दी का युद्ध']
    },
    483: {
        'date': '06.12.1939',
        'event_en': 'Winter War',
        'event_de': 'Winterkrieg',
        'locations': ['Finland', 'Karelia', 'Mannerheim Line', 'Finnland', 'Karelien'],
        'context_de': 'Fortsetzung der Berichterstattung über den sowjetisch-finnischen Winterkrieg. Finnischer Widerstand an der Mannerheim-Linie.',
        'context_en': 'Continued coverage of the Soviet-Finnish Winter War. Finnish resistance at the Mannerheim Line.',
        'tags': ['Winter War', 'Finland', 'Mannerheim Line', 'Talvisota', 'Finnish resistance'],
        'tags_intl': ['Guerra de Invierno', '冬戦争', 'Зимняя война', 'Linha Mannerheim']
    },
    488: {
        'date': '10.01.1940',
        'event_en': 'Phoney War',
        'event_de': 'Sitzkrieg',
        'locations': ['Western Front', 'Maginot Line', 'Westfront', 'Siegfried Line', 'France', 'Frankreich'],
        'context_de': 'Ruhephase an der Westfront - der "Sitzkrieg". Propaganda zeigt deutsche Stärke an der Siegfriedlinie.',
        'context_en': 'Quiet phase on the Western Front - the "Phoney War". Propaganda shows German strength at the Siegfried Line.',
        'tags': ['Phoney War', 'Sitzkrieg', 'Drôle de guerre', 'Western Front 1940', 'Maginot Line'],
        'tags_intl': ['Guerra de broma', 'まやかしの戦争', 'Странная война', 'Guerra de mentira']
    },
    508: {
        'date': '29.05.1940',
        'event_en': 'Dunkirk Pocket',
        'event_de': 'Kessel von Dünkirchen',
        'locations': ['Dunkirk', 'Dünkirchen', 'Belgium', 'Belgien', 'English Channel', 'Ärmelkanal', 'France'],
        'context_de': 'Einschließung der alliierten Truppen bei Dünkirchen. Der berühmte "Halt-Befehl" ermöglicht die spätere Evakuierung.',
        'context_en': 'Encirclement of Allied troops at Dunkirk. The famous "Halt Order" would later enable the evacuation.',
        'tags': ['Dunkirk 1940', 'Dünkirchen', 'Fall Gelb', 'BEF', 'Dunkirk pocket', 'Operation Dynamo'],
        'tags_intl': ['Batalla de Dunkerque', 'ダンケルクの戦い', 'Дюнкеркская операция', 'Batalha de Dunquerque']
    },
    509: {
        'date': '05.06.1940',
        'event_en': 'Dunkirk Evacuation',
        'event_de': 'Evakuierung Dünkirchen',
        'locations': ['Dunkirk', 'Dünkirchen', 'English Channel', 'Dover', 'France', 'England'],
        'context_de': 'Operation Dynamo - Evakuierung von 338.000 alliierten Soldaten aus Dünkirchen. Deutsche Propaganda betont die Niederlage.',
        'context_en': 'Operation Dynamo - evacuation of 338,000 Allied soldiers from Dunkirk. German propaganda emphasizes the defeat.',
        'tags': ['Dunkirk evacuation', 'Operation Dynamo', 'Little ships', 'Dunkirk 1940', 'BEF evacuation'],
        'tags_intl': ['Evacuación de Dunkerque', 'ダンケルク撤退', 'Дюнкеркская эвакуация', 'Evacuação de Dunquerque']
    },
    511: {
        'date': '14.06.1940',
        'event_en': 'Paris Falls',
        'event_de': 'Paris fällt',
        'locations': ['Paris', 'Eiffel Tower', 'Arc de Triomphe', 'Champs-Élysées', 'France', 'Frankreich'],
        'context_de': 'Deutsche Truppen marschieren in Paris ein. Ikonische Bilder am Eiffelturm und Arc de Triomphe. Frankreichs Hauptstadt ist gefallen.',
        'context_en': 'German troops enter Paris. Iconic footage at Eiffel Tower and Arc de Triomphe. France\'s capital has fallen.',
        'tags': ['Paris 1940', 'Fall of Paris', 'Eiffel Tower', 'German occupation', 'Fall of France'],
        'tags_intl': ['Caída de París', 'パリ陥落', 'Падение Парижа', 'Queda de Paris', 'पेरिस का पतन']
    },
    512: {
        'date': '22.06.1940',
        'event_en': 'French Armistice',
        'event_de': 'Waffenstillstand Frankreich',
        'locations': ['Compiègne', 'Railway Car', 'France', 'Frankreich', 'Rethondes'],
        'context_de': 'Unterzeichnung des Waffenstillstands in Compiègne im selben Eisenbahnwaggon wie 1918. Hitlers Triumph über Frankreich.',
        'context_en': 'Signing of armistice at Compiègne in the same railway car as 1918. Hitler\'s triumph over France.',
        'tags': ['French Armistice 1940', 'Compiègne', 'Armistice railway car', 'Fall of France', 'Hitler Compiègne'],
        'tags_intl': ['Armisticio francés', 'フランス休戦協定', 'Компьенское перемирие', 'Armistício francês']
    },
    513: {
        'date': '01.07.1940',
        'event_en': 'Channel Islands',
        'event_de': 'Kanalinseln besetzt',
        'locations': ['Jersey', 'Guernsey', 'Channel Islands', 'Kanalinseln', 'English Channel'],
        'context_de': 'Deutsche Besetzung der britischen Kanalinseln Jersey und Guernsey. Einziges britisches Territorium unter Nazi-Besatzung.',
        'context_en': 'German occupation of British Channel Islands Jersey and Guernsey. Only British territory under Nazi occupation.',
        'tags': ['Channel Islands 1940', 'Jersey', 'Guernsey', 'German occupation', 'British territory'],
        'tags_intl': ['Islas del Canal', 'チャンネル諸島占領', 'Оккупация Нормандских островов']
    },
    516: {
        'date': '24.07.1940',
        'event_en': 'Battle of Britain',
        'event_de': 'Luftschlacht um England',
        'locations': ['England', 'London', 'Dover', 'RAF', 'English Channel', 'Ärmelkanal', 'Luftwaffe'],
        'context_de': 'Beginn der Luftschlacht um England. Luftwaffe greift britische Konvois und Küsten an. Vorbereitung auf Operation Seelöwe.',
        'context_en': 'Beginning of Battle of Britain. Luftwaffe attacks British convoys and coasts. Preparation for Operation Sea Lion.',
        'tags': ['Battle of Britain', 'Luftschlacht', 'RAF', 'Luftwaffe', 'Summer 1940', 'Operation Sea Lion'],
        'tags_intl': ['Batalla de Inglaterra', 'バトル・オブ・ブリテン', 'Битва за Британию', 'Batalha da Grã-Bretanha', 'ब्रिटेन की लड़ाई']
    },
    521: {
        'date': '07.09.1940',
        'event_en': 'London Blitz',
        'event_de': 'London Blitz',
        'locations': ['London', 'East End', 'Thames', 'Docklands', 'England', 'Themse'],
        'context_de': 'Beginn des Blitz - massiver Luftangriff auf London. Bomben auf die Docks und East End. 430 Tote am ersten Tag.',
        'context_en': 'Start of the Blitz - massive air raid on London. Bombs on the Docks and East End. 430 dead on day one.',
        'tags': ['London Blitz', 'The Blitz', '1940 bombing', 'Luftwaffe', 'London 1940', 'East End'],
        'tags_intl': ['Blitz de Londres', 'ロンドン大空襲', 'Лондонский блиц', 'Bombardeio de Londres']
    },
    522: {
        'date': '14.09.1940',
        'event_en': 'Berlin Raid',
        'event_de': 'RAF Berlin Angriff',
        'locations': ['Berlin', 'Germany', 'Deutschland', 'RAF'],
        'context_de': 'RAF-Vergeltungsangriff auf Berlin nach dem Blitz. Hitler kündigt Vergeltung an. Eskalation des Luftkriegs.',
        'context_en': 'RAF retaliation raid on Berlin after the Blitz. Hitler announces revenge. Escalation of the air war.',
        'tags': ['Berlin bombing', 'RAF raid', 'Blitz retaliation', '1940 air war', 'Berlin 1940'],
        'tags_intl': ['Bombardeo de Berlín', 'ベルリン空襲', 'Бомбардировка Берлина']
    },
    523: {
        'date': '21.09.1940',
        'event_en': 'London Blitz',
        'event_de': 'London Blitz',
        'locations': ['London', 'Westminster', 'Buckingham Palace', 'Underground', 'England'],
        'context_de': 'Fortgesetzte Bombardierung Londons. Bilder von Zerstörung und britischem Durchhaltevermögen. Underground als Bunker.',
        'context_en': 'Continued bombing of London. Images of destruction and British resilience. Underground used as shelter.',
        'tags': ['London Blitz', 'Underground shelter', 'Buckingham Palace', 'British resilience', 'September 1940'],
        'tags_intl': ['Blitz de Londres', 'ロンドン大空襲', 'Bombardeio de Londres', 'लंदन ब्लिट्ज़']
    },
    524: {
        'date': '28.09.1940',
        'event_en': 'Sea Lion Cancelled',
        'event_de': 'Seelöwe abgesagt',
        'locations': ['English Channel', 'England', 'Germany', 'Ärmelkanal', 'Deutschland'],
        'context_de': 'Operation Seelöwe auf unbestimmte Zeit verschoben. Die Luftwaffe hat die Luftüberlegenheit nicht errungen. Wendepunkt.',
        'context_en': 'Operation Sea Lion postponed indefinitely. Luftwaffe failed to achieve air superiority. Turning point.',
        'tags': ['Operation Sea Lion', 'Seelöwe', 'Battle of Britain', 'Invasion cancelled', 'September 1940'],
        'tags_intl': ['Operación León Marino', 'あしか作戦', 'Операция Морской лев']
    },
    652: {
        'date': '17.03.1943',
        'event_en': 'Kharkov Retaken',
        'event_de': 'Charkow zurückerobert',
        'locations': ['Kharkov', 'Charkow', 'Ukraine', 'Eastern Front', 'Ostfront', 'Donets'],
        'context_de': 'Dritte Schlacht um Charkow. SS-Divisionen erobern die Stadt zurück. Letzter großer deutscher Sieg im Osten.',
        'context_en': 'Third Battle of Kharkov. SS divisions recapture the city. Last major German victory in the East.',
        'tags': ['Kharkov 1943', 'Third Battle of Kharkov', 'Charkow', 'SS Panzer', 'Eastern Front 1943'],
        'tags_intl': ['Batalla de Járkov', 'ハリコフの戦い', 'Третья битва за Харьков', 'Batalha de Carcóvia']
    },
    654: {
        'date': '01.04.1943',
        'event_en': 'Tunisia Battles',
        'event_de': 'Tunesien Kämpfe',
        'locations': ['Tunisia', 'Tunesien', 'North Africa', 'Nordafrika', 'Mareth Line', 'Kasserine'],
        'context_de': 'Kämpfe in Tunesien vor der Kapitulation des Afrikakorps. Rückzugsgefechte gegen britische und amerikanische Truppen.',
        'context_en': 'Fighting in Tunisia before Afrika Korps surrender. Rearguard actions against British and American forces.',
        'tags': ['Tunisia 1943', 'Afrika Korps', 'Rommel', 'North Africa', 'Mareth Line', 'Kasserine Pass'],
        'tags_intl': ['Campaña de Túnez', 'チュニジアの戦い', 'Тунисская кампания', 'Campanha da Tunísia']
    },
    720: {
        'date': '22.06.1944',
        'event_en': 'V1 Flying Bombs',
        'event_de': 'V1 Flugbomben',
        'locations': ['London', 'V1 launch sites', 'England', 'Pas-de-Calais', 'Vergeltungswaffe'],
        'context_de': 'V1-Vergeltungswaffe im Einsatz gegen London. "Vergeltung" für alliierte Bombenangriffe. Propaganda zeigt Erfolge.',
        'context_en': 'V1 flying bomb attacks on London. "Vengeance" for Allied bombing raids. Propaganda shows successes.',
        'tags': ['V1', 'Vergeltungswaffe', 'Flying bomb', 'Buzz bomb', 'Doodlebug', 'London 1944'],
        'tags_intl': ['Bomba voladora V1', 'V1飛行爆弾', 'Фау-1', 'Bomba voadora V1', 'वी-1 उड़ान बम']
    },
    721: {
        'date': '29.06.1944',
        'event_en': 'Bagration Begins',
        'event_de': 'Bagration beginnt',
        'locations': ['Belarus', 'Minsk', 'Weißrussland', 'Eastern Front', 'Ostfront', 'Vitebsk'],
        'context_de': 'Beginn der sowjetischen Operation Bagration. Größte Niederlage der Wehrmacht. 350.000 deutsche Soldaten eingekesselt.',
        'context_en': 'Start of Soviet Operation Bagration. Largest defeat of the Wehrmacht. 350,000 German soldiers encircled.',
        'tags': ['Operation Bagration', 'Belarus 1944', 'Minsk', 'Army Group Center', 'Soviet offensive'],
        'tags_intl': ['Operación Bagratión', 'バグラチオン作戦', 'Операция Багратион', 'Operação Bagration']
    },
    722: {
        'date': '06.07.1944',
        'event_en': 'Bagration',
        'event_de': 'Bagration',
        'locations': ['Belarus', 'Minsk', 'Weißrussland', 'Vilnius', 'Ostfront'],
        'context_de': 'Zusammenbruch der Heeresgruppe Mitte. Sowjetische Truppen befreien Minsk. Katastrophale deutsche Verluste.',
        'context_en': 'Collapse of Army Group Center. Soviet troops liberate Minsk. Catastrophic German losses.',
        'tags': ['Bagration', 'Minsk liberation', 'Army Group Center', 'July 1944', 'Eastern Front'],
        'tags_intl': ['Liberación de Minsk', 'ミンスク解放', 'Освобождение Минска']
    },
    746: {
        'date': '21.12.1944',
        'event_en': 'Battle of Bulge',
        'event_de': 'Ardennenoffensive',
        'locations': ['Ardennes', 'Ardennen', 'Bastogne', 'Belgium', 'Belgien', 'Luxembourg'],
        'context_de': 'Letzte große deutsche Offensive im Westen. Durchbruch bei Bastogne. "Wacht am Rhein" - Hitlers letzte Hoffnung.',
        'context_en': 'Last major German offensive in the West. Breakthrough at Bastogne. "Watch on the Rhine" - Hitler\'s last hope.',
        'tags': ['Battle of the Bulge', 'Ardennes 1944', 'Bastogne', 'Wacht am Rhein', 'December 1944'],
        'tags_intl': ['Batalla de las Ardenas', 'バルジの戦い', 'Арденнская операция', 'Batalha do Bulge', 'आर्डेन की लड़ाई']
    },
    750: {
        'date': '18.01.1945',
        'event_en': 'Vistula Offensive',
        'event_de': 'Weichsel-Oder',
        'locations': ['Vistula', 'Oder', 'Weichsel', 'Poland', 'Polen', 'Warsaw', 'Warschau'],
        'context_de': 'Sowjetische Weichsel-Oder-Operation. Rote Armee überrollt Ostpreußen und nähert sich der Oder.',
        'context_en': 'Soviet Vistula-Oder offensive. Red Army overruns East Prussia and approaches the Oder.',
        'tags': ['Vistula-Oder', 'January 1945', 'Soviet offensive', 'Red Army', 'East Prussia'],
        'tags_intl': ['Ofensiva Vístula-Oder', 'ヴィスワ・オーデル攻勢', 'Висло-Одерская операция']
    },
    751: {
        'date': '25.01.1945',
        'event_en': 'Eastern Collapse',
        'event_de': 'Zusammenbruch Ost',
        'locations': ['Eastern Front', 'Ostfront', 'Silesia', 'Schlesien', 'Breslau'],
        'context_de': 'Totaler Zusammenbruch der Ostfront. Flüchtlingsströme aus Ostpreußen und Schlesien. Das Ende naht.',
        'context_en': 'Total collapse of the Eastern Front. Refugee streams from East Prussia and Silesia. The end approaches.',
        'tags': ['Eastern collapse 1945', 'Refugees', 'East Prussia', 'Silesia', 'January 1945'],
        'tags_intl': ['Colapso del frente oriental', '東部戦線崩壊', 'Крах Восточного фронта']
    },
    753: {
        'date': '08.02.1945',
        'event_en': 'Yalta Conference',
        'event_de': 'Konferenz Jalta',
        'locations': ['Yalta', 'Crimea', 'Krim', 'Soviet Union', 'Sowjetunion'],
        'context_de': 'Die "Großen Drei" teilen Europa auf. Roosevelt, Churchill, Stalin entscheiden Deutschlands Schicksal.',
        'context_en': 'The Big Three divide Europe. Roosevelt, Churchill, Stalin decide Germany\'s fate.',
        'tags': ['Yalta Conference', 'Big Three', 'Roosevelt', 'Churchill', 'Stalin', 'February 1945'],
        'tags_intl': ['Conferencia de Yalta', 'ヤルタ会談', 'Ялтинская конференция', 'Conferência de Ialta', 'याल्टा सम्मेलन']
    },
    754: {
        'date': '15.02.1945',
        'event_en': 'Dresden Bombed',
        'event_de': 'Dresden bombardiert',
        'locations': ['Dresden', 'Saxony', 'Sachsen', 'Germany', 'Deutschland', 'Elbe'],
        'context_de': 'Alliierte Bombardierung Dresdens vom 13.-15.02.1945. Feuersturm zerstört die Altstadt. ~25.000 Tote.',
        'context_en': 'Allied bombing of Dresden Feb 13-15, 1945. Firestorm destroys old town. ~25,000 dead.',
        'tags': ['Dresden bombing', 'Firebombing', 'Dresden 1945', 'Allied bombing', 'February 1945'],
        'tags_intl': ['Bombardeo de Dresde', 'ドレスデン爆撃', 'Бомбардировка Дрездена', 'Bombardeio de Dresden', 'ड्रेसडेन बमबारी']
    }
}

def get_youtube():
    with open(OAUTH_FILE, 'r') as f:
        td = json.load(f)
    return build('youtube', 'v3', credentials=Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    ))

def build_title(nr, data):
    """
    TITEL-FORMEL (gemäß copilot-instructions.md):
    [KEYWORD]: [Titel] ([Jahr]) | 8K | @remAIke_IT
    
    Für Wochenschau mit DATUM:
    Wochenschau [NR]: [Event EN] ([DD.MM.YYYY]) | 8K | @remAIke_IT
    """
    # Kein "Nr." - spart 4 Zeichen!
    title = f"Wochenschau {nr}: {data['event_en']} ({data['date']}) | 8K | @remAIke_IT"
    
    # Max 70 Zeichen
    if len(title) > 70:
        # Kürze Event wenn nötig
        event_short = data['event_en'][:20]
        title = f"Wochenschau {nr}: {event_short} ({data['date']}) | 8K | @remAIke_IT"
    
    return title

def build_description(nr, data):
    """
    DESCRIPTION nach Regeln + INTERNATIONAL SEO:
    1. Erste 160 Zeichen = Keyword + wichtigste Info (in Search sichtbar!)
    2. Mehrsprachig (DE/EN + international keywords!)
    3. Locations für Local SEO
    4. Historischer Kontext
    5. CTA Block
    6. Hashtags (2-5)
    
    CRITICAL: International users search in THEIR language!
    → Add Spanish, Portuguese, Japanese keywords for global reach
    """
    locations_str = ', '.join(data['locations'][:6])
    
    # Get international tags if available
    intl_keywords = data.get('tags_intl', [])
    intl_line = ''
    if intl_keywords:
        intl_line = f"\n🌍 Also: {' | '.join(intl_keywords[:4])}"
    
    desc = f"""🎬 Wochenschau {nr}: {data['event_de']} | Die Deutsche Wochenschau {data['date']} | 8K Restored
🔎 {data['event_en']} | Segunda Guerra Mundial | 第二次世界大戦 | WWII Documentary{intl_line}

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🗺️ LOCATIONS: {locations_str}

🇩🇪 DEUTSCH:
{data['context_de']}
Originalaufnahmen aus dem Bundesarchiv in 8K restauriert.

🇬🇧 ENGLISH:
{data['context_en']}
Nazi propaganda footage from German Federal Archives, restored in 8K.

🇪🇸 ESPAÑOL: Noticiario alemán de la Segunda Guerra Mundial
🇧🇷 PORTUGUÊS: Cinejornal alemão da Segunda Guerra
🇯🇵 日本語: ドイツ週間ニュース - 第二次世界大戦の記録映像

📅 DATE: {data['date']}
📍 Die Deutsche Wochenschau - Ausgabe {nr}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you found this historically valuable!
💬 COMMENT: What do you know about this event?
🔔 SUBSCRIBE @remAIke_IT for WWII archives!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at https://frai.tv | @remAIke_IT

#Wochenschau #WWII #SegundaGuerraMundial #第二次世界大戦 #8K"""

    return desc

def build_tags(nr, data):
    """
    TAGS nach Regeln + INTERNATIONAL SEO:
    1. Keyword FIRST (Wochenschau)
    2. 5-15 Tags (minimal role laut YT 2026)
    3. Individuell pro Video
    4. MULTILINGUAL für globale Reichweite!
    
    Wie finden Inder/Japaner/Brasilianer die Wochenschau?
    → Sie suchen nach WWII in IHRER Sprache!
    """
    # Core tags (most important first)
    tags = [
        'Wochenschau',
        f'Wochenschau {nr}',
        data['event_en'],
        data['event_de'],
    ]
    
    # Video-specific historical tags (EN/DE)
    tags.extend(data.get('tags', [])[:4])
    
    # INTERNATIONAL: Add multilingual tags if available
    intl_tags = data.get('tags_intl', [])
    tags.extend(intl_tags[:3])  # Max 3 internationale Tags
    
    # Global WWII search terms (most searched languages)
    global_tags = [
        'WWII',                      # English universal
        'Segunda Guerra Mundial',     # Spanish (500M+ speakers)
        '第二次世界大戦',              # Japanese (high YouTube usage)
        'Segunda Guerra',             # Portuguese (Brazil = huge YT market)
    ]
    tags.extend(global_tags[:2])  # Add 2 global tags
    
    # Technical tags
    tags.extend(['8K', 'German Newsreel', 'Bundesarchiv'])
    
    # Limit to 15 tags (YouTube recommendation: 200-300 chars total)
    return tags[:15]

def main():
    apply_mode = '--apply' in sys.argv
    
    print("=" * 70)
    print("WOCHENSCHAU COMPLETE SEO UPDATE")
    print("Nach Regeln + 2026 Algorithm Research")
    print("=" * 70)
    
    yt = get_youtube()
    
    # Hole alle Wochenschau-Videos via Search
    print("\n📡 Fetching Wochenschau videos...")
    results = yt.search().list(
        part='snippet',
        channelId='UCVFv6Egpl0LDvigpFbQXNeQ',
        q='Wochenschau',
        type='video',
        maxResults=50
    ).execute()
    
    videos = []
    import re
    for item in results.get('items', []):
        title = item['snippet']['title']
        if 'wochenschau' in title.lower():
            match = re.search(r'\b(\d{3})\b', title)
            if match:
                nr = int(match.group(1))
                if nr in WOCHENSCHAU_DATA:
                    videos.append({
                        'id': item['id']['videoId'],
                        'nr': nr,
                        'current_title': title
                    })
    
    videos.sort(key=lambda x: x['nr'])
    print(f"Found {len(videos)} videos with data")
    
    # Zeige Updates
    print("\n" + "=" * 70)
    print("PLANNED UPDATES")
    print("=" * 70)
    
    for v in videos:
        nr = v['nr']
        data = WOCHENSCHAU_DATA[nr]
        new_title = build_title(nr, data)
        new_tags = build_tags(nr, data)
        
        print(f"\n📹 Wochenschau {nr}")
        print(f"   CURRENT: {v['current_title'][:60]}")
        print(f"   NEW:     {new_title}")
        print(f"   TAGS:    {new_tags[:5]}...")
        print(f"   LOCS:    {', '.join(data['locations'][:4])}")
    
    if not apply_mode:
        print("\n" + "=" * 70)
        print("⚠️  DRY RUN - Run with --apply to update")
        print(f"    {len(videos)} videos ready for update")
        print("=" * 70)
        return
    
    # Apply updates
    print("\n" + "=" * 70)
    print("🚀 APPLYING UPDATES...")
    print("=" * 70)
    
    success = 0
    failed = 0
    
    for v in videos:
        nr = v['nr']
        data = WOCHENSCHAU_DATA[nr]
        
        new_title = build_title(nr, data)
        new_desc = build_description(nr, data)
        new_tags = build_tags(nr, data)
        
        print(f"\n📹 Updating Wochenschau {nr}...")
        
        try:
            # Get current video to preserve categoryId
            current = yt.videos().list(part='snippet', id=v['id']).execute()
            if not current['items']:
                print(f"   ❌ Video not found")
                failed += 1
                continue
            
            category_id = current['items'][0]['snippet']['categoryId']
            
            # Update
            response = yt.videos().update(
                part='snippet',
                body={
                    'id': v['id'],
                    'snippet': {
                        'title': new_title,
                        'description': new_desc,
                        'tags': new_tags,
                        'categoryId': category_id
                    }
                }
            ).execute()
            
            print(f"   ✅ {new_title[:50]}...")
            success += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {success} ✅ | {failed} ❌")
    print("=" * 70)

if __name__ == '__main__':
    main()
