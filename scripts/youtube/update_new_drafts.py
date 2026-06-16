#!/usr/bin/env python3
"""
🚀 UPDATE NEW DRAFT VIDEOS WITH SEO
===================================
Updates die neuen Uploads (Nr502, Nr518) mit kompletten SEO-Daten
"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
DATABASE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")

def load_credentials():
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
    return Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )

def main():
    print("=" * 70)
    print("🚀 UPDATE NEW DRAFT VIDEOS WITH SEO")
    print("=" * 70)
    
    with open(DATABASE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Die neuen Private Videos / Drafts
    NEW_VIDEOS = {
        '547': '6wop-BU_XME',
        '548': 'ZuD1fAyGiUw',
        '550': 'wEMKHQPopHY',
        '573': 'tVD8197vAyE'
    }
    
    for nr, video_id in NEW_VIDEOS.items():
        seo = db['videos'].get(nr)
        if not seo:
            print(f"❌ No SEO for Nr.{nr}!")
            continue
        
        # Video holen
        response = youtube.videos().list(part='snippet,status', id=video_id).execute()
        if not response.get('items'):
            print(f"❌ Nr.{nr}: Video not found")
            continue
        
        video = response['items'][0]
        snippet = video['snippet']
        status = video['status']['privacyStatus']
        old_title = snippet.get('title', '')
        old_desc = len(snippet.get('description', ''))
        old_tags = len(snippet.get('tags', []))
        
        print(f"\n📺 Nr.{nr} ({video_id}):")
        print(f"   Status: {status}")
        print(f"   Old Title: {old_title}")
        
        # Update
        snippet['title'] = seo['title']
        snippet['description'] = seo['description']
        snippet['tags'] = seo['tags'][:30]
        snippet['categoryId'] = seo['category_id']
        snippet['defaultLanguage'] = 'de'
        
        youtube.videos().update(part='snippet', body={'id': video_id, 'snippet': snippet}).execute()
        
        print(f"   ✅ UPDATED!")
        print(f"   New Title: {seo['title']}")
        print(f"   Desc: {old_desc} → {len(seo['description'])} chars")
        print(f"   Tags: {old_tags} → {len(seo['tags'])} tags")
    
    print("\n" + "=" * 70)
    print("✅ DONE! Videos ready to publish when upload complete.")
    print("=" * 70)

if __name__ == "__main__":
    main()
