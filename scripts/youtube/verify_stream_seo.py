"""Verify live broadcast SEO state from YouTube API."""
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

bid = '2xheXbR48Z8'
r = yt.videos().list(part='snippet,localizations', id=bid).execute()
v = r['items'][0]
s = v['snippet']
loc = v.get('localizations', {})

print('=== LIVE BROADCAST SEO VERIFICATION ===')
print(f'Title:          {s["title"]}')
print(f'Category:       {s["categoryId"]}')
print(f'Default Lang:   {s.get("defaultLanguage", "NOT SET")}')
print(f'Default Audio:  {s.get("defaultAudioLanguage", "NOT SET")}')

tags = s.get('tags', [])
print(f'Tags:           {len(tags)} ({sum(len(t) for t in tags)} chars)')
for t in tags[:10]:
    print(f'  - {t}')
if len(tags) > 10:
    print(f'  ... +{len(tags)-10} more')

print(f'\nLocalizations:  {len(loc)} languages')
for lang in sorted(loc.keys()):
    title = loc[lang].get('title', '')[:60]
    print(f'  {lang:8s} → {title}')

desc_lines = s['description'].split('\n')
print(f'\nDescription:    {len(desc_lines)} lines')
print('--- First 5 lines ---')
for line in desc_lines[:5]:
    print(f'  {line}')

print('\n--- Language flags check ---')
flags = {
    '🇩🇪': 'DE', '🇬🇧': 'EN', '🇪🇸': 'ES', '🇵🇹': 'PT',
    '🇫🇷': 'FR', '🇷🇺': 'RU', '🇯🇵': 'JA', '🇮🇳': 'HI',
    '🇨🇳': 'ZH', '🇸🇦': 'AR', '🇮🇩': 'ID', '🇻🇳': 'VI',
    '🇹🇷': 'TR', '🇰🇷': 'KO'
}
ok = 0
for flag, lang in flags.items():
    found = any(flag in line for line in desc_lines)
    status = '✅' if found else '❌'
    if found: ok += 1
    print(f'  {flag} {lang:4s} {status}')

print(f'\n=== RESULT: {ok}/14 languages in description, '
      f'{len(loc)} localizations, {len(tags)} tags ===')
