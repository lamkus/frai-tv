#!/usr/bin/env python3
"""Frischer YouTube Channel Scan via OAuth - holt ALLE Videos inkl. Drafts."""
import json, sys, io
from pathlib import Path
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth laden
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth.get('access_token') or oauth.get('token'),
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

print(f"🔄 Scanne Channel {CHANNEL_ID}...")
print(f"⏰ {datetime.now().isoformat()}\n")

# 1. Channel Info
ch = youtube.channels().list(part='snippet,contentDetails,statistics', id=CHANNEL_ID).execute()
channel = ch['items'][0]
uploads_id = channel['contentDetails']['relatedPlaylists']['uploads']
print(f"📺 {channel['snippet']['title']}")
print(f"📊 {channel['statistics']['videoCount']} Videos total")
print(f"📁 Uploads Playlist: {uploads_id}\n")

# 2. Alle Videos aus Uploads holen
all_videos = []
next_page = None
while True:
    req = youtube.playlistItems().list(
        part='snippet,contentDetails,status',
        playlistId=uploads_id,
        maxResults=50,
        pageToken=next_page
    )
    resp = req.execute()
    all_videos.extend(resp['items'])
    next_page = resp.get('nextPageToken')
    print(f"  Geladen: {len(all_videos)} items...")
    if not next_page:
        break

print(f"\n✅ {len(all_videos)} Upload-Items gefunden")

# 3. Video-Details holen (für Description, Status etc.)
video_ids = [v['contentDetails']['videoId'] for v in all_videos]
detailed_videos = []

for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    vresp = youtube.videos().list(
        part='snippet,contentDetails,statistics,status',
        id=','.join(batch)
    ).execute()
    detailed_videos.extend(vresp.get('items', []))
    print(f"  Details: {len(detailed_videos)} videos...")

# 4. Nach Status kategorisieren
public_videos = []
private_videos = []
unlisted_videos = []

for v in detailed_videos:
    status = v.get('status', {}).get('privacyStatus', 'unknown')
    if status == 'public':
        public_videos.append(v)
    elif status == 'private':
        private_videos.append(v)
    elif status == 'unlisted':
        unlisted_videos.append(v)

print(f"\n📊 Status:")
print(f"  ✅ Public:   {len(public_videos)}")
print(f"  🔒 Private:  {len(private_videos)} (Drafts)")
print(f"  🔗 Unlisted: {len(unlisted_videos)}")

# 5. Speichern
result = {
    'fetched_at': datetime.now().isoformat(),
    'channel_id': CHANNEL_ID,
    'channel_name': channel['snippet']['title'],
    'total_videos': len(detailed_videos),
    'public': len(public_videos),
    'private': len(private_videos),
    'unlisted': len(unlisted_videos),
    'videos': detailed_videos,
    'public_videos': public_videos,
    'private_videos': private_videos,
    'unlisted_videos': unlisted_videos
}

out = Path('config/fresh_channel_scan.json')
out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n💾 Gespeichert: {out}")

# 6. Wochenschau-Videos finden
print("\n" + "="*60)
print("🎬 WOCHENSCHAU-VIDEOS:")
print("="*60)

wochenschau_pattern = ['wochenschau', 'newsreel', 'ufa-ton', 'deutsche woche']
wochenschau_videos = []

for v in detailed_videos:
    title = v['snippet']['title'].lower()
    desc = v['snippet'].get('description', '').lower()[:500]
    
    for pat in wochenschau_pattern:
        if pat in title or pat in desc:
            wochenschau_videos.append({
                'id': v['id'],
                'title': v['snippet']['title'],
                'description': v['snippet'].get('description', ''),
                'status': v['status']['privacyStatus'],
                'views': int(v.get('statistics', {}).get('viewCount', 0)),
                'published': v['snippet'].get('publishedAt', '')
            })
            status_icon = '✅' if v['status']['privacyStatus'] == 'public' else '🔒'
            print(f"  {status_icon} {v['snippet']['title'][:70]}")
            break

print(f"\n📊 Gefunden: {len(wochenschau_videos)} Wochenschau-Videos")
print(f"  ✅ Public: {len([v for v in wochenschau_videos if v['status']=='public'])}")
print(f"  🔒 Drafts: {len([v for v in wochenschau_videos if v['status']=='private'])}")

# Wochenschau separat speichern
ws_out = Path('config/wochenschau_videos.json')
ws_out.write_text(json.dumps(wochenschau_videos, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\n💾 Wochenschau: {ws_out}")
