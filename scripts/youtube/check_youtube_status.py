#!/usr/bin/env python3
"""Check actual YouTube video status."""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Load OAuth
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

# Check ein Soundie Video
video_id = "mReDNz-Exdk"  # Lamp of Memory
response = youtube.videos().list(part="snippet", id=video_id).execute()

if response.get("items"):
    snippet = response["items"][0]["snippet"]
    print("=== AKTUELLER STAND AUF YOUTUBE ===")
    print(f"Video ID: {video_id}")
    print(f"Titel: {snippet['title']}")
    print(f"\nDescription (erste 300 Zeichen):")
    print(snippet.get("description", "KEINE")[:300])
    print(f"\nTags: {snippet.get('tags', [])}")
else:
    print("Video nicht gefunden!")
