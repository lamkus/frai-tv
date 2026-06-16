#!/usr/bin/env python3
"""
LIVE APPLY SEO FIXES - remAIke_IT Channel
Applies all pending title fixes via YouTube API

⚠️ WARNING: This modifies LIVE videos!
📊 API Cost: 50 Units per video = ~3500 Units total for 69 videos
"""

import json
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Files
OAUTH_FILE = 'd:/remaike.TV/config/youtube_oauth.json'
FIXES_FILE = 'd:/remaike.TV/config/seo_fixes_pending.json'
LOG_FILE = 'd:/remaike.TV/config/seo_apply_log.json'

def load_credentials():
    """Load OAuth credentials from file."""
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
    
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=creds_data.get('scopes')
    )
    
    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        creds_data['token'] = creds.token
        with open(OAUTH_FILE, 'w') as f:
            json.dump(creds_data, f, indent=2)
        print("✅ Token refreshed")
    
    return creds

def apply_title_fix(youtube, video_id, new_title):
    """
    Apply a single title fix via videos.update API.
    Cost: 50 Units
    """
    try:
        # First, get current video data (need snippet for update)
        video_response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            return {'success': False, 'error': f'Video {video_id} not found'}
        
        video = video_response['items'][0]
        snippet = video['snippet']
        
        # Store old title for logging
        old_title = snippet['title']
        
        # Update title
        snippet['title'] = new_title
        
        # Apply update
        update_response = youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        return {
            'success': True,
            'video_id': video_id,
            'old_title': old_title,
            'new_title': new_title
        }
        
    except HttpError as e:
        error_content = json.loads(e.content.decode())
        return {
            'success': False,
            'video_id': video_id,
            'error': error_content.get('error', {}).get('message', str(e))
        }
    except Exception as e:
        return {
            'success': False,
            'video_id': video_id,
            'error': str(e)
        }

def main():
    print("=" * 70)
    print("🚀 LIVE SEO FIX APPLICATION - remAIke_IT")
    print("=" * 70)
    
    # Load pending fixes
    with open(FIXES_FILE, 'r', encoding='utf-8') as f:
        fixes = json.load(f)
    
    # Filter only title fixes
    title_fixes = [f for f in fixes['title_fixes'] if f.get('new_title')]
    
    print(f"\n📊 Pending Title Fixes: {len(title_fixes)}")
    print(f"📊 Estimated API Cost: {len(title_fixes) * 50} Units")
    print(f"📊 Estimated Time: ~{len(title_fixes) * 2} seconds")
    
    # Show preview
    print("\n📋 PREVIEW (erste 10):")
    print("-" * 70)
    for i, fix in enumerate(title_fixes[:10]):
        print(f"\n{i+1}. {fix['category']}")
        print(f"   ALT: {fix['current_title'][:55]}...")
        print(f"   NEU: {fix['new_title']}")
    
    if len(title_fixes) > 10:
        print(f"\n   ... und {len(title_fixes) - 10} weitere")
    
    print("\n" + "=" * 70)
    print("⚠️  DIESE AKTION ÄNDERT LIVE-VIDEOS!")
    print("=" * 70)
    
    # Load credentials and build API
    print("\n🔑 Loading OAuth credentials...")
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    print("✅ YouTube API connected")
    
    # Apply fixes
    print(f"\n🚀 Applying {len(title_fixes)} title fixes...")
    print("-" * 70)
    
    results = {
        'started_at': datetime.now().isoformat(),
        'total': len(title_fixes),
        'success': 0,
        'failed': 0,
        'details': []
    }
    
    for i, fix in enumerate(title_fixes):
        video_id = fix['video_id']
        new_title = fix['new_title']
        category = fix['category']
        
        print(f"\n[{i+1}/{len(title_fixes)}] {category}: {video_id}")
        print(f"   → {new_title[:50]}...")
        
        result = apply_title_fix(youtube, video_id, new_title)
        
        if result['success']:
            print(f"   ✅ Success!")
            results['success'] += 1
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
            results['failed'] += 1
        
        results['details'].append(result)
        
        # Rate limiting - wait between requests
        time.sleep(1.5)  # 1.5 seconds between requests to avoid quota issues
    
    # Final summary
    results['finished_at'] = datetime.now().isoformat()
    
    print("\n" + "=" * 70)
    print("📊 ERGEBNIS")
    print("=" * 70)
    print(f"   ✅ Erfolgreich: {results['success']}")
    print(f"   ❌ Fehlgeschlagen: {results['failed']}")
    print(f"   📊 API Units verbraucht: ~{results['success'] * 50}")
    
    # Save log
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Log gespeichert: {LOG_FILE}")
    
    if results['failed'] > 0:
        print("\n⚠️  Einige Updates sind fehlgeschlagen!")
        print("   Prüfe das Log für Details.")
        failed = [r for r in results['details'] if not r['success']]
        for f in failed[:5]:
            print(f"   - {f['video_id']}: {f.get('error', 'Unknown')}")

if __name__ == '__main__':
    main()
