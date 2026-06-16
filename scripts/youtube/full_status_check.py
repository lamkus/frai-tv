"""Full channel status check - OAuth only (no Public API key available)"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file(r'D:\remaike.TV\token.json')
yt = build('youtube', 'v3', credentials=creds)

# === Channel stats (1 unit) ===
ch_resp = yt.channels().list(part='statistics,snippet', mine=True).execute()
ch = ch_resp['items'][0]
stats = ch['statistics']
name = ch['snippet']['title']
print(f'=== CHANNEL: {name} ===')
print(f'Subscribers: {stats["subscriberCount"]}')
print(f'Total Views: {stats["viewCount"]}')
print(f'Total Videos: {stats["videoCount"]}')

# === Last 15 uploads (1 unit) ===
UPLOAD_PL = 'UUVFv6Egpl0LDvigpFbQXNeQ'
print(f'\n=== LAST 15 UPLOADS ===')
pl_resp = yt.playlistItems().list(
    part='contentDetails,snippet', playlistId=UPLOAD_PL, maxResults=15
).execute()
vids = []
for item in pl_resp.get('items', []):
    vid_id = item['contentDetails']['videoId']
    title = item['snippet']['title']
    pub = item['snippet'].get('publishedAt', '?')[:10]
    vids.append((vid_id, title, pub))

if vids:
    vid_ids = [v[0] for v in vids]
    detail = yt.videos().list(
        part='statistics,status', id=','.join(vid_ids)
    ).execute()
    stat_map = {v['id']: v for v in detail.get('items', [])}
    
    for vid_id, title, pub in vids:
        info = stat_map.get(vid_id, {})
        st = info.get('statistics', {})
        status = info.get('status', {})
        views = st.get('viewCount', '?')
        privacy = status.get('privacyStatus', '?')
        upload_status = status.get('uploadStatus', '?')
        print(f'  {pub} | {privacy:8s} | {upload_status:10s} | {views:>6s} views | {title[:60]}')

# === ALL private/unlisted/draft videos (100 units - search.list) ===
print(f'\n=== PRIVATE/DRAFT/UNLISTED VIDEOS ===')
resp = yt.search().list(
    part='id,snippet',
    forMine=True,
    type='video',
    maxResults=50,
    order='date'
).execute()

total = resp.get('pageInfo', {}).get('totalResults', '?')
print(f'Total videos found via search: {total}')
vid_ids_oauth = [item['id']['videoId'] for item in resp.get('items', []) if item['id'].get('videoId')]

if vid_ids_oauth:
    detail = yt.videos().list(
        part='status,snippet',
        id=','.join(vid_ids_oauth)
    ).execute()
    
    private_count = 0
    draft_count = 0
    unlisted_count = 0
    public_count = 0
    for v in detail.get('items', []):
        privacy = v['status']['privacyStatus']
        upload_status = v['status'].get('uploadStatus', '?')
        title = v['snippet']['title']
        pub = v['snippet'].get('publishedAt', '?')[:10]
        
        if privacy == 'public':
            public_count += 1
        elif privacy == 'private':
            private_count += 1
            print(f'  PRIVATE  | {upload_status:10s} | {pub} | {title[:60]}')
        elif privacy == 'unlisted':
            unlisted_count += 1
            print(f'  UNLISTED | {upload_status:10s} | {pub} | {title[:60]}')
        
        if upload_status != 'processed':
            draft_count += 1
            print(f'  !! NOT PROCESSED | {upload_status:10s} | {pub} | {title[:60]}')
    
    print(f'\nOf {len(vid_ids_oauth)} recent videos: {public_count} public, {private_count} private, {unlisted_count} unlisted, {draft_count} not-processed')
