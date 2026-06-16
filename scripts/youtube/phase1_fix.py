#!/usr/bin/env python3
"""Phase 1 Fix: Remove hashtags from titles + normalize 8K spelling"""
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
        scan = json.load(f)

    # Videos to fix
    hashtag_ids = [
        'YHlhhiAfxEA', '3UBF9ycZwJU', 'h6rDmu7FBzo', 'gVsamT781zU',
        'ZglrHGrG_oY', '_9GLuLakxgw', '90UleF637FA', 'EpzJcD6zkvs', 'EasEhYlorqQ'
    ]
    
    inconsistent_8k_ids = ['w5Yyyp0H6vo', 'T-EsdXGhqog', '3rB80OGKzrg', 'gx6eICiEYLo']
    
    all_ids = set(hashtag_ids + inconsistent_8k_ids)
    
    fixes = []
    for v in scan['videos']:
        if v['id'] not in all_ids:
            continue
        
        vid = v['id']
        sn = v['snippet']
        title = sn['title']
        new_title = title
        changes = []
        
        # Remove hashtags from title
        if '#' in title:
            # Remove hashtags and clean up
            new_title = re.sub(r'\s*#\w+', '', new_title)
            new_title = re.sub(r'\s+', ' ', new_title).strip()
            # Clean up trailing pipes or separators
            new_title = re.sub(r'\s*\|\s*$', '', new_title)
            changes.append('REMOVE_HASHTAGS')
        
        # Normalize 8K spelling
        if '8k ' in new_title or ' 8k' in new_title:
            new_title = re.sub(r'\b8k\b', '8K', new_title, flags=re.IGNORECASE)
            changes.append('8k->8K')
        
        if '8KHQ' in new_title:
            new_title = new_title.replace('8KHQ', '8K HQ')
            changes.append('8KHQ->8K HQ')
        
        if 'HQ8K' in new_title:
            new_title = new_title.replace('HQ8K', '8K HQ')
            changes.append('HQ8K->8K HQ')
        
        if changes:
            fixes.append({
                'id': vid,
                'old_title': title,
                'new_title': new_title,
                'changes': changes,
                'tags': sn.get('tags', []),
                'categoryId': sn.get('categoryId', '1'),
                'description': sn.get('description', '')
            })
    
    print(f"=== PHASE 1 FIX: {len(fixes)} VIDEOS ===\n")
    for fix in fixes:
        print(f"[{fix['id']}] {fix['changes']}")
        print(f"  OLD: {fix['old_title'][:65]}")
        print(f"  NEW: {fix['new_title'][:65]}")
        print()
    
    # Save plan
    with open('config/pending_updates/phase1_hashtag_8k_fix.json', 'w', encoding='utf-8') as f:
        json.dump(fixes, f, ensure_ascii=False, indent=2)
    
    # Apply via API
    with open("config/youtube_oauth.json") as f:
        oauth = json.load(f)

    creds = Credentials(
        token=oauth["token"],
        refresh_token=oauth["refresh_token"],
        token_uri=oauth["token_uri"],
        client_id=oauth["client_id"],
        client_secret=oauth["client_secret"],
    )
    youtube = build("youtube", "v3", credentials=creds)

    print("=== APPLYING FIXES ===\n")
    
    success = 0
    for fix in fixes:
        vid = fix['id']
        try:
            current = youtube.videos().list(part="snippet", id=vid).execute()
            if not current["items"]:
                print(f"[{vid}] NOT FOUND")
                continue

            snippet = current["items"][0]["snippet"]
            snippet["title"] = fix['new_title']
            # Keep description and tags unchanged
            
            youtube.videos().update(
                part="snippet",
                body={"id": vid, "snippet": snippet},
            ).execute()

            print(f"[{vid}] ✅ {fix['changes']}")
            success += 1
        except Exception as e:
            print(f"[{vid}] ❌ ERROR: {e}")

    print(f"\n=== DONE: {success}/{len(fixes)} ===")

if __name__ == "__main__":
    main()
