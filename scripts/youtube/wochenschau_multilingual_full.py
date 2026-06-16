"""
🌍 Wochenschau FULL Multilingual SEO Update
============================================
Updates ALL public Wochenschau videos with 14-language multilingual descriptions.
Uses individual event data from config/wochenschau_complete_locations.json.

Features:
- 14-language search blocks in description
- Individual historical event context per video
- Idempotency: skips videos already updated (checks for 🇯🇵 flag)
- Auto-stop on quota error
- Saves detailed report

Quota: ~50 units per video (videos.list=1 + videos.update=50)
Total: ~42 videos × 51 = ~2,142 units

Usage:
  python scripts/youtube/wochenschau_multilingual_full.py          # DRY RUN
  python scripts/youtube/wochenschau_multilingual_full.py --apply  # LIVE
"""

import json
import sys
import time
import re
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ============================================================
# CONFIG
# ============================================================
DRY_RUN = '--apply' not in sys.argv
BATCH_LIMIT = 50  # max videos per run
SLEEP_BETWEEN = 1.5  # seconds between API calls

# ============================================================
# AUTH
# ============================================================
with open('config/youtube_oauth.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['access_token'],
    refresh_token=token_data['refresh_token'],
    token_uri=token_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# ============================================================
# LOAD LOCATION/EVENT DATA
# ============================================================
with open('config/wochenschau_complete_locations.json', 'r', encoding='utf-8') as f:
    LOCATIONS = json.load(f)

# ============================================================
# ALL PUBLIC WOCHENSCHAU VIDEO IDs (from channel_snapshot_2026_02_06)
# ============================================================
WOCHENSCHAU_VIDEOS = [
    # 1939 - Pre-War & Poland
    {'id': 'o33-c1riv4U', 'nr': '459'},   # Pre-War Era (Jun 1939)
    {'id': 'dAp7JFDhE3U', 'nr': '468'},   # Nazi-Soviet Pact (Aug 1939)
    {'id': 't-VIxJaWE74', 'nr': '470'},   # War Begins (Sep 1939)
    {'id': '9muRRAleqdA', 'nr': '471'},   # Poland Campaign (Sep 1939)
    {'id': '3AtirtgrfUI', 'nr': '473'},   # Fall of Warsaw (Sep 1939)
    {'id': 'iRzeiRoAsj4', 'nr': '477'},   # Poland Occupied (Oct 1939)
    {'id': 'jeLWajro1As', 'nr': '480'},   # Bürgerbräu Bomb (Nov 1939)
    {'id': 'N7WPQUjFJjA', 'nr': '482'},   # Winter War Begins (Nov 1939)
    {'id': 'Qn7Nvx7eWz4', 'nr': '483'},   # Winter War (Dec 1939)

    # 1940 - Western Front, Battle of Britain
    {'id': 'DLifkhU0q1w', 'nr': '488'},   # Phoney War (Jan 1940)
    {'id': 'a5VVGGHPlsg', 'nr': '502'},   # Norway Invasion (Apr 1940)
    {'id': 'fC0MlizsAQQ', 'nr': '508'},   # Dunkirk Pocket (May 1940)
    {'id': '2uHl4LYN8O8', 'nr': '509'},   # Dunkirk Evacuation (Jun 1940)
    {'id': 'xblc6reUMr0', 'nr': '512'},   # French Armistice (Jun 1940)
    {'id': 'g8215791a7I', 'nr': '513'},   # Channel Islands (Jul 1940)
    {'id': '7st-GFEwdWQ', 'nr': '514'},   # Berlin Parade (Jul 1940)
    {'id': 'vkCoIJGAf3E', 'nr': '515'},   # Battle of Britain (Jul 1940)
    {'id': 'Yj_QcM9Ce28', 'nr': '518'},   # Channel Battles (Aug 1940)
    {'id': '7yfdqylo9qs', 'nr': '519'},   # Eagle Day (Aug 1940)
    {'id': 'i2mRp5iMxoo', 'nr': '520'},   # Battle Peak (Aug 1940)
    {'id': 'S31f7FuEvXw', 'nr': '522'},   # Berlin Retaliation (Sep 1940)
    {'id': 'fNCZYqnK3Cc', 'nr': '523'},   # London Blitz (Sep 1940)

    # 1941 - Africa, Balkans, Barbarossa
    {'id': 'J3LWOLaxuCc', 'nr': '542'},   # Tobruk Falls (Jan 1941)
    {'id': 's5d9cAM6REo', 'nr': '543'},   # Africa Corps (Jan 1941)
    {'id': 'eBzXzhNYppQ', 'nr': '544'},   # Rommel Arrives (Feb 1941)
    {'id': '7bqlAPsgzAQ', 'nr': '545'},   # Africa Offensive (Feb 1941)
    {'id': '6wop-BU_XME', 'nr': '547'},   # Africa Campaign (Feb 1941)
    {'id': 'ZuD1fAyGiUw', 'nr': '548'},   # Bulgaria Joins Axis (Mar 1941)
    {'id': 'wEMKHQPopHY', 'nr': '550'},   # Yugoslavia Crisis (Mar 1941)
    {'id': 'tVD8197vAyE', 'nr': '573'},   # Kiev Battle (Aug 1941)

    # 1943 - Turning Point
    {'id': '0sO7jVL43yQ', 'nr': '652'},   # Kharkov III (Mar 1943)
    {'id': 'dYBzf5V1TjI', 'nr': '654'},   # Tunisia Battles (Mar 1943)

    # 1944 - Late War
    {'id': '6K-MuUu6L44', 'nr': '720'},   # V1 Attacks (Jun 1944)
    {'id': 'W-UcQleew8Y', 'nr': '721'},   # Bagration Begins (Jun 1944)
    {'id': 'bZkUPQHqyfg', 'nr': '722'},   # Bagration (Jul 1944)
    {'id': 'jGz1kC1Z69A', 'nr': '746'},   # Ardennes Offensive (Dec 1944)

    # 1945 - Final Phase
    {'id': 'w2UvksMOs3c', 'nr': '750'},   # Vistula Offensive (Jan 1945)
    {'id': '6YLPpJLgVXk', 'nr': '751'},   # Eastern Collapse (Jan 1945)
    {'id': 'iEEvt-s1XhQ', 'nr': '753'},   # Yalta Conference (Feb 1945)
    {'id': 'H_n_mS-eKps', 'nr': '754'},   # Dresden Bombed (Feb 1945)

    # Post-War
    {'id': '9AgSJyMnxi8', 'nr': 'atomic'},  # Atomic Bomb Newsreel (1946)
]


def get_event_data(nr_str):
    """Get event data from wochenschau_complete_locations.json"""
    if nr_str in LOCATIONS:
        loc = LOCATIONS[nr_str]
        return {
            'event_en': loc.get('event_en', ''),
            'event_de': loc.get('event_de', ''),
            'location': loc.get('location', {}).get('desc', ''),
            'historical_note': loc.get('historical_note', ''),
            'date': loc.get('date', ''),
        }
    return None


def extract_title_info(title):
    """Extract number, date, and event from title"""
    nr_match = re.search(r'(?:Wochenschau|Nr\.?)\s*(\d+)', title)
    date_match = re.search(r'\(([A-Za-z]+\s+\d{4})\)', title)
    event_match = re.search(r':\s*(.+?)\s*\(', title)
    
    nr = nr_match.group(1) if nr_match else ''
    date_str = date_match.group(1) if date_match else ''
    event = event_match.group(1) if event_match else title.split('|')[0].strip()
    
    return nr, date_str, event


def build_multilingual_description(title, nr_str, event_data=None):
    """Build 14-language multilingual description for a Wochenschau video"""
    
    nr, date_str, event = extract_title_info(title)
    
    # Get individual location/event context
    location = ''
    hist_note_de = ''
    hist_note_en = ''
    event_de = event
    event_en = event
    
    if event_data:
        location = event_data.get('location', '')
        hist_note_de = event_data.get('historical_note', '')
        event_de = event_data.get('event_de', event)
        event_en = event_data.get('event_en', event)
        # Build English note from German if needed
        hist_note_en = f"Episode #{nr} of the Deutsche Wochenschau"
    
    # Special case: Atomic Bomb Newsreel
    if 'atomic' in nr_str.lower() or 'atomic' in title.lower():
        nr = 'N/A'
        event_de = 'Atombombentest'
        event_en = 'Atomic Bomb Test'
        location = 'Bikini Atoll, Pacific'
        hist_note_de = 'Nachkriegs-Nachrichtenfilm über Atombombentests'
    
    location_line = f"\n📍 Location: {location}" if location else ""
    hist_line_de = f"\n📜 {hist_note_de}" if hist_note_de else ""

    desc = f"""⚠️ HISTORISCHES DOKUMENT – NUR FÜR BILDUNGSZWECKE
⚠️ HISTORICAL DOCUMENT – FOR EDUCATIONAL PURPOSES ONLY

🎬 Die Deutsche Wochenschau Nr. {nr} | {event_en} | 8K Restored
{event_de} – Original-Wochenschau in 8K restauriert.{location_line}{hist_line_de}

This footage is a primary source for historical research, media studies, and education.
The contents do NOT reflect the views of the uploader.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:

🇺🇸 ENGLISH: German WWII newsreel #{nr} "{event_en}" – restored in stunning 8K quality. Primary historical source for World War II research, propaganda analysis, and media history.

🇩🇪 DEUTSCH: Deutsche Wochenschau Nr. {nr} "{event_de}" – in 8K restauriert. Historische Primärquelle für Zweiten Weltkrieg, Propagandaforschung und Mediengeschichte.

🇪🇸 ESPAÑOL: Noticiario alemán WWII #{nr} "{event_en}" – restaurado en 8K. Fuente primaria histórica para la investigación de la Segunda Guerra Mundial y análisis de propaganda.

🇫🇷 FRANÇAIS: Actualités allemandes #{nr} "{event_en}" – restaurées en 8K. Source historique primaire pour la recherche sur la Seconde Guerre mondiale et l'analyse de la propagande.

🇵🇹 PORTUGUÊS: Noticiário alemão #{nr} "{event_en}" – restaurado em 8K. Fonte histórica primária para pesquisa da Segunda Guerra Mundial e análise de propaganda.

🇮🇹 ITALIANO: Cinegiornale tedesco #{nr} "{event_en}" – restaurato in 8K. Fonte storica primaria per la ricerca sulla Seconda Guerra Mondiale e l'analisi della propaganda.

🇷🇺 РУССКИЙ: Немецкий кинохроника #{nr} "{event_en}" – восстановлена в 8K. Первичный исторический источник для исследования Второй мировой войны.

🇯🇵 日本語: ドイツWWIIニュース映画 #{nr}「{event_en}」を8Kで復元。第二次世界大戦研究とプロパガンダ分析のための歴史的一次資料。

🇨🇳 中文: 德国二战新闻片第{nr}集「{event_en}」以8K修复。二战研究与宣传分析的历史原始资料。

🇰🇷 한국어: 독일 WWII 뉴스릴 #{nr} "{event_en}" 8K 복원. 제2차 세계대전 연구와 선전 분석을 위한 역사적 1차 자료.

🇮🇳 हिंदी: जर्मन WWII न्यूज़रील #{nr} "{event_en}" 8K में पुनर्स्थापित। द्वितीय विश्व युद्ध अनुसंधान और प्रचार विश्लेषण के लिए ऐतिहासिक प्राथमिक स्रोत।

🇸🇦 العربية: فيلم إخباري ألماني #{nr} "{event_en}" بجودة 8K. مصدر تاريخي أولي لأبحاث الحرب العالمية الثانية وتحليل الدعاية.

🇮🇩 INDONESIA: Berita Jerman WWII #{nr} "{event_en}" direstorasi 8K. Sumber sejarah utama untuk penelitian Perang Dunia II dan analisis propaganda.

🇹🇷 TÜRKÇE: Alman WWII haber filmi #{nr} "{event_en}" 8K'da restore edildi. İkinci Dünya Savaşı araştırması ve propaganda analizi için birincil tarihsel kaynak.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts on this historical footage!
🔔 SUBSCRIBE for more restored WWII archives in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

📜 Source: Public Domain (UFA/DW 1939-1945)
📚 Category: Education & Historical Research

#Wochenschau #WWII #History #8K #PublicDomain"""

    return desc


def is_already_multilingual(description):
    """Check if description already has multilingual content"""
    flags = ['🇯🇵', '🇨🇳', '🇰🇷', '🇮🇳', '🇸🇦', '🇮🇩', '🇹🇷']
    flag_count = sum(1 for f in flags if f in description)
    return flag_count >= 4  # If 4+ of these flags present, already done


# ============================================================
# MAIN EXECUTION
# ============================================================
def main():
    mode = "🔴 LIVE" if not DRY_RUN else "🟡 DRY RUN"
    print(f"\n{'='*60}")
    print(f"🌍 WOCHENSCHAU MULTILINGUAL SEO UPDATE")
    print(f"   Mode: {mode}")
    print(f"   Videos: {len(WOCHENSCHAU_VIDEOS)}")
    print(f"   Languages: 14")
    print(f"   Est. Quota: ~{len(WOCHENSCHAU_VIDEOS) * 51} units")
    print(f"{'='*60}\n")

    results = {
        'timestamp': datetime.now().isoformat(),
        'mode': 'LIVE' if not DRY_RUN else 'DRY_RUN',
        'updated': [],
        'skipped': [],
        'failed': [],
        'quota_used': 0,
    }

    for idx, video in enumerate(WOCHENSCHAU_VIDEOS[:BATCH_LIMIT]):
        video_id = video['id']
        nr_str = video['nr']
        
        print(f"\n[{idx+1}/{len(WOCHENSCHAU_VIDEOS)}] {video_id} (Nr. {nr_str})...", end=" ")
        
        try:
            # READ: Get current video data (1 quota unit)
            current = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            results['quota_used'] += 1
            
            if not current.get('items'):
                print("❌ Not found!")
                results['failed'].append({'id': video_id, 'nr': nr_str, 'reason': 'not_found'})
                continue
            
            snippet = current['items'][0]['snippet']
            title = snippet['title']
            current_desc = snippet.get('description', '')
            
            print(f"\n   📹 {title[:65]}")
            
            # IDEMPOTENCY CHECK
            if is_already_multilingual(current_desc):
                print(f"   ⏭️  Already multilingual — SKIPPED")
                results['skipped'].append({'id': video_id, 'nr': nr_str, 'title': title})
                continue
            
            # Get event-specific data
            event_data = get_event_data(nr_str)
            if event_data:
                print(f"   📍 {event_data.get('location', 'N/A')} | {event_data.get('event_en', 'N/A')}")
            
            # Build new description
            new_desc = build_multilingual_description(title, nr_str, event_data)
            
            if DRY_RUN:
                print(f"   🟡 DRY RUN: Would update ({len(new_desc)} chars)")
                results['updated'].append({
                    'id': video_id, 'nr': nr_str, 'title': title,
                    'desc_length': len(new_desc), 'mode': 'dry_run'
                })
                continue
            
            # WRITE: Update video (50 quota units)
            snippet['description'] = new_desc
            
            youtube.videos().update(
                part='snippet',
                body={'id': video_id, 'snippet': snippet}
            ).execute()
            
            results['quota_used'] += 50
            print(f"   ✅ UPDATED! ({len(new_desc)} chars, {results['quota_used']} quota)")
            results['updated'].append({
                'id': video_id, 'nr': nr_str, 'title': title,
                'desc_length': len(new_desc), 'mode': 'live'
            })
            
            time.sleep(SLEEP_BETWEEN)
            
        except HttpError as e:
            error_msg = str(e)
            if 'quotaExceeded' in error_msg or '403' in error_msg:
                print(f"\n\n🛑 QUOTA EXCEEDED! Stopping immediately.")
                print(f"   Updated {len(results['updated'])} videos before quota limit.")
                results['failed'].append({'id': video_id, 'nr': nr_str, 'reason': 'quota_exceeded'})
                results['stopped_at'] = idx
                break
            else:
                print(f"   ❌ API Error: {error_msg[:80]}")
                results['failed'].append({'id': video_id, 'nr': nr_str, 'reason': error_msg[:120]})
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:80]}")
            results['failed'].append({'id': video_id, 'nr': nr_str, 'reason': str(e)[:120]})

    # ============================================================
    # REPORT
    # ============================================================
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"  ✅ Updated:  {len(results['updated'])}")
    print(f"  ⏭️  Skipped:  {len(results['skipped'])}")
    print(f"  ❌ Failed:   {len(results['failed'])}")
    print(f"  💰 Quota:    ~{results['quota_used']} units")
    print(f"{'='*60}")

    # Save report
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M')
    report_path = f'config/wochenschau_multilingual_report_{timestamp}.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Report saved: {report_path}")


if __name__ == '__main__':
    main()
