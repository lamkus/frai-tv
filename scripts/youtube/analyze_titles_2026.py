#!/usr/bin/env python3
"""Analysiere alle Video-Titel nach 2026 SEO-Regeln."""

import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    creds_data = json.load(f)
creds = Credentials(
    token=creds_data['token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
youtube = build('youtube', 'v3', credentials=creds)

# Hole alle PUBLIC Videos
all_videos = []
next_page = None
while True:
    response = youtube.playlistItems().list(
        part='snippet,status',
        playlistId='UUVFv6Egpl0LDvigpFbQXNeQ',
        maxResults=50,
        pageToken=next_page
    ).execute()
    
    for item in response['items']:
        status = item.get('status', {}).get('privacyStatus', '?')
        if status == 'public':
            vid = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            all_videos.append({'id': vid, 'title': title})
    
    next_page = response.get('nextPageToken')
    if not next_page:
        break

print(f'Analysiere {len(all_videos)} PUBLIC Videos...')
print('=' * 70)

# Titel-Analyse nach 2026 Regeln
issues = {
    'too_long': [],      # >70 Zeichen
    'no_year': [],       # Kein Jahr in Klammern
    'no_8k': [],         # Kein 8K
    'no_brand': [],      # Kein @remAIke_IT
    'perfect': []        # Alles OK
}

for v in all_videos:
    title = v['title']
    problems = []
    
    # Check Länge
    if len(title) > 70:
        problems.append('too_long')
    
    # Check Jahr
    if not re.search(r'\(\d{4}\)|\(\w+\s+\d{4}\)', title):
        problems.append('no_year')
    
    # Check 8K
    if '8K' not in title and '4K' not in title:
        problems.append('no_8k')
    
    # Check Brand
    if '@remAIke' not in title:
        problems.append('no_brand')
    
    if problems:
        for p in problems:
            issues[p].append(v)
    else:
        issues['perfect'].append(v)

print(f'\n📊 TITEL-ANALYSE NACH 2026 REGELN:')
print(f"   ✅ Perfekt: {len(issues['perfect'])}")
print(f"   ⚠️  Zu lang (>70): {len(issues['too_long'])}")
print(f"   ⚠️  Kein Jahr: {len(issues['no_year'])}")
print(f"   ⚠️  Kein 8K/4K: {len(issues['no_8k'])}")
print(f"   ⚠️  Kein @remAIke: {len(issues['no_brand'])}")

# Beispiele zeigen
print('\n--- BEISPIELE ZU LANG (>70 Zeichen) ---')
for v in issues['too_long'][:5]:
    print(f"   [{len(v['title'])}] {v['title'][:60]}...")

print('\n--- BEISPIELE OHNE JAHR ---')
for v in issues['no_year'][:5]:
    print(f"   {v['title'][:60]}")

print('\n--- BEISPIELE OHNE 8K ---')
for v in issues['no_8k'][:5]:
    print(f"   {v['title'][:60]}")

# Speichern
with open('config/title_analysis_2026.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)
print(f'\n💾 Details in config/title_analysis_2026.json')
