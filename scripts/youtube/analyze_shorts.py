#!/usr/bin/env python3
"""Find and analyze all YouTube Shorts on the channel"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def parse_duration(dur):
    """Parse ISO 8601 duration to seconds"""
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', dur)
    if m:
        h, mins, s = m.groups()
        return int(h or 0)*3600 + int(mins or 0)*60 + int(s or 0)
    return 0

def main():
    with open('config/youtube_oauth.json') as f:
        oauth = json.load(f)

    creds = Credentials(
        token=oauth['token'],
        refresh_token=oauth['refresh_token'],
        token_uri=oauth['token_uri'],
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret']
    )

    youtube = build('youtube', 'v3', credentials=creds)

    # Get channel uploads playlist
    channel = youtube.channels().list(part='contentDetails', mine=True).execute()
    uploads_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get ALL videos
    all_videos = []
    next_page = None
    while True:
        pl = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        all_videos.extend([i['contentDetails']['videoId'] for i in pl['items']])
        next_page = pl.get('nextPageToken')
        if not next_page:
            break

    print(f'Total videos on channel: {len(all_videos)}')

    # Check each batch for shorts (duration <= 180s for new shorts, but focus on <= 60s traditional)
    shorts = []
    for i in range(0, len(all_videos), 50):
        batch = all_videos[i:i+50]
        vids = youtube.videos().list(
            part='snippet,contentDetails,statistics,status',
            id=','.join(batch)
        ).execute()
        
        for item in vids['items']:
            dur = item['contentDetails']['duration']
            total_sec = parse_duration(dur)
            
            # Shorts are typically <= 60s, but can be up to 3 min now
            if total_sec <= 60:
                shorts.append({
                    'id': item['id'],
                    'title': item['snippet']['title'],
                    'duration': total_sec,
                    'status': item['status']['privacyStatus'],
                    'views': int(item['statistics'].get('viewCount', 0)),
                    'likes': int(item['statistics'].get('likeCount', 0)),
                    'category': item['snippet']['categoryId'],
                    'description': item['snippet'].get('description', ''),
                    'tags': item['snippet'].get('tags', [])
                })

    print(f'\n{"="*80}')
    print(f'Found {len(shorts)} Shorts (<= 60s)')
    print(f'{"="*80}\n')
    
    # Sort by views descending
    shorts_sorted = sorted(shorts, key=lambda x: -x['views'])
    
    print(f'{"ID":<13} {"Views":>7} {"Likes":>5} {"Dur":>4} {"Cat":>3} {"Desc":>5} {"Tags":>4}  Title')
    print('-'*100)
    
    for s in shorts_sorted:
        title_short = s['title'][:45] + '...' if len(s['title']) > 45 else s['title']
        desc_len = len(s['description'])
        tags_count = len(s['tags'])
        print(f"{s['id']:<13} {s['views']:>7} {s['likes']:>5} {s['duration']:>3}s {s['category']:>3} {desc_len:>5} {tags_count:>4}  {title_short}")
    
    # Save detailed data
    with open('config/shorts_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(shorts_sorted, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Detailed data saved to config/shorts_analysis.json')
    
    # Quick SEO score
    print(f'\n{"="*80}')
    print('QUICK SEO CHECK')
    print(f'{"="*80}')
    
    needs_work = []
    for s in shorts_sorted:
        issues = []
        if len(s['description']) < 100:
            issues.append('Short desc')
        if len(s['tags']) < 5:
            issues.append('Few tags')
        if '@remAIke_IT' not in s['title']:
            issues.append('No branding')
        if 'LIKE' not in s['description'].upper() and 'SUBSCRIBE' not in s['description'].upper():
            issues.append('No CTA')
        if s['category'] == '25':
            issues.append('Wrong category')
        
        if issues:
            needs_work.append({**s, 'issues': issues})
    
    print(f'\n⚠️ {len(needs_work)} Shorts need optimization:\n')
    for s in needs_work[:20]:
        print(f"[{s['id']}] {s['title'][:50]}")
        print(f"   Issues: {', '.join(s['issues'])}")
        print()

if __name__ == '__main__':
    main()
