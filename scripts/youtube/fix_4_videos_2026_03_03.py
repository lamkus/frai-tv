#!/usr/bin/env python3
"""
Fix 4 videos with SEO issues (from check_all_videos_now.py scan 2026-03-02).
Quota: 4 × 50 = 200 Units (videos.update)

1. o7-VFXC9xDg — Wochenschau 713 raw name → full SEO (private draft)
2. 57TykeHQYwU — Livestream, 0 tags → add tags
3. WAKX3d__J8E — Wochenschau 701, only 1 tag → add tags
4. FU9uhmbyyas — Wochenschau 706, only 1 tag → add tags

NOT touching: PI1iAvZGlxo (#1 short) — per user request
"""
import json, sys, io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

creds = Credentials.from_authorized_user_file('config/youtube_oauth.json')
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
youtube = build('youtube', 'v3', credentials=creds)

# ============================================================
# 1. o7-VFXC9xDg — Wochenschau Nr. 713 (Sevastopol Falls)
# ============================================================
WS713_TITLE = "Wochenschau 713: Sevastopol Falls (03.05.1944) | 8K HQ (4K UHD)"
WS713_DESC = """⚠️ HISTORISCHES DOKUMENT | HISTORICAL DOCUMENT | DOCUMENTO HISTÓRICO | 歴史的文書 | وثيقة تاريخية
Dieses Video zeigt Original-Material der NS-Propaganda-Wochenschau und dient ausschließlich der historischen Dokumentation und Bildung. Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.

🎬 Deutsche Wochenschau Nr. 713 (03.05.1944) – Sevastopol Falls
AI remastered in stunning 8K quality from original archive footage. The fall of Sevastopol on the Crimean Peninsula marked a significant German defeat on the Eastern Front in May 1944.

📍 Ort: Sevastopol, Crimea
📅 Datum: 03. Mai 1944
📰 Ereignis: Verlust von Sewastopol – After months of Soviet offensive operations, the strategic port city fell, ending German control of Crimea.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

🔍 Multilingual Search / Mehrsprachige Suche:
🇩🇪 Deutsche Wochenschau 1944, Sewastopol, Krim, Zweiter Weltkrieg
🇬🇧 German Newsreel 1944, Sevastopol, Crimea, World War II
🇫🇷 Actualités allemandes 1944, Sébastopol, Crimée, Seconde Guerre mondiale
🇪🇸 Noticiario alemán 1944, Sebastopol, Crimea, Segunda Guerra Mundial
🇵🇹 Noticiário alemão 1944, Sebastopol, Crimeia, Segunda Guerra Mundial
🇯🇵 ドイツニュース映画 1944年、セヴァストポリ、クリミア、第二次世界大戦
🇮🇳 जर्मन न्यूज़रील 1944, सेवस्तोपोल, क्रीमिया, द्वितीय विश्व युद्ध
🇮🇩 Berita Jerman 1944, Sevastopol, Krimea, Perang Dunia II

#Wochenschau #WWII #8K #History #PublicDomain"""

WS713_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "German Newsreel", "1944",
    "Sevastopol", "Sewastopol", "Crimea", "Krim", "Eastern Front",
    "World War II", "WWII", "8K", "remastered", "restored", "historical footage"
]

# ============================================================
# 2. 57TykeHQYwU — Livestream tags
# ============================================================
LIVE_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "German Newsreel", "WWII",
    "World War II", "4K", "livestream", "24/7", "history", "historical footage",
    "vintage newsreel", "remastered", "HistoryTV", "public domain", "documentary"
]

# ============================================================
# 3/4. Standard Wochenschau tags for 701 & 706
# ============================================================
WS_STANDARD_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "German Newsreel", "WWII",
    "World War II", "8K", "remastered", "restored", "historical footage",
    "vintage newsreel", "public domain", "documentary", "AI enhanced"
]

WS701_EXTRA = ["Monte Cassino", "1944", "Italy"]
WS706_EXTRA = ["Hungary", "1944", "Ungarn", "Eastern Front"]

# ============================================================
# EXECUTE FIXES
# ============================================================
results = []

def fix_video(video_id, updates, label):
    """Update a video. updates = dict with optional title, description, tags, categoryId"""
    print(f"\n{'='*60}")
    print(f"Fixing: {label}")
    print(f"ID: {video_id}")
    
    # First fetch current state
    current = youtube.videos().list(part='snippet,status', id=video_id).execute()
    if not current.get('items'):
        print(f"  ERROR: Video not found!")
        results.append({'id': video_id, 'label': label, 'status': 'NOT_FOUND'})
        return
    
    item = current['items'][0]
    snippet = item['snippet']
    
    print(f"  Current title: {snippet['title']}")
    print(f"  Current tags: {len(snippet.get('tags', []))} tags")
    print(f"  Privacy: {item['status']['privacyStatus']}")
    
    # Build update body
    body = {
        'id': video_id,
        'snippet': {
            'title': updates.get('title', snippet['title']),
            'description': updates.get('description', snippet.get('description', '')),
            'tags': updates.get('tags', snippet.get('tags', [])),
            'categoryId': updates.get('categoryId', snippet.get('categoryId', '27')),
        }
    }
    
    try:
        resp = youtube.videos().update(part='snippet', body=body).execute()
        new_title = resp['snippet']['title']
        new_tags = len(resp['snippet'].get('tags', []))
        print(f"  ✅ Updated!")
        print(f"  New title: {new_title}")
        print(f"  New tags: {new_tags} tags")
        results.append({'id': video_id, 'label': label, 'status': 'OK', 'title': new_title})
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        results.append({'id': video_id, 'label': label, 'status': f'ERROR: {e}'})

# 1. Wochenschau 713 — full SEO
fix_video('o7-VFXC9xDg', {
    'title': WS713_TITLE,
    'description': WS713_DESC,
    'tags': WS713_TAGS,
    'categoryId': '27',  # Education
}, 'Wochenschau 713: Sevastopol Falls (ROHNAMEN → SEO)')

# 2. Livestream — add tags
fix_video('57TykeHQYwU', {
    'tags': LIVE_TAGS,
}, 'Livestream 4K HistoryTV (0 tags → 15 tags)')

# 3. Wochenschau 701 — add tags
fix_video('WAKX3d__J8E', {
    'tags': WS_STANDARD_TAGS + WS701_EXTRA,
}, 'Wochenschau 701: Monte Cassino (1 tag → 16 tags)')

# 4. Wochenschau 706 — add tags
fix_video('FU9uhmbyyas', {
    'tags': WS_STANDARD_TAGS + WS706_EXTRA,
}, 'Wochenschau 706: Hungary (1 tag → 17 tags)')

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*60}")
print(f"ZUSAMMENFASSUNG")
print(f"{'='*60}")
for r in results:
    print(f"  {r['id']}: {r['status']} — {r['label']}")

print(f"\n📊 Quota: ~204 Units (4×videos.list + 4×videos.update)")
print(f"⚠️ PI1iAvZGlxo (#1) NICHT angefasst (per User-Wunsch)")
