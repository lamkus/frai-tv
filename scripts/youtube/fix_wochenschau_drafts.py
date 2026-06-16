#!/usr/bin/env python3
"""
Optimiere 5 Wochenschau Drafts - Titel + Description + Tags

Format:
- Title: Die Deutsche Wochenschau Nr. XXX (DD.MM.YYYY) | 8K HQ | @remAIke_IT
- Description: Trilingual (DE/EN/RU) + CTA + Hashtags
- Tags: Wochenschau-spezifisch
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import sys

# Wochenschau Drafts mit korrekten Daten
WOCHENSCHAU_DRAFTS = [
    {
        'id': 'jGz1kC1Z69A',
        'nr': 746,
        'date': '21.12.1944',
        'date_en': 'December 21, 1944',
        'date_ru': '21 декабря 1944',
    },
    {
        'id': 'dYBzf5V1TjI',
        'nr': 654,
        'date': '17.03.1943',
        'date_en': 'March 17, 1943',
        'date_ru': '17 марта 1943',
    },
    {
        'id': 'W-UcQleew8Y',
        'nr': 721,
        'date': '28.06.1944',
        'date_en': 'June 28, 1944',
        'date_ru': '28 июня 1944',
    },
    {
        'id': '0sO7jVL43yQ',
        'nr': 652,
        'date': '03.03.1943',
        'date_en': 'March 3, 1943',
        'date_ru': '3 марта 1943',
    },
    {
        'id': 'bZkUPQHqyfg',
        'nr': 722,
        'date': '06.07.1944',
        'date_en': 'July 6, 1944',
        'date_ru': '6 июля 1944',
    },
]

def generate_title(ws):
    return f"Die Deutsche Wochenschau Nr. {ws['nr']} ({ws['date']}) | 8K HQ | @remAIke_IT"

def generate_description(ws):
    return f"""Die Deutsche Wochenschau Nr. {ws['nr']} vom {ws['date']} – historische Dokumentation aus dem Zweiten Weltkrieg.

🎬 Originalaufnahmen der NS-Propaganda-Wochenschau, restauriert und hochskaliert in 8K.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇬🇧 ENGLISH:
German Newsreel No. {ws['nr']} from {ws['date_en']} – historical WWII footage.
Original Nazi propaganda newsreel, restored and upscaled in 8K.

🇷🇺 РУССКИЙ:
Немецкая кинохроника № {ws['nr']} от {ws['date_ru']} — исторические кадры Второй мировой войны.
Оригинальная нацистская пропагандистская кинохроника, восстановленная в 8K.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ HINWEIS / DISCLAIMER:
Dieses Video dient ausschließlich der historischen Dokumentation und Bildung.
This video is for historical documentation and educational purposes only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you appreciate historical preservation!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored history!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More at: https://frai.tv | @remAIke_IT

#Wochenschau #WWII #History #WW2 #DeutscheWochenschau #8K #PublicDomain #HistoricalFootage #Newsreel"""

def generate_tags(ws):
    year = ws['date'].split('.')[-1]
    return [
        'Deutsche Wochenschau',
        'Wochenschau',
        f'Wochenschau {ws["nr"]}',
        'WWII',
        'WW2',
        'World War 2',
        year,
        'Nazi Germany',
        'Historical footage',
        'Newsreel',
        'Public domain',
        '8K',
        'Restored',
        'History documentary',
        'German newsreel',
        '@remAIke_IT',
    ]

def main():
    with open('config/youtube_oauth.json', encoding='utf-8') as f:
        oauth = json.load(f)
    
    creds = Credentials(
        token=oauth['token'],
        refresh_token=oauth['refresh_token'],
        token_uri=oauth['token_uri'],
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret'],
    )
    youtube = build('youtube', 'v3', credentials=creds)
    
    print("🎬 WOCHENSCHAU DRAFTS SEO OPTIMIERUNG")
    print("=" * 70)
    print(f"Videos zu optimieren: {len(WOCHENSCHAU_DRAFTS)}")
    print()
    
    # Zeige Vorschau
    for ws in WOCHENSCHAU_DRAFTS:
        title = generate_title(ws)
        desc = generate_description(ws)
        tags = generate_tags(ws)
        
        print(f"📺 {ws['id']} - Nr. {ws['nr']}")
        print(f"   TITLE: {title}")
        print(f"   DESC: {len(desc)} chars")
        print(f"   TAGS: {len(tags)} tags")
        print()
    
    if '--apply' not in sys.argv:
        print("=" * 70)
        print("⚠️  DRY RUN - Starte mit --apply")
        return
    
    print("=" * 70)
    print("🚀 WENDE ÄNDERUNGEN AN...")
    print()
    
    success = 0
    for ws in WOCHENSCHAU_DRAFTS:
        try:
            # Hole aktuelles Video
            result = youtube.videos().list(part='snippet', id=ws['id']).execute()
            if not result['items']:
                print(f"❌ {ws['id']}: Nicht gefunden")
                continue
            
            snippet = result['items'][0]['snippet']
            
            # Update
            new_title = generate_title(ws)
            new_desc = generate_description(ws)
            new_tags = generate_tags(ws)
            
            youtube.videos().update(
                part='snippet',
                body={
                    'id': ws['id'],
                    'snippet': {
                        'title': new_title,
                        'description': new_desc,
                        'tags': new_tags,
                        'categoryId': snippet['categoryId']
                    }
                }
            ).execute()
            
            print(f"✅ Nr. {ws['nr']} ({ws['date']})")
            print(f"   {new_title}")
            success += 1
            
        except Exception as e:
            print(f"❌ {ws['id']}: {str(e)[:60]}")
    
    print()
    print("=" * 70)
    print(f"✅ Erfolgreich: {success}/{len(WOCHENSCHAU_DRAFTS)}")

if __name__ == '__main__':
    main()
