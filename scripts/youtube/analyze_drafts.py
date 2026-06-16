#!/usr/bin/env python3
"""
Analyse der 18 Draft-Videos - Was fehlt noch zur Veröffentlichung?
"""
import json, sys, io
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# OAuth für private Videos
creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
youtube = build('youtube', 'v3', credentials=creds)

# Drafts aus Channel-Scan
data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))
drafts = data.get('private_videos', [])

print("=" * 70)
print("📝 DRAFT-ANALYSE - 18 Videos zur Veröffentlichung")
print("=" * 70)
print()

for i, d in enumerate(drafts, 1):
    vid = d['id']
    snippet = d['snippet']
    title = snippet.get('title', 'Untitled')
    desc = snippet.get('description', '')
    tags = snippet.get('tags', [])
    
    print(f"[{i:2d}] {title}")
    print(f"     ID: {vid}")
    print(f"     https://studio.youtube.com/video/{vid}/edit")
    
    # Checklist
    issues = []
    
    # Title Check
    if len(title) < 30:
        issues.append("❌ Titel zu kurz")
    if '8K' not in title and '8k' not in title:
        issues.append("⚠️ Kein 8K im Titel")
    if '@remAIke' not in title:
        issues.append("⚠️ Kein @remAIke_IT")
    
    # Description Check
    if len(desc) < 100:
        issues.append("❌ Beschreibung zu kurz")
    elif len(desc) < 200:
        issues.append("⚠️ Beschreibung kurz")
    
    # Tags Check
    if len(tags) < 5:
        issues.append("⚠️ Wenige Tags ({})".format(len(tags)))
    
    if issues:
        print(f"     Issues: {', '.join(issues)}")
    else:
        print(f"     ✅ Ready to publish!")
    
    print()

# Kategorisieren
print("=" * 70)
print("📊 DRAFT-KATEGORIEN:")
print("=" * 70)

categories = {}
for d in drafts:
    title = d['snippet'].get('title', '').lower()
    if 'wochenschau' in title:
        cat = 'Wochenschau'
    elif 'bravestarr' in title:
        cat = 'BraveStarr'
    elif 'soundie' in title:
        cat = 'Soundies'
    elif 'alfred' in title or 'quack' in title:
        cat = 'Alfred J. Kwak'
    elif 'betty' in title:
        cat = 'Betty Boop'
    else:
        cat = 'Sonstige'
    
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(d['snippet'].get('title', ''))

for cat, titles in sorted(categories.items()):
    print(f"\n{cat} ({len(titles)}):")
    for t in titles:
        print(f"  • {t[:60]}")
