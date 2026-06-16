#!/usr/bin/env python3
"""Fix Ken Block draft with full SEO"""

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

VIDEO_ID = '174AyltH9OI'

new_title = 'Ken Block: Jump Jam at DiRT 2 Launch (2009) | 8K HQ | @remAIke_IT'

new_desc = '''How would you feel sitting next to Ken Block? 🏎️💨

This legendary Jump Jam event at the DiRT 2 video game launch showcases Ken Block's insane driving skills – jumps, drifts, and pure adrenaline!

🏆 KEN BLOCK (1967-2023)
Rally legend, Gymkhana pioneer, and co-founder of DC Shoes and Hoonigan Racing Division. His viral Gymkhana videos revolutionized motorsport content forever.

🎮 DiRT 2 LAUNCH EVENT (2009)
This exclusive footage captures the raw energy of Ken Block performing at the DiRT 2 game launch – a perfect blend of gaming culture and real motorsport action.

🔥 WHAT YOU'LL SEE:
• Insane jumps and airtime
• Precision drifts
• Rally car madness
• Pure Block magic

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 LIKE if Ken Block was a legend!
💬 COMMENT: Would YOU sit next to Ken Block?
🔔 SUBSCRIBE for more motorsport classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT

#KenBlock #JumpJam #DiRT2 #Rally #Gymkhana #Hoonigan #Motorsport #8K #Legend #RIP #remAIke'''

new_tags = [
    'Ken Block', 'Jump Jam', 'DiRT 2', 'Rally', 'Gymkhana', 'Hoonigan',
    'DC Shoes', 'Motorsport', 'Drifting', 'Stunt Driving', '2009',
    'Video Game Launch', 'Rally Car', '8K', 'Restored', 'Legend',
    'RIP Ken Block', 'Extreme Sports', 'remAIke'
]

# Get current video
response = youtube.videos().list(part='snippet,status', id=VIDEO_ID).execute()
video = response['items'][0]

current_title = video['snippet']['title']
print(f'Current Title: {current_title}')
print(f'New Title:     {new_title}')
print()

# Update
video['snippet']['title'] = new_title
video['snippet']['description'] = new_desc
video['snippet']['tags'] = new_tags
video['snippet']['categoryId'] = '2'  # Autos & Vehicles

youtube.videos().update(
    part='snippet',
    body={'id': VIDEO_ID, 'snippet': video['snippet']}
).execute()

print('✅ UPDATED!')
print(f'Tags: {len(new_tags)}')
print(f'Desc: {len(new_desc)} chars')
print()
print('Hook: "How would you feel sitting next to Ken Block?"')
