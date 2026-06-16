#!/usr/bin/env python3
"""Check broadcast + stream status via OAuth (mine=true)."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE = r'D:\remaike.TV'
TOKEN = os.path.join(BASE, 'token.json')
CLIENT = os.path.join(BASE, 'config', 'client_secret.json')

def get_youtube():
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN, 'w') as f:
                f.write(creds.to_json())
        else:
            print("ERROR: No valid token. Run OAuth flow first.")
            sys.exit(1)
    return build('youtube', 'v3', credentials=creds)

yt = get_youtube()

# Check ALL broadcasts (mine=true)
print("=== BROADCASTS ===")
resp = yt.liveBroadcasts().list(part='status,contentDetails,snippet', mine=True, maxResults=10).execute()
for item in resp.get('items', []):
    bid = item['id']
    status = item['status']
    snippet = item['snippet']
    content = item['contentDetails']
    print(f"\nBroadcast: {bid}")
    print(f"  Title: {snippet.get('title', '?')[:80]}")
    print(f"  LifeCycle: {status.get('lifeCycleStatus')}")
    print(f"  Recording: {status.get('recordingStatus')}")
    print(f"  Privacy: {status.get('privacyStatus')}")
    print(f"  BoundStream: {content.get('boundStreamId', 'NONE')[:40]}...")
    print(f"  AutoStart: {content.get('enableAutoStart')}")
    print(f"  AutoStop: {content.get('enableAutoStop')}")
    print(f"  MonitorStream: {content.get('monitorStream', {}).get('enableMonitorStream')}")

# Check ALL streams (mine=true)
print("\n=== STREAMS ===")
resp2 = yt.liveStreams().list(part='status,snippet,cdn', mine=True, maxResults=10).execute()
for stream in resp2.get('items', []):
    sid = stream['id']
    status = stream['status']
    snippet = stream['snippet']
    cdn = stream.get('cdn', {})
    print(f"\nStream: {sid[:40]}...")
    print(f"  Title: {snippet.get('title', '?')}")
    print(f"  StreamStatus: {status.get('streamStatus')}")
    print(f"  HealthStatus: {status.get('healthStatus', {}).get('status', '?')}")
    config = status.get('healthStatus', {}).get('configurationIssues', [])
    if config:
        for issue in config:
            print(f"  ⚠️ Issue: {issue.get('type')} - {issue.get('description')}")
    print(f"  Resolution: {cdn.get('resolution', '?')}")
    print(f"  FrameRate: {cdn.get('frameRate', '?')}")
    print(f"  IngestionType: {cdn.get('ingestionType', '?')}")

print("\nDone. (Costs: 2×1 = 2 quota units)")
