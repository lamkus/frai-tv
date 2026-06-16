#!/usr/bin/env python3
"""
🚀 FIX ONLINE WOCHENSCHAU VIDEOS - COMPLETE SEO UPDATE
========================================================
Updated: Titel (schon gemacht), Description, Tags

Videos: Nr. 459, 468, 470, 471, 473
"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
RESULT_FILE = os.path.join(BASE_DIR, "config", "online_seo_fix_result.json")

# Die 5 Online-Videos (IDs aus Scan)
ONLINE_VIDEOS = {
    "459": "o33-c1riv4U",
    "468": "dAp7JFDhE3U",
    "470": "t-VIxJaWE74",
    "471": "9muRRAleqdA",
    "473": "3AtirtgrfUI"
}

def load_credentials():
    """Lade OAuth Credentials"""
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
    return Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )

def load_database():
    """Lade SEO-Datenbank"""
    with open(DATABASE, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_video_complete(youtube, video_id, seo_data):
    """Update Video mit kompletten SEO-Daten"""
    try:
        # Aktuellen Status holen
        response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            return {"success": False, "error": "Video nicht gefunden"}
        
        video = response['items'][0]
        snippet = video['snippet']
        
        # Alte Werte speichern
        old_title = snippet['title']
        old_desc_len = len(snippet.get('description', ''))
        old_tags = snippet.get('tags', [])
        
        # Neue Werte setzen
        snippet['title'] = seo_data['title']
        snippet['description'] = seo_data['description']
        snippet['tags'] = seo_data['tags']
        snippet['categoryId'] = seo_data['category_id']
        snippet['defaultLanguage'] = 'de'
        
        # Update durchführen
        youtube.videos().update(
            part='snippet',
            body={
                'id': video_id,
                'snippet': snippet
            }
        ).execute()
        
        return {
            "success": True,
            "video_id": video_id,
            "changes": {
                "title": {"old": old_title, "new": seo_data['title']},
                "description": {"old_length": old_desc_len, "new_length": len(seo_data['description'])},
                "tags": {"old_count": len(old_tags), "new_count": len(seo_data['tags'])},
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 70)
    print("🚀 FIXING ONLINE WOCHENSCHAU VIDEOS - COMPLETE SEO")
    print("=" * 70)
    
    # Laden
    db = load_database()
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "updates": [],
        "summary": {}
    }
    
    success_count = 0
    
    print(f"\n📋 Updating {len(ONLINE_VIDEOS)} videos with complete SEO data...")
    print("-" * 70)
    
    for nr, video_id in ONLINE_VIDEOS.items():
        seo_data = db["videos"].get(nr)
        
        if not seo_data:
            print(f"   ❌ Nr. {nr}: Keine SEO-Daten gefunden!")
            continue
        
        print(f"\n   📺 Nr. {nr} ({video_id}):")
        print(f"      Title: {seo_data['title']}")
        print(f"      Desc: {seo_data['description_length']} chars")
        print(f"      Tags: {seo_data['tags_count']} tags ({seo_data['tags_total_chars']} chars)")
        
        result = update_video_complete(youtube, video_id, seo_data)
        
        if result["success"]:
            success_count += 1
            print(f"      ✅ UPDATED!")
            print(f"         Desc: {result['changes']['description']['old_length']} → {result['changes']['description']['new_length']} chars")
            print(f"         Tags: {result['changes']['tags']['old_count']} → {result['changes']['tags']['new_count']} tags")
        else:
            print(f"      ❌ ERROR: {result.get('error')}")
        
        results["updates"].append({
            "nr": nr,
            "video_id": video_id,
            "event": seo_data.get('event_en', ''),
            **result
        })
    
    # Summary
    results["summary"] = {
        "total_videos": len(ONLINE_VIDEOS),
        "successful": success_count,
        "failed": len(ONLINE_VIDEOS) - success_count
    }
    
    # Speichern
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 70)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Erfolgreich: {success_count}/{len(ONLINE_VIDEOS)}")
    print(f"\n📋 UPDATED FIELDS:")
    print(f"   • Title (optimized for SEO 2026)")
    print(f"   • Description (multilingual, 14 languages)")
    print(f"   • Tags (international keywords)")
    print(f"   • Category (News & Politics)")
    print(f"\n💾 Result: {RESULT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
