#!/usr/bin/env python3
"""Scannt alle Public Videos und erstellt Rename-Audit"""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

with open('config/youtube_oauth.json') as f:
    oauth = json.load(f)

creds = Credentials(
    token=oauth['token'],
    refresh_token=oauth['refresh_token'],
    token_uri=oauth['token_uri'],
    client_id=oauth['client_id'],
    client_secret=oauth['client_secret'],
)
youtube = build('youtube', 'v3', credentials=creds)

UPLOADS_PLAYLIST = 'UUVFv6Egpl0LDvigpFbQXNeQ'

# Hole alle Videos
videos = []
next_page = None

print("📥 Lade alle Videos...")
while True:
    result = youtube.playlistItems().list(
        part='snippet,contentDetails,status',
        playlistId=UPLOADS_PLAYLIST,
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in result.get('items', []):
        status = item.get('status', {}).get('privacyStatus', 'unknown')
        if status == 'public':
            videos.append({
                'id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'desc': item['snippet'].get('description', '')[:500]
            })
    
    next_page = result.get('nextPageToken')
    if not next_page:
        break

print(f"✅ {len(videos)} Public Videos gefunden")
print()

# Kategorie-Detection
CATEGORY_MAP = {
    'betty boop': 'Betty Boop',
    'popeye': 'Popeye',
    'superman': 'Superman',
    'fleischer': 'Fleischer',
    'looney tunes': 'Looney Tunes',
    'merrie melodies': 'Looney Tunes',
    'felix': 'Felix the Cat',
    'soundie': 'Soundie',
    'alfred j. kwak': 'Alfred J. Kwak',
    'alfred j kwak': 'Alfred J. Kwak',
    'kwak': 'Alfred J. Kwak',
    'quack': 'Alfred J. Kwak',
    'bravestarr': 'BraveStarr',
    'brave starr': 'BraveStarr',
    'astro boy': 'Astro Boy',
    'wochenschau': 'Wochenschau',
    'newsreel': 'Newsreel',
    'christmas': 'Christmas',
    'charlie chaplin': 'Charlie Chaplin',
    'chaplin': 'Chaplin',
    'buster keaton': 'Buster Keaton',
    'laurel': 'Laurel & Hardy',
    'kirby': 'Kirby',
    'maulwurf': 'Der kleine Maulwurf',
    'krtek': 'Der kleine Maulwurf',
    'asterix': 'Asterix',
    'documentary': 'Documentary',
    'metropolis': 'Metropolis',
    'nosferatu': 'Nosferatu',
    'cabinet': 'Das Cabinet des Dr. Caligari',
}

def detect_category(title):
    text = title.lower()
    for kw, cat in CATEGORY_MAP.items():
        if kw in text:
            return cat
    return 'Other'

def extract_year(title):
    match = re.search(r'\((\d{4})\)', title)
    if match:
        return match.group(1)
    return None

# Analysiere Issues
issues = {
    'no_8k': [],
    'no_branding': [],
    'hashtag_in_title': [],
    'too_long': [],
    'no_year': [],
    'inconsistent_8k': []
}

for v in videos:
    t = v['title']
    
    # 8K Check
    if '8K' not in t.upper():
        issues['no_8k'].append(v)
    elif '8K HQ' not in t:
        issues['inconsistent_8k'].append(v)
    
    # Branding Check
    if '@remAIke_IT' not in t:
        issues['no_branding'].append(v)
    
    # Hashtag Check
    if '#' in t:
        issues['hashtag_in_title'].append(v)
    
    # Length Check
    if len(t) > 90:
        issues['too_long'].append(v)
    
    # Year Check
    if not extract_year(t):
        issues['no_year'].append(v)

print("=" * 60)
print("📊 ISSUE SUMMARY")
print("=" * 60)
print(f"❌ Kein 8K:           {len(issues['no_8k'])}")
print(f"❌ Kein @remAIke_IT:  {len(issues['no_branding'])}")
print(f"❌ Hashtag im Titel:  {len(issues['hashtag_in_title'])}")
print(f"⚠️  Zu lang (>90):    {len(issues['too_long'])}")
print(f"⚠️  Kein Jahr ():     {len(issues['no_year'])}")
print(f"⚠️  8K inkonsistent:  {len(issues['inconsistent_8k'])}")
print()

# Alle IDs mit Issues
all_problem_ids = set()
for lst in issues.values():
    for v in lst:
        all_problem_ids.add(v['id'])

print(f"🔧 TOTAL Videos mit Issues: {len(all_problem_ids)}")
print()

# Zeige Details für kritische Issues
print("=" * 60)
print("❌ KRITISCH: Kein 8K")
print("=" * 60)
for v in issues['no_8k'][:20]:
    print(f"  {v['id']}: {v['title'][:70]}")
if len(issues['no_8k']) > 20:
    print(f"  ... und {len(issues['no_8k']) - 20} weitere")
print()

print("=" * 60)
print("❌ KRITISCH: Kein Branding")
print("=" * 60)
for v in issues['no_branding'][:20]:
    print(f"  {v['id']}: {v['title'][:70]}")
if len(issues['no_branding']) > 20:
    print(f"  ... und {len(issues['no_branding']) - 20} weitere")
print()

print("=" * 60)
print("⚠️ Kein Jahr")
print("=" * 60)
for v in issues['no_year'][:20]:
    cat = detect_category(v['title'])
    print(f"  [{cat}] {v['id']}: {v['title'][:60]}")
if len(issues['no_year']) > 20:
    print(f"  ... und {len(issues['no_year']) - 20} weitere")

# Speichere Ergebnis
output = {
    'scan_date': datetime.now().isoformat(),
    'total_public': len(videos),
    'issues': {
        k: [{'id': x['id'], 'title': x['title'], 'category': detect_category(x['title'])} for x in lst] 
        for k, lst in issues.items()
    },
    'total_with_issues': len(all_problem_ids),
    'all_videos': [{'id': v['id'], 'title': v['title'], 'category': detect_category(v['title'])} for v in videos]
}

with open('config/rename_audit_result.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print()
print(f"💾 Gespeichert: config/rename_audit_result.json")
