"""Check current live broadcast state and thumbnail."""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

bid = 'lm4EcKHQ45o'
r = yt.videos().list(part='snippet,status,liveStreamingDetails,localizations', id=bid).execute()
v = r['items'][0]
s = v['snippet']

print(f"Current LIVE broadcast: {bid}")
print(f"Title: {s['title'][:80]}")
print(f"Privacy: {v['status']['privacyStatus']}")
print(f"Category: {s.get('categoryId')}")
print(f"Tags: {len(s.get('tags', []))}")
print(f"DefaultLang: {s.get('defaultLanguage', 'NOT SET')}")
print(f"Localizations: {len(v.get('localizations', {}))}")

print("\nThumbnails:")
for k, t in s.get('thumbnails', {}).items():
    url = t.get('url', 'none')
    w = t.get('width', 0)
    h = t.get('height', 0)
    print(f"  {k}: {w}x{h} → {url[:90]}")

print(f"\nStream details:")
lsd = v.get('liveStreamingDetails', {})
for k2, v2 in lsd.items():
    print(f"  {k2}: {v2}")
