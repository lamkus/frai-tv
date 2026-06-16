#!/usr/bin/env python3
"""
AUDIT: Was habe ich heute kaputt gemacht?
Prüft ALLE Tags die ich vergeben habe.
"""
import os
import sys
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# OAuth laden
oauth_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'youtube_oauth.json')
with open(oauth_path, 'r') as f:
    oauth_data = json.load(f)

creds = Credentials(
    token=oauth_data['token'],
    refresh_token=oauth_data['refresh_token'],
    token_uri=oauth_data['token_uri'],
    client_id=oauth_data['client_id'],
    client_secret=oauth_data['client_secret']
)

youtube = build('youtube', 'v3', credentials=creds)

# Videos die ich heute geändert habe
CHANGED_VIDEOS = [
    # BraveStarr
    'XU7yM4H5vrY',  # Musikfestival
    'EaOwzlJuQJU',  # E02 Draft  
    '5qhJxQk89vE',  # E04 Draft
    
    # Shorts
    'Y7YQf5F_xw4',
    '_wWo_2l-zn8',
    'j2WQjj-b4F4', 
    '2QO4ZYLV4wk',
    'xKjvTL1F6dM',
]

# Problematische Tags
BAD_TAGS = [
    'sex', 'sexy', 'nude', 'naked', 'porn', 'xxx', 'adult', 'erotic',
    'tits', 'boobs', 'ass', 'fuck', 'shit', 'breast', 'bikini',
    'violence', 'gore', 'blood', 'kill', 'murder', 'death', 'brutal',
    'drug', 'cocaine', 'weed', 'marijuana', 'alcohol', 'beer', 'wine', 'vodka',
    'gun', 'weapon', 'shoot', 'terror', 'bomb',
    # German  
    'nackt', 'erotik', 'gewalt', 'blut', 'tod', 'drogen', 'waffe', 'brust',
    'krieg', 'mord', 'töten'
]

print("=" * 70)
print("🔍 TAG-AUDIT: Prüfe alle meine Änderungen")
print("=" * 70)
print()

problems = []
all_results = []

for vid in CHANGED_VIDEOS:
    try:
        response = youtube.videos().list(
            part='snippet,status',
            id=vid
        ).execute()
        
        if not response.get('items'):
            print(f"⚠️  {vid}: Nicht gefunden oder gelöscht")
            continue
            
        item = response['items'][0]
        snippet = item['snippet']
        status = item['status']
        
        title = snippet.get('title', 'N/A')
        tags = snippet.get('tags', [])
        privacy = status.get('privacyStatus', 'unknown')
        
        print(f"📹 {vid}")
        print(f"   Titel: {title}")
        print(f"   Status: {privacy}")
        print(f"   Tags ({len(tags)}): {tags}")
        
        # Prüfe auf problematische Tags
        bad_found = []
        for tag in tags:
            tag_lower = tag.lower()
            for bad in BAD_TAGS:
                if bad in tag_lower:
                    bad_found.append(f"{tag} (matched: {bad})")
                    break
        
        if bad_found:
            print(f"   ❌ PROBLEMATISCH: {bad_found}")
            problems.append({
                'id': vid,
                'title': title,
                'bad_tags': bad_found,
                'all_tags': tags
            })
        else:
            print(f"   ✅ OK")
        
        all_results.append({
            'id': vid,
            'title': title,
            'privacy': privacy,
            'tags': tags,
            'tag_count': len(tags)
        })
        
        print()
        
    except Exception as e:
        print(f"❌ {vid}: Fehler - {e}")
        print()

print("=" * 70)
print("📊 ZUSAMMENFASSUNG")
print("=" * 70)
print()

total_tags = sum(r['tag_count'] for r in all_results)
print(f"📈 Geprüfte Videos: {len(all_results)}")
print(f"📈 Gesamt Tags geprüft: {total_tags}")
print()

if problems:
    print("❌ PROBLEME GEFUNDEN:")
    for p in problems:
        print(f"   - {p['id']}: {p['title']}")
        print(f"     Bad: {p['bad_tags']}")
    print()
    print("⚠️  Diese Tags sollten SOFORT entfernt werden!")
else:
    print("✅ Keine offensichtlich unangemessenen Tags gefunden.")

# Report speichern
report = {
    'audit_date': '2026-01-13',
    'videos_checked': len(all_results),
    'total_tags': total_tags,
    'results': all_results,
    'problems': problems
}

with open('config/tag_audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print()
print("📄 Vollständiger Report: config/tag_audit_report.json")
