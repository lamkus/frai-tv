"""Fix 4 Maulwurf videos: reduce hashtags from 6 to 5 (remove #Remastered)."""
import os, json, sys, re

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

TOKEN_FILE = 'token.json'

def get_youtube():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

youtube = get_youtube()

VIDEO_IDS = ['wjpCNxf5SsY', 'UsppP3mPwHM', 'j4aBiGJcEY8', 'ts5qtXqneq8']
HASHTAG_TO_REMOVE = '#Remastered'

DRY_RUN = '--apply' not in sys.argv

if DRY_RUN:
    print("DRY RUN — add --apply to actually update")
print()

results = []
quota_used = 0

for vid in VIDEO_IDS:
    # Fetch current video
    resp = youtube.videos().list(part='snippet', id=vid).execute()
    quota_used += 1
    
    if not resp.get('items'):
        print(f"  X {vid} — not found!")
        continue
    
    item = resp['items'][0]
    snippet = item['snippet']
    title = snippet['title']
    desc = snippet['description']
    
    # Count current hashtags
    hashtags_before = [w for w in desc.split() if w.startswith('#')]
    
    if len(hashtags_before) <= 5:
        print(f"  - {vid} | {title[:50]} — already OK ({len(hashtags_before)} hashtags)")
        continue
    
    # Remove #Remastered from description
    new_desc = desc.replace(f' {HASHTAG_TO_REMOVE}', '').replace(f'{HASHTAG_TO_REMOVE} ', '').replace(HASHTAG_TO_REMOVE, '')
    # Clean up any double spaces
    new_desc = re.sub(r'  +', ' ', new_desc).strip()
    
    hashtags_after = [w for w in new_desc.split() if w.startswith('#')]
    
    print(f"  + {vid} | {title[:50]}")
    print(f"    Before: {len(hashtags_before)} hashtags → After: {len(hashtags_after)}")
    print(f"    Removed: {HASHTAG_TO_REMOVE}")
    
    if not DRY_RUN:
        snippet['description'] = new_desc
        youtube.videos().update(
            part='snippet',
            body={'id': vid, 'snippet': snippet}
        ).execute()
        quota_used += 50
        print(f"    UPDATED! (50 Quota)")
    
    results.append({
        'id': vid,
        'title': title,
        'hashtags_before': len(hashtags_before),
        'hashtags_after': len(hashtags_after),
        'removed': HASHTAG_TO_REMOVE,
        'applied': not DRY_RUN
    })
    print()

print(f"\nResults: {len(results)} videos {'UPDATED' if not DRY_RUN else 'to update'}")
print(f"Quota used: {quota_used} Units")

# Save report
with open('config/hashtag_fix_2026_02_19.json', 'w', encoding='utf-8') as f:
    json.dump({'results': results, 'quota_used': quota_used, 'dry_run': DRY_RUN}, f, indent=2)
print(f"Saved: config/hashtag_fix_2026_02_19.json")
