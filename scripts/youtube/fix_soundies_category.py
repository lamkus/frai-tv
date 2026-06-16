#!/usr/bin/env python3
"""Fixe alle Soundies: Category auf Music (10) setzen."""
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

# Nur die mit falscher Category
to_fix = [s for s in soundies if s['snippet'].get('categoryId') != '10']

print("=" * 70)
print("🎵 SOUNDIES CATEGORY FIX → Music (10)")
print("=" * 70)
print(f"\nZu fixen: {len(to_fix)} Videos")
print(f"Quota-Kosten: {len(to_fix) * 50} Units")
print()

fixed = 0
errors = []

for s in to_fix:
    vid = s['id']
    title = s['snippet']['title']
    
    print(f"🔧 {title[:50]}...")
    
    try:
        # Snippet aktualisieren
        snippet = s['snippet'].copy()
        snippet['categoryId'] = '10'  # Music
        
        youtube.videos().update(
            part='snippet',
            body={
                'id': vid,
                'snippet': snippet
            }
        ).execute()
        
        print(f"   ✅ Category → Music (10)")
        fixed += 1
        
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        errors.append({'id': vid, 'title': title, 'error': str(e)})

print("\n" + "=" * 70)
print("📊 ERGEBNIS")
print("=" * 70)
print(f"✅ Erfolgreich: {fixed}/{len(to_fix)}")
print(f"❌ Fehler: {len(errors)}")
print(f"💰 Quota verwendet: ~{fixed * 50} Units")

if errors:
    print("\nFehler:")
    for e in errors:
        print(f"  - {e['title'][:40]}: {e['error'][:50]}")

# Ergebnis speichern
result = {
    'fixed': fixed,
    'total': len(to_fix),
    'errors': errors,
    'quota_used': fixed * 50
}
Path('config/soundies_category_fix_result.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), 
    encoding='utf-8'
)
print(f"\n💾 Ergebnis: config/soundies_category_fix_result.json")
