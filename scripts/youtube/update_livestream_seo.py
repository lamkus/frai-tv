import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_youtube_client():
    creds_path = 'config/youtube_oauth.json'
    if not os.path.exists(creds_path):
        print("Error: config/youtube_oauth.json not found.")
        return None
    
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

def update_active_broadcast():
    youtube = get_youtube_client()
    if not youtube:
        return

    print("Fetching active/upcoming broadcasts...")
    request = youtube.liveBroadcasts().list(
        part="id,snippet,status",
        broadcastStatus="all",
        broadcastType="all"
    )
    response = request.execute()
    
    broadcasts = response.get('items', [])
    if not broadcasts:
        print("No broadcasts found.")
        return
        
    for b in broadcasts:
        print(f"Found Broadcast: {b['snippet']['title']} (Status: {b['status']['lifeCycleStatus']}, Privacy: {b['status']['privacyStatus']})")
        
        # We want to update the one that is currently receiving our stream
        # Usually it's 'ready' or 'testing' or 'live'
        if b['status']['lifeCycleStatus'] in ['ready', 'testing', 'live', 'created']:
            print(f"Updating broadcast {b['id']}...")
            
            # Apply SEO Rules from copilot-instructions.md
            # Title: Wochenschau: [Event] (DD.MM.YYYY) | 8K HQ (4K UHD)
            # Since it's a 24/7 stream, we might name it generally or based on the current episode.
            # Let's use a general 24/7 title for now, or specific if we know it.
            # The user complained about "History WochenschauTV : Deutsche Wochenschau..."
            
            new_title = "Wochenschau: 24/7 Livestream | 8K HQ (4K UHD)"
            new_description = """🎬 Classic vintage newsreel masterpiece, AI remastered in stunning 8K quality.
Originally released in the 1940s, now restored and upscaled for modern screens.

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
            b['snippet']['categoryId'] = "27" # Education
            
            # Update snippet
            update_request = youtube.liveBroadcasts().update(
                part="snippet,status",
                body={
                    "id": b['id'],
                    "snippet": b['snippet'],
                    "status": {
                        "privacyStatus": "public" # Make it public!
                    }
                }
            )
            try:
                update_response = update_request.execute()
                print(f"Successfully updated broadcast {b['id']} to Public with correct SEO!")
            except Exception as e:
                print(f"Error updating broadcast: {e}")

if __name__ == "__main__":
    update_active_broadcast()
