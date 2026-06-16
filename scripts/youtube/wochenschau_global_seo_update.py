#!/usr/bin/env python3
"""
WOCHENSCHAU GLOBAL SEO UPDATE - 14 LANGUAGES
============================================
Updates all 25 Wochenschau videos with complete multilingual SEO.

Languages covered (by YouTube user base 2025):
1. 🇮🇳 Hindi (500M)
2. 🇺🇸 English (254M)
3. 🇮🇩 Indonesian (151M)
4. 🇧🇷 Portuguese (150M)
5. 🇲🇽 Spanish (85M)
6. 🇯🇵 Japanese (78.5M)
7. 🇩🇪 German (64.7M)
8. 🇻🇳 Vietnamese (62.1M)
9. 🇹🇷 Turkish (57.9M)
10. 🇫🇷 French (51.5M)
11. 🇪🇬 Arabic (49.3M)
12. 🇰🇷 Korean (42.9M)
13. 🇷🇺 Russian (growing)
14. 🇨🇳 Chinese (diaspora)
"""

import os
import sys
import json
import argparse
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
OAUTH_FILE = 'config/youtube_oauth.json'

# ========================================
# 🌍 GLOBAL MULTILINGUAL TAGS (14 Languages)
# ========================================
GLOBAL_WWII_TAGS = {
    # 🇩🇪 German (64.7M users)
    "de": ["Zweiter Weltkrieg", "Deutsche Wochenschau", "Geschichte", "Dokumentation", "Nazi Deutschland"],
    
    # 🇬🇧 English (309.5M users: USA+UK)
    "en": ["World War II", "WWII", "WW2", "German newsreel", "history", "documentary", "Nazi Germany"],
    
    # 🇪🇸 Spanish (124M users: Mexico+Spain+LATAM)
    "es": ["Segunda Guerra Mundial", "noticiero alemán", "historia", "documental", "Alemania Nazi"],
    
    # 🇵🇹 Portuguese (150M users: Brazil)
    "pt": ["Segunda Guerra Mundial", "cinejornal alemão", "história", "documentário"],
    
    # 🇫🇷 French (51.5M users)
    "fr": ["Seconde Guerre mondiale", "actualités allemandes", "histoire", "documentaire"],
    
    # 🇷🇺 Russian (growing market)
    "ru": ["Вторая мировая война", "немецкая кинохроника", "история", "документальный"],
    
    # 🇯🇵 Japanese (78.5M users)
    "ja": ["第二次世界大戦", "ドイツニュース映画", "歴史", "ドキュメンタリー"],
    
    # 🇮🇳 Hindi (500M users - LARGEST MARKET!)
    "hi": ["द्वितीय विश्व युद्ध", "जर्मन न्यूज़रील", "इतिहास", "वृत्तचित्र"],
    
    # 🇨🇳 Chinese (diaspora + Taiwan/HK)
    "zh": ["二战", "第二次世界大战", "德国新闻片", "历史纪录片"],
    
    # 🇸🇦 Arabic (49.3M users: Egypt+MENA)
    "ar": ["الحرب العالمية الثانية", "النشرة الإخبارية الألمانية", "تاريخ", "وثائقي"],
    
    # 🇮🇩 Indonesian (151M users - 3rd largest!)
    "id": ["Perang Dunia II", "berita Jerman", "sejarah", "dokumenter", "Nazi Jerman"],
    
    # 🇻🇳 Vietnamese (62.1M users)
    "vi": ["Thế chiến thứ hai", "tin tức Đức", "lịch sử", "phim tài liệu"],
    
    # 🇹🇷 Turkish (57.9M users)
    "tr": ["İkinci Dünya Savaşı", "Alman haber filmi", "tarih", "belgesel"],
    
    # 🇰🇷 Korean (42.9M users)
    "ko": ["제2차 세계대전", "독일 뉴스릴", "역사", "다큐멘터리"],
}

# ========================================
# 🗓️ EVENT TRANSLATIONS
# ========================================
EVENT_TRANSLATIONS = {
    "Battle of Britain": {
        "de": "Luftschlacht um England",
        "es": "Batalla de Inglaterra", 
        "fr": "Bataille d'Angleterre",
        "pt": "Batalha da Grã-Bretanha",
        "ru": "Битва за Британию",
        "ja": "バトル・オブ・ブリテン",
        "hi": "ब्रिटेन की लड़ाई",
        "zh": "不列颠之战",
        "ar": "معركة بريطانيا",
        "id": "Pertempuran Britania",
        "tr": "Britanya Muharebesi",
        "ko": "영국 본토 항공전",
        "vi": "Trận chiến nước Anh",
    },
    "Operation Barbarossa": {
        "de": "Unternehmen Barbarossa",
        "es": "Operación Barbarroja",
        "fr": "Opération Barbarossa",
        "pt": "Operação Barbarossa",
        "ru": "Операция Барбаросса",
        "ja": "バルバロッサ作戦",
        "hi": "ऑपरेशन बारबरोसा",
        "zh": "巴巴罗萨行动",
        "ar": "عملية بارباروسا",
        "id": "Operasi Barbarossa",
        "tr": "Barbarossa Harekâtı",
        "ko": "바르바로사 작전",
        "vi": "Chiến dịch Barbarossa",
    },
    "Stalingrad": {
        "de": "Schlacht von Stalingrad",
        "es": "Batalla de Stalingrado",
        "fr": "Bataille de Stalingrad",
        "pt": "Batalha de Stalingrado",
        "ru": "Сталинградская битва",
        "ja": "スターリングラード攻防戦",
        "hi": "स्तालिनग्राद की लड़ाई",
        "zh": "斯大林格勒战役",
        "ar": "معركة ستالينغراد",
        "id": "Pertempuran Stalingrad",
        "tr": "Stalingrad Muharebesi",
        "ko": "스탈린그라드 전투",
        "vi": "Trận Stalingrad",
    },
    "D-Day": {
        "de": "Landung in der Normandie",
        "es": "Día D",
        "fr": "Jour J",
        "pt": "Dia D",
        "ru": "День Д",
        "ja": "ノルマンディー上陸作戦",
        "hi": "डी-डे",
        "zh": "诺曼底登陆",
        "ar": "يوم النصر",
        "id": "Hari-H",
        "tr": "D-Günü",
        "ko": "노르망디 상륙작전",
        "vi": "Ngày D",
    },
    "Pearl Harbor": {
        "de": "Angriff auf Pearl Harbor",
        "es": "Ataque a Pearl Harbor",
        "fr": "Attaque de Pearl Harbor",
        "pt": "Ataque a Pearl Harbor",
        "ru": "Нападение на Пёрл-Харбор",
        "ja": "真珠湾攻撃",
        "hi": "पर्ल हार्बर हमला",
        "zh": "珍珠港事件",
        "ar": "هجوم بيرل هاربر",
        "id": "Serangan Pearl Harbor",
        "tr": "Pearl Harbor Saldırısı",
        "ko": "진주만 공격",
        "vi": "Trận Trân Châu Cảng",
    },
    "Afrika Korps": {
        "de": "Afrikafeldzug",
        "es": "Afrika Korps",
        "fr": "Afrikakorps",
        "pt": "Afrika Korps",
        "ru": "Африканский корпус",
        "ja": "アフリカ軍団",
        "hi": "अफ्रीका कोर",
        "zh": "非洲军团",
        "ar": "فيلق أفريقيا",
        "id": "Korps Afrika",
        "tr": "Afrika Kolordusu",
        "ko": "아프리카 군단",
        "vi": "Quân đoàn châu Phi",
    },
    "Blitzkrieg": {
        "de": "Blitzkrieg",
        "es": "Guerra relámpago",
        "fr": "Guerre éclair",
        "pt": "Guerra relâmpago",
        "ru": "Блицкриг",
        "ja": "電撃戦",
        "hi": "बिजली युद्ध",
        "zh": "闪电战",
        "ar": "الحرب الخاطفة",
        "id": "Perang kilat",
        "tr": "Yıldırım savaşı",
        "ko": "전격전",
        "vi": "Chiến tranh chớp nhoáng",
    },
}

# ========================================
# 📺 ALL 25 WOCHENSCHAU VIDEOS
# ========================================
WOCHENSCHAU_DATA = [
    {"id": "jFJ5Hl8KD_k", "nr": 516, "date": "12.09.1940", "event": "Battle of Britain", "title_de": "Luftschlacht um England"},
    {"id": "vGjWfR3R2gM", "nr": 517, "date": "19.09.1940", "event": "Battle of Britain", "title_de": "Angriffe auf London"},
    {"id": "x3LZuZf-oLc", "nr": 518, "date": "26.09.1940", "event": "Battle of Britain", "title_de": "Kampf um England"},
    {"id": "sYIFRzQzz6s", "nr": 519, "date": "03.10.1940", "event": "Battle of Britain", "title_de": "Luftkämpfe über dem Kanal"},
    {"id": "TlCnvtjGIjc", "nr": 520, "date": "10.10.1940", "event": "Battle of Britain", "title_de": "London unter Beschuss"},
    {"id": "IWlK3i98a7s", "nr": 521, "date": "17.10.1940", "event": "Battle of Britain", "title_de": "Nachtangriffe"},
    {"id": "OQ3ntUF8tnk", "nr": 522, "date": "24.10.1940", "event": "Afrika Korps", "title_de": "Afrikafeldzug beginnt"},
    {"id": "FhJLl7-LnPE", "nr": 523, "date": "31.10.1940", "event": "Afrika Korps", "title_de": "Wüstenkrieg"},
    {"id": "RKd4wO-nnNs", "nr": 524, "date": "07.11.1940", "event": "Afrika Korps", "title_de": "Rommel in Nordafrika"},
    {"id": "q1FIZvWRvKs", "nr": 525, "date": "14.11.1940", "event": "Blitzkrieg", "title_de": "Balkanfeldzug"},
    {"id": "cG2qwKHiJCE", "nr": 526, "date": "21.11.1940", "event": "Blitzkrieg", "title_de": "Griechenland"},
    {"id": "ENZm2TCGDV8", "nr": 527, "date": "28.11.1940", "event": "Afrika Korps", "title_de": "Afrika Offensive"},
    {"id": "C3j7wnQx_gE", "nr": 528, "date": "05.12.1940", "event": "Afrika Korps", "title_de": "Tobruk"},
    {"id": "4KCm0cVy_cI", "nr": 529, "date": "12.12.1940", "event": "Afrika Korps", "title_de": "Wüstenfüchse"},
    {"id": "gEi4lHDYClU", "nr": 530, "date": "19.12.1940", "event": "Blitzkrieg", "title_de": "Winterfront"},
    {"id": "KKLT2RqOi28", "nr": 531, "date": "26.12.1940", "event": "Blitzkrieg", "title_de": "Jahresrückblick"},
    {"id": "lP3_kCi3xdY", "nr": 532, "date": "02.01.1941", "event": "Blitzkrieg", "title_de": "Neues Jahr"},
    {"id": "ZY1yxfUKNnE", "nr": 533, "date": "09.01.1941", "event": "Afrika Korps", "title_de": "Nordafrika"},
    {"id": "s35y8Lh1uSk", "nr": 534, "date": "16.01.1941", "event": "Afrika Korps", "title_de": "El Alamein Vorbereitungen"},
    {"id": "sTbzlPjKjM0", "nr": 535, "date": "23.01.1941", "event": "Blitzkrieg", "title_de": "Ostfront Vorbereitungen"},
    {"id": "WsJpg1lqdhk", "nr": 536, "date": "30.01.1941", "event": "Blitzkrieg", "title_de": "Jahrestag der Machtergreifung"},
    {"id": "fNKvKnS-zn8", "nr": 483, "date": "03.04.1940", "event": "Blitzkrieg", "title_de": "Norwegen Invasion"},
    {"id": "b-T5xJBYKbo", "nr": 488, "date": "08.05.1940", "event": "Blitzkrieg", "title_de": "Westfeldzug"},
    {"id": "cVs5kWkbeNs", "nr": 513, "date": "22.08.1940", "event": "Battle of Britain", "title_de": "Luftschlacht beginnt"},
    {"id": "iP4K0DlIlHs", "nr": 514, "date": "29.08.1940", "event": "Battle of Britain", "title_de": "Adlertag"},
]

def get_youtube_service():
    """Authenticate and return YouTube API service."""
    creds = None
    if os.path.exists(OAUTH_FILE):
        with open(OAUTH_FILE, 'r') as f:
            creds_data = json.load(f)
            creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ OAuth credentials invalid. Run auth script first.")
            sys.exit(1)
    
    return build('youtube', 'v3', credentials=creds)

def build_title(video):
    """Build SEO-optimized title (no Nr., full date, 8K, brand)."""
    # Format: Wochenschau: [Event/Titel] (DD.MM.YYYY) | 8K HQ (4K UHD)
    return f"Wochenschau: {video['title_de']} ({video['date']}) | 8K HQ (4K UHD)"

def build_tags(video):
    """Build multilingual tags covering 14 languages."""
    tags = []
    
    # Core Brand Tags
    tags.extend(["remAIke", "remAIke_IT", "8K", "8K HQ", "UHD", "upscaled"])
    
    # Series Tags
    tags.extend(["Wochenschau", "Deutsche Wochenschau", f"Wochenschau {video['nr']}"])
    
    # Add GLOBAL_WWII_TAGS (all 14 languages)
    for lang, lang_tags in GLOBAL_WWII_TAGS.items():
        # Take first 2-3 most important tags per language to stay within limit
        tags.extend(lang_tags[:3])
    
    # Add event-specific translations
    event = video.get("event", "")
    if event and event in EVENT_TRANSLATIONS:
        for lang, translation in EVENT_TRANSLATIONS[event].items():
            tags.append(translation)
    
    # Year/Date tags
    year = video['date'].split('.')[-1]
    tags.extend([year, f"1940s", "1940er", "vintage", "archival footage", "historical footage"])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            unique_tags.append(tag)
    
    return unique_tags

def build_description(video):
    """Build complete multilingual description with CTAs."""
    event = video.get("event", "World War II")
    year = video['date'].split('.')[-1]
    
    # Get event translations
    event_trans = EVENT_TRANSLATIONS.get(event, {})
    
    desc = f"""Classic German WWII newsreel footage, AI remastered and restored in 8K HQ (4K UHD).
Original Deutsche Wochenschau Nr. {video['nr']} from {video['date']} covering {event}.

🎬 WOCHENSCHAU {video['nr']} ({video['date']})
{video['title_de']} | {event}

📜 Deutsche Wochenschau from {year} - Original German newsreel footage, restored for modern 4K and 8K displays. This historical document shows {event} from the German perspective during World War II.

⚠️ Historical document - shown for educational and research purposes only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg, {video['title_de']}
🇬🇧 German Newsreel, World War II, WWII, {event}
🇪🇸 Noticiero alemán, Segunda Guerra Mundial, {event_trans.get('es', event)}
🇫🇷 Actualités allemandes, Seconde Guerre mondiale, {event_trans.get('fr', event)}
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial, {event_trans.get('pt', event)}
🇷🇺 Немецкая кинохроника, Вторая мировая война, {event_trans.get('ru', event)}
🇯🇵 ドイツニュース映画, 第二次世界大戦, {event_trans.get('ja', event)}
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध, {event_trans.get('hi', event)}
🇨🇳 德国新闻片, 二战, {event_trans.get('zh', event)}
🇸🇦 النشرة الإخبارية الألمانية, الحرب العالمية الثانية, {event_trans.get('ar', event)}
🇮🇩 Berita Jerman, Perang Dunia II, {event_trans.get('id', event)}
🇻🇳 Tin tức Đức, Thế chiến thứ hai, {event_trans.get('vi', event)}
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı, {event_trans.get('tr', event)}
🇰🇷 독일 뉴스릴, 제2차 세계대전, {event_trans.get('ko', event)}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 Organized archive: https://frai.tv/watch/{video['id']}
🌐 Project hub: https://www.remaike.IT
📺 YouTube channel: https://www.youtube.com/@remAIke_IT
🎬 Full Playlist: https://www.youtube.com/playlist?list=PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg

📜 Source: Public Domain (German State Archives)
⚠️ Educational & Historical Use Only

#Wochenschau #WWII #GermanNewsreel #{year} #8K
"""
    return desc

def update_video(youtube, video, dry_run=True):
    """Update a single video with new SEO."""
    video_id = video['id']
    
    # Build new metadata
    new_title = build_title(video)
    new_tags = build_tags(video)
    new_desc = build_description(video)
    
    print(f"\n{'='*60}")
    print(f"📺 Video {video['nr']}: {video_id}")
    print(f"   Title: {new_title[:70]}...")
    print(f"   Tags: {len(new_tags)} ({', '.join(new_tags[:5])}...)")
    print(f"   Languages in tags: 14")
    
    if dry_run:
        print("   [DRY RUN - not applied]")
        return True
    
    try:
        # Get current video info
        response = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            print(f"   ❌ Video not found!")
            return False
        
        current_snippet = response['items'][0]['snippet']
        
        # Update snippet
        youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': {
                    'title': new_title,
                    'description': new_desc,
                    'tags': new_tags,
                    'categoryId': '27',
                    'defaultLanguage': 'de',
                    'defaultAudioLanguage': 'de',
                }
            }
        ).execute()
        
        print(f"   ✅ Updated successfully!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update Wochenschau videos with global multilingual SEO')
    parser.add_argument('--apply', action='store_true', help='Actually apply changes (default: dry run)')
    parser.add_argument('--video', type=str, help='Update only specific video by ID')
    args = parser.parse_args()
    
    dry_run = not args.apply
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║  🌍 WOCHENSCHAU GLOBAL SEO UPDATE                                  ║
║  14 Languages • 25 Videos • Maximum Reach                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  Languages: DE, EN, ES, PT, FR, RU, JA, HI, ZH, AR, ID, VI, TR, KO ║
║  Target Audience: 2.5+ Billion YouTube Users                       ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be applied")
        print("   Use --apply to actually update videos\n")
    else:
        print("⚠️  LIVE MODE - Changes will be applied to YouTube!\n")
    
    youtube = get_youtube_service()
    
    # Filter videos if specific one requested
    videos_to_update = WOCHENSCHAU_DATA
    if args.video:
        videos_to_update = [v for v in WOCHENSCHAU_DATA if v['id'] == args.video]
        if not videos_to_update:
            print(f"❌ Video {args.video} not found in WOCHENSCHAU_DATA")
            sys.exit(1)
    
    success = 0
    failed = 0
    
    for video in videos_to_update:
        if update_video(youtube, video, dry_run):
            success += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"   ✅ Success: {success}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📺 Total: {len(videos_to_update)}")
    
    if dry_run:
        print(f"\n💡 To apply changes, run: python {sys.argv[0]} --apply")

if __name__ == '__main__':
    main()
