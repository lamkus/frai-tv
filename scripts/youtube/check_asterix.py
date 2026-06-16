#!/usr/bin/env python3
"""Check Asterix Videos"""
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))

print('=' * 70)
print('🏛️ ASTERIX VIDEOS')
print('=' * 70)
print()

all_videos = data.get('public_videos', []) + data.get('private_videos', [])

for v in all_videos:
    title = v['snippet'].get('title', '').lower()
    if 'asterix' in title:
        vid = v['id']
        full_title = v['snippet'].get('title', '')
        status = v['status'].get('privacyStatus', 'unknown')
        desc = v['snippet'].get('description', '')
        tags = v['snippet'].get('tags', [])
        
        status_icon = '🟢 PUBLIC' if status == 'public' else '🔴 DRAFT'
        
        print(f"📹 {full_title}")
        print(f"   ID: {vid}")
        print(f"   Status: {status_icon}")
        print(f"   Studio: https://studio.youtube.com/video/{vid}/edit")
        print(f"   Desc: {len(desc)} chars")
        print(f"   Tags: {len(tags)}")
        
        # SEO Check
        issues = []
        if '8K' not in full_title and '8k' not in full_title:
            issues.append("❌ Kein 8K")
        if '@remAIke' not in full_title:
            issues.append("❌ Kein @remAIke_IT")
        if len(desc) < 100:
            issues.append("❌ Keine Description")
        if len(tags) < 5:
            issues.append("❌ Keine Tags")
            
        if issues:
            print(f"   Issues: {', '.join(issues)}")
        else:
            print(f"   ✅ SEO OK")
        print()
