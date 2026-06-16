#!/usr/bin/env python3
"""
FIX ALLE LANGEN TITEL - Universal Fixer
Behandelt: Alfred J. Kwak, Felix, Soundies, Other

102 Videos total, 56 Betty Boop separat
"""

import json
import os
import sys
import re
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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

def shorten_title(title, series):
    """Universal Title Shortener"""
    
    if len(title) <= 70:
        return title, False
    
    original = title
    
    # === ALFRED J. KWAK ===
    if series == 'Alfred J. Kwak':
        # Format: Alfred Jodokus Quack (14/52): Skrupellose Geschäfte | Deutsch | 8K HQ (4K UHD) | @remAIke_IT
        # Ziel:   Alfred J. Kwak E14: Skrupellose Geschäfte | 8K | @remAIke_IT
        
        match = re.match(r'Alfred\s+Jodokus\s+Quack\s+\((\d+)/\d+\):\s*([^|]+)\|.+', title)
        if match:
            ep_num = match.group(1)
            ep_name = match.group(2).strip()
            
            new_title = f"Alfred J. Kwak E{ep_num}: {ep_name} | 8K | @remAIke_IT"
            
            if len(new_title) > 70:
                max_len = 70 - len(f"Alfred J. Kwak E{ep_num}:  | 8K | @remAIke_IT")
                ep_name = ep_name[:max_len].rstrip()
                new_title = f"Alfred J. Kwak E{ep_num}: {ep_name} | 8K | @remAIke_IT"
            
            return new_title, True
    
    # === SOUNDIES ===
    elif series == 'Soundies':
        # Format: Louis Armstrong: Musical Review | Soundie (1940s) | 8K HQ | @remAIke_IT
        # Ziel:   Louis Armstrong: Musical Review | Soundie | 8K | @remAIke_IT
        
        # Entferne (1940s) und HQ
        new_title = re.sub(r'\s*\(1940s?\)\s*', ' ', title)
        new_title = re.sub(r'\|\s*8K HQ\s*\|', '| 8K |', new_title)
        new_title = re.sub(r'\s+', ' ', new_title).strip()
        
        if len(new_title) > 70:
            # Kürze Artist/Song
            match = re.match(r'([^:]+):\s*([^|]+)\|(.+)', new_title)
            if match:
                artist = match.group(1).strip()[:20]
                song = match.group(2).strip()[:25]
                rest = '| Soundie | 8K | @remAIke_IT'
                new_title = f"{artist}: {song} {rest}"
        
        return new_title, title != new_title
    
    # === FELIX THE CAT ===
    elif series == 'Felix':
        # Entferne überflüssige Infos
        new_title = re.sub(r'\|\s*8K HQ\s*\(4K UHD\)\s*\|', '| 8K |', title)
        new_title = re.sub(r'\|\s*8K HQ\s*\|', '| 8K |', new_title)
        new_title = re.sub(r'\s+', ' ', new_title).strip()
        
        if len(new_title) > 70:
            # Kürze auf Essentials
            match = re.match(r'Felix[^:]*:\s*([^(]+)\((\d{4})\)', new_title)
            if match:
                ep_name = match.group(1).strip()[:30]
                year = match.group(2)
                new_title = f"Felix the Cat: {ep_name} ({year}) | 8K | @remAIke_IT"
        
        return new_title, title != new_title
    
    # === OTHER ===
    else:
        # Generische Kürzung
        new_title = re.sub(r'\|\s*8K HQ\s*\(4K UHD\)\s*\|', '| 8K |', title)
        new_title = re.sub(r'\|\s*8K HQ\s*\|', '| 8K |', new_title)
        new_title = re.sub(r'\|\s*Best Online Version\s*', '', new_title)
        new_title = re.sub(r'\s+', ' ', new_title).strip()
        
        # Wenn immer noch zu lang, brutal kürzen
        if len(new_title) > 70:
            # Behalte Anfang und Ende
            new_title = new_title[:67] + "..."
        
        return new_title, title != new_title


def main():
    print("=" * 70)
    print("🔧 UNIVERSAL TITEL FIXER")
    print("=" * 70)
    
    if DRY_RUN:
        print("\n⚠️  DRY RUN MODE - Keine Änderungen!")
        print("    Für echte Updates: python script.py --apply\n")
    else:
        print("\n🔴 LIVE MODE - Änderungen werden gespeichert!\n")
    
    # Lade Audit-Daten
    with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
        audit = json.load(f)
    
    long_titles = audit.get('long_titles_detail', {})
    
    all_fixes = []
    
    # Prozessiere jede Serie (außer Betty Boop - separates Script)
    for series in ['Alfred J. Kwak', 'Soundies', 'Felix', 'Other']:
        videos = long_titles.get(series, [])
        
        if not videos:
            continue
        
        print(f"\n{'='*40}")
        print(f"📺 {series}: {len(videos)} Videos")
        print('='*40)
        
        for v in videos:
            old_title = v['title']
            new_title, changed = shorten_title(old_title, series)
            
            if changed:
                fix = {
                    'id': v['id'],
                    'series': series,
                    'old_title': old_title,
                    'old_len': len(old_title),
                    'new_title': new_title,
                    'new_len': len(new_title)
                }
                all_fixes.append(fix)
                
                status = "✅" if len(new_title) <= 70 else "⚠️"
                print(f"\n{status} [{v['id']}]")
                print(f"   ALT ({len(old_title)}): {old_title[:70]}...")
                print(f"   NEU ({len(new_title)}): {new_title}")
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("📋 ZUSAMMENFASSUNG")
    print("=" * 70)
    
    by_series = {}
    for fix in all_fixes:
        s = fix['series']
        by_series[s] = by_series.get(s, 0) + 1
    
    for s, count in by_series.items():
        print(f"   {s}: {count}")
    
    print(f"\n   TOTAL: {len(all_fixes)} zu fixen")
    
    ok_count = sum(1 for f in all_fixes if f['new_len'] <= 70)
    print(f"   Nach Fix <=70: {ok_count}")
    print(f"   Nach Fix >70:  {len(all_fixes) - ok_count}")
    
    # API Updates
    if not DRY_RUN and all_fixes:
        print("\n🔄 Starte API Updates...")
        
        creds = load_credentials()
        youtube = build('youtube', 'v3', credentials=creds)
        
        success = 0
        errors = 0
        
        for fix in all_fixes:
            try:
                video = youtube.videos().list(
                    part='snippet',
                    id=fix['id']
                ).execute()
                
                if not video.get('items'):
                    print(f"   ❌ {fix['id']}: nicht gefunden")
                    errors += 1
                    continue
                
                snippet = video['items'][0]['snippet']
                
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
                
                print(f"   ✅ {fix['id']}: OK")
                success += 1
                
            except Exception as e:
                print(f"   ❌ {fix['id']}: {str(e)[:50]}")
                errors += 1
        
        print(f"\n✅ Erfolgreich: {success}")
        print(f"❌ Fehler: {errors}")
    
    # Speichere Plan
    with open('config/other_title_fixes.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(all_fixes),
            'by_series': by_series,
            'fixes': all_fixes
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Plan gespeichert: config/other_title_fixes.json")


if __name__ == '__main__':
    main()
