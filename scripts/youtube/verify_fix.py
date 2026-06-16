"""
VERIFY FIX — Quick check of the 37 fixed videos directly from API.
Reads current state live and checks compliance.
"""
import json
import os
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PFLICHT_TAGS = {'remastered', 'restored'}
MAX_HASHTAGS = 5
MAX_TAGS = 15

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
    # Load fixed video IDs
    issues_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                'full_compliance_issues_2026_02_17.json')
    with open(os.path.abspath(issues_path), 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    video_ids = [v['id'] for v in data['fixable']]
    original_issues = {v['id']: v['issues'] for v in data['fixable']}
    
    print(f"=== VERIFY FIX — Checking {len(video_ids)} videos LIVE ===\n")
    
    youtube = get_youtube_service()
    
    still_broken = []
    fixed = []
    
    # Fetch in batches of 50
    for batch_start in range(0, len(video_ids), 50):
        batch_ids = video_ids[batch_start:batch_start + 50]
        resp = youtube.videos().list(
            part='snippet',
            id=','.join(batch_ids)
        ).execute()
        
        for item in resp.get('items', []):
            vid = item['id']
            snippet = item['snippet']
            title = snippet['title']
            desc = snippet['description']
            tags = [t.lower() for t in snippet.get('tags', [])]
            remaining_issues = []
            
            # R1b: Check (4K UHD) in title
            if '8K HQ' in title and '(4K UHD)' not in title:
                remaining_issues.append('R1b: Still missing (4K UHD)')
            
            # R5: www.remaike.IT  
            if 'remaike.it' not in desc.lower():
                remaining_issues.append('R5: Still missing www.remaike.IT')
            
            # R7: Hashtags
            hashtags = re.findall(r'#\w+', desc)
            if len(hashtags) > MAX_HASHTAGS:
                remaining_issues.append(f'R7: Still {len(hashtags)} hashtags')
            
            # R8: Tags count
            if len(tags) > MAX_TAGS:
                remaining_issues.append(f'R8: Still {len(tags)} tags')
            
            # R13: Pflicht-Tags
            missing = PFLICHT_TAGS - set(tags)
            if missing:
                remaining_issues.append(f'R13: Still missing: {missing}')
            
            if remaining_issues:
                still_broken.append({
                    'id': vid, 'title': title,
                    'original': original_issues.get(vid, []),
                    'remaining': remaining_issues
                })
                status = '❌'
            else:
                fixed.append(vid)
                status = '✅'
            
            print(f"  {status} {vid}: {title[:50]}")
            for issue in remaining_issues:
                print(f"      ⚠️  {issue}")
    
    print(f"\n{'='*60}")
    print(f"RESULT: {len(fixed)}/{len(video_ids)} FIXED | {len(still_broken)} REMAINING")
    
    if still_broken:
        print(f"\n⚠️  STILL BROKEN:")
        for v in still_broken:
            print(f"  {v['id']}: {v['title'][:50]}")
            for i in v['remaining']:
                print(f"    → {i}")
    else:
        print(f"\n🎉 ALL {len(fixed)} VIDEOS FULLY COMPLIANT!")

if __name__ == '__main__':
    main()
