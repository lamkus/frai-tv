"""
COMPREHENSIVE FIX — Fix ALL remaining issues in one pass.
Uses live API to get current state, then fixes everything.

Issues to fix:
- R1b: 1 video missing (4K UHD) in title
- R5: 1 video missing www.remaike.IT  
- R7: 3 videos too many hashtags
- R8: 1 video too many tags  
- R13: 34 videos missing pflicht-tags (remastered, restored)

Strategy: Batch all fixes per video into ONE API call each.
Quota: 37 × 50 = 1,850 units (1 read + 1 update per video = 50 per video)
"""
import json
import os
import sys
import re
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

PFLICHT_TAGS = ['remastered', 'restored']
MAX_HASHTAGS = 5
MAX_TAGS = 15

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


def fix_hashtags(desc, max_count=5):
    """Reduce hashtags to max_count, keeping the most relevant ones."""
    lines = desc.split('\n')
    new_lines = []
    hashtag_count = 0
    
    for line in lines:
        # Find hashtags in this line
        tags_in_line = re.findall(r'#\w+', line)
        if tags_in_line:
            remaining = max_count - hashtag_count
            if remaining <= 0:
                # Skip entire hashtag line
                continue
            elif len(tags_in_line) > remaining:
                # Keep only 'remaining' hashtags from this line
                kept = tags_in_line[:remaining]
                for tag in tags_in_line[remaining:]:
                    line = line.replace(tag, '').strip()
                line = re.sub(r'\s+', ' ', line).strip()
                hashtag_count += len(kept)
            else:
                hashtag_count += len(tags_in_line)
        new_lines.append(line)
    
    # Clean up empty lines at the end
    while new_lines and new_lines[-1].strip() == '':
        new_lines.pop()
    
    return '\n'.join(new_lines)


def ensure_remaike_link(desc):
    """Add www.remaike.IT and YouTube link if missing."""
    additions = []
    if 'remaike.it' not in desc.lower() and 'remaike.IT' not in desc:
        additions.append('🌐 www.remaike.IT')
    if 'youtube.com/@remAIke_IT' not in desc and '@remAIke_IT' not in desc:
        additions.append('📺 https://www.youtube.com/@remAIke_IT')
    
    if additions:
        if not desc.endswith('\n'):
            desc += '\n'
        desc += '\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        desc += '\n'.join(additions)
    
    return desc


def fix_title_4k(title):
    """Add (4K UHD) after 8K HQ if missing."""
    if '8K HQ' in title and '(4K UHD)' not in title:
        title = title.replace('8K HQ', '8K HQ (4K UHD)')
    elif '| 8K' in title and '4K' not in title:
        title = title.replace('| 8K', '| 8K HQ (4K UHD)')
    return title


def fix_tags(tags, max_count=15):
    """Ensure pflicht-tags present, trim to max."""
    tag_lower = [t.lower() for t in tags]
    
    # Add missing pflicht-tags
    for pt in PFLICHT_TAGS:
        if pt not in tag_lower:
            tags.append(pt)
    
    # Trim if over max
    if len(tags) > max_count:
        # Keep pflicht-tags, remove least important
        keep = []
        rest = []
        for t in tags:
            if t.lower() in [p.lower() for p in PFLICHT_TAGS]:
                keep.append(t)
            else:
                rest.append(t)
        tags = keep + rest[:max_count - len(keep)]
    
    return tags


def remove_handle_from_title(title):
    """Remove @remAIke_IT from title."""
    title = title.replace(' | @remAIke_IT', '')
    title = title.replace(' @remAIke_IT', '')
    title = title.replace('@remAIke_IT', '')
    return title.strip()


def main():
    dry_run = '--apply' not in sys.argv
    mode = 'DRY RUN' if dry_run else 'APPLYING'
    
    print(f"=== Comprehensive Fix ({mode}) ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if dry_run:
        print("\n⚠️  DRY RUN — use --apply to update videos")
    
    # Load issues
    issues_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                'full_compliance_issues_2026_02_17.json')
    issues_path = os.path.abspath(issues_path)
    with open(issues_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixable = data['fixable']
    print(f"\nVideos to fix: {len(fixable)}")
    
    youtube = get_youtube_service()
    
    results = []
    quota_used = 0
    errors = 0
    
    # Process in batches of 50 for reading
    video_ids = [v['id'] for v in fixable]
    video_issues = {v['id']: v for v in fixable}
    
    for batch_start in range(0, len(video_ids), 50):
        batch_ids = video_ids[batch_start:batch_start + 50]
        
        # Read current state
        resp = youtube.videos().list(
            part='snippet,status',
            id=','.join(batch_ids)
        ).execute()
        
        for item in resp.get('items', []):
            vid = item['id']
            snippet = item['snippet']
            current_title = snippet['title']
            current_desc = snippet['description']
            current_tags = snippet.get('tags', [])
            current_cat = snippet['categoryId']
            issues = video_issues[vid]
            
            new_title = current_title
            new_desc = current_desc
            new_tags = list(current_tags)
            new_cat = current_cat
            changes = []
            
            # R1b: Fix title - add (4K UHD)
            if issues['needs_title_fix']:
                if any('R1b' in i or 'R1c' in i for i in issues['issues']):
                    new_title = fix_title_4k(new_title)
                    if new_title != current_title:
                        changes.append(f'Title: +4K UHD')
                
                if any('R2' in i for i in issues['issues']):
                    new_title = remove_handle_from_title(new_title)
                    if new_title != current_title:
                        changes.append('Title: -@handle')
            
            # R5/R6: Add missing links
            if any('R5' in i or 'R6' in i for i in issues['issues']):
                new_desc = ensure_remaike_link(new_desc)
                if new_desc != current_desc:
                    changes.append('Desc: +links')
            
            # R7: Fix hashtags
            if any('R7' in i for i in issues['issues']):
                new_desc = fix_hashtags(new_desc, MAX_HASHTAGS)
                changes.append('Desc: hashtags trimmed')
            
            # R8: Trim tags
            if any('R8' in i for i in issues['issues']):
                new_tags = fix_tags(new_tags, MAX_TAGS)
                changes.append(f'Tags: trimmed to {len(new_tags)}')
            
            # R13: Add pflicht-tags
            if any('R13' in i for i in issues['issues']):
                new_tags = fix_tags(new_tags, MAX_TAGS)
                changes.append('Tags: +remastered/restored')
            
            # R9: Category fix
            if issues['needs_cat_fix']:
                new_cat = issues['needs_cat_fix']
                changes.append(f'Cat: {current_cat}→{new_cat}')
            
            if not changes:
                print(f"  [SKIP] {vid}: No changes needed")
                continue
            
            change_str = ' | '.join(changes)
            
            if dry_run:
                print(f"  [DRY] {vid}: {current_title[:45]} → {change_str}")
                results.append({
                    'id': vid, 'title': new_title,
                    'changes': changes, 'status': 'dry_run'
                })
            else:
                body = {
                    'id': vid,
                    'snippet': {
                        'title': new_title,
                        'description': new_desc,
                        'tags': new_tags,
                        'categoryId': new_cat,
                    }
                }
                try:
                    youtube.videos().update(part='snippet', body=body).execute()
                    print(f"  [OK] {vid}: {current_title[:40]} → {change_str}")
                    results.append({
                        'id': vid, 'old_title': current_title,
                        'title': new_title, 'changes': changes,
                        'status': 'success'
                    })
                    quota_used += 50
                except Exception as e:
                    print(f"  [ERR] {vid}: {e}")
                    results.append({
                        'id': vid, 'status': 'error', 'error': str(e)
                    })
                    errors += 1
    
    # Summary
    success = sum(1 for r in results if r['status'] in ('success', 'dry_run'))
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {len(results)} | Success: {success} | Errors: {errors}")
    print(f"Quota used: {quota_used} units")
    
    # Save report
    report = {
        'date': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'applied',
        'total': len(results),
        'success': success,
        'errors': errors,
        'quota_used': quota_used,
        'results': results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                f'comprehensive_fix_report_{datetime.now().strftime("%Y_%m_%d")}.json')
    report_path = os.path.abspath(report_path)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"Report: {report_path}")
    if dry_run:
        print(f"\n🔄 To apply: python {sys.argv[0]} --apply")


if __name__ == '__main__':
    main()
