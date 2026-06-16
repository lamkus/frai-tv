#!/usr/bin/env python3
"""Check Popeye + Drafts Status"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json') as f:
    oauth = json.load(f)

creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri=oauth['token_uri'],
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret'],
)
youtube = build('youtube', 'v3', credentials=creds)

# 1. POPEYE VIDEO PRÜFEN
print("=" * 70)
print("🍿 POPEYE MARATHON STATUS")
print("=" * 70)
vid = '3gzbxznJ_PM'
result = youtube.videos().list(part='snippet,statistics,contentDetails', id=vid).execute()
if result['items']:
    v = result['items'][0]
    sn = v['snippet']
    stats = v.get('statistics', {})
    
    print(f"TITLE: {sn['title']}")
    print(f"LENGTH: {len(sn['title'])} chars")
    print()
    
    # Check Title Quality
    title_issues = []
    if '8K HQ' not in sn['title']:
        title_issues.append("❌ Kein '8K HQ'")
    if '@remAIke_IT' not in sn['title']:
        title_issues.append("❌ Kein Branding")
    if not title_issues:
        print("✅ TITLE: PERFEKT!")
    else:
        print("TITLE ISSUES:", title_issues)
    print()
    
    print("DESCRIPTION (erste 1500 chars):")
    print("-" * 50)
    print(sn['description'][:1500])
    print("-" * 50)
    print()
    
    # Check Description Quality
    desc = sn['description']
    desc_issues = []
    if 'SUBSCRIBE' not in desc.upper() and 'ABONNIER' not in desc.upper():
        desc_issues.append("❌ Kein SUBSCRIBE CTA")
    if 'LIKE' not in desc.upper():
        desc_issues.append("❌ Kein LIKE CTA")
    if '0:00' not in desc:
        desc_issues.append("❌ Keine Chapters")
    if '#' not in desc:
        desc_issues.append("⚠️ Keine Hashtags")
    
    if desc_issues:
        print("DESCRIPTION ISSUES:")
        for i in desc_issues:
            print(f"  {i}")
    else:
        print("✅ DESCRIPTION: PERFEKT!")
    print()
    
    tags = sn.get('tags', [])
    print(f"TAGS: {len(tags)} tags")
    if tags:
        print(f"  {tags[:15]}")
    print()
    
    print(f"📊 STATS:")
    print(f"  Views: {stats.get('viewCount', '?')}")
    print(f"  Likes: {stats.get('likeCount', '?')}")
    print(f"  Duration: {v['contentDetails']['duration']}")

print()
print("=" * 70)
print("📝 DRAFTS (Private Videos) STATUS")
print("=" * 70)

# Hole alle Videos inkl. Private
UPLOADS = 'UUVFv6Egpl0LDvigpFbQXNeQ'
drafts = []
next_page = None
while True:
    result = youtube.playlistItems().list(
        part='snippet,contentDetails,status',
        playlistId=UPLOADS,
        maxResults=50,
        pageToken=next_page
    ).execute()
    for item in result.get('items', []):
        status = item.get('status', {}).get('privacyStatus', 'unknown')
        if status == 'private':
            drafts.append({
                'id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'desc': item['snippet'].get('description', '')
            })
    next_page = result.get('nextPageToken')
    if not next_page:
        break

print(f"Total Drafts: {len(drafts)}")
print()

for d in drafts:
    desc_len = len(d['desc'])
    desc_upper = d['desc'].upper()
    has_cta = 'SUBSCRIBE' in desc_upper or 'LIKE' in desc_upper or 'ABONNIER' in desc_upper
    has_hashtags = '#' in d['desc']
    
    # Status icons
    status = []
    if desc_len < 100:
        status.append("❌ LEER")
    elif not has_cta:
        status.append("⚠️ Kein CTA")
    else:
        status.append("✅")
    
    print(f"📺 {d['id']}")
    print(f"   TITLE: {d['title'][:60]}")
    print(f"   DESC: {desc_len} chars | CTA: {'✅' if has_cta else '❌'} | #: {'✅' if has_hashtags else '❌'}")
    print(f"   STATUS: {' '.join(status)}")
    print()
