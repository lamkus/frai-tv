#!/usr/bin/env python3
"""Apply SEO updates from shorts_seo folder"""
import json
import os
import glob
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def main():
    seo_dir = 'config/pending_updates/shorts_seo'
    
    print("=" * 60)
    print("🎬 SHORTS SEO APPLY SCRIPT")
    print("=" * 60)
    
    # Load OAuth
    print("\n📂 Loading OAuth credentials...")
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
    
    # Load SEO files
    print(f"📂 Loading SEO files from {seo_dir}...")
    seo_files = glob.glob(os.path.join(seo_dir, '*.json'))
    
    if not seo_files:
        print("❌ No SEO files found!")
        return
    
    print(f"   Found {len(seo_files)} SEO files")
    
    updated = 0
    errors = 0
    
    print("\n" + "=" * 60)
    print("🚀 APPLYING UPDATES")
    print("=" * 60)
    
    for seo_file in seo_files:
        with open(seo_file, encoding='utf-8') as f:
            seo = json.load(f)
        
        if 'optimized_seo' not in seo:
            print(f"⏭️  No optimized_seo in {os.path.basename(seo_file)}")
            continue
        
        video_id = seo['video_id']
        opt = seo['optimized_seo']
        
        print(f"🔄 Updating: {video_id} - {opt['title'][:50]}...")
        
        try:
            # Get current video data
            current = youtube.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            if not current['items']:
                print(f"❌ Video not found: {video_id}")
                errors += 1
                continue
            
            video = current['items'][0]
            snippet = video['snippet']
            
            # Update snippet
            snippet['title'] = opt['title']
            snippet['description'] = opt['description']
            snippet['tags'] = opt['tags']
            snippet['categoryId'] = opt['categoryId']
            
            # Apply update
            youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            print(f"✅ Updated: {video_id}")
            updated += 1
            
        except Exception as e:
            print(f"❌ Error updating {video_id}: {e}")
            errors += 1
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Updated: {updated}")
    print(f"❌ Errors:  {errors}")

if __name__ == '__main__':
    main()
