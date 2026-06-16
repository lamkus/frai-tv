#!/usr/bin/env python3
"""
Fix Nuremberg Title - HIGH PRIORITY SEO
"""
import json, sys, io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
youtube = build('youtube', 'v3', credentials=creds)

VIDEO_ID = 'DO8dSN4aAB4'
NEW_TITLE = 'Nuremberg Trials: Nazi Concentration Camps (1945) | 8K HQ | @remAIke_IT'

print('=' * 70)
print('🏛️ NUREMBERG TITLE FIX')
print('=' * 70)

# Get current
resp = youtube.videos().list(part='snippet', id=VIDEO_ID).execute()
if not resp['items']:
    print('❌ Video not found!')
    sys.exit(1)

snippet = resp['items'][0]['snippet']
old_title = snippet['title']

print(f'Old Title: {old_title}')
print(f'New Title: {NEW_TITLE}')
print()

if '--apply' not in sys.argv:
    print('🧪 DRY RUN - use --apply to change')
else:
    snippet['title'] = NEW_TITLE
    # Also change category to Education
    snippet['categoryId'] = '27'
    
    youtube.videos().update(
        part='snippet',
        body={'id': VIDEO_ID, 'snippet': snippet}
    ).execute()
    
    print('✅ Title updated!')
    print('✅ Category changed to Education (27)')
