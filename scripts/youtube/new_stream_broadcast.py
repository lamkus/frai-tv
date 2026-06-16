"""
new_stream_broadcast.py — Create a FRESH YouTube Live Broadcast with full SEO.

Flow:
  1. End current broadcast (transition → complete)
  2. Create NEW broadcast with multilingual SEO metadata
  3. Find existing stream (RTMP key)
  4. Bind new broadcast to stream
  5. → User starts FFmpeg → broadcast goes live

Usage:
    python scripts/youtube/new_stream_broadcast.py
"""
import os, sys, json
from datetime import datetime, timezone
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CLIENT_SECRET = os.path.join(BASE_DIR, 'config', 'client_secret.json')
SCOPES = ['https://www.googleapis.com/auth/youtube']

# ══════════════════════════════════════════════════════════════════════════════
# STREAM SEO — nach remAIke.TV Workspace Rules + WOCHENSCHAU_MULTILINGUAL_SEO.md
# ══════════════════════════════════════════════════════════════════════════════

STREAM_TITLE = (
    "Wochenschau: Deutsche Wochenschau 1939-1945 | "
    "24/7 LIVE | 8K HQ (4K UHD)"
)

STREAM_DESCRIPTION = """\u26a0\ufe0f HISTORISCHES DOKUMENT / HISTORICAL DOCUMENT
Dieses Material dient ausschlie\u00dflich der historischen Dokumentation und Bildung.
This material serves exclusively for historical documentation and education.
Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.

\U0001f3ac 24/7 Livestream: Deutsche Wochenschau (1939-1945), AI-remastered in stunning 8K quality.
Originally produced 1939-1945, now restored and upscaled for modern screens. Public Domain.

\U0001f4fa Chronologische Wiedergabe historischer Wochenschau-Episoden aus dem Zweiten Weltkrieg.
Originalton, historische Kommentare \u2014 unver\u00e4ndert als Zeitdokument.

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
\U0001f30d SEARCH IN YOUR LANGUAGE:
\U0001f1e9\U0001f1ea Deutsche Wochenschau, Zweiter Weltkrieg, Geschichte, Dokumentation
\U0001f1ec\U0001f1e7 German Newsreel, World War II, WWII, WW2, history, documentary
\U0001f1ea\U0001f1f8 Noticiero alem\u00e1n, Segunda Guerra Mundial, historia, documental
\U0001f1eb\U0001f1f7 Actualit\u00e9s allemandes, Seconde Guerre mondiale, histoire, documentaire
\U0001f1f5\U0001f1f9 Cinejornal alem\u00e3o, Segunda Guerra Mundial, hist\u00f3ria, document\u00e1rio
\U0001f1f7\U0001f1fa \u041d\u0435\u043c\u0435\u0446\u043a\u0430\u044f \u043a\u0438\u043d\u043e\u0445\u0440\u043e\u043d\u0438\u043a\u0430, \u0412\u0442\u043e\u0440\u0430\u044f \u043c\u0438\u0440\u043e\u0432\u0430\u044f \u0432\u043e\u0439\u043d\u0430, \u0438\u0441\u0442\u043e\u0440\u0438\u044f
\U0001f1ef\U0001f1f5 \u30c9\u30a4\u30c4\u30cb\u30e5\u30fc\u30b9\u6620\u753b, \u7b2c\u4e8c\u6b21\u4e16\u754c\u5927\u6226, \u6b74\u53f2, \u30c9\u30ad\u30e5\u30e1\u30f3\u30bf\u30ea\u30fc
\U0001f1ee\U0001f1f3 \u091c\u0930\u094d\u092e\u0928 \u0928\u094d\u092f\u0942\u091c\u093c\u0930\u0940\u0932, \u0926\u094d\u0935\u093f\u0924\u0940\u092f \u0935\u093f\u0936\u094d\u0935 \u092f\u0941\u0926\u094d\u0927, \u0907\u0924\u093f\u0939\u093e\u0938
\U0001f1e8\U0001f1f3 \u5fb7\u56fd\u65b0\u95fb\u7247, \u4e8c\u6218, \u7b2c\u4e8c\u6b21\u4e16\u754c\u5927\u6218, \u5386\u53f2\u7eaa\u5f55\u7247
\U0001f1f8\U0001f1e6 \u0627\u0644\u0646\u0634\u0631\u0629 \u0627\u0644\u0625\u062e\u0628\u0627\u0631\u064a\u0629 \u0627\u0644\u0623\u0644\u0645\u0627\u0646\u064a\u0629, \u0627\u0644\u062d\u0631\u0628 \u0627\u0644\u0639\u0627\u0644\u0645\u064a\u0629 \u0627\u0644\u062b\u0627\u0646\u064a\u0629, \u062a\u0627\u0631\u064a\u062e
\U0001f1ee\U0001f1e9 Berita Jerman, Perang Dunia II, sejarah, dokumenter
\U0001f1fb\U0001f1f3 Tin t\u1ee9c \u0110\u1ee9c, Th\u1ebf chi\u1ebfn th\u1ee9 hai, l\u1ecbch s\u1eed
\U0001f1f9\U0001f1f7 Alman haber filmi, \u0130kinci D\u00fcnya Sava\u015f\u0131, tarih, belgesel
\U0001f1f0\U0001f1f7 \ub3c5\uc77c \ub274\uc2a4\ub9b4, \uc81c2\ucc28 \uc138\uacc4\ub300\uc804, \uc5ed\uc0ac, \ub2e4\ud050\uba58\ud130\ub9ac
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

\U0001f446 LIKE if you found this valuable!
\U0001f4ac COMMENT your thoughts!
\U0001f514 SUBSCRIBE for more historical footage!
\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501
\U0001f310 www.remaike.IT
\U0001f4fa https://www.youtube.com/@remAIke_IT

\U0001f4dc Source: Public Domain (UFA 1939-1945)
\u26a0\ufe0f Educational & Historical Use Only

#Wochenschau #WWII #History #8K #PublicDomain #DeutscheWochenschau"""

STREAM_TAGS = [
    # Core (Brand + Quality)
    "remAIke", "8K", "8K HQ", "4K UHD", "remastered", "restored", "AI enhanced",
    # Serie DE
    "Wochenschau", "Deutsche Wochenschau",
    # EN
    "German newsreel", "World War II", "WWII", "WW2", "history", "documentary",
    # ES + PT
    "Segunda Guerra Mundial",
    # JA
    "\u7b2c\u4e8c\u6b21\u4e16\u754c\u5927\u6226",
    # HI
    "\u0926\u094d\u0935\u093f\u0924\u0940\u092f \u0935\u093f\u0936\u094d\u0935 \u092f\u0941\u0926\u094d\u0927",
    # ID
    "Perang Dunia II",
    # Core
    "public domain", "historical footage", "vintage newsreel", "live stream",
]

STREAM_CATEGORY = "27"  # Education


def get_youtube_service():
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


def end_current_broadcasts(youtube):
    """End ALL active/ready broadcasts to clean up."""
    ended = 0
    for status in ['active', 'live']:
        try:
            resp = youtube.liveBroadcasts().list(
                part='id,snippet,status',
                broadcastStatus=status,
                maxResults=10
            ).execute()
            for item in resp.get('items', []):
                bid = item['id']
                title = item['snippet']['title']
                lcs = item['status']['lifeCycleStatus']
                print(f"  [END] Ending broadcast {bid}: '{title}' (status: {lcs})")
                try:
                    youtube.liveBroadcasts().transition(
                        broadcastStatus='complete',
                        id=bid,
                        part='id,status'
                    ).execute()
                    ended += 1
                    print(f"  [END] \u2705 Broadcast {bid} ended")
                except Exception as e:
                    print(f"  [END] \u26a0\ufe0f Could not end {bid}: {e}")
        except Exception as e:
            pass

    # Also end 'ready' broadcasts
    try:
        resp = youtube.liveBroadcasts().list(
            part='id,snippet,status',
            broadcastType='all',
            mine=True,
            maxResults=20
        ).execute()
        for item in resp.get('items', []):
            lcs = item['status']['lifeCycleStatus']
            if lcs in ('ready', 'testing', 'liveStarting'):
                bid = item['id']
                title = item['snippet']['title']
                print(f"  [END] Ending ready broadcast {bid}: '{title}'")
                try:
                    youtube.liveBroadcasts().transition(
                        broadcastStatus='complete',
                        id=bid,
                        part='id,status'
                    ).execute()
                    ended += 1
                except Exception:
                    # Can't transition 'ready' directly to 'complete' — just leave it
                    pass
    except Exception:
        pass

    return ended


def find_stream(youtube):
    """Find the existing liveStream (RTMP ingestion point) for our channel."""
    resp = youtube.liveStreams().list(
        part='id,snippet,cdn,status',
        mine=True,
        maxResults=10
    ).execute()
    streams = resp.get('items', [])
    if not streams:
        print("  [ERROR] No liveStream found!")
        return None

    for s in streams:
        sid = s['id']
        title = s['snippet'].get('title', '???')
        key = s['cdn']['ingestionInfo']['streamName']
        status = s['status']['streamStatus']
        print(f"  [STREAM] ID={sid}  title='{title}'  status={status}  key=****{key[-4:]}")
    
    # Return first stream (usually the default one)
    return streams[0]


def create_broadcast(youtube):
    """Create a NEW liveBroadcast with full multilingual SEO."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    body = {
        'snippet': {
            'title': STREAM_TITLE,
            'description': STREAM_DESCRIPTION,
            'scheduledStartTime': now,
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        },
        'contentDetails': {
            'enableAutoStart': True,    # Auto-start when FFmpeg connects!
            'enableAutoStop': False,    # NEVER auto-stop!
            'enableDvr': True,
            'enableEmbed': True,
            'recordFromStart': True,
            'monitorStream': {
                'enableMonitorStream': False,
            },
        },
    }
    
    result = youtube.liveBroadcasts().insert(
        part='snippet,status,contentDetails',
        body=body
    ).execute()
    
    broadcast_id = result['id']
    print(f"\n  \u2705 NEW BROADCAST CREATED!")
    print(f"  ID:     {broadcast_id}")
    print(f"  Title:  {result['snippet']['title']}")
    print(f"  Status: {result['status']['lifeCycleStatus']}")
    print(f"  Auto-Start: ON  (stream goes live when FFmpeg connects)")
    print(f"  Auto-Stop:  OFF (stays alive even if FFmpeg disconnects briefly)")
    
    # Set tags + category via videos.update (broadcast ID = video ID)
    try:
        video_resp = youtube.videos().list(
            part='snippet',
            id=broadcast_id
        ).execute()
        
        if video_resp.get('items'):
            video_snippet = video_resp['items'][0]['snippet']
            video_snippet['tags'] = STREAM_TAGS
            video_snippet['categoryId'] = STREAM_CATEGORY
            
            youtube.videos().update(
                part='snippet',
                body={'id': broadcast_id, 'snippet': video_snippet}
            ).execute()
            print(f"  \u2705 Tags set: {len(STREAM_TAGS)} multilingual tags")
            print(f"  \u2705 Category: Education (27)")
    except Exception as e:
        print(f"  \u26a0\ufe0f Tags/category: {e}")
    
    return result


def bind_broadcast_to_stream(youtube, broadcast_id, stream_id):
    """Bind the new broadcast to the existing RTMP stream."""
    result = youtube.liveBroadcasts().bind(
        id=broadcast_id,
        part='id,snippet,contentDetails,status',
        streamId=stream_id
    ).execute()
    
    print(f"\n  \u2705 BOUND broadcast {broadcast_id} to stream {stream_id}")
    print(f"  Status: {result['status']['lifeCycleStatus']}")
    return result


def main():
    print("=" * 60)
    print("  CREATE NEW LIVESTREAM BROADCAST")
    print("  Full Multilingual SEO from the START")
    print("=" * 60)
    
    youtube = get_youtube_service()
    print("\n  [AUTH] OAuth connected")
    
    # Step 1: Find existing stream (RTMP key)
    print("\n--- STEP 1: Find RTMP stream ---")
    stream = find_stream(youtube)
    if not stream:
        print("  FATAL: No stream found. Create one in YouTube Studio first.")
        sys.exit(1)
    stream_id = stream['id']
    
    # Step 2: End current broadcasts
    print("\n--- STEP 2: End old broadcasts ---")
    ended = end_current_broadcasts(youtube)
    print(f"  Ended {ended} broadcast(s)")
    
    # Step 3: Create new broadcast with full SEO
    print("\n--- STEP 3: Create NEW broadcast ---")
    broadcast = create_broadcast(youtube)
    broadcast_id = broadcast['id']
    
    # Step 4: Bind to RTMP stream
    print(f"\n--- STEP 4: Bind to stream {stream_id} ---")
    bind_broadcast_to_stream(youtube, broadcast_id, stream_id)
    
    # Step 5: Summary
    print(f"\n{'=' * 60}")
    print(f"  NEW BROADCAST READY!")
    print(f"  Broadcast ID: {broadcast_id}")
    print(f"  Title: {STREAM_TITLE}")
    print(f"  Tags: {len(STREAM_TAGS)} multilingual")
    print(f"  Auto-Start: ON")
    print(f"  Auto-Stop: OFF")
    print(f"")
    print(f"  \u27a1\ufe0f  Start FFmpeg now → broadcast goes LIVE automatically!")
    print(f"  \u27a1\ufe0f  python stream_4k.py")
    print(f"{'=' * 60}")
    
    # Save broadcast ID for reference
    info = {
        'broadcast_id': broadcast_id,
        'stream_id': stream_id,
        'title': STREAM_TITLE,
        'created': datetime.now(timezone.utc).isoformat(),
    }
    info_file = os.path.join(BASE_DIR, 'config', 'current_broadcast.json')
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    print(f"\n  Saved to {info_file}")


if __name__ == '__main__':
    main()
