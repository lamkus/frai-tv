"""Quick channel status check — Public API only (1 quota unit)"""
import requests, os, json

API_KEY = os.environ.get('YOUTUBE_API_KEY')
if not API_KEY:
    print('ERROR: YOUTUBE_API_KEY not set!')
    exit(1)

# Channel stats
r = requests.get('https://youtube.googleapis.com/youtube/v3/channels', params={
    'part': 'statistics,snippet',
    'id': 'UCVFv6Egpl0LDvigpFbQXNeQ',
    'key': API_KEY
})
data = r.json()
if 'items' not in data:
    print('ERROR:', data)
    exit(1)

ch = data['items'][0]
stats = ch['statistics']
title = ch['snippet']['title']
subs = stats['subscriberCount']
views = stats['viewCount']
vids = stats['videoCount']

print(f"Channel: {title}")
print(f"Subscribers: {subs}")
print(f"Total Views: {views}")
print(f"Videos: {vids}")
print(f"Quota used: 1 unit (channels.list)")
