#!/usr/bin/env python3
"""Analysiere Soundies für YouTube Music Optimierung."""
import json, sys, io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth laden
oauth = json.loads(Path('config/youtube_oauth.json').read_text(encoding='utf-8'))
creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Soundies laden
data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))
soundies = [v for v in data['videos'] if 'soundie' in v['snippet']['title'].lower()]

print("=" * 70)
print("🎵 YOUTUBE MUSIC OPTIMIERUNG - SOUNDIES")
print("=" * 70)

# YouTube Music Anforderungen:
# 1. Category: Music (10)
# 2. "Official Audio" / "Music Video" in Tags
# 3. Artist + Song Title klar im Titel
# 4. Music Category im Upload

print("\n📋 YOUTUBE MUSIC REQUIREMENTS CHECK:\n")

issues_by_video = []

for s in soundies[:10]:
    vid = s['id']
    title = s['snippet']['title']
    category = s['snippet'].get('categoryId', 'unknown')
    tags = s['snippet'].get('tags', [])
    
    print(f"🎵 {title[:55]}...")
    print(f"   Category ID: {category} {'✅ Music' if category == '10' else '❌ NICHT Music!'}")
    
    # Check wichtige Tags
    tag_lower = ' '.join(tags).lower()
    checks = {
        'official audio': 'official audio' in tag_lower,
        'music video': 'music video' in tag_lower,
        'soundie': 'soundie' in tag_lower,
        'jazz/swing': 'jazz' in tag_lower or 'swing' in tag_lower,
    }
    
    for check, passed in checks.items():
        status = '✅' if passed else '❌'
        print(f"   {status} {check}")
    
    if category != '10':
        issues_by_video.append({
            'id': vid,
            'title': title,
            'current_category': category,
            'fix': 'Change to category 10 (Music)'
        })
    print()

print("=" * 70)
print("🔧 HAUPTPROBLEM IDENTIFIZIERT")
print("=" * 70)

if issues_by_video:
    print(f"\n❌ {len(issues_by_video)} Videos NICHT in Category 'Music' (10)")
    print("   → YouTube Music indexiert nur Videos mit Category 10!")
    print("\n   FIX: Category auf 'Music' ändern für alle Soundies")
else:
    print("\n✅ Alle Soundies in Music Category")

# Speichern
Path('config/soundies_music_issues.json').write_text(
    json.dumps(issues_by_video, ensure_ascii=False, indent=2), 
    encoding='utf-8'
)
print(f"\n💾 Issues gespeichert: config/soundies_music_issues.json")
