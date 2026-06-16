#!/usr/bin/env python3
"""Create Best Of playlist with top videos from each category"""

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

# Create Best Of playlist
print('Creating Best Of playlist...')

new_playlist = youtube.playlists().insert(
    part='snippet,status',
    body={
        'snippet': {
            'title': 'Best of remAIke_IT | 8K Restored Classics',
            'description': '''Die besten restaurierten Klassiker von remAIke_IT in 8K HQ!

Eine handverlesene Auswahl unserer Top-Videos:
- Legendaere Cartoons
- Klassische Musikfilme  
- Historische Dokumente
- Und mehr!

Perfekt fuer neue Besucher - entdecke das Beste aus unserem Archiv!

SUBSCRIBE for weekly restorations!
https://frai.tv | @remAIke_IT

#BestOf #8K #PublicDomain #ClassicFilms #remAIke'''
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
).execute()

playlist_id = new_playlist['id']
print(f"Created: {new_playlist['snippet']['title']}")
print(f"ID: {playlist_id}")

# Best videos to add (mix from all categories)
BEST_VIDEOS = [
    # Betty Boop classics
    'uI1gKIPbpW4',  # Minnie the Moocher (1932)
    'dwbvRpAcspE',  # Snow White (1933)
    
    # Alfred J. Kwak
    '1R9NzjOFE1Y',  # Episode 1
    
    # Superman Fleischer  
    'sL78rCHW7E0',  # Superman (1941)
    
    # Soundies
    'gB_KUOpsNnM',  # Heaven Help a Sailor
    
    # Popeye
    '3gzbxznJ_PM',  # Popeye Marathon
    
    # Casper
    'QIhpffT3wpc',  # Casper classic
    
    # Felix
    'GlCHK1g-5SY',  # Felix the Cat
    
    # Documentary
    'eF81rBeXbzk',  # Hindenburg
    
    # Christmas Special
    'cZR9qnDgn2w',  # Christmas cartoon
]

print(f"Adding {len(BEST_VIDEOS)} videos...")
added = 0
for vid in BEST_VIDEOS:
    try:
        youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': vid
                    }
                }
            }
        ).execute()
        added += 1
        print(f"  Added: {vid}")
    except Exception as e:
        print(f"  Skip: {vid} - {str(e)[:40]}")

print(f"Done! Added {added} videos to Best Of playlist")
print(f"URL: https://www.youtube.com/playlist?list={playlist_id}")
