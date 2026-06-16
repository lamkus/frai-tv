"""
Batch update Wochenschau videos with 18-language multilingual descriptions
RUN AFTER 09:00 MEZ (Quota Reset)
"""
import json
import time
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

# Wochenschau Video IDs that need multilingual
WOCHENSCHAU_IDS = [
    '6K-MuUu6L44',  # Nr. 720
    'W-UcQleew8Y',  # Nr. 721
    'dYBzf5V1TjI',  # Nr. 654
    'jGz1kC1Z69A',  # Nr. 746
    'bZkUPQHqyfg',  # Nr. 722
    'iEEvt-s1XhQ',  # Nr. 753
    'H_n_mS-eKps',  # Nr. 754
    'w2UvksMOs3c',  # Nr. 750
    '6YLPpJLgVXk',  # Nr. 751
    'T-EsdXGhqog',  # Nr. 516
    '3rB80OGKzrg',  # Nr. 511
]

def create_wochenschau_description(title):
    """Create 18-language description for Deutsche Wochenschau"""
    
    # Extract number and date
    nr_match = re.search(r'Nr\.\s*(\d+)', title)
    date_match = re.search(r'\((\d{2}\.\d{2}\.\d{4})\)', title)
    
    nr = nr_match.group(1) if nr_match else "???"
    date = date_match.group(1) if date_match else ""
    
    desc = f"""🎬 Die Deutsche Wochenschau Nr. {nr} | WWII German Newsreel | 8K Restored

⚠️ HISTORICAL DOCUMENT – FOR EDUCATIONAL PURPOSES ONLY
This footage is presented as a primary source for historical research and education.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 ENGLISH: German WWII newsreel #{nr} restored in 8K. Historical document showing the German perspective during World War II. Important primary source for understanding propaganda and media history.

🇩🇪 DEUTSCH: Deutsche Wochenschau Nr. {nr} in 8K restauriert. Historisches Dokument mit deutscher Perspektive im Zweiten Weltkrieg. Wichtige Primärquelle für Propaganda- und Mediengeschichte.

🇪🇸 ESPAÑOL: Noticiario alemán WWII #{nr} restaurado en 8K. Documento histórico mostrando la perspectiva alemana durante la Segunda Guerra Mundial. Fuente primaria importante.

🇫🇷 FRANÇAIS: Actualités allemandes WWII #{nr} restaurées en 8K. Document historique montrant la perspective allemande pendant la Seconde Guerre mondiale. Source primaire importante.

🇵🇹 PORTUGUÊS: Noticiário alemão WWII #{nr} restaurado em 8K. Documento histórico mostrando a perspectiva alemã durante a Segunda Guerra Mundial. Fonte primária importante.

🇮🇹 ITALIANO: Cinegiornale tedesco WWII #{nr} restaurato in 8K. Documento storico che mostra la prospettiva tedesca durante la Seconda Guerra Mondiale. Fonte primaria importante.

🇳🇱 NEDERLANDS: Duitse WWII journaal #{nr} gerestaureerd in 8K. Historisch document dat het Duitse perspectief toont tijdens de Tweede Wereldoorlog. Belangrijke primaire bron.

🇵🇱 POLSKI: Niemiecki kronika wojenna #{nr} odrestaurowana w 8K. Dokument historyczny pokazujący niemiecką perspektywę podczas II wojny światowej. Ważne źródło pierwotne.

🇷🇺 РУССКИЙ: Немецкая кинохроника WWII #{nr} восстановлена в 8K. Исторический документ, показывающий немецкую перспективу во время Второй мировой войны. Важный первичный источник.

🇯🇵 日本語: ドイツWWIIニュース映画 #{nr} を8Kで復元。第二次世界大戦中のドイツの視点を示す歴史的文書。重要な一次資料。

🇨🇳 中文: 德国二战新闻片 #{nr} 以8K修复。展示二战期间德国视角的历史文件。重要的第一手资料。

🇰🇷 한국어: 독일 WWII 뉴스릴 #{nr} 8K 복원. 제2차 세계대전 당시 독일의 관점을 보여주는 역사적 문서. 중요한 1차 자료.

🇹🇷 TÜRKÇE: Alman WWII haber filmi #{nr} 8K'da restore edildi. İkinci Dünya Savaşı sırasında Alman perspektifini gösteren tarihi belge. Önemli birincil kaynak.

🇸🇦 العربية: فيلم إخباري ألماني من الحرب العالمية الثانية رقم {nr} بجودة 8K. وثيقة تاريخية تُظهر المنظور الألماني خلال الحرب العالمية الثانية. مصدر أولي مهم.

🇮🇳 हिंदी: जर्मन WWII न्यूज़रील #{nr} 8K में पुनर्स्थापित। द्वितीय विश्व युद्ध के दौरान जर्मन परिप्रेक्ष्य दिखाने वाला ऐतिहासिक दस्तावेज़। महत्वपूर्ण प्राथमिक स्रोत।

🇹🇭 ไทย: ข่าวเยอรมัน WWII #{nr} บูรณะใน 8K เอกสารประวัติศาสตร์แสดงมุมมองเยอรมันในสงครามโลกครั้งที่ 2 แหล่งข้อมูลปฐมภูมิที่สำคัญ

🇻🇳 TIẾNG VIỆT: Tin tức Đức WWII #{nr} phục hồi 8K. Tài liệu lịch sử thể hiện góc nhìn Đức trong Thế chiến II. Nguồn tư liệu gốc quan trọng.

🇮🇩 BAHASA INDONESIA: Berita Jerman WWII #{nr} direstorasi 8K. Dokumen sejarah yang menunjukkan perspektif Jerman selama Perang Dunia II. Sumber primer penting.

🇸🇪 SVENSKA: Tysk WWII nyhetsjournalen #{nr} restaurerad i 8K. Historiskt dokument som visar det tyska perspektivet under andra världskriget. Viktig primärkälla.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 FOR EDUCATIONAL & RESEARCH USE
🎬 LIKE for more historical content!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored archives!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 https://frai.tv | @remAIke_IT

#Wochenschau #WWII #History #8K #Archives #Documentary #remAIke"""

    return desc

print(f"🎬 Wochenschau Multilingual Update - {len(WOCHENSCHAU_IDS)} Videos")
print("="*50)

updated = 0
failed = 0

for video_id in WOCHENSCHAU_IDS:
    print(f"\n[{updated+failed+1}/{len(WOCHENSCHAU_IDS)}] Processing {video_id}...", end=" ")
    
    try:
        current = youtube.videos().list(part='snippet', id=video_id).execute()
        
        if not current.get('items'):
            print("❌ Not found")
            failed += 1
            continue
        
        snippet = current['items'][0]['snippet']
        title = snippet['title']
        print(f"{title[:40]}...")
        
        new_desc = create_wochenschau_description(title)
        snippet['description'] = new_desc
        
        youtube.videos().update(
            part='snippet',
            body={'id': video_id, 'snippet': snippet}
        ).execute()
        
        print(f"  ✅ Updated! {len(new_desc)} chars")
        updated += 1
        time.sleep(1)
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:60]}")
        failed += 1

print(f"\n{'='*50}")
print(f"✅ Updated: {updated}")
print(f"❌ Failed: {failed}")
print(f"💡 Quota used: ~{updated * 50} units")
