#!/usr/bin/env python3
"""
Verify Wochenschau SEO is correctly applied online
Check multilingual coverage
"""

import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

with open('config/youtube_oauth.json', 'r') as f:
    td = json.load(f)

yt = build('youtube', 'v3', credentials=Credentials(
    token=td['token'],
    refresh_token=td['refresh_token'],
    token_uri='https://oauth2.googleapis.com/token',
    client_id=td['client_id'],
    client_secret=td['client_secret']
))

# Check video 516 (Battle of Britain) as example
video_id = 'T-EsdXGhqog'
response = yt.videos().list(
    part='snippet',
    id=video_id
).execute()

if response['items']:
    snippet = response['items'][0]['snippet']
    
    print("=" * 70)
    print("ONLINE VERIFICATION: Wochenschau 516")
    print("=" * 70)
    
    print(f"\n📝 TITLE:")
    print(f"   {snippet['title']}")
    print(f"   Length: {len(snippet['title'])} chars")
    
    # Check title format
    title = snippet['title']
    checks = {
        'No "Nr."': 'Nr.' not in title,
        'Has date (DD.MM.YYYY)': '24.07.1940' in title,
        'Has 8K': '8K' in title,
        'Has @remAIke_IT': '@remAIke_IT' in title,
        'Keyword first': title.startswith('Wochenschau'),
    }
    
    print(f"\n✅ TITLE CHECKS:")
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    print(f"\n🏷️ TAGS ({len(snippet.get('tags', []))} total):")
    tags = snippet.get('tags', [])
    for i, tag in enumerate(tags[:15]):
        print(f"   {i+1:2d}. {tag}")
    
    # Check multilingual tags
    print(f"\n🌍 MULTILINGUAL CHECK:")
    languages = {
        'English': any(t for t in tags if 'WWII' in t or 'Battle' in t),
        'German': any(t for t in tags if 'Luftschlacht' in t or 'Wochenschau' in t),
        'Spanish': any(t for t in tags if 'Segunda' in t or 'Batalla' in t),
        'Japanese': any(t for t in tags if 'バトル' in t or '第二次' in t or '戦' in t),
        'Russian': any(t for t in tags if 'Битва' in t or 'война' in t),
        'Portuguese': any(t for t in tags if 'Guerra' in t or 'Batalha' in t),
        'Hindi': any(t for t in tags if 'युद्ध' in t or 'लड़ाई' in t),
        'Chinese': any(t for t in tags if '二战' in t or '战争' in t),
        'Arabic': any(t for t in tags if 'الحرب' in t),
        'French': any(t for t in tags if 'Bataille' in t or 'Guerre' in t),
    }
    
    for lang, found in languages.items():
        status = "✅" if found else "❌ MISSING"
        print(f"   {status} {lang}")
    
    print(f"\n📄 DESCRIPTION (first 500 chars):")
    print("-" * 70)
    desc = snippet['description']
    print(desc[:500])
    print("...")
    print("-" * 70)
    
    # Check description content
    print(f"\n✅ DESCRIPTION CHECKS:")
    desc_checks = {
        'Has Spanish line': 'ESPAÑOL' in desc or 'Segunda Guerra' in desc,
        'Has Portuguese line': 'PORTUGUÊS' in desc or 'Segunda Guerra' in desc,
        'Has Japanese line': '日本語' in desc or '第二次世界大戦' in desc,
        'Has CTA (LIKE)': 'LIKE' in desc,
        'Has CTA (SUBSCRIBE)': 'SUBSCRIBE' in desc,
        'Has locations': 'LOCATIONS' in desc,
        'Has historical context DE': '🇩🇪' in desc or 'DEUTSCH' in desc,
        'Has historical context EN': '🇬🇧' in desc or 'ENGLISH' in desc,
        'Has hashtags': '#Wochenschau' in desc,
    }
    
    for check, passed in desc_checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
    
    # Summary
    title_score = sum(checks.values()) / len(checks) * 100
    tag_score = sum(languages.values()) / len(languages) * 100
    desc_score = sum(desc_checks.values()) / len(desc_checks) * 100
    
    print(f"\n" + "=" * 70)
    print(f"SCORES:")
    print(f"   Title Format:  {title_score:.0f}%")
    print(f"   Multilingual:  {tag_score:.0f}% ({sum(languages.values())}/{len(languages)} languages)")
    print(f"   Description:   {desc_score:.0f}%")
    print(f"   OVERALL:       {(title_score + tag_score + desc_score) / 3:.0f}%")
    print("=" * 70)
    
    # Show what's missing
    missing_langs = [lang for lang, found in languages.items() if not found]
    if missing_langs:
        print(f"\n⚠️ MISSING LANGUAGES IN TAGS: {', '.join(missing_langs)}")
