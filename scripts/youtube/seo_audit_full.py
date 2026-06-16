#!/usr/bin/env python3
"""Full channel SEO audit - find videos needing optimization"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

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

    # Get uploads playlist
    channel = youtube.channels().list(part='contentDetails', mine=True).execute()
    uploads_id = channel['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Get ALL video IDs
    all_ids = []
    next_page = None
    while True:
        pl = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        ).execute()
        all_ids.extend([i['contentDetails']['videoId'] for i in pl['items']])
        next_page = pl.get('nextPageToken')
        if not next_page:
            break

    print(f'Total videos: {len(all_ids)}')

    # Analyze each video
    needs_work = []
    all_videos = []
    
    for i in range(0, len(all_ids), 50):
        batch = all_ids[i:i+50]
        vids = youtube.videos().list(
            part='snippet,status,statistics',
            id=','.join(batch)
        ).execute()
        
        for v in vids['items']:
            if v['status']['privacyStatus'] != 'public':
                continue
                
            snip = v['snippet']
            stats = v.get('statistics', {})
            
            issues = []
            score = 100
            
            # Check tags
            tags = snip.get('tags', [])
            if len(tags) == 0:
                issues.append('NO TAGS!')
                score -= 30
            elif len(tags) < 5:
                issues.append(f'Few tags ({len(tags)})')
                score -= 15
            
            # Check description
            desc = snip.get('description', '')
            if len(desc) < 100:
                issues.append('Short desc')
                score -= 20
            
            # Check CTAs
            if 'LIKE' not in desc.upper() and 'SUBSCRIBE' not in desc.upper():
                issues.append('No CTA')
                score -= 10
            
            # Check branding
            if '@remAIke' not in snip['title'] and '@remAIke' not in desc:
                issues.append('No branding')
                score -= 5
            
            # Check category (25 = News, should be 1 for most)
            cat = snip['categoryId']
            title_lower = snip['title'].lower()
            if cat == '25' and not any(x in title_lower for x in ['wochenschau', 'newsreel', 'news']):
                issues.append(f'Wrong cat ({cat})')
                score -= 10
            
            video_data = {
                'id': v['id'],
                'title': snip['title'],
                'views': int(stats.get('viewCount', 0)),
                'tags': len(tags),
                'desc_len': len(desc),
                'cat': cat,
                'issues': issues,
                'score': score
            }
            
            all_videos.append(video_data)
            if issues:
                needs_work.append(video_data)

    # Sort by score (worst first)
    needs_work.sort(key=lambda x: x['score'])

    print(f'\n{"="*100}')
    print(f'Videos needing optimization: {len(needs_work)} / {len(all_videos)} public')
    print(f'{"="*100}')
    print(f'{"Score":>5} {"Views":>7} {"Tags":>4} {"Desc":>5} {"Cat":>3}  {"Issues":<35} Title')
    print('-'*100)

    for v in needs_work[:40]:
        issues_str = ', '.join(v['issues'])[:35]
        title_short = v['title'][:38]
        print(f"{v['score']:>5} {v['views']:>7} {v['tags']:>4} {v['desc_len']:>5} {v['cat']:>3}  {issues_str:<35} {title_short}")

    # Save for batch processing
    with open('config/seo_audit_needs_work.json', 'w', encoding='utf-8') as f:
        json.dump(needs_work, f, indent=2, ensure_ascii=False)
    
    print(f'\n✅ Full list saved to config/seo_audit_needs_work.json')
    
    # Priority breakdown
    print(f'\n{"="*60}')
    print('PRIORITY BREAKDOWN')
    print(f'{"="*60}')
    
    no_tags = [v for v in needs_work if 'NO TAGS!' in v['issues']]
    no_cta = [v for v in needs_work if 'No CTA' in v['issues']]
    wrong_cat = [v for v in needs_work if any('Wrong cat' in i for i in v['issues'])]
    
    print(f'🔴 NO TAGS (critical):     {len(no_tags)}')
    print(f'🟡 No CTA:                 {len(no_cta)}')
    print(f'🟠 Wrong category:         {len(wrong_cat)}')

if __name__ == '__main__':
    main()
