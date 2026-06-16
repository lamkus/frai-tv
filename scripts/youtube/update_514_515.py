#!/usr/bin/env python3
"""Update Nr.514 und Nr.515 mit SEO-Daten."""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Video IDs
NEW_DRAFTS = {
    '514': '7st-GFEwdWQ',
    '515': 'vkCoIJGAf3E'
}

# Lade SEO-Datenbank
with open('config/wochenschau_complete_upload_database.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)
    db = raw.get('videos', raw)  # Handle both structures

# Lade OAuth
with open('config/youtube_oauth.json', 'r') as f:
    creds_data = json.load(f)
creds = Credentials(
    token=creds_data['token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Update beide Videos
for nr, vid in NEW_DRAFTS.items():
    if nr not in db:
        print(f'❌ Nr.{nr} nicht in SEO-Datenbank!')
        continue
    
    seo = db[nr]
    print(f'\n📝 Updating Nr.{nr} ({vid})...')
    print(f'   Title: {seo["title"]}')
    
    # Sanitize tags (remove non-ASCII if needed)
    safe_tags = []
    for tag in seo['tags']:
        # Keep only ASCII-safe tags for YouTube API
        try:
            tag.encode('ascii')
            safe_tags.append(tag)
        except UnicodeEncodeError:
            pass
    
    # API Update
    try:
        youtube.videos().update(
            part='snippet',
            body={
                'id': vid,
                'snippet': {
                    'title': seo['title'],
                    'description': seo['description'],
                    'tags': safe_tags[:15],
                    'categoryId': '27',  # Education
                    'defaultLanguage': 'de',
                    'defaultAudioLanguage': 'de'
                }
            }
        ).execute()
        print(f'   ✅ SUCCESS!')
    except Exception as e:
        print(f'   ❌ ERROR: {e}')

print('\n🎉 Done!')
