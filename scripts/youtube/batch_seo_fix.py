#!/usr/bin/env python3
"""Batch fix remaining SEO issues"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    with open('config/youtube_oauth.json') as f:
        oauth = json.load(f)

    creds = Credentials(
        token=oauth['token'],
        refresh_token=oauth['refresh_token'],
        token_uri=oauth['token_uri'],
        client_id=oauth['client_id'],
        client_secret=oauth['client_secret']
    )

    youtube = build('youtube', 'v3', credentials=creds)

    # Videos to fix
    fixes = [
        # Alfred J. Kwak Intro - category fix
        {'id': 'w5Yyyp0H6vo', 'fix_category': '1'},  # Already has CTA
        # Astro Boy - needs CTA
        {'id': 'lNcvMYyLPVU', 'add_cta': True},
        # The Frog - needs CTA
        {'id': 'dfUyhjEnAqw', 'add_cta': True},
    ]
    
    # Standard CTA block
    CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if you loved it!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE @remAIke_IT for more!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT"""

    print("=" * 60)
    print("🔧 BATCH SEO FIX")
    print("=" * 60)
    
    updated = 0
    errors = 0
    
    for fix in fixes:
        video_id = fix['id']
        print(f"\n🔄 Processing: {video_id}")
        
        try:
            # Get current video
            response = youtube.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            if not response['items']:
                print(f"   ❌ Video not found!")
                errors += 1
                continue
            
            video = response['items'][0]
            snippet = video['snippet']
            
            print(f"   Title: {snippet['title'][:50]}...")
            
            # Fix category
            if 'fix_category' in fix:
                old_cat = snippet['categoryId']
                snippet['categoryId'] = fix['fix_category']
                print(f"   📁 Category: {old_cat} → {fix['fix_category']}")
            
            # Add tags
            if 'add_tags' in fix:
                existing_tags = snippet.get('tags', [])
                new_tags = list(set(existing_tags + fix['add_tags']))
                snippet['tags'] = new_tags
                print(f"   🏷️  Tags: {len(existing_tags)} → {len(new_tags)}")
            
            # Add CTA if missing
            if fix.get('add_cta') and 'SUBSCRIBE' not in snippet.get('description', '').upper():
                snippet['description'] = snippet.get('description', '') + CTA_BLOCK
                print(f"   📢 Added CTA block")
            
            # Apply update
            youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            print(f"   ✅ Updated!")
            updated += 1
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            errors += 1
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Updated: {updated}")
    print(f"❌ Errors:  {errors}")

if __name__ == '__main__':
    main()
