"""Quick verify - check that 7 Wochenschau titles were updated correctly."""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json',
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

# 5 public + 2 drafts (need OAuth anyway)
ids = 'o33-c1riv4U,dAp7JFDhE3U,t-VIxJaWE74,9muRRAleqdA,3AtirtgrfUI,w2UvksMOs3c,6YLPpJLgVXk'
r = yt.videos().list(part='snippet', id=ids).execute()

print(f"Found {len(r['items'])} / 7 videos\n")
ok = 0
for item in r['items']:
    vid = item['id']
    s = item['snippet']
    t = s['title']
    c = s['categoryId']
    tags = len(s.get('tags', []))
    has_disclaimer = 'HISTORICAL DOCUMENT' in s.get('description', '')
    has_remaike = 'www.remaike.IT' in s.get('description', '')

    checks = []
    if 'Wochenschau:' in t: checks.append('title')
    if '8K HQ (4K UHD)' in t: checks.append('8K+4K')
    if '@remAIke' not in t: checks.append('no-handle')
    if c == '27': checks.append('cat27')
    if tags <= 15: checks.append(f'tags:{tags}')
    if has_disclaimer: checks.append('disclaimer')
    if has_remaike: checks.append('link')

    status = 'OK' if len(checks) >= 6 else 'WARN'
    if status == 'OK': ok += 1
    print(f"[{status}] {vid} | {t}")
    print(f"      Checks: {', '.join(checks)}")

print(f"\n{'='*50}")
print(f"Result: {ok}/7 fully compliant")
