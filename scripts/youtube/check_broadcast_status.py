#!/usr/bin/env python3
"""Quick broadcast status check via public API."""
import os, requests, json

API_KEY = os.getenv('YOUTUBE_API_KEY')
if not API_KEY:
    print("ERROR: YOUTUBE_API_KEY not set!")
    exit(1)

for bid in ['F4SwdhCvHAo', '57TykeHQYwU']:
    r = requests.get('https://youtube.googleapis.com/youtube/v3/liveBroadcasts', params={
        'id': bid, 'part': 'status,contentDetails,snippet', 'key': API_KEY
    })
    data = r.json()
    if data.get('items'):
        item = data['items'][0]
        status = item['status']
        snippet = item['snippet']
        content = item['contentDetails']
        title = snippet.get('title', '???')
        print(f"Broadcast {bid}:")
        print(f"  Title: {title[:70]}")
        print(f"  LifeCycleStatus: {status.get('lifeCycleStatus')}")
        print(f"  RecordingStatus: {status.get('recordingStatus')}")
        print(f"  Privacy: {status.get('privacyStatus')}")
        print(f"  BoundStream: {content.get('boundStreamId', 'NONE')}")
        print(f"  AutoStart: {content.get('enableAutoStart')}")
        print(f"  AutoStop: {content.get('enableAutoStop')}")
        print()
    else:
        print(f"Broadcast {bid}: NOT FOUND or not accessible via public API")
        err = data.get('error', {})
        if err:
            print(f"  Error: {err.get('message', '???')}")
        print()

# Also check stream status
print("--- Stream Status ---")
r = requests.get('https://youtube.googleapis.com/youtube/v3/liveStreams', params={
    'part': 'status,snippet', 'mine': 'true', 'key': API_KEY
})
data = r.json()
if data.get('error'):
    # Public API can't check streams with mine=true, need OAuth
    print("(Stream status requires OAuth - checking via broadcast binding)")
else:
    for stream in data.get('items', []):
        print(f"  Stream: {stream['id'][:30]}... Status: {stream['status'].get('streamStatus')}")
