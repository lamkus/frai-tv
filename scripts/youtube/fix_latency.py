"""Fix latency on current broadcast to 'normal' for max buffer tolerance."""
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

state = json.load(open('config/broadcast_state.json'))
bid = state['broadcast_id']
print(f'Broadcast: {bid}')

# 1. Check current
r = yt.liveBroadcasts().list(part='contentDetails,status', id=bid).execute()
item = r['items'][0]
cd = item['contentDetails']
lc = item['status']['lifeCycleStatus']
print(f'Lifecycle: {lc}')
print(f'Current latencyPreference: {cd.get("latencyPreference", "not set")}')
print(f'enableAutoStart: {cd.get("enableAutoStart")}')
print(f'enableAutoStop: {cd.get("enableAutoStop")}')
print(f'enableDvr: {cd.get("enableDvr")}')
print()

# 2. Update latency
try:
    cd['latencyPreference'] = 'normal'
    yt.liveBroadcasts().update(
        part='contentDetails',
        body={'id': bid, 'contentDetails': cd}
    ).execute()
    print('OK: latencyPreference -> normal (max buffer, no lag)')
except Exception as e:
    print(f'Update failed: {e}')
    print('YouTube may not allow latency changes while live.')
    print('New broadcasts from broadcast_manager.py will use normal latency.')
