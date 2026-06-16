"""Quick verification: check a few fixed videos live."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from mega_fix import get_youtube_service

yt = get_youtube_service()

# Check some previously broken Betty Boop titles
check_ids = [
    'EMQSoqxYWEI',  # Betty Boop May Party - had @remA...
    'VJZPCGZFfTA',  # Betty Boop Bamboo Isle - had @re...
    'I8R0mmVKXm4',  # Betty Boop Ups and Downs - had @...
    'zogZ5nzJCTE',  # Betty Boop Stop That Noise - had |...|
    'Ot4M_FexpnQ',  # BraveStarr Intro - had @remAIke_IT
    'h_4m9a7wqoc',  # Betty Boop Dizzy Dishes - had @re...
    'ttE5cijN2XM',  # Betty Boop M.D. - had ||
]

resp = yt.videos().list(part='snippet', id=','.join(check_ids)).execute()

print("=== LIVE VERIFICATION ===\n")
issues = 0
for item in resp['items']:
    t = item['snippet']['title']
    d = item['snippet']['description']
    tags = item['snippet'].get('tags', [])
    
    problems = []
    if '@rem' in t or '@re' in t:
        problems.append('HANDLE IN TITLE')
    if '||' in t or '| |' in t:
        problems.append('DOUBLE PIPE')
    if '  ' in t:
        problems.append('DOUBLE SPACE')
    if '...' in t:
        problems.append('DOTS IN TITLE')
    if 'remaike.it' not in d.lower() and 'remaike.IT' not in d:
        problems.append('MISSING LINK')
    
    status = 'FAIL: ' + ', '.join(problems) if problems else 'OK'
    print(f"  [{status}] {t[:70]}")
    if problems:
        issues += 1

print(f"\n{'OK' if issues == 0 else 'ISSUES'}: {len(resp['items'])} checked, {issues} issues")
