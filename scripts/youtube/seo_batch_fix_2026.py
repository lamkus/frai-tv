#!/usr/bin/env python3
"""
SEO Batch Fix 2026 - Basierend auf YouTube Official Ranking Factors
Fixes: Missing CTAs, Missing Hashtags, Missing 8K Markers

QUOTA: ~50 units per video.update() - Max 100 videos = 5000 units
"""
import json, sys, io, os, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth für WRITE
creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
youtube = build('youtube', 'v3', credentials=creds)

# Audit-Daten laden
audit = json.loads(Path('config/seo_audit_2026.json').read_text(encoding='utf-8'))
scores = audit['all_scores']

# Standard CTA Block
CTA_BLOCK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 Enjoyed this video? Don't forget to:
👍 LIKE if you loved it!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more classic content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 More at: https://www.frai.tv | @remAIke_IT
"""

# Standard Hashtags
HASHTAGS = "\n\n#PublicDomain #VintageAnimation #ClassicCartoons #8K #remAIke"

DRY_RUN = '--apply' not in sys.argv
fixed = []
errors = []

print("=" * 70)
print("🔧 SEO BATCH FIX 2026 - YouTube Official Ranking Factors")
print("=" * 70)
print(f"Mode: {'🧪 DRY RUN' if DRY_RUN else '⚡ APPLYING CHANGES'}")
print()

# Finde Videos die Fixes brauchen
to_fix = []
for s in scores:
    needs_fix = False
    fixes_needed = []
    
    # Check for missing CTA
    if '⚠️ Desc: Kein CTA' in str(s['issues']):
        needs_fix = True
        fixes_needed.append('CTA')
    
    # Check for missing hashtags
    if '⚠️ Desc: Keine Hashtags' in str(s['issues']):
        needs_fix = True
        fixes_needed.append('Hashtags')
    
    # Check for missing 8K marker
    if '❌ Title: Kein 8K Marker' in str(s['issues']):
        needs_fix = True
        fixes_needed.append('8K Title')
    
    if needs_fix:
        to_fix.append({
            'id': s['id'],
            'title': s['title'],
            'score': s['score'],
            'fixes': fixes_needed
        })

print(f"📊 {len(to_fix)} Videos brauchen Fixes:\n")

# Gruppiere nach Fix-Typ
cta_needed = [v for v in to_fix if 'CTA' in v['fixes']]
hashtag_needed = [v for v in to_fix if 'Hashtags' in v['fixes']]
title_8k_needed = [v for v in to_fix if '8K Title' in v['fixes']]

print(f"  📝 Fehlende CTAs:     {len(cta_needed)}")
print(f"  #️⃣ Fehlende Hashtags: {len(hashtag_needed)}")
print(f"  🎬 Fehlende 8K Title: {len(title_8k_needed)}")

if DRY_RUN:
    print("\n" + "-" * 70)
    print("🧪 DRY RUN - Zeige erste 10 geplante Änderungen:")
    print("-" * 70)
    
    for v in to_fix[:10]:
        print(f"\n📹 {v['title'][:50]}...")
        print(f"   ID: {v['id']}")
        print(f"   Fixes: {', '.join(v['fixes'])}")
    
    print(f"\n\n💡 Zum Anwenden: python {sys.argv[0]} --apply")
    
else:
    print("\n" + "-" * 70)
    print("⚡ APPLYING FIXES...")
    print("-" * 70)
    
    # Nur Description-Fixes (CTA + Hashtags) - Title-Fixes sind riskanter
    desc_fixes = [v for v in to_fix if 'CTA' in v['fixes'] or 'Hashtags' in v['fixes']]
    
    for i, v in enumerate(desc_fixes[:50]):  # Max 50 pro Run
        vid = v['id']
        print(f"\n[{i+1}/{min(50, len(desc_fixes))}] {v['title'][:45]}...")
        
        try:
            # Aktuellen Stand holen
            resp = youtube.videos().list(part='snippet', id=vid).execute()
            if not resp['items']:
                print("   ⚠️ Video nicht gefunden")
                continue
            
            snippet = resp['items'][0]['snippet']
            desc = snippet.get('description', '')
            
            # Fixes anwenden
            new_desc = desc
            applied = []
            
            # CTA hinzufügen (wenn nicht vorhanden)
            if 'CTA' in v['fixes'] and 'SUBSCRIBE' not in desc.upper():
                new_desc = new_desc.rstrip() + CTA_BLOCK
                applied.append('CTA')
            
            # Hashtags hinzufügen (wenn nicht vorhanden)
            if 'Hashtags' in v['fixes'] and '#' not in desc:
                new_desc = new_desc.rstrip() + HASHTAGS
                applied.append('Hashtags')
            
            if applied:
                # Update
                snippet['description'] = new_desc
                youtube.videos().update(
                    part='snippet',
                    body={'id': vid, 'snippet': snippet}
                ).execute()
                
                print(f"   ✅ Fixed: {', '.join(applied)}")
                fixed.append({'id': vid, 'title': v['title'], 'fixes': applied})
                time.sleep(0.5)  # Rate limiting
            else:
                print("   ℹ️ Keine Änderung nötig")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            errors.append({'id': vid, 'error': str(e)})

# Ergebnis speichern
result = {
    'date': '2026-01-14',
    'dry_run': DRY_RUN,
    'total_needing_fix': len(to_fix),
    'fixed': fixed,
    'errors': errors,
    'breakdown': {
        'cta_needed': len(cta_needed),
        'hashtags_needed': len(hashtag_needed),
        'title_8k_needed': len(title_8k_needed)
    }
}
Path('config/seo_batch_fix_result.json').write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8'
)

print("\n" + "=" * 70)
print("📊 ZUSAMMENFASSUNG:")
print("=" * 70)
print(f"  ✅ Fixed: {len(fixed)}")
print(f"  ❌ Errors: {len(errors)}")
print(f"  💾 Saved: config/seo_batch_fix_result.json")
