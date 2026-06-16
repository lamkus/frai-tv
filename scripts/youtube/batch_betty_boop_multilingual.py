"""
Batch update Betty Boop videos with 18-language multilingual descriptions
"""
import json
import time
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

# Load international videos
with open('config/international_videos.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

betty_boop_videos = data['categories'].get('Betty Boop', [])
print(f"Found {len(betty_boop_videos)} Betty Boop videos to update")

def create_multilingual_description(title, year, episode_info=""):
    """Create 18-language description for Betty Boop"""
    
    # Extract episode number if present
    ep_text = ""
    if episode_info:
        ep_text = f" ({episode_info})"
    
    desc = f"""🎬 {title}{ep_text} | Betty Boop Classic Animation | 8K AI Upscaled

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇺🇸 ENGLISH: Classic Betty Boop cartoon from {year}, restored in stunning 8K quality. The iconic flapper girl in one of her most beloved adventures. Public domain animation brought back to life with AI upscaling technology.

🇩🇪 DEUTSCH: Klassischer Betty Boop Cartoon aus {year}, restauriert in atemberaubender 8K Qualität. Das ikonische Flapper-Girl in einem ihrer beliebtesten Abenteuer. Public Domain Animation mit KI-Upscaling zum Leben erweckt.

🇪🇸 ESPAÑOL: Dibujo animado clásico de Betty Boop de {year}, restaurado en impresionante calidad 8K. La icónica chica flapper en una de sus aventuras más queridas. Animación de dominio público revivida con tecnología de escalado IA.

🇫🇷 FRANÇAIS: Dessin animé classique de Betty Boop de {year}, restauré en qualité 8K époustouflante. L'iconique flapper girl dans l'une de ses aventures les plus appréciées. Animation du domaine public ramenée à la vie avec l'upscaling IA.

🇵🇹 PORTUGUÊS: Desenho clássico da Betty Boop de {year}, restaurado em qualidade 8K deslumbrante. A icônica garota flapper em uma de suas aventuras mais amadas. Animação de domínio público revivida com tecnologia de upscaling IA.

🇮🇹 ITALIANO: Classico cartone di Betty Boop del {year}, restaurato in straordinaria qualità 8K. L'iconica flapper girl in una delle sue avventure più amate. Animazione di pubblico dominio riportata in vita con upscaling IA.

🇳🇱 NEDERLANDS: Klassieke Betty Boop cartoon uit {year}, gerestaureerd in verbluffende 8K kwaliteit. Het iconische flapper meisje in een van haar meest geliefde avonturen. Public domain animatie tot leven gebracht met AI-upscaling.

🇵🇱 POLSKI: Klasyczna kreskówka Betty Boop z {year}, odrestaurowana w oszałamiającej jakości 8K. Kultowa flapper girl w jednej ze swoich najbardziej lubianych przygód. Animacja public domain ożywiona technologią AI upscaling.

🇷🇺 РУССКИЙ: Классический мультфильм Бетти Буп {year} года, восстановленный в потрясающем качестве 8K. Культовая девушка-флэппер в одном из своих самых любимых приключений. Анимация общественного достояния, возрождённая с помощью ИИ-апскейлинга.

🇯🇵 日本語: {year}年のクラシックなベティ・ブープアニメ、驚異の8K画質で復元。象徴的なフラッパーガールの最も愛される冒険の一つ。AIアップスケーリング技術でパブリックドメインアニメーションが蘇る。

🇨🇳 中文: {year}年经典贝蒂娃娃动画，以惊艳的8K画质修复。标志性的时髦女郎最受欢迎的冒险之一。公共领域动画通过AI放大技术重获新生。

🇰🇷 한국어: {year}년 클래식 베티 붑 만화, 놀라운 8K 화질로 복원. 상징적인 플래퍼 소녀의 가장 사랑받는 모험 중 하나. AI 업스케일링 기술로 되살아난 퍼블릭 도메인 애니메이션.

🇹🇷 TÜRKÇE: {year} yılından klasik Betty Boop çizgi filmi, muhteşem 8K kalitesinde restore edildi. İkonik flapper kızın en sevilen maceralarından biri. AI upscaling teknolojisiyle yeniden hayat bulan kamu malı animasyon.

🇸🇦 العربية: رسوم متحركة كلاسيكية لبيتي بوب من عام {year}، تم ترميمها بجودة 8K المذهلة. فتاة الفلابر الأيقونية في واحدة من أكثر مغامراتها المحبوبة. رسوم متحركة من الملكية العامة أُعيد إحياؤها بتقنية الترقية بالذكاء الاصطناعي.

🇮🇳 हिंदी: {year} की क्लासिक बेट्टी बूप कार्टून, शानदार 8K गुणवत्ता में पुनर्स्थापित। प्रतिष्ठित फ्लैपर गर्ल अपने सबसे प्रिय साहसिक कार्यों में से एक में। AI अपस्केलिंग तकनीक से पुनर्जीवित पब्लिक डोमेन एनिमेशन।

🇹🇭 ไทย: การ์ตูน Betty Boop คลาสสิกจากปี {year} ได้รับการบูรณะในคุณภาพ 8K ที่น่าทึ่ง สาวแฟลปเปอร์ในตำนานในการผจญภัยที่รักที่สุดครั้งหนึ่งของเธอ แอนิเมชันสาธารณสมบัติที่ฟื้นคืนชีพด้วยเทคโนโลยี AI upscaling

🇻🇳 TIẾNG VIỆT: Phim hoạt hình Betty Boop cổ điển từ năm {year}, được phục hồi với chất lượng 8K tuyệt đẹp. Cô gái flapper biểu tượng trong một trong những cuộc phiêu lưu được yêu thích nhất. Hoạt hình thuộc phạm vi công cộng được hồi sinh với công nghệ AI upscaling.

🇮🇩 BAHASA INDONESIA: Kartun klasik Betty Boop dari tahun {year}, direstorasi dalam kualitas 8K yang menakjubkan. Gadis flapper ikonik dalam salah satu petualangan paling dicintainya. Animasi domain publik dihidupkan kembali dengan teknologi AI upscaling.

🇸🇪 SVENSKA: Klassisk Betty Boop-tecknad film från {year}, restaurerad i fantastisk 8K-kvalitet. Den ikoniska flapperflickan i ett av hennes mest älskade äventyr. Public domain-animation återupplivad med AI-uppskalning.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 LIKE if you loved this classic!
💬 COMMENT your favorite Betty Boop moment!
🔔 SUBSCRIBE for more vintage animation in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at: https://frai.tv | @remAIke_IT

#BettyBoop #VintageAnimation #8K #PublicDomain #ClassicCartoon #Fleischer #1930s #Animation #remAIke"""

    return desc

def extract_info_from_title(title):
    """Extract episode info and year from title"""
    import re
    
    # Try to find year (1930-1939)
    year_match = re.search(r'\(19[23]\d\)', title)
    year = year_match.group(0).strip('()') if year_match else "1930s"
    
    # Try to find episode number
    ep_match = re.search(r'\((\d+)/105\)', title)
    episode_info = ep_match.group(1) if ep_match else ""
    
    # Extract cartoon name
    name_match = re.search(r'Betty Boop.*?:\s*([^|]+)', title)
    if not name_match:
        name_match = re.search(r'^([^|]+)', title)
    cartoon_name = name_match.group(1).strip() if name_match else title.split('|')[0].strip()
    
    return cartoon_name, year, episode_info

# Process videos
updated = 0
failed = 0
results = []

# LIMIT: Process next batch (skip already done)
SKIP = 50  # Already processed
BATCH_LIMIT = 10
print(f"\n⚠️ Processing videos {SKIP+1} to {SKIP+BATCH_LIMIT} (quota limit)")

for i, video in enumerate(betty_boop_videos[SKIP:SKIP+BATCH_LIMIT]):
    video_id = video['id']
    title = video['title']
    
    print(f"\n[{i+1}/{BATCH_LIMIT}] Processing: {title[:50]}...")
    
    try:
        # Get current video details
        current = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if not current.get('items'):
            print(f"  ❌ Video not found!")
            failed += 1
            continue
        
        snippet = current['items'][0]['snippet']
        current_title = snippet['title']
        
        # Extract info
        cartoon_name, year, episode_info = extract_info_from_title(current_title)
        
        # Create new description
        new_desc = create_multilingual_description(cartoon_name, year, episode_info)
        
        # Update video
        snippet['description'] = new_desc
        
        youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        print(f"  ✅ Updated! Description: {len(new_desc)} chars")
        updated += 1
        results.append({'id': video_id, 'title': current_title, 'status': 'success', 'chars': len(new_desc)})
        
        # Rate limiting
        time.sleep(1)
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1
        results.append({'id': video_id, 'title': title, 'status': 'failed', 'error': str(e)})

print(f"\n" + "="*50)
print(f"✅ Updated: {updated}")
print(f"❌ Failed: {failed}")
print(f"📊 Remaining Betty Boop videos: {len(betty_boop_videos) - BATCH_LIMIT}")
print(f"💡 Quota used: ~{updated * 50} units")

# Save results
with open('config/betty_boop_batch_result.json', 'w', encoding='utf-8') as f:
    json.dump({
        'updated': updated,
        'failed': failed,
        'remaining': len(betty_boop_videos) - BATCH_LIMIT,
        'results': results
    }, f, ensure_ascii=False, indent=2)
