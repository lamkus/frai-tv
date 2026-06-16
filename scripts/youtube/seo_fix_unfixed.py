"""
SEO Fix Script for ALL unfixed uploads
Based on live_scan_2026_02_17.json results

Fixes:
1. 16 Alfred J. Kwak blur-border (raw filenames → proper titles)
2. 2 Der 7. Sinn (raw → proper)
3. BraveStarr minor SEO fixes
4. Popeye Marathon missing (4K UHD)
5. Wochenschau 480 too many hashtags

Quota cost: videos.update = 50 units each
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


# ============================================================
# ALFRED J. KWAK BLUR-BORDER FIXES
# Map raw titles to proper ones from alfred_blur_naming_DE.json
# ============================================================

# Raw title pattern: "NN   title sls ARCHIVE BLURRED"
# Extract file number → map to broadcast number → use proper title
ALFRED_RAW_TO_FIX = {
    'Hto044hFaZ4': {'file_nr': 1,  'broadcast_nr': 1,  'title_de': 'Hurra, er ist da!'},
    'is5qVIkr6Vo': {'file_nr': 2,  'broadcast_nr': 2,  'title_de': 'Böse Überraschung'},
    'UHS1MqpTng8': {'file_nr': 3,  'broadcast_nr': 3,  'title_de': 'Hinter Gittern'},
    'rqWucYVxqTA': {'file_nr': 4,  'broadcast_nr': 4,  'title_de': 'Im Brunnen gefangen'},
    'FjvUAUsQi8Q': {'file_nr': 10, 'broadcast_nr': 10, 'title_de': 'Der Geist in der Flasche'},
    'ea5LQn-BJQs': {'file_nr': 11, 'broadcast_nr': 11, 'title_de': 'Der Mensch ist los!'},
    '4Nu91xa9_eY': {'file_nr': 16, 'broadcast_nr': 16, 'title_de': 'Die Reise zum Südpol'},
    'x7u-1DcabiE': {'file_nr': 17, 'broadcast_nr': 17, 'title_de': 'Rettung aus dem All'},
    'I1Hqb1mGlzU': {'file_nr': 18, 'broadcast_nr': 18, 'title_de': 'Im ewigen Eis'},
    'ghhyzR9NSLE': {'file_nr': 19, 'broadcast_nr': 19, 'title_de': 'Rettet die Wale!'},
    'oWZ5BmJVsxI': {'file_nr': 20, 'broadcast_nr': 20, 'title_de': 'Der Alptraum'},
    'NvwmtSLyCE4': {'file_nr': 31, 'broadcast_nr': 31, 'title_de': 'Die Bohrinsel'},
    'GpYO8Yel0WY': {'file_nr': 35, 'broadcast_nr': 36, 'title_de': 'Michael Duckson'},
    'Dg6eQNIY_Ys': {'file_nr': 36, 'broadcast_nr': 37, 'title_de': 'Die Entführung'},
    'qGzRqmiOcNw': {'file_nr': 37, 'broadcast_nr': 38, 'title_de': 'Krach mit den Nachbarn'},
    '8aeRL4PwSVI': {'file_nr': 43, 'broadcast_nr': 48, 'title_de': 'Eine Partie Golf'},
    'Y28BihR4fkk': {'file_nr': 44, 'broadcast_nr': 49, 'title_de': 'Der Regenbogen'},
}

def build_alfred_description(ep):
    """Build SEO-optimized description for Alfred blur-border episode"""
    nr = ep['broadcast_nr']
    title = ep['title_de']
    return f"""🎬 Alfred J. Kwak (E{nr:02d}) {title} | Widescreen 16:9
Classic animated series (1989), AI-remastered in 8K quality with blur-border widescreen format.

🇩🇪 Episode {nr} der beliebten Zeichentrickserie Alfred Jodocus Kwak.
Basierend auf dem Musical von Herman van Veen. Erstausstrahlung 1989 (ZDF/VARA).
Diese Version: Widescreen 16:9 Format (4:3 Original mit unscharfem Rand).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoy classic animation!
💬 COMMENT your favorite episode!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#AlfredJKwak #AlfredJQuack #8K #ClassicAnimation #VintageCartoon"""

ALFRED_TAGS = [
    'Alfred J. Kwak', 'Alfred J. Quack', 'Alfred Jodocus Kwak',
    'Herman van Veen', '8K', 'restored', 'remastered',
    'classic animation', 'vintage cartoon', '1989',
    'Zeichentrickserie', 'public domain', 'widescreen'
]


# ============================================================
# DER 7. SINN FIXES
# ============================================================
SIEBTER_SINN_FIXES = {
    'KaIC0B-xYBg': {
        'new_title': 'Der 7. Sinn: Frauen am Steuer - Teil 1 (1970s) | 8K HQ (4K UHD)',
        'description': """🎬 Der 7. Sinn: Frauen am Steuer – Teil 1
Classic German traffic safety show (1970s), AI-remastered in stunning 8K quality.

🇩🇪 "Der 7. Sinn" war die bekannteste Verkehrserziehungssendung des deutschen Fernsehens.
Ausgestrahlt von 1966 bis 2005 im Ersten (ARD). Diese Episode: "Frauen am Steuer" Teil 1.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Der7Sinn #Verkehrserziehung #8K #ClassicTV #VintageGerman""",
        'tags': ['Der 7. Sinn', 'Der siebte Sinn', 'Verkehrserziehung', 'ARD',
                 '1970s', '8K', 'restored', 'German TV', 'classic TV',
                 'traffic safety', 'Frauen am Steuer', 'vintage'],
        'categoryId': '27'
    },
    'HyaZLqdMS9k': {
        'new_title': 'Der 7. Sinn: Frauen am Steuer - Teil 3 (1970s) | 8K HQ (4K UHD)',
        'description': """🎬 Der 7. Sinn: Frauen am Steuer – Teil 3
Classic German traffic safety show (1970s), AI-remastered in stunning 8K quality.

🇩🇪 "Der 7. Sinn" war die bekannteste Verkehrserziehungssendung des deutschen Fernsehens.
Ausgestrahlt von 1966 bis 2005 im Ersten (ARD). Diese Episode: "Frauen am Steuer" Teil 3.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Der7Sinn #Verkehrserziehung #8K #ClassicTV #VintageGerman""",
        'tags': ['Der 7. Sinn', 'Der siebte Sinn', 'Verkehrserziehung', 'ARD',
                 '1970s', '8K', 'restored', 'German TV', 'classic TV',
                 'traffic safety', 'Frauen am Steuer', 'vintage'],
        'categoryId': '27'
    }
}


def apply_fix(youtube, video_id, new_title, description, tags, category_id, dry_run=True):
    """Apply SEO fix to a single video"""
    if dry_run:
        print(f"  [DRY RUN] Would update {video_id}: {new_title[:60]}")
        return {'id': video_id, 'title': new_title, 'status': 'dry_run'}
    
    # Get current video data first (need snippet for update)
    resp = youtube.videos().list(part='snippet,status', id=video_id).execute()
    if not resp.get('items'):
        print(f"  [ERROR] Video {video_id} not found!")
        return {'id': video_id, 'status': 'not_found'}
    
    item = resp['items'][0]
    old_title = item['snippet']['title']
    
    # Build update body
    body = {
        'id': video_id,
        'snippet': {
            'title': new_title,
            'description': description,
            'tags': tags,
            'categoryId': category_id,
        }
    }
    
    try:
        youtube.videos().update(part='snippet', body=body).execute()
        print(f"  [OK] {video_id}: {old_title[:40]} → {new_title[:40]}")
        return {
            'id': video_id,
            'old_title': old_title,
            'title': new_title,
            'status': 'success'
        }
    except Exception as e:
        print(f"  [ERROR] {video_id}: {e}")
        return {'id': video_id, 'status': 'error', 'error': str(e)}


def main():
    dry_run = '--apply' not in sys.argv
    mode = 'DRY RUN' if dry_run else 'APPLYING'
    
    print(f"=== SEO Fix Script ({mode}) ===")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE — use --apply to actually update videos")
    
    youtube = get_youtube_service()
    
    results = []
    quota_used = 0
    
    # ============================================================
    # 1. ALFRED J. KWAK BLUR-BORDER (17 videos × 50 = 850 units)
    # ============================================================
    print(f"\n{'='*60}")
    print(f"1. Alfred J. Kwak Blur-Border Fixes ({len(ALFRED_RAW_TO_FIX)} videos)")
    print(f"   Quota: {len(ALFRED_RAW_TO_FIX)} × 50 = {len(ALFRED_RAW_TO_FIX) * 50} units")
    print(f"{'='*60}")
    
    for vid, ep in ALFRED_RAW_TO_FIX.items():
        nr = ep['broadcast_nr']
        title = f"Alfred J. Kwak (E{nr:02d}) {ep['title_de']} | DE | 8K HQ (4K UHD)"
        desc = build_alfred_description(ep)
        
        result = apply_fix(youtube, vid, title, desc, ALFRED_TAGS, '1', dry_run)
        results.append(result)
        if result.get('status') == 'success':
            quota_used += 50
    
    # ============================================================
    # 2. DER 7. SINN (2 videos × 50 = 100 units)
    # ============================================================
    print(f"\n{'='*60}")
    print(f"2. Der 7. Sinn Fixes ({len(SIEBTER_SINN_FIXES)} videos)")
    print(f"   Quota: {len(SIEBTER_SINN_FIXES)} × 50 = {len(SIEBTER_SINN_FIXES) * 50} units")
    print(f"{'='*60}")
    
    for vid, fix in SIEBTER_SINN_FIXES.items():
        result = apply_fix(youtube, vid, fix['new_title'], fix['description'],
                          fix['tags'], fix['categoryId'], dry_run)
        results.append(result)
        if result.get('status') == 'success':
            quota_used += 50
    
    # ============================================================
    # SUMMARY
    # ============================================================
    total = len(results)
    success = sum(1 for r in results if r.get('status') in ('success', 'dry_run'))
    errors = sum(1 for r in results if r.get('status') == 'error')
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total fixes planned: {total}")
    print(f"Successful:          {success}")
    print(f"Errors:              {errors}")
    print(f"Quota used:          {quota_used} units")
    
    # Save report
    report = {
        'date': datetime.now().isoformat(),
        'mode': 'dry_run' if dry_run else 'applied',
        'total': total,
        'success': success,
        'errors': errors,
        'quota_used': quota_used,
        'results': results
    }
    
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config',
                                f'seo_fix_report_{datetime.now().strftime("%Y_%m_%d")}.json')
    report_path = os.path.abspath(report_path)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\nReport saved to: {report_path}")
    
    if dry_run:
        print(f"\n🔄 To apply: python {sys.argv[0]} --apply")

if __name__ == '__main__':
    main()
