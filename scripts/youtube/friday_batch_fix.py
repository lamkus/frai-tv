#!/usr/bin/env python3
"""Friday batch fix - add branding, 8K, CTA to 11 videos"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    with open('config/fresh_channel_scan.json', encoding='utf-8') as f:
        scan = json.load(f)

    problem_ids = [
        'CSLfwklQq9s', 'YU9W-d33yYg', 'w5Yyyp0H6vo', 'h6rDmu7FBzo', 
        '90UleF637FA', 'gx6eICiEYLo', 'dpF2uQVgCsM', '_3Z1GTYFUAM', 
        'tk3DHvp9CFs', 'YHlhhiAfxEA', '4vaim28zk50'
    ]

    fixes = []
    for vid in problem_ids:
        v = next((x for x in scan['videos'] if x['id'] == vid), None)
        if not v:
            continue
            
        sn = v['snippet']
        title = sn['title']
        desc = sn.get('description', '')
        tags = sn.get('tags', [])
        cat = sn.get('categoryId', '1')
        
        new_title = title
        new_desc = desc
        changes = []
        
        # Fix missing @remAIke_IT
        if '@remAIke' not in title and '@remaike' not in title.lower():
            if len(title) < 85:
                new_title = title.rstrip() + ' | @remAIke_IT'
            else:
                new_title = title[:80].rstrip() + ' | @remAIke_IT'
            changes.append('BRANDING')
        
        # Fix missing 8K
        if '8K' not in new_title and '8k' not in new_title:
            if '4K' in new_title:
                new_title = new_title.replace('4K', '8K')
                changes.append('4K->8K')
            elif '4k' in new_title:
                new_title = new_title.replace('4k', '8K')
                changes.append('4k->8K')
            else:
                if ' | ' in new_title:
                    parts = new_title.split(' | ', 1)
                    new_title = parts[0] + ' | 8K HQ | ' + parts[1]
                else:
                    new_title = new_title + ' | 8K HQ'
                changes.append('+8K')
        
        # Fix missing CTA
        if 'SUBSCRIBE' not in desc.upper() and 'ABONNIEREN' not in desc.upper():
            cta_block = "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎬 LIKE if you loved it!\n💬 COMMENT your thoughts!\n🔔 SUBSCRIBE for more!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📺 More: https://frai.tv | @remAIke_IT"
            new_desc = desc.rstrip() + cta_block
            changes.append('+CTA')
        
        if changes:
            fixes.append({
                'id': vid,
                'old_title': title,
                'new_title': new_title,
                'new_desc': new_desc,
                'tags': tags,
                'categoryId': cat,
                'changes': changes
            })

    print(f"=== FRIDAY BATCH FIX: {len(fixes)} VIDEOS ===\n")
    for fix in fixes:
        print(f"[{fix['id']}] {fix['changes']}")
        print(f"  OLD: {fix['old_title'][:55]}...")
        print(f"  NEW: {fix['new_title'][:55]}...")
        print()

    # Save plan
    with open('config/pending_updates/friday_batch_fix.json', 'w', encoding='utf-8') as f:
        json.dump(fixes, f, ensure_ascii=False, indent=2)
    print("Saved: config/pending_updates/friday_batch_fix.json")

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

    print("\n=== APPLYING FIXES ===\n")
    
    for fix in fixes:
        vid = fix['id']
        try:
            current = youtube.videos().list(part="snippet", id=vid).execute()
            if not current["items"]:
                print(f"[{vid}] NOT FOUND - SKIP")
                continue

            snippet = current["items"][0]["snippet"]
            snippet["title"] = fix['new_title']
            snippet["description"] = fix['new_desc']
            snippet["tags"] = fix['tags']
            snippet["categoryId"] = fix['categoryId']

            youtube.videos().update(
                part="snippet",
                body={"id": vid, "snippet": snippet},
            ).execute()

            print(f"[{vid}] ✅ UPDATED: {fix['changes']}")
        except Exception as e:
            print(f"[{vid}] ❌ ERROR: {e}")

    print("\n=== DONE ===")

if __name__ == "__main__":
    main()
