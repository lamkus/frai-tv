#!/usr/bin/env python3
"""
FIX BETTY BOOP TITEL - Alle auf <70 Zeichen kürzen
YouTube 2026 Algo Compliance

56 Videos betroffen!
"""

import json
import os
import sys
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# === CONFIG ===
OAUTH_FILE = 'config/youtube_oauth.json'
AUDIT_FILE = 'config/full_audit_2026_02.json'
DRY_RUN = '--apply' not in sys.argv

def load_credentials():
    with open(OAUTH_FILE, 'r') as f:
        token_data = json.load(f)
    return Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret')
    )

def shorten_betty_boop_title(title):
    """
    Kürzt Betty Boop Titel auf max 70 Zeichen
    
    Aktuelle Formate:
    - Betty Boop: Snow-White (1933) | Fleischer Studios | 8K | @remAIke_IT (73)
    - Betty Boop: Minnie the Moocher (1932) | 8K HQ | @remAIke_IT (56) ✅
    
    Ziel-Format:
    - Betty Boop: [Title] ([Year]) | 8K | @remAIke_IT
    """
    
    # Bereits OK?
    if len(title) <= 70:
        return title, False
    
    # Parse Titel
    # Pattern: Betty Boop: [Name] (Year) | [stuff] | [more stuff]
    match = re.match(
        r'^(Betty Boop[:\s]+)([^(]+)\((\d{4})\)\s*\|(.+)$',
        title,
        re.IGNORECASE
    )
    
    if match:
        prefix = "Betty Boop: "
        episode_name = match.group(2).strip()
        year = match.group(3)
        rest = match.group(4).strip()
        
        # Ziel: Betty Boop: [Name] (Year) | 8K | @remAIke_IT
        new_title = f"{prefix}{episode_name} ({year}) | 8K | @remAIke_IT"
        
        # Falls immer noch zu lang, Episode-Name kürzen
        if len(new_title) > 70:
            max_name_len = 70 - len(f"{prefix} ({year}) | 8K | @remAIke_IT") - 1
            episode_name = episode_name[:max_name_len].rstrip()
            new_title = f"{prefix}{episode_name} ({year}) | 8K | @remAIke_IT"
        
        return new_title, True
    
    # Fallback: Einfaches Kürzen
    # Entferne "Fleischer Studios |" oder "8K HQ" → "8K"
    new_title = title
    new_title = re.sub(r'\|\s*Fleischer Studios\s*', '| ', new_title)
    new_title = re.sub(r'\|\s*8K HQ\s*', '| 8K ', new_title)
    new_title = re.sub(r'\s+', ' ', new_title).strip()
    
    # Immer noch zu lang? Härter kürzen
    if len(new_title) > 70:
        # Entferne alles außer Name + Year + 8K + @remAIke_IT
        new_title = re.sub(r'\|[^|]+\|', '|', new_title)
        new_title = re.sub(r'\s+', ' ', new_title).strip()
    
    if len(new_title) > 70:
        new_title = new_title[:67] + "..."
    
    return new_title, title != new_title


def main():
    print("=" * 70)
    print("🎀 BETTY BOOP TITEL FIXER")
    print("=" * 70)
    
    if DRY_RUN:
        print("\n⚠️  DRY RUN MODE - Keine Änderungen!")
        print("    Für echte Updates: python script.py --apply\n")
    else:
        print("\n🔴 LIVE MODE - Änderungen werden gespeichert!\n")
    
    # Lade Audit-Daten
    with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
        audit = json.load(f)
    
    betty_videos = audit.get('long_titles_detail', {}).get('Betty Boop', [])
    
    if not betty_videos:
        print("❌ Keine Betty Boop Videos mit langen Titeln gefunden!")
        return
    
    print(f"📊 {len(betty_videos)} Betty Boop Videos mit Titeln >70 chars\n")
    
    # Analysiere und plane Fixes
    fixes = []
    for v in betty_videos:
        old_title = v['title']
        new_title, changed = shorten_betty_boop_title(old_title)
        
        if changed:
            fixes.append({
                'id': v['id'],
                'old_title': old_title,
                'old_len': len(old_title),
                'new_title': new_title,
                'new_len': len(new_title)
            })
            
            status = "✅" if len(new_title) <= 70 else "⚠️"
            print(f"{status} [{v['id']}]")
            print(f"   ALT ({len(old_title)}): {old_title}")
            print(f"   NEU ({len(new_title)}): {new_title}")
            print()
    
    # Zusammenfassung
    print("=" * 70)
    print(f"📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    print(f"   Zu fixen:        {len(fixes)}")
    print(f"   Bereits OK:      {len(betty_videos) - len(fixes)}")
    
    ok_count = sum(1 for f in fixes if f['new_len'] <= 70)
    print(f"   Nach Fix <=70:   {ok_count}")
    print(f"   Nach Fix >70:    {len(fixes) - ok_count}")
    
    if not DRY_RUN and fixes:
        print("\n🔄 Starte API Updates...")
        
        creds = load_credentials()
        youtube = build('youtube', 'v3', credentials=creds)
        
        success = 0
        errors = 0
        
        for fix in fixes:
            try:
                # Hole aktuelles Video
                video = youtube.videos().list(
                    part='snippet',
                    id=fix['id']
                ).execute()
                
                if not video.get('items'):
                    print(f"   ❌ {fix['id']}: Video nicht gefunden")
                    errors += 1
                    continue
                
                # Update Titel
                snippet = video['items'][0]['snippet']
                snippet['title'] = fix['new_title']
                
                youtube.videos().update(
                    part='snippet',
                    body={
                        'id': fix['id'],
                        'snippet': {
                            'title': fix['new_title'],
                            'description': snippet['description'],
                            'tags': snippet.get('tags', []),
                            'categoryId': snippet['categoryId']
                        }
                    }
                ).execute()
                
                print(f"   ✅ {fix['id']}: Titel aktualisiert")
                success += 1
                
            except Exception as e:
                print(f"   ❌ {fix['id']}: {str(e)[:50]}")
                errors += 1
        
        print(f"\n✅ Erfolgreich: {success}")
        print(f"❌ Fehler:      {errors}")
    
    # Speichere Plan
    plan_file = 'config/betty_boop_title_fixes.json'
    with open(plan_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(betty_videos),
            'to_fix': len(fixes),
            'fixes': fixes
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Plan gespeichert: {plan_file}")


if __name__ == '__main__':
    main()
