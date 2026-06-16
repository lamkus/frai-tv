#!/usr/bin/env python3
"""Update the 4 missing Wochenschau videos that still have old format"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Die 4 fehlenden Videos mit altem Format
MISSING_VIDEOS = {
    483: {
        'id': 'Qn7Nvx7eWz4',
        'date': '06.12.1939',
        'event_en': 'Winter War',
        'event_de': 'Winterkrieg',
        'locations': ['Finland', 'Karelia', 'Mannerheim Line', 'Finnland'],
        'context_de': 'Fortsetzung der Berichterstattung über den sowjetisch-finnischen Winterkrieg. Finnischer Widerstand an der Mannerheim-Linie.',
        'context_en': 'Continued coverage of the Soviet-Finnish Winter War. Finnish resistance at the Mannerheim Line.',
        'tags': ['Winter War', 'Finland', 'Mannerheim Line', 'Talvisota', 'Finnish resistance'],
        'tags_intl': ['Guerra de Invierno', '冬戦争', 'Зимняя война', 'Linha Mannerheim']
    },
    488: {
        'id': 'DLifkhU0q1w',
        'date': '10.01.1940',
        'event_en': 'Phoney War',
        'event_de': 'Sitzkrieg',
        'locations': ['Western Front', 'Maginot Line', 'Siegfried Line', 'France', 'Frankreich'],
        'context_de': 'Ruhephase an der Westfront - der "Sitzkrieg". Propaganda zeigt deutsche Stärke an der Siegfriedlinie.',
        'context_en': 'Quiet phase on the Western Front - the "Phoney War". Propaganda shows German strength at the Siegfried Line.',
        'tags': ['Phoney War', 'Sitzkrieg', 'Drôle de guerre', 'Western Front 1940', 'Maginot Line'],
        'tags_intl': ['Guerra de broma', 'まやかしの戦争', 'Странная война', 'Guerra de mentira']
    },
    513: {
        'id': 'D_kLmNFlbZI',
        'date': '01.07.1940',
        'event_en': 'Channel Islands',
        'event_de': 'Kanalinseln besetzt',
        'locations': ['Jersey', 'Guernsey', 'Channel Islands', 'Kanalinseln', 'English Channel'],
        'context_de': 'Deutsche Besetzung der britischen Kanalinseln Jersey und Guernsey. Einziges britisches Territorium unter Nazi-Besatzung.',
        'context_en': 'German occupation of British Channel Islands Jersey and Guernsey. Only British territory under Nazi occupation.',
        'tags': ['Channel Islands 1940', 'Jersey', 'Guernsey', 'German occupation', 'British territory'],
        'tags_intl': ['Islas del Canal', 'チャンネル諸島占領', 'Оккупация Нормандских островов']
    },
    524: {
        'id': '1O8sVLS-zfI',
        'date': '28.09.1940',
        'event_en': 'Sea Lion Cancelled',
        'event_de': 'Seelöwe abgesagt',
        'locations': ['English Channel', 'England', 'Germany', 'Ärmelkanal', 'Deutschland'],
        'context_de': 'Operation Seelöwe auf unbestimmte Zeit verschoben. Die Luftwaffe hat die Luftüberlegenheit nicht errungen. Wendepunkt.',
        'context_en': 'Operation Sea Lion postponed indefinitely. Luftwaffe failed to achieve air superiority. Turning point.',
        'tags': ['Operation Sea Lion', 'Seelöwe', 'Battle of Britain', 'Invasion cancelled', 'September 1940'],
        'tags_intl': ['Operación León Marino', 'あしか作戦', 'Операция Морской лев']
    }
}

def build_title(nr, data):
    return f"Wochenschau {nr}: {data['event_en']} ({data['date']}) | 8K | @remAIke_IT"

def build_tags(nr, data):
    tags = ['Wochenschau', f'Wochenschau {nr}', data['event_en'], data['event_de']]
    tags.extend(data['tags'][:4])
    tags.extend(data.get('tags_intl', [])[:3])
    tags.extend(['WWII', 'Segunda Guerra Mundial', '8K', 'German Newsreel'])
    return tags[:15]

def build_description(nr, data):
    intl_line = ''
    if data.get('tags_intl'):
        intl_line = '\n🌍 Also: ' + ' | '.join(data['tags_intl'][:4])
    
    return f"""🎬 Wochenschau {nr}: {data['event_de']} | Die Deutsche Wochenschau {data['date']} | 8K Restored
🔎 {data['event_en']} | Segunda Guerra Mundial | 第二次世界大戦 | WWII Documentary{intl_line}

⚠️ HISTORICAL DOCUMENT – EDUCATIONAL USE ONLY / NUR FÜR BILDUNGSZWECKE

🗺️ LOCATIONS: {', '.join(data['locations'][:5])}

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

def main():
    with open('config/youtube_oauth.json', 'r') as f:
        td = json.load(f)

    yt = build('youtube', 'v3', credentials=Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    ))

    print('=' * 70)
    print('UPDATING 4 MISSING WOCHENSCHAU VIDEOS')
    print('=' * 70)
    
    success = 0
    for nr, data in MISSING_VIDEOS.items():
        vid = data['id']
        title = build_title(nr, data)
        tags = build_tags(nr, data)
        desc = build_description(nr, data)
        
        print(f'\n📹 Updating Wochenschau {nr}...')
        print(f'   OLD: [old format with Nr.]')
        print(f'   NEW: {title[:55]}...')
        
        try:
            # Get current categoryId
            current = yt.videos().list(part='snippet', id=vid).execute()
            if not current['items']:
                print(f'   ❌ Video not found')
                continue
            category_id = current['items'][0]['snippet']['categoryId']
            
            # Update
            response = yt.videos().update(
                part='snippet',
                body={
                    'id': vid,
                    'snippet': {
                        'title': title,
                        'description': desc,
                        'tags': tags,
                        'categoryId': category_id
                    }
                }
            ).execute()
            print(f'   ✅ Updated!')
            success += 1
        except Exception as e:
            print(f'   ❌ Error: {e}')

    print('\n' + '=' * 70)
    print(f'COMPLETE: {success}/4 updated')
    print('=' * 70)

if __name__ == '__main__':
    main()
