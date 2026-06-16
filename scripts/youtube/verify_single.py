"""Quick verify: check localizations on a specific video."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds_data = json.load(open('config/youtube_oauth.json'))
creds = Credentials(
    token=creds_data['access_token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
yt = build('youtube', 'v3', credentials=creds)

resp = yt.videos().list(part='snippet,localizations', id='ndAzCIUxo-c').execute()
v = resp['items'][0]
snippet = v['snippet']
locs = v.get('localizations', {})

print(f"Title: {snippet['title']}")
print(f"defaultLanguage: {snippet.get('defaultLanguage', 'NONE')}")
print(f"Localizations ({len(locs)}): {list(locs.keys())}")
print()
for lang, loc in locs.items():
    print(f"  [{lang}]")
    print(f"    Title: {loc['title'][:70]}")
    desc_preview = loc['description'][:120].replace('\n', ' | ')
    print(f"    Desc:  {desc_preview}...")
    print()
