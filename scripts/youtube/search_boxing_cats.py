#!/usr/bin/env python3
"""Search for Boxing Cats via Public API."""
import requests
import os

API_KEY = os.getenv('YOUTUBE_API_KEY')
CHANNEL_ID = 'UCVFv6Egpl0LDvigpFbQXNeQ'

# Search for boxing cats
response = requests.get(
    'https://www.googleapis.com/youtube/v3/search',
    params={
        'part': 'snippet',
        'channelId': CHANNEL_ID,
        'q': 'boxing cats 1894',
        'type': 'video',
        'maxResults': 10,
        'key': API_KEY
    }
)

data = response.json()
print('Status:', response.status_code)
if 'items' in data:
    for item in data['items']:
        vid = item['id']['videoId']
        title = item['snippet']['title']
        print(f"ID: {vid}")
        print(f"Title: {title}")
        print()
else:
    print(data)
