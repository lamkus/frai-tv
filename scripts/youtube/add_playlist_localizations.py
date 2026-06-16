#!/usr/bin/env python3
"""
add_playlist_localizations.py

Fügt mehrsprachige Titel und Beschreibungen zu YouTube-Playlists hinzu.
YouTube zeigt automatisch die passende Sprache basierend auf User-Einstellungen.

Usage:
    python add_playlist_localizations.py --dry-run
    python add_playlist_localizations.py --apply
"""

import json
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Playlist-Lokalisierungen (Titel + Beschreibung in mehreren Sprachen)
# ECHTE PLAYLIST-IDs vom Channel remAIke_IT
PLAYLIST_LOCALIZATIONS = {
    # Wochenschau - PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg
    "PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg": {
        "de": {
            "title": "Die Deutsche Wochenschau 1939-1945 | WWII Newsreels | 8K",
            "description": "Historische Dokumentation: Original-Wochenschau-Material aus dem Zweiten Weltkrieg. 8K restauriert. Nur für Bildungszwecke."
        },
        "en": {
            "title": "German Newsreels 1939-1945 | WWII Documentary | 8K Restored",
            "description": "Historical documentation: Original WWII German newsreel footage. 8K restored. For educational purposes only."
        },
        "es": {
            "title": "Noticieros Alemanes 1939-1945 | Documental WWII | 8K",
            "description": "Documentación histórica: Material original de noticieros de la Segunda Guerra Mundial. Restaurado en 8K. Solo con fines educativos."
        },
        "pt": {
            "title": "Noticiários Alemães 1939-1945 | Documentário WWII | 8K",
            "description": "Documentação histórica: Material original de noticiários da Segunda Guerra Mundial. Restaurado em 8K. Apenas para fins educacionais."
        },
        "ja": {
            "title": "ドイツ週間ニュース 1939-1945 | 第二次世界大戦 | 8K",
            "description": "歴史的ドキュメンタリー：第二次世界大戦のオリジナル映像。8K修復版。教育目的のみ。"
        },
        "fr": {
            "title": "Actualités Allemandes 1939-1945 | Documentaire WWII | 8K",
            "description": "Documentation historique : Images originales des actualités de la Seconde Guerre mondiale. Restauré en 8K. À des fins éducatives uniquement."
        },
        "ru": {
            "title": "Немецкая кинохроника 1939-1945 | Документальный фильм | 8K",
            "description": "Историческая документация: Оригинальные кадры немецкой кинохроники Второй мировой войны. Восстановлено в 8K. Только в образовательных целях."
        },
        "hi": {
            "title": "जर्मन न्यूज़रील 1939-1945 | द्वितीय विश्व युद्ध | 8K",
            "description": "ऐतिहासिक दस्तावेज़: द्वितीय विश्व युद्ध की मूल फुटेज। 8K में पुनर्स्थापित। केवल शैक्षिक उद्देश्यों के लिए।"
        },
        "zh": {
            "title": "德国新闻周报 1939-1945 | 二战纪录片 | 8K",
            "description": "历史文献：二战德国原始新闻影像。8K修复版。仅供教育目的。"
        },
        "ar": {
            "title": "الأخبار الألمانية 1939-1945 | وثائقي الحرب العالمية الثانية | 8K",
            "description": "وثائق تاريخية: لقطات أصلية من الحرب العالمية الثانية. تم ترميمها بدقة 8K. للأغراض التعليمية فقط."
        },
        "ko": {
            "title": "독일 뉴스릴 1939-1945 | 제2차 세계대전 | 8K",
            "description": "역사적 다큐멘터리: 제2차 세계대전 원본 영상. 8K 복원. 교육 목적으로만 사용."
        },
        "id": {
            "title": "Berita Jerman 1939-1945 | Dokumenter WWII | 8K",
            "description": "Dokumentasi sejarah: Rekaman asli berita Perang Dunia II. Direstorasi dalam 8K. Hanya untuk tujuan pendidikan."
        },
        "tr": {
            "title": "Alman Haber Filmleri 1939-1945 | İkinci Dünya Savaşı | 8K",
            "description": "Tarihi belgesel: İkinci Dünya Savaşı orijinal görüntüleri. 8K restore edilmiş. Sadece eğitim amaçlı."
        },
        "vi": {
            "title": "Bản tin Đức 1939-1945 | Thế chiến II | 8K",
            "description": "Tài liệu lịch sử: Thước phim gốc từ Thế chiến II. Phục hồi 8K. Chỉ dành cho mục đích giáo dục."
        }
    },
    
    # Betty Boop - PL3d2Tsr13ihMNCgAFrHLvjx4YIoDCcx-o
    "PL3d2Tsr13ihMNCgAFrHLvjx4YIoDCcx-o": {
        "de": {
            "title": "Betty Boop - Jazz Age Kollektion (1930er) | 8K",
            "description": "Die komplette Betty Boop Sammlung aus den 1930er Jahren. 8K restauriert von @remAIke_IT"
        },
        "en": {
            "title": "Betty Boop - Jazz Age Collection (1930s) | 8K Restored",
            "description": "The complete Betty Boop collection from the 1930s. 8K restored by @remAIke_IT"
        },
        "es": {
            "title": "Betty Boop - Colección Era del Jazz (1930s) | 8K",
            "description": "La colección completa de Betty Boop de los años 1930. Restaurado en 8K por @remAIke_IT"
        },
        "pt": {
            "title": "Betty Boop - Coleção Era do Jazz (1930s) | 8K",
            "description": "A coleção completa de Betty Boop dos anos 1930. Restaurado em 8K por @remAIke_IT"
        },
        "ja": {
            "title": "ベティ・ブープ - ジャズエイジコレクション (1930年代) | 8K",
            "description": "1930年代のベティ・ブープ完全版。@remAIke_ITによる8K修復版"
        },
        "fr": {
            "title": "Betty Boop - Collection Années Jazz (1930s) | 8K",
            "description": "La collection complète de Betty Boop des années 1930. Restauré en 8K par @remAIke_IT"
        }
    },
    
    # Soundies - PL3d2Tsr13ihMFH1EDv8To7SBS04OW5tBL
    "PL3d2Tsr13ihMFH1EDv8To7SBS04OW5tBL": {
        "de": {
            "title": "Soundies - Vintage Musikvideos (1940er) | 8K",
            "description": "Original Soundies aus den 1940er Jahren - die ersten Musikvideos! 8K restauriert."
        },
        "en": {
            "title": "Soundies - Vintage Music Videos (1940s) | 8K Remastered",
            "description": "Original Soundies from the 1940s - the first music videos! 8K remastered."
        },
        "es": {
            "title": "Soundies - Videos Musicales Vintage (1940s) | 8K",
            "description": "Soundies originales de los años 1940 - ¡los primeros videos musicales! Remasterizado en 8K."
        },
        "ja": {
            "title": "サウンディーズ - ヴィンテージミュージックビデオ (1940年代) | 8K",
            "description": "1940年代のオリジナルサウンディーズ - 最初のミュージックビデオ！8Kリマスター。"
        }
    },
    
    # Alfred J. Kwak - PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL
    "PL3d2Tsr13ihO4514Eao7ttTv6PRKtEReL": {
        "de": {
            "title": "Alfred Jodokus Quack - Komplette Serie | 8K Deutsch",
            "description": "Die komplette Alfred J. Kwak Serie auf Deutsch. 8K restauriert."
        },
        "en": {
            "title": "Alfred J. Kwak - Complete Series | 8K German Dub",
            "description": "The complete Alfred J. Kwak series in German. 8K restored."
        },
        "es": {
            "title": "Alfred J. Kwak - Serie Completa | 8K Alemán",
            "description": "La serie completa de Alfred J. Kwak en alemán. Restaurado en 8K."
        },
        "ja": {
            "title": "アルフレッド・J・クワック - 完全版 | 8K ドイツ語",
            "description": "アルフレッド・J・クワックの完全版シリーズ（ドイツ語）。8K修復版。"
        },
        "nl": {
            "title": "Alfred Jodocus Kwak - Complete Serie | 8K",
            "description": "De complete Alfred J. Kwak serie. 8K gerestaureerd."
        }
    },
    
    # Superman Fleischer - PL3d2Tsr13ihNGGfilho9PHb3gqsOrhksr
    "PL3d2Tsr13ihNGGfilho9PHb3gqsOrhksr": {
        "de": {
            "title": "Superman - Fleischer Studios (1941-1943) | 8K",
            "description": "Die legendären Superman Cartoons von Fleischer Studios. 8K restauriert."
        },
        "en": {
            "title": "Superman - Fleischer Studios (1941-1943) | 8K Restored",
            "description": "The legendary Superman cartoons by Fleischer Studios. 8K restored."
        },
        "es": {
            "title": "Superman - Fleischer Studios (1941-1943) | 8K",
            "description": "Los legendarios dibujos animados de Superman de Fleischer Studios. Restaurado en 8K."
        },
        "ja": {
            "title": "スーパーマン - フライシャー・スタジオ (1941-1943) | 8K",
            "description": "フライシャー・スタジオの伝説的なスーパーマンアニメ。8K修復版。"
        }
    },
    
    # Popeye - PL3d2Tsr13ihMGVG70VrIyLTfZVnNnpggj
    "PL3d2Tsr13ihMGVG70VrIyLTfZVnNnpggj": {
        "de": {
            "title": "Popeye der Seemann | 8K Restauriert",
            "description": "Klassische Popeye Cartoons in 8K restauriert."
        },
        "en": {
            "title": "Popeye the Sailor | 8K Restored",
            "description": "Classic Popeye cartoons restored in 8K."
        },
        "es": {
            "title": "Popeye el Marino | 8K Restaurado",
            "description": "Dibujos animados clásicos de Popeye restaurados en 8K."
        },
        "ja": {
            "title": "ポパイ | 8K修復版",
            "description": "クラシックなポパイアニメ。8K修復版。"
        }
    },
    
    # Looney Tunes - PL3d2Tsr13ihN5gZXFcC8gjn9I3yQG_eYR
    "PL3d2Tsr13ihN5gZXFcC8gjn9I3yQG_eYR": {
        "de": {
            "title": "Looney Tunes - Classic Cartoons | 8K",
            "description": "Klassische Looney Tunes Cartoons in 8K restauriert."
        },
        "en": {
            "title": "Looney Tunes - Classic Cartoons | 8K Restored",
            "description": "Classic Looney Tunes cartoons restored in 8K."
        },
        "es": {
            "title": "Looney Tunes - Dibujos Clásicos | 8K",
            "description": "Dibujos animados clásicos de Looney Tunes restaurados en 8K."
        },
        "ja": {
            "title": "ルーニー・テューンズ | 8K修復版",
            "description": "クラシックなルーニー・テューンズアニメ。8K修復版。"
        }
    },
    
    # Casper - PL3d2Tsr13ihNlMyu7m1gUrorwDsPL0Szf
    "PL3d2Tsr13ihNlMyu7m1gUrorwDsPL0Szf": {
        "de": {
            "title": "Casper der freundliche Geist | 8K",
            "description": "Klassische Casper Cartoons in 8K restauriert."
        },
        "en": {
            "title": "Casper the Friendly Ghost | 8K Restored",
            "description": "Classic Casper cartoons restored in 8K."
        },
        "es": {
            "title": "Gasparín el Fantasma | 8K Restaurado",
            "description": "Dibujos animados clásicos de Gasparín restaurados en 8K."
        },
        "ja": {
            "title": "キャスパー | 8K修復版",
            "description": "クラシックなキャスパーアニメ。8K修復版。"
        }
    },
    
    # Color Classics - PL3d2Tsr13ihN-FoO36o1nSSYAfsat2TLJ
    "PL3d2Tsr13ihN-FoO36o1nSSYAfsat2TLJ": {
        "de": {
            "title": "Color Classics - Fleischer Studios | 8K",
            "description": "Die wunderschönen Color Classics von Fleischer Studios in 8K."
        },
        "en": {
            "title": "Color Classics - Fleischer Studios | 8K Restored",
            "description": "The beautiful Color Classics from Fleischer Studios in 8K."
        },
        "es": {
            "title": "Color Classics - Fleischer Studios | 8K",
            "description": "Los hermosos Color Classics de Fleischer Studios en 8K."
        },
        "ja": {
            "title": "カラー・クラシックス | 8K修復版",
            "description": "フライシャー・スタジオのカラー・クラシックス。8K修復版。"
        }
    },
    
    # Best of remAIke_IT - PL3d2Tsr13ihOkdoE8nvG_xou6vbLh98_a
    "PL3d2Tsr13ihOkdoE8nvG_xou6vbLh98_a": {
        "de": {
            "title": "Best of remAIke_IT | 8K Restauriert",
            "description": "Die besten Videos unseres Kanals - handverlesen. 8K AI-restauriert."
        },
        "en": {
            "title": "Best of remAIke_IT | 8K Restored",
            "description": "The best videos from our channel - hand-picked. 8K AI-restored."
        },
        "es": {
            "title": "Lo Mejor de remAIke_IT | 8K",
            "description": "Los mejores videos de nuestro canal. Restaurado en 8K con IA."
        },
        "ja": {
            "title": "remAIke_IT ベストセレクション | 8K",
            "description": "チャンネルのベスト動画。8K AI修復版。"
        }
    }
}


def load_credentials():
    with open('config/youtube_oauth.json') as f:
        td = json.load(f)
    return Credentials(
        token=td['token'],
        refresh_token=td['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=td['client_id'],
        client_secret=td['client_secret']
    )


def get_all_playlists(yt, channel_id):
    playlists = []
    request = yt.playlists().list(
        part='snippet,localizations',
        channelId=channel_id,
        maxResults=50
    )
    while request:
        response = request.execute()
        playlists.extend(response.get('items', []))
        request = yt.playlists().list_next(request, response)
    return playlists


def update_playlist_localizations(yt, playlist_id, localizations, dry_run=True):
    """Update a playlist with localizations."""
    
    # First get current playlist data
    current = yt.playlists().list(
        part='snippet,localizations,status',
        id=playlist_id
    ).execute()
    
    if not current.get('items'):
        print(f"  Playlist {playlist_id} nicht gefunden!")
        return False
    
    item = current['items'][0]
    title = item['snippet']['title']
    
    print(f"\nPlaylist: {title}")
    print(f"  ID: {playlist_id}")
    print(f"  Aktuelle Lokalisierungen: {list(item.get('localizations', {}).keys())}")
    print(f"  Neue Lokalisierungen: {list(localizations.keys())}")
    
    if dry_run:
        print("  [DRY-RUN] Würde aktualisieren...")
        for lang, data in localizations.items():
            print(f"    {lang}: {data['title'][:40]}...")
        return True
    
    # Update with localizations
    # WICHTIG: defaultLanguage muss ZUERST gesetzt werden!
    snippet = item['snippet'].copy()
    
    # Bestimme die Default-Sprache (erste in unserer Liste, meist 'de' oder 'en')
    default_lang = list(localizations.keys())[0]
    snippet['defaultLanguage'] = default_lang
    
    body = {
        'id': playlist_id,
        'snippet': snippet,
        'localizations': localizations
    }
    
    try:
        yt.playlists().update(
            part='snippet,localizations',
            body=body
        ).execute()
        print("  ✅ Erfolgreich aktualisiert!")
        return True
    except Exception as e:
        print(f"  ❌ Fehler: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='Nur simulieren')
    parser.add_argument('--apply', action='store_true', help='Änderungen anwenden')
    parser.add_argument('--playlist-id', help='Nur eine Playlist aktualisieren')
    args = parser.parse_args()
    
    if not args.dry_run and not args.apply:
        print("Bitte --dry-run oder --apply angeben!")
        return
    
    dry_run = args.dry_run
    
    print("=" * 70)
    print("PLAYLIST LOKALISIERUNGEN HINZUFÜGEN")
    print("=" * 70)
    
    creds = load_credentials()
    yt = build('youtube', 'v3', credentials=creds)
    
    # Get all playlists
    playlists = get_all_playlists(yt, 'UCVFv6Egpl0LDvigpFbQXNeQ')
    print(f"\nGefunden: {len(playlists)} Playlists")
    
    # Match playlists with our localizations
    updated = 0
    for pl in playlists:
        pl_id = pl['id']
        title = pl['snippet']['title']
        
        if args.playlist_id and pl_id != args.playlist_id:
            continue
        
        if pl_id in PLAYLIST_LOCALIZATIONS:
            success = update_playlist_localizations(
                yt, pl_id, 
                PLAYLIST_LOCALIZATIONS[pl_id],
                dry_run=dry_run
            )
            if success:
                updated += 1
        else:
            # Check if we have localizations based on title keywords
            matching_locs = None
            for loc_id, locs in PLAYLIST_LOCALIZATIONS.items():
                for lang, data in locs.items():
                    if lang == 'en' and data['title'].lower() in title.lower():
                        matching_locs = locs
                        break
            
            if not matching_locs:
                current_locs = pl.get('localizations', {})
                if not current_locs:
                    print(f"\n⚠️  Keine Lokalisierungen definiert für: {title}")
    
    print(f"\n{'=' * 70}")
    print(f"Fertig! {updated} Playlists {'würden aktualisiert' if dry_run else 'aktualisiert'}")


if __name__ == '__main__':
    main()
