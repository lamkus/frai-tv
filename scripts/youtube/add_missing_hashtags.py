#!/usr/bin/env python3
"""
Add Missing Hashtags zu 3 Videos
"""

import json
import sys
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

OAUTH_FILE = 'config/youtube_oauth.json'
DRY_RUN = '--apply' not in sys.argv

# Die 3 Videos ohne Hashtags (aus Audit)
VIDEOS_TO_FIX = [
    {"id": "EZxg1D958mo", "title": "A Corny Concerto (1943)"},
    {"id": "2nT_DjkOWn8", "title": "Pigs In A Polka (1943)"},
    {"id": "0ZT_5BmyixM", "title": "A Tale Of Two Kitties (1942)"},
]

# Hashtag-Block für Looney Tunes
HASHTAG_BLOCK = """

#LooneyTunes #WB #VintageCartoons #8K #PublicDomain #WarneBros #ClassicAnimation #remAIke"""


def load_credentials():
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    return Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )


def main():
    print("=" * 70)
    print("🏷️ ADD MISSING HASHTAGS")
    print("=" * 70)
    
    if DRY_RUN:
        print("\n⚠️  DRY RUN MODE")
        print("    Für echte Updates: python script.py --apply\n")
    else:
        print("\n🔴 LIVE MODE\n")
    
    print(f"Videos zu fixen: {len(VIDEOS_TO_FIX)}")
    for v in VIDEOS_TO_FIX:
        print(f"  - {v['id']}: {v['title']}")
    
    if not DRY_RUN:
        creds = load_credentials()
        youtube = build('youtube', 'v3', credentials=creds)
        
        for v in VIDEOS_TO_FIX:
            try:
                # Hole Video
                video = youtube.videos().list(
                    part='snippet',
                    id=v['id']
                ).execute()
                
                if not video.get('items'):
                    print(f"❌ {v['id']}: nicht gefunden")
                    continue
                
                snippet = video['items'][0]['snippet']
                old_desc = snippet['description']
                
                # Füge Hashtags hinzu (wenn nicht schon vorhanden)
                if '#' in old_desc:
                    print(f"⚠️ {v['id']}: Hat bereits Hashtags")
                    continue
                
                new_desc = old_desc + HASHTAG_BLOCK
                
                # Update
                youtube.videos().update(
                    part='snippet',
                    body={
                        'id': v['id'],
                        'snippet': {
                            'title': snippet['title'],
                            'description': new_desc,
                            'tags': snippet.get('tags', []),
                            'categoryId': snippet['categoryId']
                        }
                    }
                ).execute()
                
                print(f"✅ {v['id']}: Hashtags hinzugefügt")
                
            except Exception as e:
                print(f"❌ {v['id']}: {str(e)[:50]}")
    
    print("\n✅ Fertig!")


if __name__ == '__main__':
    main()
