"""
MEGA FIX — Fix ALL remaining issues across entire channel in one pass.

Fixes:
1. Broken Betty Boop titles with truncated @rem... handle
2. BraveStarr Intro: remove @remAIke_IT from title, add links, trim hashtags
3. BraveStarr E1 + Alfred Trailer: add links, trim hashtags  
4. Krtek Best Of: remove "ausgestrahlt" forbidden ref
5. Double-space artifacts in titles
6. Missing www.remaike.IT links
7. Missing pflicht-tags (remastered/restored)
8. Any remaining forbidden refs (ausgestrahlt, Erstausstrahlung)
"""
import json
import os
import sys
import re
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PFLICHT_TAGS = {'remastered', 'restored'}
MAX_HASHTAGS = 5
MAX_TAGS = 15

FORBIDDEN_DESC_PATTERNS = [
    r'[^\n]*Erstausstrahlung[^\n]*\n?',
    r'[^\n]*ausgestrahlt in über 80 Ländern[^\n]*\n?',
    r'[^\n]*wurde in über 80 Ländern ausgestrahlt[^\n]*\n?',
    r'[^\n]*Original ausgestrahlt[^\n]*\n?',
    r'[^\n]*Deutsche Erstausstrahlung[^\n]*\n?',
    r'[^\n]*\bZDF\b[^\n]*\n?',
    r'[^\n]*\bARD\b[^\n]*\n?',
    r'[^\n]*\bWDR\b[^\n]*\n?',
    r'[^\n]*\bVARA\b[^\n]*\n?',
]

CTA_BLOCK = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoy classic content!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""


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


def fix_title(title):
    """Fix all title issues."""
    original = title
    
    # 1. Remove ALL truncated @handle artifacts:
    #    Patterns: "| @remA... |", "| @rem... |", "| @re... |", "| @r... |", "| @... |"
    #    Also: "|  | @...", "|... |" etc.
    # First: full pipe-enclosed truncated handles
    title = re.sub(r'\s*\|\s*\|\s*@\S*\s*\|', ' |', title)
    title = re.sub(r'\s*\|\s*@rem\S*\s*\|', ' |', title)
    title = re.sub(r'\s*\|\s*@re\.\.\.\s*\|', ' |', title)
    title = re.sub(r'\s*\|\s*@r\.\.\.\s*\|', ' |', title)
    title = re.sub(r'\s*\|\s*@\.\.\.\s*\|', ' |', title)
    title = re.sub(r'\s*\|\s*\.\.\.\s*\|', ' |', title)
    # Also at end of title
    title = re.sub(r'\s*\|\s*@\S*\.\.\.\s*$', '', title)
    title = re.sub(r'\s*\|\s*@remAIke_IT', '', title)
    title = title.replace('@remAIke_IT', '').strip()
    
    # 2. Fix double spaces
    title = re.sub(r'  +', ' ', title)
    
    # 3. Fix double pipes: "| |" or "||"  
    title = re.sub(r'\|\s*\|', '|', title)
    
    # 4. Fix trailing/leading pipe issues
    title = re.sub(r'\|\s*$', '', title).strip()
    title = re.sub(r'^\s*\|', '', title).strip()
    
    # 5. Clean multiple spaces again
    title = re.sub(r'  +', ' ', title)
    
    # 6. Ensure 8K HQ (4K UHD) is present and correct
    if '8K HQ' in title and '(4K UHD)' not in title:
        title = title.replace('8K HQ', '8K HQ (4K UHD)')
    elif '8K' in title and '8K HQ' not in title and '(4K UHD)' not in title:
        # Has "8K" but not "8K HQ (4K UHD)"
        title = re.sub(r'\b8K\b(?!\s*HQ)', '8K HQ (4K UHD)', title, count=1)
    
    changed = title != original
    return title, changed


def fix_description(desc):
    """Fix description issues."""
    original = desc
    
    # Remove forbidden references
    for pattern in FORBIDDEN_DESC_PATTERNS:
        desc = re.sub(pattern, '', desc, flags=re.IGNORECASE)
    
    # Trim hashtags to max 5
    hashtags = re.findall(r'#\w+', desc)
    if len(hashtags) > MAX_HASHTAGS:
        # Keep first 5, remove rest
        count = 0
        lines = desc.split('\n')
        new_lines = []
        for line in lines:
            tags_in_line = re.findall(r'#\w+', line)
            if tags_in_line:
                remaining = MAX_HASHTAGS - count
                if remaining <= 0:
                    continue
                elif len(tags_in_line) > remaining:
                    for tag in tags_in_line[remaining:]:
                        line = line.replace(tag, '').strip()
                    line = re.sub(r'\s+', ' ', line).strip()
                    count += remaining
                else:
                    count += len(tags_in_line)
            new_lines.append(line)
        desc = '\n'.join(new_lines)
    
    # Ensure www.remaike.IT is present
    if 'remaike.it' not in desc.lower() and 'remaike.IT' not in desc:
        # Add CTA block at end if not already present
        if 'www.remaike' not in desc.lower():
            if not desc.endswith('\n'):
                desc += '\n'
            desc += '\n' + CTA_BLOCK
    
    # Clean multiple blank lines
    desc = re.sub(r'\n{3,}', '\n\n', desc)
    desc = desc.strip()
    
    changed = desc != original
    return desc, changed


def fix_tags(tags):
    """Fix tag issues."""
    original = list(tags)
    tag_lower = [t.lower() for t in tags]
    
    # Remove @remAIke_IT from tags if present
    tags = [t for t in tags if t != '@remAIke_IT' and t.lower() != '@remaike_it']
    
    # Remove forbidden tags
    forbidden = {'ard', 'wdr', 'zdf', 'vara', 'zdf/vara'}
    tags = [t for t in tags if t.lower().strip() not in forbidden]
    
    # Add pflicht-tags if missing
    tag_lower = [t.lower() for t in tags]
    for pt in PFLICHT_TAGS:
        if pt not in tag_lower:
            tags.append(pt)
    
    # Trim to max 15
    if len(tags) > MAX_TAGS:
        keep = [t for t in tags if t.lower() in {p.lower() for p in PFLICHT_TAGS}]
        rest = [t for t in tags if t.lower() not in {p.lower() for p in PFLICHT_TAGS}]
        tags = keep + rest[:MAX_TAGS - len(keep)]
    
    changed = tags != original
    return tags, changed


def main():
    dry_run = '--apply' not in sys.argv
    mode = 'DRY RUN' if dry_run else 'APPLYING'
    
    print(f"=== MEGA FIX ({mode}) ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    
    if dry_run:
        print("⚠️  DRY RUN — use --apply to update\n")
    
    # Load scan
    scan_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'live_scan_2026_02_18.json')
    with open(os.path.abspath(scan_path), 'r', encoding='utf-8') as f:
        scan = json.load(f)
    
    # Skip private raw uploads (sls ARCHIVE etc.) — they're not ready
    skip_raw = set()
    for v in scan['all_videos']:
        title = v.get('title', '')
        if v['privacy'] == 'private' and ('sls' in title.lower() or 'ARCHIVE' in title):
            skip_raw.add(v['id'])
    
    youtube = get_youtube_service()
    
    # Get ALL public videos that might need any fix
    all_public = [v for v in scan['all_videos'] 
                  if v['privacy'] in ('public', 'unlisted') and v['id'] not in skip_raw]
    
    print(f"Checking {len(all_public)} public/unlisted videos...\n")
    
    # Fetch full details in batches
    results = []
    quota_used = 0
    errors = 0
    skipped = 0
    
    # Deduplicate video IDs (scan may contain duplicates)
    seen = set()
    all_ids = []
    for v in all_public:
        if v['id'] not in seen:
            all_ids.append(v['id'])
            seen.add(v['id'])
    
    for batch_start in range(0, len(all_ids), 50):
        batch_ids = all_ids[batch_start:batch_start + 50]
        
        resp = youtube.videos().list(
            part='snippet',
            id=','.join(batch_ids)
        ).execute()
        
        for item in resp.get('items', []):
            vid = item['id']
            snippet = item['snippet']
            old_title = snippet['title']
            old_desc = snippet['description']
            old_tags = snippet.get('tags', [])
            cat_id = snippet['categoryId']
            
            new_title, title_changed = fix_title(old_title)
            new_desc, desc_changed = fix_description(old_desc)
            new_tags, tags_changed = fix_tags(old_tags)
            
            if not (title_changed or desc_changed or tags_changed):
                skipped += 1
                continue
            
            changes = []
            if title_changed:
                changes.append(f'TITLE: "{old_title[:40]}" → "{new_title[:40]}"')
            if desc_changed:
                changes.append('DESC: fixed')
            if tags_changed:
                changes.append(f'TAGS: {len(old_tags)}→{len(new_tags)}')
            
            change_str = ' | '.join(changes)
            
            if dry_run:
                print(f"  [DRY] {vid}: {change_str}")
                results.append({
                    'id': vid, 'old_title': old_title, 'new_title': new_title,
                    'changes': changes, 'status': 'dry_run'
                })
            else:
                body = {
                    'id': vid,
                    'snippet': {
                        'title': new_title,
                        'description': new_desc,
                        'tags': new_tags,
                        'categoryId': cat_id,
                    }
                }
                try:
                    youtube.videos().update(part='snippet', body=body).execute()
                    print(f"  [OK] {vid}: {change_str}")
                    results.append({
                        'id': vid, 'old_title': old_title, 'new_title': new_title,
                        'changes': changes, 'status': 'success'
                    })
                    quota_used += 50
                except Exception as e:
                    print(f"  [ERR] {vid}: {e}")
                    results.append({'id': vid, 'status': 'error', 'error': str(e)})
                    errors += 1
    
    success = sum(1 for r in results if r['status'] in ('success', 'dry_run'))
    
    print(f"\n{'='*60}")
    print(f"SUMMARY: {success} fixed | {skipped} already OK | {errors} errors")
    print(f"Quota used: {quota_used} units")
    
    # Show title changes for review
    if results:
        print(f"\n--- TITLE CHANGES ---")
        for r in results:
            if 'old_title' in r and r.get('old_title') != r.get('new_title'):
                print(f"  BEFORE: {r['old_title']}")
                print(f"  AFTER:  {r['new_title']}")
                print()
    
    report = {
        'date': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'applied',
        'total': success + skipped,
        'fixed': success,
        'skipped': skipped,
        'errors': errors,
        'quota_used': quota_used,
        'results': results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                f'mega_fix_report_{datetime.now().strftime("%Y_%m_%d")}.json')
    with open(os.path.abspath(report_path), 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nReport: {report_path}")
    if dry_run:
        print(f"\n🔄 To apply: python {sys.argv[0]} --apply")


if __name__ == '__main__':
    main()
