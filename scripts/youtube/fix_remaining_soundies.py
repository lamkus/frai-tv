#!/usr/bin/env python3
"""Fix remaining 3 Soundies with old format."""
import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
OAUTH_PATH = os.path.join(CONFIG_DIR, 'youtube_oauth.json')

# Find and fix remaining old-format Soundies
def load_credentials():
    with open(OAUTH_PATH, 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    if creds.expired:
        creds.refresh(Request())
        token_data['token'] = creds.token
        with open(OAUTH_PATH, 'w') as f:
            json.dump(token_data, f, indent=2)
    
    return creds

def fix_soundie_title(old_title):
    """Convert 'Soundie: Song Name | ...' to 'Song Name (1940s) | Soundie | 8K HQ | @remAIke_IT'"""
    import re
    
    # Extract song name from "Soundie: Song Name | ..."
    if old_title.lower().startswith('soundie:'):
        parts = old_title.split('|')
        song_part = parts[0].replace('Soundie:', '').replace('Soundie -', '').strip()
        
        # Clean up song name
        song_name = song_part.strip()
        
        # Build new title: "Song Name (1940s) | Soundie | 8K HQ | @remAIke_IT"
        new_title = f"{song_name} (1940s) | Soundie | 8K HQ | @remAIke_IT"
        
        # Ensure max 70 chars
        if len(new_title) > 70:
            # Shorten song name
            max_song_len = 70 - len(" (1940s) | Soundie | 8K HQ | @remAIke_IT")
            song_name = song_name[:max_song_len-3] + "..."
            new_title = f"{song_name} (1940s) | Soundie | 8K HQ | @remAIke_IT"
        
        return new_title
    
    return old_title

def main():
    # Load channel data
    data = json.load(open('config/fresh_channel_scan.json', encoding='utf-8'))
    
    # Find old-format Soundies
    old_format_soundies = []
    for v in data['videos']:
        title = v['snippet']['title']
        if title.lower().startswith('soundie:') or title.lower().startswith('soundie -'):
            old_format_soundies.append({
                'id': v['id'],
                'old_title': title,
                'new_title': fix_soundie_title(title)
            })
    
    print("=" * 70)
    print("🎵 FIX REMAINING SOUNDIES WITH OLD FORMAT")
    print("=" * 70)
    print(f"📊 Found: {len(old_format_soundies)} Soundies with old format")
    print()
    
    for s in old_format_soundies:
        print(f"❌ OLD: {s['old_title']}")
        print(f"✅ NEW: {s['new_title']}")
        print()
    
    if not old_format_soundies:
        print("✅ Alle Soundies haben bereits das neue Format!")
        return
    
    # Load credentials
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    success = 0
    for i, fix in enumerate(old_format_soundies, 1):
        try:
            # Get current video
            response = youtube.videos().list(part='snippet', id=fix['id']).execute()
            if not response.get('items'):
                print(f"[{i}] ❌ Video nicht gefunden: {fix['id']}")
                continue
            
            snippet = response['items'][0]['snippet']
            snippet['title'] = fix['new_title']
            
            # Apply
            youtube.videos().update(part='snippet', body={'id': fix['id'], 'snippet': snippet}).execute()
            print(f"[{i}/{len(old_format_soundies)}] ✅ {fix['new_title'][:50]}...")
            success += 1
            
        except Exception as e:
            print(f"[{i}] ❌ Fehler: {e}")
    
    print()
    print("=" * 70)
    print(f"✅ Erfolgreich: {success}/{len(old_format_soundies)}")

if __name__ == '__main__':
    main()
