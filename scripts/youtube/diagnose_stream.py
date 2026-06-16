"""Quick diagnostic: Why is the stream offline?"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

bid = '2xheXbR48Z8'
sid = 'VFv6Egpl0LDvigpFbQXNeQ1771887015419315'

print('='*60)
print('  STREAM DIAGNOSTIC')
print('='*60)

# Broadcast
br = yt.liveBroadcasts().list(part='status,snippet', id=bid).execute()
if br.get('items'):
    b = br['items'][0]
    st = b['status']
    sn = b['snippet']
    print(f'\n📺 Broadcast: {bid}')
    print(f'   Title:      {sn["title"][:70]}')
    print(f'   Lifecycle:  {st["lifeCycleStatus"]}')
    print(f'   Recording:  {st.get("recordingStatus", "N/A")}')
    print(f'   Privacy:    {st["privacyStatus"]}')
    print(f'   Scheduled:  {sn.get("scheduledStartTime", "N/A")}')
    print(f'   Actual:     {sn.get("actualStartTime", "N/A")}')
    print(f'   End:        {sn.get("actualEndTime", "not ended")}')
else:
    print(f'\n❌ Broadcast {bid} NOT FOUND!')

# Stream
sr = yt.liveStreams().list(part='status,snippet,cdn', id=sid).execute()
if sr.get('items'):
    s = sr['items'][0]
    ss = s['status']
    cdn = s.get('cdn', {})
    ing = cdn.get('ingestionInfo', {})
    print(f'\n📡 Stream: {sid[:30]}...')
    print(f'   Status:     {ss["streamStatus"]}')
    health = ss.get('healthStatus', {})
    print(f'   Health:     {health.get("status", "N/A")}')
    if health.get('configurationIssues'):
        for issue in health['configurationIssues']:
            print(f'   ⚠️  Issue:   {issue.get("type","?")} - {issue.get("description","?")}')
    print(f'   Key:        {ing.get("streamName", "?")[:8]}...')
    print(f'   RTMP:       {ing.get("ingestionAddress", "?")[:50]}')
    print(f'   Resolution: {cdn.get("resolution", "auto")}')
    print(f'   Framerate:  {cdn.get("frameRate", "auto")}')
else:
    print(f'\n❌ Stream {sid} NOT FOUND!')

# Also check if there are ANY active broadcasts
print(f'\n🔍 All broadcasts (active/live):')
for status_filter in ['active', 'upcoming', 'completed']:
    try:
        r = yt.liveBroadcasts().list(
            part='status,snippet',
            broadcastStatus=status_filter,
            maxResults=5
        ).execute()
        for item in r.get('items', []):
            ist = item['status']
            isn_ = item['snippet']
            print(f'   [{status_filter}] {item["id"]} | {ist["lifeCycleStatus"]} | {isn_["title"][:50]}')
    except Exception as e:
        print(f'   [{status_filter}] error: {e}')

print(f'\n{"="*60}')
