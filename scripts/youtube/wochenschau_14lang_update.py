#!/usr/bin/env python3
"""
WOCHENSCHAU GLOBAL SEO UPDATE - 14 LANGUAGES
=============================================
Updates all 25 Wochenschau videos with complete multilingual SEO.

REAL VIDEO IDs from playlist (2026-01-16):
"""

import json
import sys
import argparse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_FILE = 'config/youtube_oauth.json'

# ========================================
# 🌍 GLOBAL MULTILINGUAL TAGS (14 Languages)
# ========================================
GLOBAL_WWII_TAGS = {
    "de": ["Zweiter Weltkrieg", "Deutsche Wochenschau", "Geschichte"],
    "en": ["World War II", "WWII", "WW2", "German newsreel", "history"],
    "es": ["Segunda Guerra Mundial", "noticiero alemán", "historia"],
    "pt": ["Segunda Guerra Mundial", "cinejornal alemão", "história"],
    "fr": ["Seconde Guerre mondiale", "actualités allemandes", "histoire"],
    "ru": ["Вторая мировая война", "немецкая кинохроника", "история"],
    "ja": ["第二次世界大戦", "ドイツニュース映画", "歴史"],
    "hi": ["द्वितीय विश्व युद्ध", "जर्मन न्यूज़रील", "इतिहास"],
    "zh": ["二战", "第二次世界大战", "德国新闻片"],
    "ar": ["الحرب العالمية الثانية", "النشرة الإخبارية الألمانية"],
    "id": ["Perang Dunia II", "berita Jerman", "sejarah"],
    "vi": ["Thế chiến thứ hai", "tin tức Đức", "lịch sử"],
    "tr": ["İkinci Dünya Savaşı", "Alman haber filmi", "tarih"],
    "ko": ["제2차 세계대전", "독일 뉴스릴", "역사"],
}

# ========================================
# 📺 ALL 25 REAL WOCHENSCHAU VIDEO IDs
# ========================================
REAL_VIDEO_IDS = [
    {"id": "iRzeiRoAsj4", "nr": 477, "date": "11.10.1939", "event": "Poland Occupied"},
    {"id": "N7WPQUjFJjA", "nr": 482, "date": "30.11.1939", "event": "Winter War Begins"},
    {"id": "3rB80OGKzrg", "nr": 511, "date": "14.06.1940", "event": "Paris Falls"},
    {"id": "Qn7Nvx7eWz4", "nr": 483, "date": "06.12.1939", "event": "Winter War"},
    {"id": "DLifkhU0q1w", "nr": 488, "date": "10.01.1940", "event": "Phoney War"},
    {"id": "fC0MlizsAQQ", "nr": 508, "date": "29.05.1940", "event": "Dunkirk Pocket"},
    {"id": "T-EsdXGhqog", "nr": 516, "date": "24.07.1940", "event": "Battle of Britain"},
    {"id": "4raY-jvtci4", "nr": 521, "date": "07.09.1940", "event": "London Blitz"},
    {"id": "S31f7FuEvXw", "nr": 522, "date": "14.09.1940", "event": "Berlin Raid"},
    {"id": "D_kLmNFlbZI", "nr": 513, "date": "01.07.1940", "event": "Channel Islands"},
    {"id": "0sO7jVL43yQ", "nr": 652, "date": "17.03.1943", "event": "Kharkov Retaken"},
    {"id": "dYBzf5V1TjI", "nr": 654, "date": "01.04.1943", "event": "Tunisia Battles"},
    {"id": "fNCZYqnK3Cc", "nr": 523, "date": "21.09.1940", "event": "London Blitz"},
    {"id": "1O8sVLS-zfI", "nr": 524, "date": "28.09.1940", "event": "Sea Lion Cancelled"},
    {"id": "6K-MuUu6L44", "nr": 720, "date": "22.06.1944", "event": "V1 Flying Bombs"},
    {"id": "w2UvksMOs3c", "nr": 750, "date": "18.01.1945", "event": "Vistula Offensive"},
    {"id": "6YLPpJLgVXk", "nr": 751, "date": "25.01.1945", "event": "Eastern Collapse"},
    {"id": "iEEvt-s1XhQ", "nr": 753, "date": "08.02.1945", "event": "Yalta Conference"},
    {"id": "H_n_mS-eKps", "nr": 754, "date": "15.02.1945", "event": "Dresden Bombed"},
    {"id": "W-UcQleew8Y", "nr": 721, "date": "29.06.1944", "event": "Bagration Begins"},
    {"id": "bZkUPQHqyfg", "nr": 722, "date": "06.07.1944", "event": "Bagration"},
    {"id": "jGz1kC1Z69A", "nr": 746, "date": "21.12.1944", "event": "Battle of Bulge"},
    {"id": "jeLWajro1As", "nr": 480, "date": "08.11.1939", "event": "Bürgerbräukeller Bomb"},
    {"id": "2uHl4LYN8O8", "nr": 509, "date": "05.06.1940", "event": "Dunkirk Evacuation"},
    {"id": "xblc6reUMr0", "nr": 512, "date": "22.06.1940", "event": "French Armistice"},
]

def get_youtube_service():
    """Authenticate and return YouTube API service."""
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
        creds = Credentials.from_authorized_user_info(creds_data)
    return build('youtube', 'v3', credentials=creds)

def build_title(video):
    """Build SEO-optimized title."""
    # Format: Wochenschau: [Event] (DD.MM.YYYY) | 8K HQ (4K UHD)
    return f"Wochenschau: {video['event']} ({video['date']}) | 8K HQ (4K UHD)"

def build_tags(video):
    """Build multilingual tags - RESPECTS 500 char YouTube limit."""
    tags = ["remAIke", "remAIke_IT", "8K", "UHD", "Wochenschau", f"Wochenschau {video['nr']}"]
    
    # Priority languages by user base (only key terms to fit limit)
    priority_tags = [
        # English (254M)
        "World War II", "WWII", "German newsreel",
        # Spanish (124M)
        "Segunda Guerra Mundial",
        # Portuguese (150M)
        "Segunda Guerra",
        # Japanese (78.5M)
        "第二次世界大戦",
        # Russian
        "Вторая мировая",
        # German
        "Zweiter Weltkrieg", "Deutsche Wochenschau",
        # Hindi (500M!)
        "द्वितीय विश्व युद्ध",
        # Arabic (49M)
        "الحرب العالمية",
        # Indonesian (151M!)
        "Perang Dunia II",
        # French (51M)
        "Seconde Guerre",
        # Turkish (58M)
        "İkinci Dünya Savaşı",
        # Korean (43M)
        "제2차 세계대전",
    ]
    
    tags.extend(priority_tags)
    
    # Event + Year
    tags.append(video['event'])
    year = video['date'].split('.')[-1]
    tags.extend([year, "history", "archival"])
    
    # Remove duplicates and limit total characters
    unique_tags = list(dict.fromkeys(tags))
    
    # Check character limit (~500 chars)
    final_tags = []
    total_chars = 0
    for tag in unique_tags:
        if total_chars + len(tag) + 1 < 480:  # Leave buffer
            final_tags.append(tag)
            total_chars += len(tag) + 1
    
    return final_tags

def build_description(video):
    """Build complete multilingual description."""
    return f"""Classic German WWII newsreel footage, AI remastered and restored in 8K HQ (4K UHD).
Original Deutsche Wochenschau Nr. {video['nr']} from {video['date']} covering {video['event']}.

🎬 WOCHENSCHAU {video['nr']} ({video['date']})
{video['event']} | Deutsche Wochenschau

📜 German newsreel from {video['date'].split('.')[-1]} - restored for modern 4K and 8K displays.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg
🇬🇧 German Newsreel, World War II, WWII
🇪🇸 Noticiero alemán, Segunda Guerra Mundial
🇫🇷 Actualités allemandes, Seconde Guerre mondiale
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial
🇷🇺 Немецкая кинохроника, Вторая мировая война
🇯🇵 ドイツニュース映画, 第二次世界大戦
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध
🇨🇳 德国新闻片, 二战
🇸🇦 النشرة الإخبارية الألمانية, الحرب العالمية الثانية
🇮🇩 Berita Jerman, Perang Dunia II
🇻🇳 Tin tức Đức, Thế chiến thứ hai
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı
🇰🇷 독일 뉴스릴, 제2차 세계대전
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 Organized archive: https://frai.tv/watch/{video['id']}
🌐 Project hub: https://www.remaike.IT
📺 YouTube channel: https://www.youtube.com/@remAIke_IT
📜 Source: Public Domain

#Wochenschau #WWII #GermanNewsreel #{video['date'].split('.')[-1]} #8K
"""

def update_video(youtube, video, dry_run=True):
    """Update a single video."""
    video_id = video['id']
    new_title = build_title(video)
    new_tags = build_tags(video)
    new_desc = build_description(video)
    
    print(f"\n📺 {video['nr']}: {video_id}")
    print(f"   NEW Title: {new_title[:65]}...")
    print(f"   Tags: {len(new_tags)} (14 languages)")
    
    if dry_run:
        print("   [DRY RUN]")
        return True
    
    try:
        # Get current
        current = youtube.videos().list(part='snippet', id=video_id).execute()
        if not current.get('items'):
            print("   ❌ Not found!")
            return False
        
        snippet = current['items'][0]['snippet']
        
        # Update
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
        
        print("   ✅ Updated!")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║  🌍 WOCHENSCHAU GLOBAL SEO UPDATE - 14 LANGUAGES                   ║
║  Target: 2.5+ Billion YouTube Users                                ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    if not args.apply:
        print("🔍 DRY RUN - Use --apply to update\n")
    
    youtube = get_youtube_service()
    
    success = 0
    for video in REAL_VIDEO_IDS:
        if update_video(youtube, video, not args.apply):
            success += 1
    
    print(f"\n📊 SUMMARY: {success}/{len(REAL_VIDEO_IDS)} videos")

if __name__ == '__main__':
    main()
