#!/usr/bin/env python3
"""
Apply SEO optimizations to draft videos.
Reads JSON files from config/pending_updates/draft_seo/ and applies via YouTube API.

QUOTA COSTS:
- videos.list: 1 unit (to get current snippet)
- videos.update: 50 units per video

SKIPS: Duplicates (status=DUPLICATE), Already optimized (status=ALREADY_OPTIMIZED)
"""

import os
import json
import sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SEO_DIR = PROJECT_ROOT / "config" / "pending_updates" / "draft_seo"
OAUTH_PATH = PROJECT_ROOT / "config" / "youtube_oauth.json"

def load_credentials():
    """Load OAuth credentials."""
    if not OAUTH_PATH.exists():
        print(f"❌ OAuth file not found: {OAUTH_PATH}")
        sys.exit(1)
    
    with open(OAUTH_PATH, 'r') as f:
        creds_data = json.load(f)
    
    return Credentials(
        token=creds_data.get('access_token') or creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri', 'https://oauth2.googleapis.com/token'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret')
    )

def load_seo_files():
    """Load all SEO JSON files."""
    seo_files = []
    for f in sorted(SEO_DIR.glob("*.json")):
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            data['_filename'] = f.name
            seo_files.append(data)
    return seo_files

def apply_seo_update(youtube, seo_data):
    """Apply SEO update to a single video."""
    video_id = seo_data.get('video_id')
    status = seo_data.get('status', '')
    action = seo_data.get('action', '')
    
    # Skip duplicates and already optimized
    if status == 'DUPLICATE':
        print(f"⏭️  Skipping DUPLICATE: {video_id} - Delete manually in YouTube Studio!")
        return {'skipped': True, 'reason': 'DUPLICATE'}
    
    if status == 'ALREADY_OPTIMIZED' and action != 'FIX_CATEGORY_AND_ENHANCE':
        print(f"✅ Already optimized: {video_id}")
        return {'skipped': True, 'reason': 'ALREADY_OPTIMIZED'}
    
    # Get optimized SEO data
    optimized = seo_data.get('optimized_seo', {})
    if not optimized:
        print(f"⏭️  No optimized_seo found for {video_id}")
        return {'skipped': True, 'reason': 'NO_OPTIMIZED_SEO'}
    
    try:
        # First, get current video data (1 quota unit)
        current = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not current.get('items'):
            print(f"❌ Video not found: {video_id}")
            return {'error': 'NOT_FOUND'}
        
        video = current['items'][0]
        snippet = video['snippet']
        
        # Build update body
        new_title = optimized.get('title', snippet.get('title'))
        new_tags = optimized.get('tags', snippet.get('tags', []))
        new_category = str(optimized.get('category', snippet.get('categoryId', '1')))
        is_wochenschau = new_title.lower().startswith('wochenschau')
        final_category = '27' if is_wochenschau else new_category
        final_default_language = 'de' if is_wochenschau else snippet.get('defaultLanguage', 'en')
        final_default_audio_language = 'de' if is_wochenschau else snippet.get('defaultAudioLanguage', final_default_language)
        
        # Build description from EN + DE parts
        desc_en = optimized.get('description_en', '')
        desc_de = optimized.get('description_de', '')
        if desc_en and desc_de:
            new_description = f"{desc_en}\n\n{desc_de}\n\n#PublicDomain #VintageClassic #8K #remAIke"
        else:
            new_description = snippet.get('description', '')
        
        # Update body
        update_body = {
            'id': video_id,
            'snippet': {
                'title': new_title,
                'description': new_description,
                'tags': new_tags,
                'categoryId': final_category,
                'defaultLanguage': final_default_language,
                'defaultAudioLanguage': final_default_audio_language
            }
        }
        
        # Apply update (50 quota units)
        print(f"🔄 Updating: {video_id} - {new_title[:50]}...")
        result = youtube.videos().update(
            part='snippet',
            body=update_body
        ).execute()
        
        print(f"✅ Updated: {video_id}")
        return {'success': True, 'video_id': video_id}
        
    except HttpError as e:
        error_msg = str(e)
        print(f"❌ API Error for {video_id}: {error_msg}")
        if 'quotaExceeded' in error_msg:
            print("🛑 QUOTA EXCEEDED - Stopping!")
            sys.exit(1)
        return {'error': error_msg}

def main():
    print("=" * 60)
    print("🎬 DRAFT SEO APPLY SCRIPT")
    print("=" * 60)
    
    # Load credentials
    print("\n📂 Loading OAuth credentials...")
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Load SEO files
    print(f"📂 Loading SEO files from {SEO_DIR}...")
    seo_files = load_seo_files()
    print(f"   Found {len(seo_files)} SEO files")
    
    # Filter: only READY_FOR_REVIEW, NEEDS_FIX
    to_apply = [s for s in seo_files if s.get('status') in ['READY_FOR_REVIEW', 'NEEDS_FIX']]
    print(f"   {len(to_apply)} videos need updates")
    
    # Quota estimation
    estimated_quota = len(to_apply) * 51  # 1 list + 50 update per video
    print(f"   Estimated quota: {estimated_quota} units")
    
    # Apply updates
    print("\n" + "=" * 60)
    print("🚀 APPLYING UPDATES")
    print("=" * 60)
    
    results = {
        'success': 0,
        'skipped': 0,
        'errors': 0
    }
    
    for seo_data in seo_files:
        result = apply_seo_update(youtube, seo_data)
        if result.get('success'):
            results['success'] += 1
        elif result.get('skipped'):
            results['skipped'] += 1
        else:
            results['errors'] += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Updated: {results['success']}")
    print(f"⏭️  Skipped: {results['skipped']}")
    print(f"❌ Errors:  {results['errors']}")
    print(f"\n💡 Remember: Delete duplicates manually in YouTube Studio!")
    print("   - Da76UFZiTw4 (Asterix Duplikat)")
    print("   - U6CAhg95Izk (Porky's Bear Facts Duplikat)")

if __name__ == '__main__':
    main()
