#!/usr/bin/env python3
"""Check Wochenschau/Nürnberg Videos"""
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

data = json.loads(Path('config/fresh_channel_scan.json').read_text(encoding='utf-8'))

print('=' * 70)
print('🎬 WOCHENSCHAU / NÜRNBERG VIDEOS')
print('=' * 70)
print()

all_videos = data.get('public_videos', []) + data.get('private_videos', [])

found = []
for v in all_videos:
    title = v['snippet'].get('title', '').lower()
    desc = v['snippet'].get('description', '').lower()
    
    # Suche nach Wochenschau, Nürnberg, Nuremberg
    if any(kw in title or kw in desc for kw in ['wochenschau', 'nr 7', 'nürnberg', 'nuremberg', 'nazi', 'trial']):
        found.append(v)

print(f"Gefunden: {len(found)} Videos\n")

for v in found:
    vid = v['id']
    title = v['snippet'].get('title', '')
    status = v['status'].get('privacyStatus', 'unknown')
    desc = v['snippet'].get('description', '')
    tags = v['snippet'].get('tags', [])
    
    print(f"📹 {title}")
    print(f"   ID: {vid}")
    print(f"   Status: {'🟢 PUBLIC' if status == 'public' else '🔴 ' + status.upper()}")
    print(f"   Studio: https://studio.youtube.com/video/{vid}/edit")
    print(f"   Desc length: {len(desc)} chars")
    print(f"   Tags: {len(tags)}")
    
    # Check für Nürnberg-Keywords
    nurnberg_kw = ['nürnberg', 'nuremberg', 'trial', 'prozess', 'nazi', 'kriegsverbrecher']
    has_nurnberg = any(kw in title.lower() or kw in desc.lower() for kw in nurnberg_kw)
    if has_nurnberg:
        print(f"   🎯 NÜRNBERG-BEZUG erkannt!")
    
    print()
