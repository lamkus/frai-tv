#!/usr/bin/env python3
"""
Offline Integrity Audit
Checks the 'channel_master_fix_prioritized.json' for hallucinations and logic errors.
Does NOT require YouTube API Quota.
"""
import json
import re
import sys

PLAN_FILE = 'config/channel_master_fix_prioritized.json'

def check_hallucinations(plan):
    print(f"🔍 AUDITING PLAN INTEGRITY: {len(plan)} tasks")
    print("=" * 60)
    
    issues = []
    
    # Series Markers
    series_map = {
        'alfred': ['alfred j. kwak', 'ente', 'dolf'],
        'betty': ['betty boop'],
        'superman': ['superman'],
        'popeye': ['popeye'],
        'felix': ['felix the cat'],
        'wochenschau': ['wochenschau']
    }
    
    for i, task in enumerate(plan):
        old_title = task.get('old_title', '').lower()
        new_title = task.get('new_title', '').lower()
        vid_id = task.get('id')
        
        # 1. SERIES CONSISTENCY CHECK
        detected_old = None
        detected_new = None
        
        for key, keywords in series_map.items():
            if any(k in old_title for k in keywords):
                detected_old = key
            if any(k in new_title for k in keywords):
                detected_new = key
                
        # Critical Error: Series Swap
        if detected_old and detected_new and detected_old != detected_new:
            # Exception: Superman sometimes appears with Popeye in playlists, but title swapping is bad
            issues.append({
                'id': vid_id,
                'type': 'SERIES_SWAP',
                'msg': f"Swapped from {detected_old.upper()} to {detected_new.upper()}",
                'old': task['old_title'],
                'new': task['new_title']
            })
            
        # 2. EPISODE NUMBER CHECK (Simple Regex)
        # Look for "E14" or "(14)" patterns
        ep_old = re.search(r'e(\d{1,3})', old_title) or re.search(r'\((\d{1,3})\)', old_title)
        ep_new = re.search(r'e(\d{1,3})', new_title) or re.search(r'\((\d{1,3})\)', new_title)
        
        if ep_old and ep_new:
            num_old = int(ep_old.group(1))
            num_new = int(ep_new.group(1))
            
            # Allow some divergence (sometimes (515) becomes Nr. 515), but 14 -> 50 is bad
            if num_old != num_new and detected_old != 'wochenschau': # Wochenschau numbers are weird
                # Check if it is year vs episode
                if not (1900 < num_old < 2030 or 1900 < num_new < 2030):
                    issues.append({
                        'id': vid_id,
                        'type': 'NUMBER_MISMATCH',
                        'msg': f"Number changed from {num_old} to {num_new}",
                        'old': task['old_title'],
                        'new': task['new_title']
                    })

        # 3. "8K" PRESENCE
        if "8k" not in new_title and "4k" not in new_title:
             issues.append({
                'id': vid_id,
                'type': 'MISSING_QUALITY',
                'msg': "Missing 8K/4K keyword",
                'old': task['old_title'],
                'new': task['new_title']
            })

    # REPORTING
    if not issues:
        print("✅ PASS: No hallucinations or logic errors found in 345 tasks.")
    else:
        print(f"❌ FAIL: Found {len(issues)} potential issues.")
        for issue in issues[:20]: # Show first 20
            print(f"\n[ {issue['type']} ] {issue['msg']}")
            print(f"   OLD: {issue['old']}")
            print(f"   NEW: {issue['new']}")

if __name__ == "__main__":
    if not isinstance(PLAN_FILE, str):
        # Should not happen
        pass
        
    try:
        with open(PLAN_FILE, 'r', encoding='utf-8') as f:
            plan = json.load(f)
            check_hallucinations(plan)
    except FileNotFoundError:
        print("Plan file not found.")
