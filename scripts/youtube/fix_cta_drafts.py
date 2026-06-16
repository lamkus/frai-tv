#!/usr/bin/env python3
"""Fix die 2 Drafts ohne CTA"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import sys

with open('config/youtube_oauth.json') as f:
    oauth = json.load(f)

creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri=oauth['token_uri'],
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret'],
)
youtube = build('youtube', 'v3', credentials=creds)

# Die 2 ohne CTA
DRAFTS = [
    {
        'id': 'RmfemqBK3tw',
        'name': 'Drei Mäuse Musketiere'
    },
    {
        'id': 'ehjlG5IEZGg', 
        'name': 'Kleene Punker'
    }
]

CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👍 LIKE if you enjoyed!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 More at: https://frai.tv | @remAIke_IT"""

for draft in DRAFTS:
    result = youtube.videos().list(part='snippet', id=draft['id']).execute()
    if result['items']:
        sn = result['items'][0]['snippet']
        print("=" * 60)
        print(f"ID: {draft['id']} - {draft['name']}")
        print(f"TITLE: {sn['title']}")
        print()
        print("CURRENT DESC:")
        print(sn['description'])
        print()
        
        # Füge CTA hinzu wenn nicht vorhanden
        if 'SUBSCRIBE' not in sn['description'].upper():
            new_desc = sn['description'].rstrip() + "\n" + CTA_BLOCK
            print(">>> ADDING CTA BLOCK")
            
            if '--apply' in sys.argv:
                youtube.videos().update(
                    part='snippet',
                    body={
                        'id': draft['id'],
                        'snippet': {
                            'title': sn['title'],
                            'description': new_desc,
                            'tags': sn.get('tags', []),
                            'categoryId': sn['categoryId']
                        }
                    }
                ).execute()
                print("✅ UPDATED!")
            else:
                print("(dry run)")

if '--apply' not in sys.argv:
    print()
    print("⚠️ DRY RUN - Starte mit --apply")
