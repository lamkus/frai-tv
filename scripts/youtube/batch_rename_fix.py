#!/usr/bin/env python3
"""
Batch Rename Fix - Korrigiert alle Titel nach SEO-Regeln

Fixes:
1. "8K" → "8K HQ" (wo nur 8K steht)
2. Fehlendes @remAIke_IT hinzufügen
3. Konsistente Formatierung

Format-Ziel: [Content] ([Jahr]) | 8K HQ | @remAIke_IT
"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import sys

# Lade OAuth
with open('config/youtube_oauth.json', encoding='utf-8') as f:
    oauth = json.load(f)

creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri=oauth['token_uri'],
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret'],
)
youtube = build('youtube', 'v3', credentials=creds)

def fix_title(title):
    """Korrigiert einen Titel nach SEO-Regeln"""
    original = title
    
    # Fix 1: "8K" am Anfang → ans Ende verschieben mit "| 8K HQ |"
    if title.startswith('8K '):
        title = title[3:]  # Entferne "8K " am Anfang
        # Füge 8K HQ am Ende hinzu (vor @remAIke_IT falls vorhanden)
        if '@remAIke_IT' in title:
            title = title.replace('| @remAIke_IT', '| 8K HQ | @remAIke_IT')
            title = title.replace(' @remAIke_IT', ' | 8K HQ | @remAIke_IT')
        else:
            title = title.rstrip() + ' | 8K HQ | @remAIke_IT'
    
    # Fix 2: "| 8K |" oder "| 8K" → "| 8K HQ |"
    title = re.sub(r'\|\s*8K\s*\|', '| 8K HQ |', title)
    title = re.sub(r'\|\s*8K\s*$', '| 8K HQ |', title)
    title = re.sub(r'\|\s*8K\s*@', '| 8K HQ | @', title)
    
    # Fix 3: "8K|" ohne Space → "8K HQ |"
    title = re.sub(r'8K\|', '8K HQ |', title)
    
    # Fix 4: " 8K " in der Mitte → sicherstellen es ist "8K HQ"
    # Aber nicht "8K HQ" nochmal ändern
    if ' 8K ' in title and '8K HQ' not in title:
        title = title.replace(' 8K ', ' 8K HQ ')
    
    # Fix 5: "–8K" oder "-8K" → " | 8K HQ"
    title = re.sub(r'[–-]\s*8K\s*(Edition|Restoration)?', ' | 8K HQ', title, flags=re.IGNORECASE)
    
    # Fix 6: " in 8K" → " | 8K HQ"
    title = re.sub(r'\s+in\s+8K', ' | 8K HQ', title, flags=re.IGNORECASE)
    
    # Fix 7: Fehlende Branding hinzufügen
    if '@remAIke_IT' not in title:
        title = title.rstrip() + ' | @remAIke_IT'
    
    # Fix 8: "8K @remAIke_IT" → "8K HQ | @remAIke_IT"
    title = re.sub(r'8K\s+@remAIke_IT', '8K HQ | @remAIke_IT', title)
    
    # Fix 9: Doppelte Pipes entfernen
    title = re.sub(r'\|\s*\|', '|', title)
    
    # Fix 10: Spaces normalisieren
    title = re.sub(r'\s+', ' ', title)
    title = re.sub(r'\s*\|\s*', ' | ', title)
    
    # Fix 11: "@reAImastered 8 K" → "@remAIke_IT" (alter Branding-Fehler)
    title = re.sub(r'@reAImastered\s*8\s*K[^|]*', '', title)
    title = re.sub(r'\breAImastering\s*8\s*K[^|]*', '', title)
    
    # Fix 12: Trailing/Leading pipes entfernen
    title = title.strip(' |')
    
    # Sicherstellen dass @remAIke_IT am Ende ist
    if '@remAIke_IT' in title and not title.endswith('@remAIke_IT'):
        title = re.sub(r'\s*\|\s*@remAIke_IT\s*\|?', '', title)
        title = title.rstrip(' |') + ' | @remAIke_IT'
    
    # Max 100 Zeichen
    if len(title) > 100:
        # Kürze den Content-Teil
        suffix = ' | 8K HQ | @remAIke_IT'
        max_content = 100 - len(suffix)
        content = re.sub(r'\s*\|\s*8K.*$', '', title)
        title = content[:max_content].rstrip() + suffix
    
    return title if title != original else None

def get_video_details(video_id):
    """Holt aktuelle Video-Details"""
    result = youtube.videos().list(part='snippet', id=video_id).execute()
    if result['items']:
        return result['items'][0]['snippet']
    return None

def update_video_title(video_id, new_title, snippet):
    """Aktualisiert Video-Titel"""
    snippet['title'] = new_title
    
    youtube.videos().update(
        part='snippet',
        body={
            'id': video_id,
            'snippet': {
                'title': new_title,
                'description': snippet['description'],
                'tags': snippet.get('tags', []),
                'categoryId': snippet['categoryId']
            }
        }
    ).execute()

def main():
    # Lade Audit-Ergebnis
    with open('config/rename_audit_result.json', encoding='utf-8') as f:
        data = json.load(f)
    
    # Sammle alle zu fixenden Videos
    to_fix = []
    seen_ids = set()
    
    for v in data['issues']['inconsistent_8k']:
        if v['id'] not in seen_ids:
            to_fix.append(v)
            seen_ids.add(v['id'])
    
    for v in data['issues']['no_branding']:
        if v['id'] not in seen_ids:
            to_fix.append(v)
            seen_ids.add(v['id'])
    
    print(f"🔧 BATCH RENAME FIX")
    print(f"=" * 70)
    print(f"Videos zu fixen: {len(to_fix)}")
    print()
    
    # Zeige Vorschau
    fixes = []
    for v in to_fix:
        new_title = fix_title(v['title'])
        if new_title:
            fixes.append({
                'id': v['id'],
                'old': v['title'],
                'new': new_title
            })
            print(f"📺 {v['id']}")
            print(f"   ALT: {v['title']}")
            print(f"   NEU: {new_title}")
            print()
    
    print(f"=" * 70)
    print(f"Total Fixes: {len(fixes)}")
    print()
    
    # Prüfe ob --apply Flag gesetzt
    if '--apply' not in sys.argv:
        print("⚠️  DRY RUN - Keine Änderungen durchgeführt!")
        print("    Starte mit --apply um Änderungen anzuwenden")
        
        # Speichere Fix-Plan
        with open('config/rename_fix_plan.json', 'w', encoding='utf-8') as f:
            json.dump(fixes, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Fix-Plan gespeichert: config/rename_fix_plan.json")
        return
    
    # Apply fixes
    print("🚀 WENDE FIXES AN...")
    print()
    
    success = 0
    failed = []
    
    for fix in fixes:
        try:
            snippet = get_video_details(fix['id'])
            if snippet:
                update_video_title(fix['id'], fix['new'], snippet)
                print(f"✅ {fix['id']}: {fix['new'][:60]}...")
                success += 1
            else:
                print(f"❌ {fix['id']}: Video nicht gefunden")
                failed.append(fix)
        except Exception as e:
            print(f"❌ {fix['id']}: {str(e)[:50]}")
            failed.append(fix)
    
    print()
    print(f"=" * 70)
    print(f"✅ Erfolgreich: {success}")
    print(f"❌ Fehlgeschlagen: {len(failed)}")
    
    # Speichere Ergebnis
    result = {
        'date': datetime.now().isoformat(),
        'success': success,
        'failed': len(failed),
        'fixes': fixes,
        'errors': [f['id'] for f in failed]
    }
    
    with open('config/rename_fix_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Ergebnis gespeichert: config/rename_fix_result.json")

if __name__ == '__main__':
    main()
