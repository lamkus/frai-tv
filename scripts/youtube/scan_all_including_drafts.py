#!/usr/bin/env python3
"""
🔍 SCAN ALL VIDEOS INCLUDING DRAFTS
===================================
Findet auch Entwürfe und private Videos
"""

import json
import os
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OAUTH_FILE = os.path.join(BASE_DIR, "config", "youtube_oauth.json")
DATABASE = os.path.join(BASE_DIR, "config", "wochenschau_complete_upload_database.json")
OUTPUT = os.path.join(BASE_DIR, "config", "wochenschau_full_scan.json")

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
    patterns = [
        r'[Ww]ochenschau\s*[#]?(\d{3})',
        r'[Nn]r\.?\s*(\d{3})',
        r'^[Nn]r(\d{3})',
        r'#(\d{3})',
    ]
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return match.group(1)
    return None

def main():
    print("=" * 70)
    print("🔍 FULL SCAN - INCLUDING DRAFTS & PRIVATE")
    print("=" * 70)
    
    creds = load_credentials()
    youtube = build('youtube', 'v3', credentials=creds)
    
    # Lade SEO-Datenbank
    with open(DATABASE, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    # Alle Videos aus Upload-Playlist
    print("\n📡 Fetching ALL videos from upload playlist...")
    all_videos = []
    next_page = None
    
    while True:
        response = youtube.playlistItems().list(
            part='snippet,status',
            playlistId=UPLOAD_PLAYLIST,
            maxResults=50,
            pageToken=next_page
        ).execute()
        
        for item in response['items']:
            vid = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            status = item.get('status', {}).get('privacyStatus', 'unknown')
            all_videos.append({
                'id': vid, 
                'title': title, 
                'status': status,
                'published': item['snippet'].get('publishedAt', '')
            })
        
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    
    print(f"   Total videos on channel: {len(all_videos)}")
    
    # Filter auf Wochenschau (inkl. "NrXXX" Drafts)
    wochenschau = []
    for v in all_videos:
        title_lower = v['title'].lower()
        nr = extract_number(v['title'])
        
        if nr or 'wochenschau' in title_lower or title_lower.startswith('nr'):
            v['nr'] = nr
            v['has_seo'] = nr in db['videos'] if nr else False
            wochenschau.append(v)
    
    # Nach Nummer sortieren
    wochenschau_sorted = sorted(wochenschau, key=lambda x: int(x['nr']) if x.get('nr') else 9999)
    
    # Statistiken
    public = [v for v in wochenschau_sorted if v['status'] == 'public']
    private = [v for v in wochenschau_sorted if v['status'] == 'private']
    unlisted = [v for v in wochenschau_sorted if v['status'] == 'unlisted']
    drafts = [v for v in wochenschau_sorted if v['status'] not in ['public', 'private', 'unlisted']]
    
    print(f"\n📊 WOCHENSCHAU VIDEOS FOUND: {len(wochenschau)}")
    print(f"   🌐 Public: {len(public)}")
    print(f"   🔒 Private: {len(private)}")
    print(f"   🔗 Unlisted: {len(unlisted)}")
    print(f"   📝 Drafts/Other: {len(drafts)}")
    
    # Liste alle
    print(f"\n" + "=" * 70)
    print("📋 ALL WOCHENSCHAU VIDEOS (inkl. Drafts):")
    print("-" * 70)
    
    status_icons = {
        'public': '🌐',
        'private': '🔒',
        'unlisted': '🔗',
        'unknown': '📝'
    }
    
    for v in wochenschau_sorted:
        nr = v.get('nr') or '???'
        icon = status_icons.get(v['status'], '📝')
        seo = "✅" if v.get('has_seo') else "❌"
        title_short = v['title'][:45]
        print(f"   Nr.{nr:>4} | {icon} {seo} | {v['id']} | {title_short}")
    
    # Videos die SEO brauchen
    needs_seo = [v for v in wochenschau_sorted if v.get('nr') and v.get('has_seo') and v['status'] in ['public', 'private']]
    print(f"\n✅ Videos mit SEO-Daten verfügbar: {len(needs_seo)}")
    
    # Speichern
    result = {
        "total": len(all_videos),
        "wochenschau": len(wochenschau),
        "public": len(public),
        "private": len(private),
        "videos": wochenschau_sorted
    }
    
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved: {OUTPUT}")
    print("=" * 70)

if __name__ == "__main__":
    main()
