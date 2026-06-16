"""
Batch update remaining international categories with 18-language descriptions
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

with open('config/international_videos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def create_generic_description(title, category):
    """Create 18-language description based on category"""
    
    # Category-specific templates
    templates = {
        'Superman': {
            'en': 'Classic Fleischer Superman cartoon restored in 8K. The Man of Steel in stunning action.',
            'de': 'Klassischer Fleischer Superman-Cartoon in 8K restauriert. Der Stählerne in atemberaubender Action.',
            'tags': '#Superman #Fleischer #8K #Animation #ClassicCartoon #remAIke'
        },
        'Casper': {
            'en': 'Classic Casper the Friendly Ghost cartoon restored in 8K. The lovable ghost in another adventure.',
            'de': 'Klassischer Casper-Cartoon in 8K restauriert. Der freundliche Geist in einem neuen Abenteuer.',
            'tags': '#Casper #FriendlyGhost #8K #Animation #ClassicCartoon #remAIke'
        },
        'Felix the Cat': {
            'en': 'Classic Felix the Cat silent cartoon restored in 8K. The legendary cat in vintage animation.',
            'de': 'Klassischer Felix-Stummfilm in 8K restauriert. Die legendäre Katze in Vintage-Animation.',
            'tags': '#FelixTheCat #SilentFilm #8K #Animation #VintageCartoon #remAIke'
        },
        'Popeye': {
            'en': 'Classic Popeye cartoon by Fleischer Studios restored in 8K. The sailor man in action.',
            'de': 'Klassischer Popeye-Cartoon von Fleischer Studios in 8K restauriert. Der Seemann in Aktion.',
            'tags': '#Popeye #Fleischer #8K #Animation #ClassicCartoon #remAIke'
        },
        'Porky Pig': {
            'en': 'Classic Porky Pig cartoon restored in 8K. The lovable stuttering pig in another adventure.',
            'de': 'Klassischer Porky Pig-Cartoon in 8K restauriert. Das liebenswerte Schweinchen in neuem Abenteuer.',
            'tags': '#PorkyPig #LooneyTunes #8K #Animation #WB #remAIke'
        },
        'Christmas': {
            'en': 'Classic Christmas animation restored in 8K. Holiday nostalgia at its finest.',
            'de': 'Klassische Weihnachtsanimation in 8K restauriert. Festtagsnostalgie vom Feinsten.',
            'tags': '#Christmas #Holiday #8K #VintageAnimation #PublicDomain #remAIke'
        },
        'Looney Tunes': {
            'en': 'Classic Looney Tunes cartoon restored in 8K. Golden age animation at its finest.',
            'de': 'Klassischer Looney Tunes-Cartoon in 8K restauriert. Goldenes Zeitalter der Animation.',
            'tags': '#LooneyTunes #WB #8K #Animation #ClassicCartoon #remAIke'
        },
        'Silent Films': {
            'en': 'Classic silent film restored in 8K. Cinema history brought back to life.',
            'de': 'Klassischer Stummfilm in 8K restauriert. Kinogeschichte zum Leben erweckt.',
            'tags': '#SilentFilm #ClassicCinema #8K #FilmHistory #PublicDomain #remAIke'
        },
        'Documentaries': {
            'en': 'Historic documentary restored in 8K. Important footage preserved for future generations.',
            'de': 'Historische Dokumentation in 8K restauriert. Wichtiges Filmmaterial für künftige Generationen.',
            'tags': '#Documentary #History #8K #Archives #PublicDomain #remAIke'
        },
        'Other': {
            'en': 'Classic film restored in stunning 8K quality. Vintage cinema brought back to life.',
            'de': 'Klassischer Film in atemberaubender 8K Qualität restauriert. Vintage-Kino zum Leben erweckt.',
            'tags': '#Vintage #8K #PublicDomain #ClassicFilm #remAIke'
        }
    }
    
    t = templates.get(category, templates['Other'])
    
    desc = f"""🎬 {title.split('|')[0].strip()} | 8K Restored

🇺🇸 {t['en']}
🇩🇪 {t['de']}
🇪🇸 Animación clásica restaurada en impresionante calidad 8K.
🇫🇷 Animation classique restaurée en qualité 8K époustouflante.
🇵🇹 Animação clássica restaurada em qualidade 8K deslumbrante.
🇮🇹 Animazione classica restaurata in straordinaria qualità 8K.
🇳🇱 Klassieke animatie gerestaureerd in verbluffende 8K kwaliteit.
🇵🇱 Klasyczna animacja odrestaurowana w oszałamiającej jakości 8K.
🇷🇺 Классическая анимация восстановлена в потрясающем качестве 8K.
🇯🇵 クラシックアニメーションを驚異の8K画質で復元。
🇨🇳 经典动画以惊艳的8K画质修复。
🇰🇷 클래식 애니메이션 놀라운 8K 화질로 복원.
🇹🇷 Klasik animasyon muhteşem 8K kalitesinde restore edildi.
🇸🇦 رسوم متحركة كلاسيكية تم ترميمها بجودة 8K المذهلة.
🇮🇳 क्लासिक एनिमेशन शानदार 8K गुणवत्ता में पुनर्स्थापित।
🇹🇭 แอนิเมชันคลาสสิกบูรณะในคุณภาพ 8K ที่น่าทึ่ง
🇻🇳 Hoạt hình cổ điển được phục hồi với chất lượng 8K tuyệt đẹp.
🇮🇩 Animasi klasik direstorasi dalam kualitas 8K yang menakjubkan.
🇸🇪 Klassisk animation restaurerad i fantastisk 8K-kvalitet.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you loved it!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 https://frai.tv | @remAIke_IT

{t['tags']}"""

    return desc

# Process remaining categories
categories_to_process = ['Superman', 'Casper', 'Felix the Cat', 'Popeye', 'Porky Pig', 
                         'Christmas', 'Looney Tunes', 'Silent Films', 'Documentaries', 'Other']

total_updated = 0
total_failed = 0

for category in categories_to_process:
    videos = data['categories'].get(category, [])
    if not videos:
        continue
    
    print(f"\n{'='*50}")
    print(f"📁 {category}: {len(videos)} videos")
    print('='*50)
    
    for i, video in enumerate(videos):
        video_id = video['id']
        title = video['title']
        
        print(f"[{i+1}/{len(videos)}] {title[:40]}...", end=" ")
        
        try:
            current = youtube.videos().list(part='snippet', id=video_id).execute()
            
            if not current.get('items'):
                print("❌ Not found")
                total_failed += 1
                continue
            
            snippet = current['items'][0]['snippet']
            new_desc = create_generic_description(snippet['title'], category)
            snippet['description'] = new_desc
            
            youtube.videos().update(
                part='snippet',
                body={'id': video_id, 'snippet': snippet}
            ).execute()
            
            print(f"✅ {len(new_desc)} chars")
            total_updated += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ {str(e)[:50]}")
            total_failed += 1

print(f"\n{'='*50}")
print(f"TOTAL: ✅ {total_updated} updated | ❌ {total_failed} failed")
print(f"💡 Quota used: ~{total_updated * 50} units")
