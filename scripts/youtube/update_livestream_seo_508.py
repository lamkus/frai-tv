import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube_client():
    creds_path = 'config/youtube_oauth.json'
    with open(creds_path, 'r') as f:
        creds_data = json.load(f)
        
    creds = Credentials(
        token=creds_data.get('token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri=creds_data.get('token_uri'),
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
        scopes=creds_data.get('scopes')
    )
    return build('youtube', 'v3', credentials=creds)

def update_broadcast_508():
    youtube = get_youtube_client()
    
    request = youtube.liveBroadcasts().list(
        part="id,snippet,status",
        broadcastStatus="all",
        broadcastType="all"
    )
    response = request.execute()
    
    for b in response.get('items', []):
        if b['status']['lifeCycleStatus'] in ['ready', 'testing', 'live', 'created']:
            print(f"Updating broadcast {b['id']}...")
            
            new_title = "Wochenschau: Dunkirk Pocket (29.05.1940) | 8K HQ (4K UHD)"
            new_description = """🎬 Classic vintage newsreel masterpiece, AI remastered in stunning 8K quality.
Originally released in 1940, now restored and upscaled for modern screens.

📍 Location: Dunkirk, France
📜 Historical Note: Alliierte eingekesselt bei Dünkirchen (26.05.-04.06.1940)

🌍 MULTILINGUAL SEARCH:
Hindi: द्वितीय विश्व युद्ध
English: World War II, WWII
Indonesian: Perang Dunia II
Portuguese: Segunda Guerra Mundial
Spanish: Segunda Guerra Mundial

🕐 CHAPTERS:
0:00 Intro

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #WWII #8K #History #PublicDomain"""

            b['snippet']['title'] = new_title
            b['snippet']['description'] = new_description
            
            update_request = youtube.liveBroadcasts().update(
                part="snippet,status",
                body={
                    "id": b['id'],
                    "snippet": {
                        "title": new_title,
                        "description": new_description
                    },
                    "status": {
                        "privacyStatus": "public"
                    }
                }
            )
            try:
                update_response = update_request.execute()
                print(f"Successfully updated broadcast {b['id']} to Public with correct SEO!")
            except Exception as e:
                print(f"Error updating broadcast: {e}")

if __name__ == "__main__":
    update_broadcast_508()
