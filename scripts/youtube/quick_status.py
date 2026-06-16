"""Quick channel status + latest uploads check via OAuth (2 quota)"""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'youtube_oauth.json')

with open(OAUTH_PATH) as f:
    tok = json.load(f)

creds = Credentials(
    token=tok['access_token'],
    refresh_token=tok['refresh_token'],
    token_uri=tok['token_uri'],
    client_id=tok['client_id'],
    client_secret=tok['client_secret'],
    scopes=tok.get('scopes', ['https://www.googleapis.com/auth/youtube.force-ssl'])
)

youtube = build('youtube', 'v3', credentials=creds)

# Channel stats
ch = youtube.channels().list(part='statistics,contentDetails', id='UCVFv6Egpl0LDvigpFbQXNeQ').execute()
stats = ch['items'][0]['statistics']
print(f"=== CHANNEL STATUS (LIVE) ===")
print(f"  Subscribers: {stats['subscriberCount']}")
print(f"  Videos:      {stats['videoCount']}")
print(f"  Views:       {stats['viewCount']}")

upload_pl = ch['items'][0]['contentDetails']['relatedPlaylists']['uploads']

# Latest 15 uploads
resp = youtube.playlistItems().list(
    part='contentDetails,snippet',
    playlistId=upload_pl,
    maxResults=15
).execute()

print(f"\n=== NEUESTE 15 UPLOADS ===")
for i, item in enumerate(resp['items'], 1):
    vid = item['contentDetails']['videoId']
    title = item['snippet']['title'][:70]
    pub = item['contentDetails'].get('videoPublishedAt', '?')[:10]
    print(f"  {i:2}. {pub} | {vid} | {title}")

# Save updated token
if creds.token != tok['access_token']:
    tok['access_token'] = creds.token
    with open(OAUTH_PATH, 'w') as f:
        json.dump(tok, f, indent=2)
    print("\n  [Token refreshed]")
