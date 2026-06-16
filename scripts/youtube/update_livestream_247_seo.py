import os
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def get_youtube_client():
    token_path = 'config/youtube_oauth.json'
    if not os.path.exists(token_path):
        print(f"Error: {token_path} not found.")
        return None
    with open(token_path, 'r') as f:
        creds_data = json.load(f)
    creds = Credentials.from_authorized_user_info(creds_data)
    return build('youtube', 'v3', credentials=creds)

def update_to_247_format():
    youtube = get_youtube_client()
    if not youtube:
        return

    # 1. Get active broadcast
    request = youtube.liveBroadcasts().list(
        part="id,snippet,status",
        broadcastStatus="active",
        broadcastType="all"
    )
    response = request.execute()

    if not response.get("items"):
        print("No active broadcast found.")
        return

    broadcast = response["items"][0]
    broadcast_id = broadcast["id"]
    snippet = broadcast["snippet"]
    status = broadcast["status"]

    print(f"Found active broadcast: {broadcast_id}")

    # 2. Define 24/7 Global SEO Metadata
    new_title = "Wochenschau 24/7 LIVE: World War 2 History Archive | 8K HQ (4K UHD)"
    
    new_description = """🔴 Welcome to the 24/7 Wochenschau TV Live Stream!
Classic vintage newsreel masterpieces, AI remastered in stunning 8K quality.
Experience historical World War 2 documentary footage broadcasting continuously.

🌍 MULTILINGUAL SEARCH:
Hindi: द्वितीय विश्व युद्ध लाइव
English: World War II Live Stream, WWII Archive
Indonesian: Perang Dunia II Siaran Langsung
Portuguese: Segunda Guerra Mundial Ao Vivo
Spanish: Segunda Guerra Mundial En Vivo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #WWII #Live #History #PublicDomain"""

    new_tags = [
        "wochenschau live", "24/7 history stream", "world war 2 live", 
        "ww2 archive", "vintage newsreel", "historical footage", 
        "remastered", "restored", "AI enhanced", "classic", 
        "public domain", "free documentary"
    ]

    # Update snippet
    snippet["title"] = new_title
    snippet["description"] = new_description
    
    # Remove scheduledStartTime if present to avoid errors on active streams
    if "scheduledStartTime" in snippet:
        del snippet["scheduledStartTime"]

    # 3. Execute Update
    try:
        update_request = youtube.liveBroadcasts().update(
            part="snippet,status",
            body={
                "id": broadcast_id,
                "snippet": snippet,
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        update_response = update_request.execute()
        print("✅ Successfully updated livestream to 24/7 Global SEO format!")
        print(f"New Title: {update_response['snippet']['title']}")
        
        # Also update the video tags (liveBroadcasts doesn't support tags directly, need videos.update)
        video_id = broadcast_id # For broadcasts, broadcast ID is usually the video ID
        video_request = youtube.videos().list(part="snippet", id=video_id).execute()
        if video_request.get("items"):
            video_snippet = video_request["items"][0]["snippet"]
            video_snippet["tags"] = new_tags
            video_snippet["categoryId"] = "27"
            
            youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": video_snippet
                }
            ).execute()
            print("✅ Successfully updated video tags for global reach!")
            
    except Exception as e:
        print(f"❌ Error updating broadcast: {e}")

if __name__ == "__main__":
    update_to_247_format()
