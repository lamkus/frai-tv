"""
set_stream_metadata.py — Set YouTube Livestream title, description, tags via API.
Uses OAuth (WRITE operation) to update the active liveBroadcast.

Usage:
    python scripts/youtube/set_stream_metadata.py
"""
import os, sys, json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CLIENT_SECRET = os.path.join(BASE_DIR, 'config', 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']

# ══════════════════════════════════════════════════════════════════════════════
# STREAM METADATA — nach remAIke.TV SEO-Regeln
# ══════════════════════════════════════════════════════════════════════════════

STREAM_TITLE = (
    "Wochenschau: Deutsche Wochenschau 1939-1945 | "
    "24/7 LIVE | 8K HQ (4K UHD)"
)

STREAM_DESCRIPTION = """⚠️ HISTORISCHES DOKUMENT / HISTORICAL DOCUMENT
Dieses Material dient ausschließlich der historischen Dokumentation und Bildung.
This material serves exclusively for historical documentation and education.
Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.

🎬 24/7 Livestream: Deutsche Wochenschau (1939-1945), AI-remastered in stunning 8K quality.
Originally produced 1939-1945, now restored and upscaled for modern screens. Public Domain.

📺 Chronologische Wiedergabe historischer Wochenschau-Episoden aus dem Zweiten Weltkrieg.
Originalton, historische Kommentare — unverändert als Zeitdokument.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg, Geschichte, Dokumentation
🇬🇧 German Newsreel, World War II, WWII, WW2, history, documentary
🇪🇸 Noticiero alemán, Segunda Guerra Mundial, historia, documental
🇫🇷 Actualités allemandes, Seconde Guerre mondiale, histoire, documentaire
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial, história, documentário
🇷🇺 Немецкая кинохроника, Вторая мировая война, история
🇯🇵 ドイツニュース映画, 第二次世界大戦, 歴史, ドキュメンタリー
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध, इतिहास
🇨🇳 德国新闻片, 二战, 第二次世界大战, 历史纪录片
🇸🇦 النشرة الإخبارية الألمانية, الحرب العالمية الثانية, تاريخ
🇮🇩 Berita Jerman, Perang Dunia II, sejarah, dokumenter
🇻🇳 Tin tức Đức, Thế chiến thứ hai, lịch sử
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı, tarih, belgesel
🇰🇷 독일 뉴스릴, 제2차 세계대전, 역사, 다큐멘터리
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

📜 Source: Public Domain (UFA 1939-1945)
⚠️ Educational & Historical Use Only

#Wochenschau #WWII #History #8K #PublicDomain #DeutscheWochenschau"""

STREAM_TAGS = [
    # Core (Brand + Quality)
    "remAIke", "8K", "8K HQ", "4K UHD", "remastered", "restored", "AI enhanced",
    # Serie DE
    "Wochenschau", "Deutsche Wochenschau",
    # EN
    "German newsreel", "World War II", "WWII", "WW2", "history", "documentary",
    # ES
    "Segunda Guerra Mundial",
    # PT
    "Segunda Guerra Mundial cinejornal",
    # JA
    "第二次世界大戦",
    # HI
    "द्वितीय विश्व युद्ध",
    # ID
    "Perang Dunia II",
    # Core
    "public domain", "historical footage", "vintage newsreel", "live stream",
]

STREAM_CATEGORY = "27"  # Education


def get_youtube_service():
    """Authenticate and return YouTube API service."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)


def find_active_broadcast(youtube):
    """Find the currently active/live broadcast."""
    # Check active broadcasts
    for status in ['active', 'live', 'ready', 'testing']:
        try:
            resp = youtube.liveBroadcasts().list(
                part='id,snippet,status',
                broadcastStatus=status,
                maxResults=5
            ).execute()
            items = resp.get('items', [])
            if items:
                return items[0]
        except Exception as e:
            if 'broadcastStatus' in str(e):
                continue
            print(f"  [WARN] {status}: {e}")
    
    # Fallback: list all upcoming
    try:
        resp = youtube.liveBroadcasts().list(
            part='id,snippet,status',
            broadcastType='all',
            mine=True,
            maxResults=10
        ).execute()
        items = resp.get('items', [])
        for item in items:
            ls = item.get('status', {}).get('lifeCycleStatus', '')
            if ls in ('live', 'ready', 'testing', 'liveStarting'):
                return item
        # Return most recent if nothing is live
        if items:
            return items[0]
    except Exception as e:
        print(f"  [ERROR] listing broadcasts: {e}")
    
    return None


def update_broadcast(youtube, broadcast):
    """Update broadcast title, description, tags."""
    broadcast_id = broadcast['id']
    current = broadcast.get('snippet', {})
    
    print(f"\n  Current title: {current.get('title', '???')}")
    print(f"  Broadcast ID:  {broadcast_id}")
    print(f"  Status:        {broadcast.get('status', {}).get('lifeCycleStatus', '???')}")
    
    # Update snippet
    body = {
        'id': broadcast_id,
        'snippet': {
            'title': STREAM_TITLE,
            'description': STREAM_DESCRIPTION,
            'scheduledStartTime': current.get('scheduledStartTime'),
            'categoryId': STREAM_CATEGORY,
        },
    }
    
    try:
        result = youtube.liveBroadcasts().update(
            part='snippet',
            body=body
        ).execute()
        print(f"\n  ✅ Title updated: {result['snippet']['title']}")
    except Exception as e:
        print(f"\n  ❌ Failed to update broadcast: {e}")
        return False
    
    # Also try to update the associated video's tags
    video_id = broadcast_id  # For live broadcasts, broadcast ID = video ID
    try:
        # Get current video details
        video_resp = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()
        
        if video_resp.get('items'):
            video = video_resp['items'][0]
            video_snippet = video['snippet']
            video_snippet['tags'] = STREAM_TAGS
            video_snippet['categoryId'] = STREAM_CATEGORY
            video_snippet['title'] = STREAM_TITLE
            video_snippet['description'] = STREAM_DESCRIPTION
            
            youtube.videos().update(
                part='snippet',
                body={'id': video_id, 'snippet': video_snippet}
            ).execute()
            print(f"  ✅ Tags set: {len(STREAM_TAGS)} tags")
            print(f"  ✅ Category: Education (27)")
    except Exception as e:
        print(f"  ⚠️ Tags/category update: {e}")
    
    return True


def main():
    print("=" * 60)
    print("  SET LIVESTREAM METADATA")
    print("=" * 60)
    print(f"\n  New title: {STREAM_TITLE}")
    
    youtube = get_youtube_service()
    print("\n  [AUTH] OAuth connected")
    
    broadcast = find_active_broadcast(youtube)
    if not broadcast:
        print("\n  ❌ No active broadcast found!")
        print("  Make sure the stream is running in YouTube Studio.")
        sys.exit(1)
    
    success = update_broadcast(youtube, broadcast)
    
    if success:
        print(f"\n{'=' * 60}")
        print("  STREAM METADATA SET SUCCESSFULLY")
        print(f"{'=' * 60}")
    else:
        print(f"\n  ❌ Failed — check YouTube Studio manually")
        sys.exit(1)


if __name__ == '__main__':
    main()
