#!/usr/bin/env python3
"""
UPDATE 5 ONLINE WOCHENSCHAU VIDEOS MIT OPTIMIERTEN TITELN
==========================================================
Videos: Nr. 459, 468, 470, 471, 473

VORHER (91 chars):
"Die Deutsche Wochenschau Nr. 459 | 21.06.1939 | Germany WWII Newsreel | 8K HQ | @remAIke_IT"

NACHHER (~45 chars):
"Wochenschau 459: Pre-War Era (Jun 1939) | 8K"
"""

import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MASTER_TITLES = os.path.join(BASE_DIR, "config", "wochenschau_master_titles.json")
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
RESULT_FILE = os.path.join(BASE_DIR, "config", "title_update_result.json")

# Die 5 hochgeladenen Videos mit ALTEM Format (aktualisierte IDs aus Scan)
ONLINE_VIDEOS = {
    "459": "o33-c1riv4U",  # Die Deutsche Wochenschau Nr. 459 | 21.06.1939
    "468": "dAp7JFDhE3U",  # Die Deutsche Wochenschau Nr. 468 | 23.08.1939
    "470": "t-VIxJaWE74",  # Die Deutsche Wochenschau Nr. 470 | 06.09.1939
    "471": "9muRRAleqdA",  # Die Deutsche Wochenschau Nr. 471 | 13.09.1939
    "473": "3AtirtgrfUI"   # Die Deutsche Wochenschau Nr. 473 | 27.09.1939
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

def load_master_titles():
    """Lade Master-Titel"""
    with open(MASTER_TITLES, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_video_title(youtube, video_id, new_title, nr):
    """Update Video-Titel auf YouTube"""
    try:
        # Erst aktuellen Status holen
        response = youtube.videos().list(
            part='snippet,status',
            id=video_id
        ).execute()
        
        if not response.get('items'):
            return {"success": False, "error": "Video nicht gefunden"}
        
        video = response['items'][0]
        snippet = video['snippet']
        old_title = snippet['title']
        
        # Titel updaten
        snippet['title'] = new_title
        
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
            "old_title": old_title,
            "new_title": new_title,
            "old_length": len(old_title),
            "new_length": len(new_title),
            "savings": len(old_title) - len(new_title)
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=" * 70)
    print("🎬 UPDATE WOCHENSCHAU TITLES ON YOUTUBE")
    print("=" * 70)
    
    # Laden
    master = load_master_titles()
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "updates": [],
        "summary": {}
    }
    
    success_count = 0
    total_savings = 0
    
    print(f"\n📋 Updating {len(ONLINE_VIDEOS)} videos...")
    print("-" * 70)
    
    for nr, video_id in ONLINE_VIDEOS.items():
        title_data = master["titles"].get(nr, {})
        new_title = title_data.get("optimized_title", "")
        
        if not new_title:
            print(f"   ❌ Nr. {nr}: Kein Titel in Master gefunden!")
            continue
        
        print(f"\n   Nr. {nr} ({video_id}):")
        result = update_video_title(youtube, video_id, new_title, nr)
        
        if result["success"]:
            success_count += 1
            total_savings += result.get("savings", 0)
            print(f"   ✅ UPDATED!")
            print(f"      Vorher ({result['old_length']} chars): {result['old_title'][:50]}...")
            print(f"      Nachher ({result['new_length']} chars): {result['new_title']}")
            print(f"      Ersparnis: {result['savings']} chars")
        else:
            print(f"   ❌ FEHLER: {result.get('error')}")
        
        results["updates"].append({
            "nr": nr,
            "video_id": video_id,
            **result
        })
    
    # Summary
    results["summary"] = {
        "total_videos": len(ONLINE_VIDEOS),
        "successful": success_count,
        "failed": len(ONLINE_VIDEOS) - success_count,
        "total_chars_saved": total_savings,
        "avg_chars_saved": total_savings / success_count if success_count else 0
    }
    
    # Speichern
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n" + "=" * 70)
    print(f"📊 SUMMARY:")
    print(f"   ✅ Erfolgreich:    {success_count}/{len(ONLINE_VIDEOS)}")
    print(f"   📉 Chars gespart:  {total_savings} total")
    print(f"   📉 Ø pro Video:    {total_savings/success_count:.0f} chars" if success_count else "")
    print(f"\n💾 Result: {RESULT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
