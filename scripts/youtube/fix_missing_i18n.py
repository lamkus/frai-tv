"""
Fix 4 videos with missing localizations (<5 languages).
Each gets 5 language localizations: DE, EN, ES, FR, JA
Cost: 4 × 50 = 200 quota
"""
import os, sys, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = r"D:\remaike.TV\token.json"

DRY_RUN = "--apply" not in sys.argv

# The 4 videos needing localizations
VIDEOS = {
    'eX5cbYwNvnI': {
        'current_title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ (4K UHD)',
        'localizations': {
            'de': {'title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ', 'description': 'Betty Boop (19/105): Betty Boop Limited (1932) – animiert von Max Fleischer Studios. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'en': {'title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ', 'description': 'Betty Boop (19/105): Betty Boop Limited (1932) – animated by Max Fleischer Studios. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'es': {'title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ', 'description': 'Betty Boop (19/105): Betty Boop Limited (1932) – animado por Max Fleischer Studios. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'fr': {'title': 'Betty Boop (19/105): Betty Boop Limited (1932) | 8K HQ', 'description': 'Betty Boop (19/105): Betty Boop Limited (1932) – animé par Max Fleischer Studios. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'ja': {'title': 'ベティ・ブープ (19/105): Betty Boop Limited (1932) | 8K HQ', 'description': 'ベティ・ブープ (19/105): Betty Boop Limited (1932) – マックス・フライシャー・スタジオ制作。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        }
    },
    'A8LWgWF5f5k': {
        'current_title': 'The Hut-Sut Song (1940s) | Soundie | 8K HQ (4K UHD)',
        'localizations': {
            'de': {'title': 'The Hut-Sut Song (1940er) | Soundie | 8K HQ', 'description': 'The Hut-Sut Song – Original Soundie aus den 1940er Jahren. Vintage-Musikvideo (Jukebox-Film). Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'en': {'title': 'The Hut-Sut Song (1940s) | Soundie | 8K HQ', 'description': 'The Hut-Sut Song – original 1940s Soundie (jukebox music film). Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'es': {'title': 'The Hut-Sut Song (1940s) | Soundie | 8K HQ', 'description': 'The Hut-Sut Song – Soundie original de los años 1940 (video musical de rockola). Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'fr': {'title': 'The Hut-Sut Song (1940s) | Soundie | 8K HQ', 'description': 'The Hut-Sut Song – Soundie original des années 1940 (film de jukebox). Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'ja': {'title': 'ハット・サット・ソング (1940年代) | サウンディ | 8K HQ', 'description': 'The Hut-Sut Song – 1940年代のオリジナルサウンディ（ジュークボックス映像）。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        }
    },
    'TWodj8k8-zU': {
        'current_title': 'Alfred J. Kwak (29/52): Die Burengänse | 8K HQ (4K UHD)',
        'localizations': {
            'de': {'title': 'Alfred J. Kwak (29/52): Die Burengänse | 8K HQ', 'description': 'Alfred J. Kwak Folge 29: Die Burengänse – Eine Geschichte über Apartheid und Diskriminierung. Klassische Zeichentrickserie von Herman van Veen.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'en': {'title': 'Alfred J. Kwak (29/52): The Boer Geese | 8K HQ', 'description': 'Alfred J. Kwak Episode 29: The Boer Geese – A story about apartheid and discrimination. Classic animated series by Herman van Veen.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'es': {'title': 'Alfred J. Kwak (29/52): Los Gansos Bóer | 8K HQ', 'description': 'Alfred J. Kwak Episodio 29: Los Gansos Bóer – Una historia sobre el apartheid y la discriminación. Serie animada clásica de Herman van Veen.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'fr': {'title': 'Alfred J. Kwak (29/52): Les Oies Boers | 8K HQ', 'description': "Alfred J. Kwak Épisode 29: Les Oies Boers – Une histoire sur l'apartheid et la discrimination. Série animée classique de Herman van Veen.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT"},
            'ja': {'title': 'アルフレッド・J・クワック (29/52): ボーア・ガチョウ | 8K HQ', 'description': 'アルフレッド・J・クワック 第29話：ボーア・ガチョウ – アパルトヘイトと差別についての物語。ヘルマン・ファン・フェーンの名作アニメ。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        }
    },
    'D1WD7sS637k': {
        'current_title': 'The Most Disturbing Soviet Experiment Ever Filmed | 8K HQ (4K UHD)',
        'localizations': {
            'de': {'title': 'Das verstörendste sowjetische Experiment | 8K HQ', 'description': 'Experiments in the Revival of Organisms (1940) – Sowjetischer Dokumentarfilm über Wiederbelebungsexperimente. Public Domain, restauriert in 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'en': {'title': 'Most Disturbing Soviet Experiment Ever Filmed | 8K HQ', 'description': 'Experiments in the Revival of Organisms (1940) – Soviet documentary about reanimation experiments. Public domain, restored to 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'es': {'title': 'El Experimento Soviético Más Perturbador | 8K HQ', 'description': 'Experiments in the Revival of Organisms (1940) – Documental soviético sobre experimentos de reanimación. Dominio público, restaurado en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'fr': {'title': "L'Expérience Soviétique la Plus Perturbante | 8K HQ", 'description': 'Experiments in the Revival of Organisms (1940) – Documentaire soviétique sur les expériences de réanimation. Domaine public, restauré en 8K.\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
            'ja': {'title': '最も衝撃的なソ連の実験映像 | 8K HQ', 'description': '生体蘇生実験 (1940) – ソ連の蘇生実験ドキュメンタリー。パブリックドメイン、8K復元。\n\n🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT'},
        }
    },
}

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def main():
    print(f"🌍 Localization Fix — {'DRY RUN' if DRY_RUN else 'APPLYING!'}")
    print(f"   Videos: {len(VIDEOS)}")
    print(f"   Quota: ~{len(VIDEOS) * 50} units\n")
    
    youtube = get_youtube()
    fixed = 0
    
    for vid_id, data in VIDEOS.items():
        print(f"[{fixed+1}/{len(VIDEOS)}] {vid_id}: {data['current_title'][:60]}")
        
        if DRY_RUN:
            for lang, loc in data['localizations'].items():
                print(f"   {lang}: {loc['title'][:50]}")
            fixed += 1
            continue
        
        try:
            # Get current video data
            resp = youtube.videos().list(part="snippet,localizations", id=vid_id).execute()
            if not resp['items']:
                print(f"   ❌ Video not found!")
                continue
            
            video = resp['items'][0]
            snippet = video['snippet']
            current_locs = video.get('localizations', {})
            
            # Merge new localizations (don't overwrite existing)
            merged_locs = {**current_locs, **data['localizations']}
            
            youtube.videos().update(
                part="snippet,localizations",
                body={
                    'id': vid_id,
                    'snippet': {
                        'title': snippet['title'],
                        'description': snippet['description'],
                        'tags': snippet.get('tags', []),
                        'categoryId': snippet['categoryId'],
                    },
                    'localizations': merged_locs,
                }
            ).execute()
            
            fixed += 1
            print(f"   ✅ Added {len(data['localizations'])} localizations!")
            time.sleep(1.2)
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:100]}")
    
    print(f"\n{'='*50}")
    print(f"✅ Localized: {fixed}/{len(VIDEOS)}")
    print(f"Quota: ~{fixed * 50} units")

if __name__ == '__main__':
    main()
