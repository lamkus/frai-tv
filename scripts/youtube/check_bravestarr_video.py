#!/usr/bin/env python3
"""Aktuellen Stand des BraveStarr Videos prüfen"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json
from pathlib import Path

oauth = json.loads(Path("config/youtube_oauth.json").read_text(encoding="utf-8"))
creds = Credentials(
    token=oauth.get("token"),
    refresh_token=oauth.get("refresh_token"),
    token_uri=oauth.get("token_uri"),
    client_id=oauth.get("client_id"),
    client_secret=oauth.get("client_secret"),
    scopes=oauth.get("scopes"),
)

youtube = build("youtube", "v3", credentials=creds)

# BraveStarr Musikfestival pruefen
vid = "XU7yM4H5vrY"
resp = youtube.videos().list(part="snippet", id=vid).execute()
if resp.get("items"):
    s = resp["items"][0]["snippet"]
    print("AKTUELLER STAND Video XU7yM4H5vrY:")
    print("=" * 60)
    print(f"TITEL: {s['title']}")
    print()
    print("BESCHREIBUNG (erste 800 Zeichen):")
    print("-" * 60)
    print(s["description"][:800])
    print("-" * 60)
    print()
    tags = s.get("tags", [])
    print(f"TAGS ({len(tags)}):")
    print(tags)
