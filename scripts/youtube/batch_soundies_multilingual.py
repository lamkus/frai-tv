"""
Batch update Soundie videos with 18-language multilingual descriptions
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

soundie_videos = data['categories'].get('Soundie', [])
print(f"Found {len(soundie_videos)} Soundie videos to update")

def create_soundie_description(title):
    """Create 18-language description for Soundies - COMPACT VERSION"""
    
    # Extract song name from title
    import re
    song_match = re.search(r'Soundie:\s*([^|]+)', title)
    song_name = song_match.group(1).strip() if song_match else title.split('|')[0].strip()
    
    desc = f"""🎵 {song_name} | Soundie | 1940s Music | 8K

🇺🇸 Rare 1940s Soundie restored in 8K. Soundies were music films for Panoram jukeboxes.
🇩🇪 Seltener 1940er Soundie in 8K restauriert. Musikfilme für Panoram-Jukeboxen.
🇪🇸 Raro Soundie de los 40 restaurado en 8K. Películas musicales para Panoram.
🇫🇷 Soundie rare des années 40 restauré en 8K. Films musicaux pour juke-box Panoram.
🇵🇹 Raro Soundie dos anos 40 restaurado em 8K. Filmes musicais para jukeboxes Panoram.
🇮🇹 Raro Soundie anni '40 restaurato in 8K. Film musicali per jukebox Panoram.
🇳🇱 Zeldzame 1940s Soundie gerestaureerd in 8K. Muziekfilms voor Panoram jukeboxen.
🇵🇱 Rzadki Soundie z lat 40. odrestaurowany w 8K. Filmy muzyczne dla automatów Panoram.
🇷🇺 Редкий Soundie 1940-х восстановлен в 8K. Музыкальные фильмы для автоматов Panoram.
🇯🇵 1940年代の貴重なサウンディを8Kで復元。パノラムジュークボックス用音楽映画。
🇨🇳 珍贵1940年代Soundie以8K修复。Panoram点唱机音乐电影。
🇰🇷 희귀한 1940년대 사운디 8K 복원. 파노람 주크박스용 뮤직필름.
🇹🇷 1940'lardan nadir Soundie 8K'da restore edildi. Panoram müzik kutuları için.
🇸🇦 فيلم Soundie نادر من الأربعينيات بجودة 8K. أفلام موسيقية لآلات Panoram.
🇮🇳 दुर्लभ 1940 के दशक का Soundie 8K में। Panoram ज्यूकबॉक्स के लिए संगीत फिल्में।
🇹🇭 Soundie หายากจาก 1940s ใน 8K สำหรับตู้เพลง Panoram
🇻🇳 Soundie hiếm từ 1940s phục hồi 8K. Phim nhạc cho máy Panoram.
🇮🇩 Soundie langka 1940-an direstorasi 8K. Film musik untuk jukebox Panoram.
🇸🇪 Sällsynt 1940-tals Soundie restaurerad i 8K. Musikfilmer för Panoram-jukeboxar.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 LIKE if you love vintage music!
💬 COMMENT your favorite jazz & swing!
🔔 SUBSCRIBE for more 1940s Soundies!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 https://frai.tv | @remAIke_IT

#Soundie #VintageMusic #1940s #Jazz #Swing #8K #remAIke"""

    return desc

# Process videos
updated = 0
failed = 0
results = []

SKIP = 30
BATCH_LIMIT = 15
print(f"\n⚠️ Processing videos {SKIP+1} to {SKIP+BATCH_LIMIT}")

for i, video in enumerate(soundie_videos[SKIP:SKIP+BATCH_LIMIT]):
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
        
        # Create new description
        new_desc = create_soundie_description(current_title)
        
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
        
        time.sleep(1)
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        failed += 1
        results.append({'id': video_id, 'title': title, 'status': 'failed', 'error': str(e)})

print(f"\n" + "="*50)
print(f"✅ Updated: {updated}")
print(f"❌ Failed: {failed}")
print(f"📊 Remaining Soundie videos: {len(soundie_videos) - SKIP - BATCH_LIMIT}")
print(f"💡 Quota used: ~{updated * 50} units")
