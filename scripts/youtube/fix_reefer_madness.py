#!/usr/bin/env python3
"""Fix Reefer Madness draft with full SEO - researched facts"""

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

VIDEO_ID = 'oGw7_7xazhU'

# Note: The film is from 1936, released 1938 in some markets
new_title = 'Reefer Madness (1936) | 8K HQ | Cult Classic Propaganda | @remAIke_IT'

new_desc = '''🔥 The most infamous propaganda film ever made!

"Tell Your Children" – the anti-cannabis hysteria film that became a stoner cult classic. Originally financed by a church group, later exploited by Dwain Esper, and now a legendary piece of cinema history.

🎬 REEFER MADNESS (1936)
• Original Title: "Tell Your Children"
• Director: Louis J. Gasnier
• Runtime: 66 minutes
• Also known as: "The Burning Question", "Dope Addict", "Love Madness"
• Public Domain since 1972

📖 THE STORY:
High school students are lured by pushers to try marijuana – portrayed as causing hallucinations, murder, suicide, rape, and descent into madness. What was meant as a warning became the ultimate example of propaganda gone wrong.

🏆 CULT STATUS:
In the 1970s, NORML began screening this film to show the absurdity of anti-drug campaigns. It became a midnight movie sensation, forever changing how we view propaganda.

🎭 CAST:
• Dorothy Short as Mary Lane
• Kenneth Craig as Bill Harper  
• Lillian Miles as Blanche
• Dave O'Brien as Ralph Wiley
• Thelma White as Mae Coleman
• Carleton Young as Jack Perry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇩🇪 DEUTSCH:
Der berüchtigtste Propaganda-Film aller Zeiten! "Reefer Madness" zeigt Cannabis als Ursache für Mord, Wahnsinn und moralischen Verfall – heute ein Kultobjekt der Stoner-Kultur.

🇪🇸 ESPAÑOL:
¡La película de propaganda más infame jamás hecha! "Reefer Madness" retrata el cannabis como causa de locura – hoy un clásico de culto.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎬 LIKE if you love cult classics!
💬 COMMENT: Is this the worst propaganda ever?
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More: https://frai.tv | @remAIke_IT

#ReeferMadness #CultClassic #Propaganda #Cannabis #1936 #PublicDomain #8K #Restored #TellYourChildren #Vintage #ClassicFilm #Marijuana #420 #remAIke'''

new_tags = [
    'Reefer Madness', 'Tell Your Children', 'Cult Classic', 'Propaganda',
    '1936', 'Louis Gasnier', 'Cannabis', 'Marijuana', 'Public Domain',
    '8K', 'Restored', 'Vintage', 'Classic Film', 'Exploitation Film',
    'Anti-Drug', 'Midnight Movie', 'Stoner Culture', '420', 'NORML',
    'Dorothy Short', 'Dave OBrien', 'Burning Question', 'remAIke'
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
video['snippet']['categoryId'] = '1'  # Film & Animation

youtube.videos().update(
    part='snippet',
    body={'id': VIDEO_ID, 'snippet': video['snippet']}
).execute()

print('✅ REEFER MADNESS UPDATED!')
print(f'Tags: {len(new_tags)}')
print(f'Desc: {len(new_desc)} chars')
print()
print('Highlights:')
print('- Director: Louis J. Gasnier')
print('- Original: "Tell Your Children"')
print('- Cult classic since 1970s NORML screenings')
