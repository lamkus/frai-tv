"""
Create pending updates for Wochenschau videos with specific content per video
Save to config/pending_updates/ for user review BEFORE applying
"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Wochenschau videos with historical context
WOCHENSCHAU_DATA = {
    '6K-MuUu6L44': {'nr': 720, 'date': '21.06.1944', 'year': 1944, 
                   'content_de': 'Ostfront, Luftangriffe auf England, V1-Raketen',
                   'content_en': 'Eastern Front, air raids on England, V1 rockets'},
    'W-UcQleew8Y': {'nr': 721, 'date': '28.06.1944', 'year': 1944,
                   'content_de': 'Invasion Normandie, Vergeltungswaffen, Ostfront',
                   'content_en': 'Normandy invasion, retaliation weapons, Eastern Front'},
    'dYBzf5V1TjI': {'nr': 654, 'date': '17.03.1943', 'year': 1943,
                   'content_de': 'Nach Stalingrad, Kriegswirtschaft, Ostfront',
                   'content_en': 'Post-Stalingrad, war economy, Eastern Front'},
    'jGz1kC1Z69A': {'nr': 746, 'date': '21.12.1944', 'year': 1944,
                   'content_de': 'Ardennenoffensive, Weihnachten an der Front',
                   'content_en': 'Battle of the Bulge, Christmas at the front'},
    'bZkUPQHqyfg': {'nr': 722, 'date': '06.07.1944', 'year': 1944,
                   'content_de': 'D-Day Nachwirkungen, V1-Einsatz, Ostfront',
                   'content_en': 'D-Day aftermath, V1 deployment, Eastern Front'},
    'iEEvt-s1XhQ': {'nr': 753, 'date': '05.03.1945', 'year': 1945,
                   'content_de': 'Vorletzte Wochenschau, Endkampf, Volkssturm',
                   'content_en': 'Second-to-last newsreel, final battles, Volkssturm'},
    'H_n_mS-eKps': {'nr': 754, 'date': '16.03.1945', 'year': 1945,
                   'content_de': 'VORLETZTE AUSGABE! Nur Nr. 755 folgte noch',
                   'content_en': 'SECOND-TO-LAST EDITION! Only No. 755 followed'},
    'w2UvksMOs3c': {'nr': 750, 'date': '25.01.1945', 'year': 1945,
                   'content_de': 'Ostfront-Rückzug, Flüchtlinge, Endphase',
                   'content_en': 'Eastern Front retreat, refugees, final phase'},
    '6YLPpJLgVXk': {'nr': 751, 'date': '10.02.1945', 'year': 1945,
                   'content_de': 'Dresden-Angriffe, Oder-Front, Volkssturm',
                   'content_en': 'Dresden attacks, Oder Front, Volkssturm'},
    'T-EsdXGhqog': {'nr': 516, 'date': '22.07.1940', 'year': 1940,
                   'content_de': 'Frankreich besiegt, Siegesparaden, Luftschlacht um England',
                   'content_en': 'France defeated, victory parades, Battle of Britain'},
    '3rB80OGKzrg': {'nr': 511, 'date': '20.06.1940', 'year': 1940,
                   'content_de': 'Fall Frankreichs, Waffenstillstand Compiègne',
                   'content_en': 'Fall of France, Armistice at Compiègne'},
}

def create_description(data):
    """Create 18-language description with specific content - MAX 5000 chars"""
    nr = data['nr']
    date = data['date']
    year = data['year']
    content_de = data['content_de']
    content_en = data['content_en']
    
    # Year-specific hashtag
    year_tag = f"#{year}" if year else ""
    
    desc = f"""🎬 Die Deutsche Wochenschau Nr. {nr} ({date}) | WWII German Newsreel | 8K

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🇩🇪 Wochenschau Nr. {nr} vom {date}. {content_de}. NS-Propaganda in 8K restauriert. Bundesarchiv-Material.

🇺🇸 Newsreel #{nr}, {date}. {content_en}. Nazi propaganda restored in 8K. Federal Archives footage.

🇪🇸 Noticiario #{nr} del {date}. {content_en}. Propaganda nazi restaurada en 8K.

🇫🇷 Actualités #{nr} du {date}. {content_en}. Propagande nazie restaurée en 8K.

🇵🇹 Noticiário #{nr} de {date}. {content_en}. Propaganda nazista restaurada em 8K.

🇮🇹 Cinegiornale #{nr} del {date}. {content_en}. Propaganda nazista in 8K.

🇳🇱 Journaal #{nr} van {date}. {content_en}. Nazi-propaganda in 8K.

🇵🇱 Kronika #{nr} z {date}. {content_en}. Propaganda nazistowska w 8K.

🇷🇺 Кинохроника #{nr} от {date}. {content_en}. Нацистская пропаганда в 8K.

🇯🇵 週報 #{nr} {date}。{content_en}。ナチス宣伝8K復元。

🇨🇳 新闻片 #{nr} {date}。{content_en}。纳粹宣传8K修复。

🇰🇷 주간뉴스 #{nr} {date}. {content_en}. 나치 선전 8K 복원.

🇹🇷 Haber #{nr} {date}. {content_en}. Nazi propagandası 8K.

🇸🇦 الأخبار #{nr} {date}. {content_en}. دعاية نازية 8K.

🇮🇳 न्यूज़रील #{nr} {date}। {content_en}। नाज़ी प्रचार 8K।

🇹🇭 ข่าว #{nr} {date}. {content_en}. โฆษณานาซี 8K.

🇻🇳 Tin #{nr} {date}. {content_en}. Tuyên truyền 8K.

🇮🇩 Berita #{nr} {date}. {content_en}. Propaganda Nazi 8K.

🇸🇪 Veckojournal #{nr} {date}. {content_en}. Nazipropaganda 8K.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 PRIMARY SOURCE | BUNDESARCHIV FOOTAGE
🎬 LIKE for historical archives! 🔔 SUBSCRIBE @remAIke_IT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 https://frai.tv | @remAIke_IT

#Wochenschau #GermanNewsreel #WWII #WW2 #WorldWar2 #SecondWorldWar #NaziGermany #ThirdReich #Wehrmacht #Goebbels #Propaganda #EasternFront #WesternFront #DDay #Normandy #Stalingrad #Berlin{year} #HistoricalFootage #PrimarySource #Bundesarchiv #Archives #Documentary #8K #Restored #remAIke"""
    
    return desc

# Generate pending updates
pending = []
for vid_id, data in WOCHENSCHAU_DATA.items():
    desc = create_description(data)
    pending.append({
        'video_id': vid_id,
        'nr': data['nr'],
        'date': data['date'],
        'new_description': desc,
        'char_count': len(desc)
    })
    print(f"Nr. {data['nr']}: {len(desc)} chars")

# Save for user review
import os
os.makedirs('config/pending_updates', exist_ok=True)

with open('config/pending_updates/wochenschau_multilingual.json', 'w', encoding='utf-8') as f:
    json.dump(pending, f, ensure_ascii=False, indent=2)

print(f"\n✅ Created {len(pending)} pending updates")
print(f"📁 Saved to: config/pending_updates/wochenschau_multilingual.json")
print(f"\n⚠️ REVIEW BEFORE APPLYING!")
