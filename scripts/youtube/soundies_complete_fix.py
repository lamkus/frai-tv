#!/usr/bin/env python3
"""
Soundies Complete Fix - Category → Music (10) + Add CTAs
"""
import json, sys, io, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth
creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
youtube = build('youtube', 'v3', credentials=creds)

# CTA Block for Music
MUSIC_CTA = """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎵 Love vintage music? Don't miss out:
👍 LIKE for more classic tunes!
💬 COMMENT your favorite era of music!
🔔 SUBSCRIBE for daily vintage music!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at: https://www.frai.tv | @remAIke_IT

#Soundie #VintageMusic #1940s #Jazz #Swing #JukeboxMusic #PublicDomain #8K #remAIke"""

DRY_RUN = '--apply' not in sys.argv

# Load current data
data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))
soundies = [v for v in data['public_videos'] if 'soundie' in v['snippet'].get('title','').lower()]

print('=' * 70)
print('🎵 SOUNDIES COMPLETE FIX - Category + CTAs')
print('=' * 70)
print(f"Mode: {'🧪 DRY RUN' if DRY_RUN else '⚡ APPLYING'}")
print(f"Total Soundies: {len(soundies)}")

# Find ones that need fixing
to_fix = []
for s in soundies:
    vid = s['id']
    cat = s['snippet'].get('categoryId', '')
    desc = s['snippet'].get('description', '')
    
    needs_category = cat != '10'
    needs_cta = 'SUBSCRIBE' not in desc.upper()
    
    if needs_category or needs_cta:
        to_fix.append({
            'id': vid,
            'title': s['snippet'].get('title', ''),
            'needs_category': needs_category,
            'needs_cta': needs_cta,
            'current_cat': cat
        })

print(f"Need fixing: {len(to_fix)}")
print(f"  - Category fix: {len([t for t in to_fix if t['needs_category']])}")
print(f"  - CTA fix: {len([t for t in to_fix if t['needs_cta']])}")
print()

fixed = []
errors = []

if DRY_RUN:
    print('-' * 70)
    print('🧪 DRY RUN - First 5 changes:')
    print('-' * 70)
    for t in to_fix[:5]:
        print(f"\n📹 {t['title'][:50]}...")
        print(f"   ID: {t['id']}")
        if t['needs_category']:
            print(f"   📁 Category: {t['current_cat']} → 10 (Music)")
        if t['needs_cta']:
            print(f"   📝 Add CTA block")
    
    print(f"\n\n💡 Run with --apply to fix all {len(to_fix)} videos")
    print(f"   Estimated quota: ~{len(to_fix) * 50} units")

else:
    print('-' * 70)
    print('⚡ APPLYING FIXES...')
    print('-' * 70)
    
    for i, t in enumerate(to_fix):
        vid = t['id']
        print(f"\n[{i+1}/{len(to_fix)}] {t['title'][:45]}...")
        
        try:
            # Get current video data
            resp = youtube.videos().list(part='snippet', id=vid).execute()
            if not resp['items']:
                print("   ⚠️ Video not found")
                continue
            
            snippet = resp['items'][0]['snippet']
            changes = []
            
            # Fix category
            if t['needs_category']:
                snippet['categoryId'] = '10'
                changes.append('Category→Music')
            
            # Add CTA
            if t['needs_cta']:
                desc = snippet.get('description', '')
                if 'SUBSCRIBE' not in desc.upper():
                    snippet['description'] = desc.rstrip() + MUSIC_CTA
                    changes.append('CTA added')
            
            if changes:
                youtube.videos().update(
                    part='snippet',
                    body={'id': vid, 'snippet': snippet}
                ).execute()
                print(f"   ✅ {', '.join(changes)}")
                fixed.append({'id': vid, 'changes': changes})
                time.sleep(0.5)
            else:
                print("   ℹ️ No changes needed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            errors.append({'id': vid, 'error': str(e)})

# Save results
result = {
    'date': '2026-01-14',
    'dry_run': DRY_RUN,
    'total_soundies': len(soundies),
    'needed_fix': len(to_fix),
    'fixed': fixed,
    'errors': errors
}
Path('config/soundies_fix_complete.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)

print('\n' + '=' * 70)
print('📊 ZUSAMMENFASSUNG:')
print('=' * 70)
print(f"  ✅ Fixed: {len(fixed)}")
print(f"  ❌ Errors: {len(errors)}")
print(f"  💾 Saved: config/soundies_fix_complete.json")
