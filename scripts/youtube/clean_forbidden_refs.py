"""
CLEAN FORBIDDEN REFERENCES — Remove all broadcaster/network references from descriptions + tags.
Removes: ZDF, ARD, WDR, VARA, Fernsehen, Erstausstrahlung, Ausgestrahlt, Sender, etc.
Keeps: Everything else intact.

31 videos affected:
- 17 Alfred J. Kwak: Remove "Erstausstrahlung 1989 (ZDF/VARA)." sentence
- 11 Krtek: Remove "ausgestrahlt in über 80 Ländern" sentences
- 3 Der 7. Sinn: Rewrite descriptions without ARD/WDR, remove ARD/WDR tags
"""
import json
import os
import sys
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


def get_youtube_service():
    token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')
    token_path = os.path.abspath(token_path)
    with open(token_path, 'r') as f:
        token_data = json.load(f)
    creds = Credentials(
        token=token_data.get('token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data.get('client_id'),
        client_secret=token_data.get('client_secret'),
        scopes=token_data.get('scopes', ['https://www.googleapis.com/auth/youtube.force-ssl'])
    )
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        token_data['token'] = creds.token
        token_data['expiry'] = creds.expiry.isoformat() if creds.expiry else None
        with open(token_path, 'w') as f:
            json.dump(token_data, f, indent=2)
    return build('youtube', 'v3', credentials=creds)


# Patterns to remove from descriptions (full sentences/lines)
REMOVE_PATTERNS = [
    # Alfred: "Erstausstrahlung 1989 (ZDF/VARA)." and surrounding context
    r'Erstausstrahlung \d{4} \([^)]*\)\.\s*',
    r'Basierend auf dem Musical von Herman van Veen\.\s*Erstausstrahlung[^\n]*\n?',
    # Krtek: "ausgestrahlt in über 80 Ländern" sentences
    r'[^\n]*ausgestrahlt in über 80 Ländern[^\n]*\n?',
    r'[^\n]*wurde in über 80 Ländern ausgestrahlt[^\n]*\n?',
    # Der 7. Sinn: ARD/WDR references
    r'[^\n]*\bARD\b[^\n]*\n?',
    r'[^\n]*\bWDR\b[^\n]*\n?',
    r'[^\n]*Verkehrserziehungssendung des deutschen Fernsehens[^\n]*\n?',
    r'[^\n]*traffic safety show[^\n]*\n?',
    r'[^\n]*Produced by WDR[^\n]*\n?',
    r'[^\n]*Produziert vom WDR[^\n]*\n?',
    # Generic
    r'[^\n]*\bZDF/VARA\b[^\n]*\n?',
    r'[^\n]*\bZDF\b[^\n]*\n?',
]

# Tags to remove
FORBIDDEN_TAGS = {'ard', 'wdr', 'zdf', 'vara', 'zdf/vara'}


def clean_description(desc):
    """Remove all forbidden references from description."""
    original = desc
    
    for pattern in REMOVE_PATTERNS:
        desc = re.sub(pattern, '', desc, flags=re.IGNORECASE)
    
    # Clean up multiple blank lines
    desc = re.sub(r'\n{3,}', '\n\n', desc)
    desc = desc.strip()
    
    changed = desc != original
    return desc, changed


def clean_tags(tags):
    """Remove forbidden tags."""
    original_count = len(tags)
    cleaned = [t for t in tags if t.lower().strip() not in FORBIDDEN_TAGS]
    return cleaned, len(cleaned) < original_count


def main():
    dry_run = '--apply' not in sys.argv
    mode = 'DRY RUN' if dry_run else 'APPLYING'
    
    print(f"=== Clean Forbidden References ({mode}) ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    if dry_run:
        print("⚠️  DRY RUN — use --apply to update videos\n")
    
    # Load violations
    violations_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'forbidden_refs_check.json')
    with open(os.path.abspath(violations_path), 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    video_ids = [v['id'] for v in data['violations']]
    print(f"Videos to clean: {len(video_ids)}\n")
    
    youtube = get_youtube_service()
    results = []
    quota_used = 0
    errors = 0
    
    for batch_start in range(0, len(video_ids), 50):
        batch_ids = video_ids[batch_start:batch_start + 50]
        
        resp = youtube.videos().list(
            part='snippet',
            id=','.join(batch_ids)
        ).execute()
        
        for item in resp.get('items', []):
            vid = item['id']
            snippet = item['snippet']
            title = snippet['title']
            desc = snippet['description']
            tags = snippet.get('tags', [])
            cat_id = snippet['categoryId']
            
            new_desc, desc_changed = clean_description(desc)
            new_tags, tags_changed = clean_tags(tags)
            
            changes = []
            if desc_changed:
                changes.append('DESC: cleaned')
            if tags_changed:
                removed = set(t.lower() for t in tags) - set(t.lower() for t in new_tags)
                changes.append(f'TAGS: removed {removed}')
            
            if not changes:
                print(f"  [SKIP] {vid}: {title[:50]}")
                continue
            
            # Verify no forbidden refs remain
            remaining = []
            for pattern in [r'\bZDF\b', r'\bARD\b', r'\bWDR\b', r'\bVARA\b', 
                           r'\bFernsehen\b', r'\bAusstrahlung\b', r'\bAusgestrahlt\b']:
                if re.search(pattern, new_desc, re.IGNORECASE):
                    remaining.append(pattern)
            
            if remaining:
                print(f"  [WARN] {vid}: Still has refs after cleaning: {remaining}")
                # Show the problematic lines
                for line in new_desc.split('\n'):
                    for p in remaining:
                        if re.search(p, line, re.IGNORECASE):
                            print(f"         → {line[:80]}")
            
            change_str = ' | '.join(changes)
            
            if dry_run:
                print(f"  [DRY] {vid}: {title[:50]} → {change_str}")
                if remaining:
                    print(f"        ⚠️ WARNING: Still has refs! Manual review needed.")
                results.append({
                    'id': vid, 'title': title,
                    'changes': changes, 'status': 'dry_run',
                    'remaining_refs': remaining
                })
            else:
                body = {
                    'id': vid,
                    'snippet': {
                        'title': title,
                        'description': new_desc,
                        'tags': new_tags,
                        'categoryId': cat_id,
                    }
                }
                try:
                    youtube.videos().update(part='snippet', body=body).execute()
                    print(f"  [OK] {vid}: {title[:50]} → {change_str}")
                    results.append({
                        'id': vid, 'title': title,
                        'changes': changes, 'status': 'success',
                        'remaining_refs': remaining
                    })
                    quota_used += 50
                except Exception as e:
                    print(f"  [ERR] {vid}: {e}")
                    results.append({
                        'id': vid, 'status': 'error', 'error': str(e)
                    })
                    errors += 1
    
    success = sum(1 for r in results if r['status'] in ('success', 'dry_run'))
    warnings = sum(1 for r in results if r.get('remaining_refs'))
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {success} cleaned | {errors} errors | {warnings} warnings")
    print(f"Quota used: {quota_used} units")
    
    report = {
        'date': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'applied',
        'total': len(results),
        'success': success,
        'errors': errors,
        'warnings': warnings,
        'quota_used': quota_used,
        'results': results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                f'clean_refs_report_{datetime.now().strftime("%Y_%m_%d")}.json')
    with open(os.path.abspath(report_path), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Report: {report_path}")
    if dry_run:
        print(f"\n🔄 To apply: python {sys.argv[0]} --apply")


if __name__ == '__main__':
    main()
