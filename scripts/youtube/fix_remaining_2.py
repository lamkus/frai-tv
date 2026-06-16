"""Quick fix for 2 remaining videos with missing pflicht-tags."""
import json
import os
import sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PFLICHT_TAGS = ['remastered', 'restored']
FIX_IDS = ['LOTXPLYeRAc', 'u5poUF6KQfA']

def get_youtube_service():
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
    token_path = os.path.abspath(token_path)
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    )
    if creds.expired or not creds.valid:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def main():
    dry_run = '--apply' not in sys.argv
    youtube = get_youtube_service()
    
    resp = youtube.videos().list(part='snippet', id=','.join(FIX_IDS)).execute()
    
    for item in resp.get('items', []):
        vid = item['id']
        snippet = item['snippet']
        tags = snippet.get('tags', [])
        tag_lower = [t.lower() for t in tags]
        
        added = []
        for pt in PFLICHT_TAGS:
            if pt not in tag_lower:
                tags.append(pt)
                added.append(pt)
        
        # Trim to 15 if needed
        if len(tags) > 15:
            keep = [t for t in tags if t.lower() in [p.lower() for p in PFLICHT_TAGS]]
            rest = [t for t in tags if t.lower() not in [p.lower() for p in PFLICHT_TAGS]]
            tags = keep + rest[:15 - len(keep)]
        
        if not added:
            print(f"  [SKIP] {vid}: {snippet['title'][:50]} — already has pflicht-tags")
            continue
        
        print(f"  {'[DRY]' if dry_run else '[FIX]'} {vid}: {snippet['title'][:50]}")
        print(f"         Tags before: {len(tag_lower)} → after: {len(tags)}, added: {added}")
        
        if not dry_run:
            body = {
                'id': vid,
                'snippet': {
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'tags': tags,
                    'categoryId': snippet['categoryId']
                }
            }
            try:
                youtube.videos().update(part='snippet', body=body).execute()
                print(f"         ✅ Updated!")
            except Exception as e:
                print(f"         ❌ Error: {e}")
    
    if dry_run:
        print(f"\n🔄 To apply: python {sys.argv[0]} --apply")

if __name__ == '__main__':
    main()
