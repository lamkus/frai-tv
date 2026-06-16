"""
Check current Wochenschau descriptions
"""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    token_data = json.load(f)

creds = Credentials(
    token=token_data['token'],
    refresh_token=token_data['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=token_data['client_id'],
    client_secret=token_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Wochenschau IDs
IDS = ['6K-MuUu6L44', 'W-UcQleew8Y', 'dYBzf5V1TjI', 'jGz1kC1Z69A', 'bZkUPQHqyfg', 
       'iEEvt-s1XhQ', 'H_n_mS-eKps', 'w2UvksMOs3c', '6YLPpJLgVXk', 'T-EsdXGhqog', '3rB80OGKzrg']

result = youtube.videos().list(part='snippet', id=','.join(IDS)).execute()

print('=== WOCHENSCHAU VIDEOS - AKTUELLE DESCRIPTIONS ===\n')
for v in result.get('items', []):
    vid_id = v['id']
    title = v['snippet']['title']
    desc = v['snippet']['description']
    print('='*60)
    print(f'ID: {vid_id}')
    print(f'TITLE: {title}')
    print(f'DESC LENGTH: {len(desc)} chars')
    print('DESCRIPTION PREVIEW:')
    print(desc[:400])
    print('...\n')
