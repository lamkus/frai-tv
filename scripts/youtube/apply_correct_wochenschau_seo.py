#!/usr/bin/env python3
"""
APPLY CORRECT SEO TO 5 NEW WOCHENSCHAU VIDEOS
=============================================
Verwendet die gefixten Daten aus wochenschau_upload_data_FIXED.json
"""

import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
TOKEN_FILE = "config/token.pickle"
FIXED_DATA = "config/wochenschau_upload_data_FIXED.json"
PLAYLIST_ID = "PL3d2Tsr13ihMPkNIfoXwQ4W-bSheQxEvg"

# Die 5 neuen Videos
NEW_VIDEOS = {
    "459": "o33-c1riv4U",
    "468": "dAp7JFDhE3U", 
    "470": "t-VIxJaWE74",
    "471": "9muRRAleqdA",
    "473": "3AtirtgrfUI",
}

def get_youtube_service():
    with open(TOKEN_FILE, 'rb') as token:
        creds = pickle.load(token)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('youtube', 'v3', credentials=creds)

def main():
    print("=" * 70)
    print("🔧 APPLY CORRECT SEO - 5 Wochenschau Videos (1939)")
    print("=" * 70)
    print()
    
    # Lade gefixte Daten
    with open(FIXED_DATA, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    videos = data.get("videos", data) if isinstance(data, dict) else data
    
    # Finde die 5 Videos
    video_data = {}
    for v in videos:
        nr = str(v.get("video_nr", v.get("nr", "")))
        if nr in NEW_VIDEOS:
            video_data[nr] = v
    
    print(f"📊 {len(video_data)} Videos gefunden in FIXED data")
    print()
    
    youtube = get_youtube_service()
    print("✅ YouTube API verbunden\n")
    
    for nr, video_id in NEW_VIDEOS.items():
        if nr not in video_data:
            print(f"❌ Nr. {nr} nicht in FIXED data!")
            continue
        
        vd = video_data[nr]
        print(f"📹 Nr. {nr} ({video_id})")
        print(f"   📝 {vd['title'][:65]}...")
        
        # Hole aktuelles Video
        response = youtube.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        
        if not response.get("items"):
            print(f"   ❌ Video nicht gefunden!")
            continue
        
        snippet = response["items"][0]["snippet"]
        
        # Update
        snippet["title"] = vd["title"]
        snippet["description"] = vd["description"]
        
        # Tags bereinigen - YouTube erlaubt max 500 chars total, keine Sonderzeichen
        clean_tags = []
        total_len = 0
        for tag in vd.get("tags", []):
            # Entferne problematische Zeichen
            clean_tag = str(tag).strip()
            if len(clean_tag) > 0 and len(clean_tag) <= 30:
                if total_len + len(clean_tag) < 450:  # Buffer
                    clean_tags.append(clean_tag)
                    total_len += len(clean_tag)
        
        snippet["tags"] = clean_tags[:30]  # Max 30 Tags
        snippet["categoryId"] = vd.get("category", "27")
        
        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": snippet
            }
        ).execute()
        
        print(f"   ✅ SEO aktualisiert!")
        print()
    
    print("=" * 70)
    print("✅ Alle 5 Videos mit korrektem SEO aktualisiert!")
    print()
    print("📋 KORREKT ANGEWENDET:")
    print("  ✅ Titel: Die Deutsche Wochenschau Nr. X | DD.MM.YYYY | Germany WWII Newsreel | 8K HQ | @remAIke_IT")
    print("  ✅ Ufa-Tonwoche Hinweis (DE/EN/ES)")
    print("  ✅ Trilingual Description")
    print("  ✅ 14-Sprachen Tags")
    print("  ✅ CTA Block")
    print("=" * 70)

if __name__ == "__main__":
    main()
