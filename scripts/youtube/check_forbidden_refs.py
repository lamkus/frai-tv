"""Check ALL recently fixed videos for forbidden references (ZDF, ARD, WDR, Sender etc.)"""
import json
import os
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

FORBIDDEN_PATTERNS = [
    r'\bZDF\b', r'\bARD\b', r'\bWDR\b', r'\bSender\b', r'\bFernsehen\b',
    r'\bTV-Serie\b', r'\bRundfunk\b', r'\bAusstrahlung\b', r'\bErstausstrahlung\b',
    r'\bAusgestrahlt\b', r'\bVARA\b', r'\bNIPPON\b',
]

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
    return build('youtube', 'v3', credentials=creds)

def main():
    # All videos fixed today (19 Alfred + 2 Der 7. Sinn + 37 comprehensive)  
    # Load from both reports
    all_ids = set()
    
    for report_file in [
        'config/seo_fix_report_2026_02_17.json',
        'config/comprehensive_fix_report_2026_02_17.json'
    ]:
        path = os.path.join(os.path.dirname(__file__), '..', '..', report_file)
        path = os.path.abspath(path)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for r in data.get('results', []):
                all_ids.add(r['id'])
    
    # Also check ALL public videos from live scan for forbidden refs
    scan_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'live_scan_2026_02_17.json')
    scan_path = os.path.abspath(scan_path)
    with open(scan_path, 'r', encoding='utf-8') as f:
        scan = json.load(f)
    
    for v in scan['all_videos']:
        all_ids.add(v['id'])
    
    print(f"=== SCANNING {len(all_ids)} VIDEOS FOR FORBIDDEN REFERENCES ===\n")
    
    youtube = get_youtube_service()
    id_list = list(all_ids)
    
    violations = []
    
    for batch_start in range(0, len(id_list), 50):
        batch = id_list[batch_start:batch_start + 50]
        resp = youtube.videos().list(part='snippet', id=','.join(batch)).execute()
        
        for item in resp.get('items', []):
            vid = item['id']
            snippet = item['snippet']
            title = snippet['title']
            desc = snippet['description']
            tags = snippet.get('tags', [])
            
            found = []
            
            # Check title
            for pattern in FORBIDDEN_PATTERNS:
                m = re.search(pattern, title, re.IGNORECASE)
                if m:
                    found.append(f'TITLE: "{m.group()}" in "{title}"')
            
            # Check description
            for pattern in FORBIDDEN_PATTERNS:
                for m in re.finditer(pattern, desc, re.IGNORECASE):
                    # Get surrounding context
                    start = max(0, m.start() - 30)
                    end = min(len(desc), m.end() + 30)
                    ctx = desc[start:end].replace('\n', ' ')
                    found.append(f'DESC: "...{ctx}..."')
            
            # Check tags
            for tag in tags:
                for pattern in FORBIDDEN_PATTERNS:
                    m = re.search(pattern, tag, re.IGNORECASE)
                    if m:
                        found.append(f'TAG: "{tag}"')
            
            if found:
                violations.append({
                    'id': vid,
                    'title': title,
                    'found': found
                })
    
    if violations:
        print(f"❌ FOUND {len(violations)} VIDEOS WITH FORBIDDEN REFERENCES:\n")
        for v in violations:
            print(f"  {v['id']}: {v['title'][:60]}")
            for f in v['found']:
                print(f"    ⚠️  {f}")
            print()
    else:
        print("✅ No forbidden references found!")
    
    # Save
    report_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'forbidden_refs_check.json')
    with open(os.path.abspath(report_path), 'w', encoding='utf-8') as f:
        json.dump({'violations': violations, 'total_checked': len(id_list)}, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved to config/forbidden_refs_check.json")

if __name__ == '__main__':
    main()
