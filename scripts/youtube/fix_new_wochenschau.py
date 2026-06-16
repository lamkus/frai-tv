#!/usr/bin/env python3
"""Fix 4 new Wochenschau uploads (titles, description, tags, category)"""
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import sys
import json

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if creds.expired:
    creds.refresh(Request())
yt = build('youtube', 'v3', credentials=creds)

# Wochenschau description template
WS_DESCRIPTION_TEMPLATE = """⚠️ HISTORISCHES DOKUMENT — Dieses Video zeigt Original-Material der NS-Propaganda-Wochenschau. Es dient ausschließlich der historischen Dokumentation und Bildung. Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.

🎬 Deutsche Wochenschau Nr. {nr} – {event} ({date})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #WWII #History #Documentary #8K
"""

FIXES = {
    '2HZx5FumOo8': {
        'nr': '552',
        'date': '02.04.1941',
        'event': 'Belgrade Coup',
        'title': 'Wochenschau 552: Belgrade Coup (02.04.1941) | 8K HQ (4K UHD)',
    },
    'Yhz7gsTVqNA': {
        'nr': '567',
        'date': '16.07.1941',
        'event': 'Smolensk Pocket',
        'title': 'Wochenschau 567: Smolensk Pocket (16.07.1941) | 8K HQ (4K UHD)',
    },
    'suxhPHyaQHU': {
        'nr': '569',
        'date': '30.07.1941',
        'event': 'Kiev Encirclement',
        'title': 'Wochenschau 569: Kiev Encirclement (30.07.1941) | 8K HQ (4K UHD)',
    },
    '6Mh7zjUCmHw': {
        'nr': '749',
        'date': '10.01.1945',
        'event': 'Ardennes Fails',
        'title': 'Wochenschau 749: Ardennes Fails (10.01.1945) | 8K HQ (4K UHD)',
    }
}

# Standard tags for Wochenschau
WS_TAGS = [
    "Wochenschau",
    "Deutsche Wochenschau",
    "World War II",
    "WWII",
    "WW2",
    "History",
    "Documentary",
    "8K",
    "remastered",
    "restored",
    "public domain",
    "vintage newsreel",
    "historical footage",
    "1940s",
    "AI enhanced"
]

apply = "--apply" in sys.argv
mode = "APPLY" if apply else "DRY-RUN"

print(f"=== Fix 4 Wochenschau Uploads [{mode}] ===\n")

quota_used = 0
results = []

for vid_id, fix in FIXES.items():
    print(f"[{vid_id}] Wochenschau {fix['nr']}")
    print(f"  Title: {fix['title'][:60]}")
    
    description = WS_DESCRIPTION_TEMPLATE.format(
        nr=fix['nr'],
        event=fix['event'],
        date=fix['date']
    )
    
    if apply:
        try:
            yt.videos().update(
                part='snippet',
                body={
                    'id': vid_id,
                    'snippet': {
                        'title': fix['title'],
                        'description': description,
                        'tags': WS_TAGS,
                        'categoryId': '27',  # Education
                        'defaultLanguage': 'de'
                    }
                }
            ).execute()
            quota_used += 50
            print(f"  ✅ Updated!")
            results.append({'id': vid_id, 'nr': fix['nr'], 'status': 'updated'})
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({'id': vid_id, 'nr': fix['nr'], 'status': 'error', 'error': str(e)})
    else:
        print(f"  🔍 [DRY-RUN] Would update")
        results.append({'id': vid_id, 'nr': fix['nr'], 'status': 'dry_run'})
    print()

print("=" * 60)
print(f"📊 Results: {len([r for r in results if r['status']=='updated'])} updated")
print(f"📊 Quota: {quota_used} units")

# Save report
with open('config/new_wochenschau_fix_report.json', 'w', encoding='utf-8') as f:
    json.dump({
        'date': '2026-02-20',
        'mode': mode,
        'quota_used': quota_used,
        'results': results
    }, f, indent=2)

print(f"💾 Report: config/new_wochenschau_fix_report.json")
