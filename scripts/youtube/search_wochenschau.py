#!/usr/bin/env python3
"""Search for ALL Wochenschau videos via Search API"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json','r') as f:
    td = json.load(f)

c = Credentials(
    token=td['token'],
    refresh_token=td['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=td['client_id'],
    client_secret=td['client_secret']
)

yt = build('youtube','v3',credentials=c)

# Search for Wochenschau videos on the channel
print("Searching for 'Wochenschau' on channel...")
r = yt.search().list(
    part='snippet',
    channelId='UCVFv6Egpl0LDvigpFbQXNeQ',
    q='Wochenschau',
    type='video',
    maxResults=50
).execute()

results = r.get('items', [])
print(f"Found {len(results)} results:")
print()

for item in results:
    vid = item['id']['videoId']
    title = item['snippet']['title']
    marker = ' <<< 516!' if '516' in title else ''
    print(f"{vid}: {title[:55]}{marker}")

# Also check specifically for T-EsdXGhqog
print()
print("=" * 60)
print("Checking video T-EsdXGhqog specifically:")
r2 = yt.videos().list(
    part='snippet,status',
    id='T-EsdXGhqog'
).execute()

if r2['items']:
    item = r2['items'][0]
    print(f"Title: {item['snippet']['title']}")
    print(f"Channel: {item['snippet']['channelTitle']}")
    print(f"Status: {item['status']['privacyStatus']}")
    print(f"Published: {item['snippet']['publishedAt']}")
