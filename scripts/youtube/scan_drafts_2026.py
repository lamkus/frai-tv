"""Scan channel for all draft/private videos needing SEO naming."""
import json, os, sys

# Use google auth to refresh token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
TOKEN = os.path.abspath(TOKEN)

creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN, 'w') as f:
        f.write(creds.to_json())
    print('Token refreshed OK')

yt = build('youtube', 'v3', credentials=creds)

# Get upload playlist
ch = yt.channels().list(part='contentDetails', mine=True).execute()
upload_pl = ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']
print(f'Upload playlist: {upload_pl}')

# Scan ALL videos (public + private/draft)
all_videos = []
token = None
while True:
    req = yt.playlistItems().list(
        part='contentDetails,status,snippet',
        playlistId=upload_pl, maxResults=50, pageToken=token
    )
    resp = req.execute()
    for item in resp['items']:
        vid = {
            'id': item['contentDetails']['videoId'],
            'title': item['snippet']['title'],
            'privacy': item['status']['privacyStatus'],
            'published': item['snippet'].get('publishedAt', ''),
        }
        all_videos.append(vid)
    token = resp.get('nextPageToken')
    if not token:
        break

print(f'Total videos: {len(all_videos)}')

# Now get detailed info for private/unlisted videos
private = [v for v in all_videos if v['privacy'] in ('private', 'unlisted')]
public = [v for v in all_videos if v['privacy'] == 'public']
print(f'Public: {len(public)} | Private/Unlisted: {len(private)}')

# Get full details for private videos (batch of 50)
detailed_private = []
for i in range(0, len(private), 50):
    batch_ids = ','.join(v['id'] for v in private[i:i+50])
    resp = yt.videos().list(
        part='snippet,status,contentDetails',
        id=batch_ids
    ).execute()
    for item in resp.get('items', []):
        detailed_private.append({
            'id': item['id'],
            'title': item['snippet']['title'],
            'description': item['snippet'].get('description', ''),
            'tags': item['snippet'].get('tags', []),
            'categoryId': item['snippet'].get('categoryId', ''),
            'privacy': item['status']['privacyStatus'],
            'duration': item['contentDetails'].get('duration', ''),
            'publishedAt': item['snippet'].get('publishedAt', ''),
        })

print(f'\n{"="*60}')
print(f'PRIVATE/DRAFT VIDEOS ({len(detailed_private)})')
print(f'{"="*60}')
for v in detailed_private:
    print(f'\n  ID: {v["id"]}')
    print(f'  Title: {v["title"]}')
    print(f'  Category: {v["categoryId"]}')
    print(f'  Duration: {v["duration"]}')
    print(f'  Tags: {v["tags"][:5]}...' if len(v["tags"]) > 5 else f'  Tags: {v["tags"]}')
    desc_preview = v["description"][:150].replace('\n', ' | ')
    print(f'  Desc: {desc_preview}...' if len(v["description"]) > 150 else f'  Desc: {desc_preview}')
    
    # Identify content type from filename/title
    title_lower = v['title'].lower()
    issues = []
    if 'sls' in title_lower or 'xvid' in title_lower or 'aac' in title_lower:
        issues.append('RAW_FILENAME (needs proper title)')
    if '_' in v['title'] and not v['title'].startswith('WochenschauTV'):
        issues.append('UNDERSCORE_TITLE (needs cleanup)')
    if not any(kw in title_lower for kw in ['8k', '4k', 'hq']):
        issues.append('NO_QUALITY_TAG')
    if len(v['tags']) == 0:
        issues.append('NO_TAGS')
    if len(v['description']) < 100:
        issues.append('SHORT_DESC')
    if issues:
        print(f'  ISSUES: {", ".join(issues)}')

# Save
out_path = os.path.join(os.path.dirname(TOKEN), 'config', 'draft_scan_2026_02_23.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump({
        'scan_date': '2026-02-23',
        'total': len(all_videos),
        'public': len(public),
        'private': len(private),
        'detailed_private': detailed_private,
        'all_videos_summary': [{'id': v['id'], 'title': v['title'], 'privacy': v['privacy']} for v in all_videos]
    }, f, indent=2, ensure_ascii=False)

print(f'\nSaved to {out_path}')
