#!/usr/bin/env python3
"""
🔄 UPDATE ALL WOCHENSCHAU VIDEOS WITH COMPLETE SEO
==================================================
Prüft jedes Video und updated Title, Description, Tags
"""

import json
import os
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
DATABASE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")
SCAN_FILE = os.path.join(BASE_DIR, "config", "wochenschau_online_scan.json")
RESULT_FILE = os.path.join(BASE_DIR, "config", "wochenschau_update_result.json")

def load_credentials():
    with open(OAUTH_FILE, 'r') as f:
        creds_data = json.load(f)
    return Credentials(
        token=creds_data['token'],
        refresh_token=creds_data['refresh_token'],
        token_uri=creds_data['token_uri'],
        client_id=creds_data['client_id'],
        client_secret=creds_data['client_secret']
    )

def needs_update(current_title, current_desc, target_title, target_desc):
    """Prüfe ob Update nötig ist"""
    # Title anders?
    if current_title.strip() != target_title.strip():
        return True, "title_different"
    # Description zu kurz? (unter 1500 = nicht vollständig)
    if len(current_desc) < 1500:
        return True, "desc_too_short"
    return False, "ok"

def main():
    print("=" * 70)
    print("🔄 UPDATE ALL WOCHENSCHAU VIDEOS WITH COMPLETE SEO")
    print("=" * 70)
    
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Laden
    with open(DATABASE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    with open(SCAN_FILE, 'r', encoding='utf-8') as f:
        scan = json.load(f)
    
    videos = [v for v in scan['videos'] if v.get('nr') and v.get('has_seo')]
    
    print(f"\n📋 Videos to check: {len(videos)}")
    print("-" * 70)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "updated": [],
        "skipped": [],
        "failed": [],
        "no_seo": []
    }
    
    for v in videos:
        nr = v['nr']
        video_id = v['id']
        
        seo = db['videos'].get(nr)
        if not seo:
            print(f"   ❌ Nr. {nr}: Keine SEO-Daten in DB")
            results['no_seo'].append({"nr": nr, "id": video_id})
            continue
        
        # Aktuellen Status von YouTube holen
        try:
            response = youtube.videos().list(
                part='snippet',
                id=video_id
            ).execute()
            
            if not response.get('items'):
                print(f"   ❌ Nr. {nr}: Video nicht gefunden")
                results['failed'].append({"nr": nr, "id": video_id, "error": "not_found"})
                continue
            
            snippet = response['items'][0]['snippet']
            current_title = snippet.get('title', '')
            current_desc = snippet.get('description', '')
            current_tags = snippet.get('tags', [])
            
            # Prüfen ob Update nötig
            needs, reason = needs_update(current_title, current_desc, seo['title'], seo['description'])
            
            if not needs:
                print(f"   ⏭️  Nr. {nr}: Bereits aktuell")
                results['skipped'].append({"nr": nr, "id": video_id})
                continue
            
            # Update durchführen
            snippet['title'] = seo['title']
            snippet['description'] = seo['description']
            snippet['tags'] = seo['tags'][:30]
            snippet['categoryId'] = seo['category_id']
            snippet['defaultLanguage'] = 'de'
            
            youtube.videos().update(
                part='snippet',
                body={'id': video_id, 'snippet': snippet}
            ).execute()
            
            print(f"   ✅ Nr. {nr}: UPDATED ({reason})")
            print(f"      Title: {seo['title'][:50]}...")
            print(f"      Desc: {len(current_desc)} → {len(seo['description'])} chars")
            print(f"      Tags: {len(current_tags)} → {len(seo['tags'])} tags")
            
            results['updated'].append({
                "nr": nr,
                "id": video_id,
                "reason": reason,
                "changes": {
                    "title": {"old": current_title, "new": seo['title']},
                    "desc_length": {"old": len(current_desc), "new": len(seo['description'])},
                    "tags_count": {"old": len(current_tags), "new": len(seo['tags'])}
                }
            })
            
        except Exception as e:
            print(f"   ❌ Nr. {nr}: ERROR - {str(e)[:50]}")
            results['failed'].append({"nr": nr, "id": video_id, "error": str(e)})
    
    # Summary
    print(f"\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"   ✅ Updated: {len(results['updated'])}")
    print(f"   ⏭️  Skipped (already ok): {len(results['skipped'])}")
    print(f"   ❌ Failed: {len(results['failed'])}")
    print(f"   ⚠️  No SEO data: {len(results['no_seo'])}")
    
    # Speichern
    with open(RESULT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Result: {RESULT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
