#!/usr/bin/env python3
"""List all Soundie videos with their privacy status."""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open("D:/remaike.TV/config/youtube_oauth.json", "r") as f:
    token_data = json.load(f)

credentials = Credentials(
    token=token_data["token"],
    refresh_token=token_data["refresh_token"],
    token_uri=token_data["token_uri"],
    client_id=token_data["client_id"],
    client_secret=token_data["client_secret"],
)

youtube = build("youtube", "v3", credentials=credentials)

# Get all videos from uploads playlist
channel_response = youtube.channels().list(part="contentDetails", mine=True).execute()
uploads_playlist = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Get all videos and check for Soundies
soundie_public = []
soundie_private = []
all_videos = []

next_page = None
while True:
    playlist_response = youtube.playlistItems().list(
        part="snippet,status",
        playlistId=uploads_playlist,
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in playlist_response.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]
        title = item["snippet"]["title"]
        status = item["status"].get("privacyStatus", "unknown")
        
        all_videos.append({"id": video_id, "title": title, "status": status})
        
        # Check if it's a Soundie
        if "soundie" in title.lower():
            if status == "public":
                soundie_public.append({"id": video_id, "title": title})
            else:
                soundie_private.append({"id": video_id, "title": title, "status": status})
    
    next_page = playlist_response.get("nextPageToken")
    if not next_page:
        break

print(f"TOTAL VIDEOS: {len(all_videos)}")
print(f"SOUNDIE PUBLIC: {len(soundie_public)}")
print(f"SOUNDIE PRIVATE/DRAFT: {len(soundie_private)}")
print("=" * 70)

print("\n✅ PUBLIC SOUNDIES:")
for v in soundie_public:
    print(f"  {v['title'][:65]}")

print("\n🔒 PRIVATE/DRAFT SOUNDIES:")
for v in soundie_private:
    print(f"  [{v['status']}] {v['title'][:55]}")
