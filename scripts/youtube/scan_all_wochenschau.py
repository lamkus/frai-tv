#!/usr/bin/env python3
"""
🔍 SCAN ALL WOCHENSCHAU VIDEOS ON CHANNEL
=========================================
Step 1: Finde alle Wochenschau-Videos online
Step 2: Extrahiere Nummer aus Titel
Step 3: Vergleiche mit Datenbank
Step 4: Update alle mit korrekten SEO-Daten
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
SCAN_RESULT = os.path.join(BASE_DIR, "config", "wochenschau_online_scan.json")

UPLOAD_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

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

def extract_number(title):
    """Extrahiere Wochenschau-Nummer aus Titel"""
    # Pattern: "Wochenschau 459" oder "Nr. 459" oder "#459"
    patterns = [
        r'[Ww]ochenschau\s*[#]?(\d{3})',
        r'[Nn]r\.?\s*(\d{3})',
        r'[Nn]ewsreel\s*[#]?(\d{3})',
        r'#(\d{3})',
        r'\s(\d{3})[\s:\-]'
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return match.group(1)
    return None

def main():
    print("=" * 70)
    print("🔍 SCANNING ALL WOCHENSCHAU VIDEOS ON CHANNEL")
    print("=" * 70)
    
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Lade SEO-Datenbank
    with open(DATABASE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Alle Videos vom Channel holen
    print("\n📡 Fetching all videos from channel...")
    all_videos = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='snippet',
            playlistId=UPLOAD_PLAYLIST,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response['items']:
            vid = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            all_videos.append({'id': vid, 'title': title})
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    print(f"   Total videos on channel: {len(all_videos)}")
    
    # Wochenschau-Videos filtern
    wochenschau_keywords = ['wochenschau', 'newsreel', 'deutsche wochenschau']
    wochenschau = []
    
    for v in all_videos:
        title_lower = v['title'].lower()
        if any(kw in title_lower for kw in wochenschau_keywords):
            nr = extract_number(v['title'])
            v['nr'] = nr
            v['has_seo'] = nr in db['videos'] if nr else False
            wochenschau.append(v)
    
    print(f"   Wochenschau videos found: {len(wochenschau)}")
    
    # Sortieren nach Nummer
    wochenschau_sorted = sorted(wochenschau, key=lambda x: int(x['nr']) if x['nr'] else 9999)
    
    # Analyse
    with_nr = [v for v in wochenschau_sorted if v['nr']]
    without_nr = [v for v in wochenschau_sorted if not v['nr']]
    with_seo = [v for v in with_nr if v['has_seo']]
    
    print(f"\n📊 ANALYSIS:")
    print(f"   Videos with extracted number: {len(with_nr)}")
    print(f"   Videos without number (manual check): {len(without_nr)}")
    print(f"   Videos with SEO data available: {len(with_seo)}")
    
    # Liste
    print(f"\n" + "=" * 70)
    print("📋 ALL WOCHENSCHAU VIDEOS ONLINE:")
    print("-" * 70)
    
    for v in wochenschau_sorted:
        nr = v['nr'] or '???'
        seo_status = "✅" if v.get('has_seo') else "❌"
        print(f"   Nr.{nr:>4} | {seo_status} | {v['id']} | {v['title'][:50]}")
    
    if without_nr:
        print(f"\n⚠️  VIDEOS WITHOUT EXTRACTED NUMBER:")
        for v in without_nr:
            print(f"   {v['id']}: {v['title']}")
    
    # Nummern-Bereich ermitteln
    numbers = [int(v['nr']) for v in with_nr if v['nr']]
    if numbers:
        print(f"\n📈 NUMBER RANGE: {min(numbers)} - {max(numbers)}")
        print(f"   Total unique numbers: {len(set(numbers))}")
        
        # Fehlende Nummern im Bereich
        all_expected = set(range(min(numbers), max(numbers) + 1))
        found = set(numbers)
        missing = all_expected - found
        if missing and len(missing) < 50:
            print(f"   Missing in range: {sorted(missing)}")
    
    # Speichern
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_channel_videos": len(all_videos),
        "wochenschau_count": len(wochenschau),
        "with_number": len(with_nr),
        "with_seo": len(with_seo),
        "number_range": {"min": min(numbers) if numbers else 0, "max": max(numbers) if numbers else 0},
        "videos": wochenschau_sorted
    }
    
    with open(SCAN_RESULT, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved: {SCAN_RESULT}")
    print("=" * 70)
    
    return wochenschau_sorted

if __name__ == "__main__":
    main()
