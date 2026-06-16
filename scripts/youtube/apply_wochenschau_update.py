#!/usr/bin/env python3
"""Apply pending Wochenschau multilingual updates."""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

PENDING_FILE = "config/pending_updates/wochenschau_multilingual.json"
OAUTH_FILE = "config/youtube_oauth.json"

def load_credentials():
    """Load OAuth credentials."""
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    
    return Credentials(
        token=token_data['token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

def main():
    # Load pending updates
    with open(PENDING_FILE, 'r', encoding='utf-8') as f:
        updates = json.load(f)
    
    print(f"📋 {len(updates)} Wochenschau updates to apply\n")
    
    # Build YouTube API client
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    success = 0
    failed = 0
    
    for update in updates:
        video_id = update['video_id']
        nr = update['nr']
        new_desc = update['new_description']
        
        print(f"🔄 Nr. {nr} ({video_id})...", end=" ")
        
        try:
            # Get current video data first
            response = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                print("❌ Video not found!")
                failed += 1
                continue
            
            video = response['items'][0]
            snippet = video['snippet']
            
            # Update only description, keep everything else
            snippet['description'] = new_desc
            
            # Apply update
            youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            ).execute()
            
            print(f"✅ Updated ({len(new_desc)} chars)")
            success += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Success: {success}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Quota used: ~{success * 51} units (1 read + 50 write per video)")
    
    if success == len(updates):
        # Archive the pending file
        archive_path = PENDING_FILE.replace('.json', '_applied.json')
        os.rename(PENDING_FILE, archive_path)
        print(f"\n📁 Archived to: {archive_path}")

if __name__ == "__main__":
    main()
