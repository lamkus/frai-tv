#!/usr/bin/env python3
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    oauth_data = json.load(f)

creds = Credentials(
    token=oauth_data['token'],
    refresh_token=oauth_data['refresh_token'],
    token_uri=oauth_data['token_uri'],
    client_id=oauth_data['client_id'],
    client_secret=oauth_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

video_id = 'gB_KUOpsNnM'
new_title = 'Soundie: Heaven Help a Sailor | 8K HQ | Vintage Music | @remAIke_IT'

description = """🎵 Heaven Help a Sailor on a Night Like This

📅 Original Soundie aus den 1940er Jahren
🎬 Remastered in 8K HQ (4K UHD) by remAIke

═══════════════════════════════════════════════
🎬 WAS SIND SOUNDIES?
═══════════════════════════════════════════════

Soundies waren kurze Musikfilme (3-4 Minuten), die von 1940-1947 für spezielle Musikautomaten namens "Panoram" produziert wurden.

🎹 GENRE: Vintage Music / Jazz / Swing

═══════════════════════════════════════════════
📺 MEHR AUF DIESEM KANAL
═══════════════════════════════════════════════

🎵 Channel: https://www.youtube.com/@remAIke_IT

👍 LIKE & SUBSCRIBE für mehr Vintage Music!

#Soundie #VintageMusic #1940s #Jazz #Swing #ClassicMusic #PublicDomain #8K #remAIke
"""

tags = ['soundie', 'soundies', '1940s', 'vintage music', 'jazz', 'swing', 'big band', 
        'classic music', 'public domain', '8K', '4K UHD', 'remastered', 'remAIke',
        'Heaven Help a Sailor']

response = youtube.videos().list(part='snippet,status', id=video_id).execute()
item = response['items'][0]
snippet = item['snippet']

snippet['title'] = new_title
snippet['description'] = description
snippet['tags'] = tags
snippet['categoryId'] = '10'

youtube.videos().update(part='snippet', body={'id': video_id, 'snippet': snippet}).execute()
print(f'DONE: {new_title}')
