"""Quick sample check of video metadata for SEO diagnosis."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
yt = build('youtube', 'v3', credentials=creds)

# Get latest 10 videos
pl = yt.playlistItems().list(
    part='contentDetails', 
    playlistId='UUVFv6Egpl0LDvigpFbQXNeQ', 
    maxResults=10
).execute()
sample_ids = [i['contentDetails']['videoId'] for i in pl.get('items', [])]

data = yt.videos().list(
    part='snippet,statistics,contentDetails,status,topicDetails',
    id=','.join(sample_ids)
).execute()

for v in data.get('items', []):
    s = v['snippet']
    st = v.get('statistics', {})
    status = v.get('status', {})
    topics = v.get('topicDetails', {})
    
    print('=' * 70)
    print(f'ID:         {v["id"]}')
    print(f'TITLE:      {s["title"]}')
    print(f'VIEWS:      {st.get("viewCount",0)} | Likes: {st.get("likeCount",0)}')
    print(f'CATEGORY:   {s.get("categoryId")}')
    print(f'PUBLISHED:  {s["publishedAt"]}')
    print(f'EMBEDDABLE: {status.get("embeddable")}')
    print(f'LICENSE:    {status.get("license")}')
    print(f'MFKids:     {status.get("madeForKids")}')
    print(f'SELF_DECL:  {status.get("selfDeclaredMadeForKids")}')
    
    tags = s.get('tags', [])
    print(f'TAGS ({len(tags)}):  {tags[:8]}{"..." if len(tags)>8 else ""}')
    print(f'TOPICS:     {topics.get("topicCategories",[])}')
    
    desc = s.get('description', '')
    lines = desc.split('\n')
    print(f'DESC LINE1: {lines[0][:120]}')
    if len(lines) > 1:
        print(f'DESC LINE2: {lines[1][:120]}')
    print(f'DESC LEN:   {len(desc)} chars')
    
    # Check for critical SEO elements
    issues = []
    if '@remAIke_IT' in s['title']:
        issues.append('@channel in title')
    if '8K HQ' not in s['title'] and '8K' not in s['title']:
        issues.append('no 8K in title')
    if lines[0].strip() == s['title'].strip():
        issues.append('DESC LINE1 = TITLE (wasted!)')
    if not status.get('embeddable'):
        issues.append('NOT EMBEDDABLE!')
    if status.get('madeForKids'):
        issues.append('MADE_FOR_KIDS = TRUE!')
    if '0:00' not in desc:
        issues.append('no chapters')
    
    hashtags = [w for w in desc.split() if w.startswith('#')]
    if len(hashtags) > 5:
        issues.append(f'too many hashtags ({len(hashtags)})')
    
    if issues:
        print(f'** ISSUES: {issues}')
    print()
