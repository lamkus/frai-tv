#!/usr/bin/env python3
"""Rename drafts + fix livestream title.
Quota: 5 x videos.update = 250 Units
"""
import os, json, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_youtube():
    creds = Credentials.from_authorized_user_file('token.json')
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

# === DRAFT RENAMES (4 Wochenschau ARCHIVE PROTECTED) ===
DRAFT_UPDATES = [
    {
        "id": "NKjPNR8t_Yk",
        "nr": 705,
        "title": "Wochenschau 705: Cassino III (08.03.1944) | 8K HQ (4K UHD)",
        "event_en": "Cassino III",
        "event_de": "Cassino III",
        "date": "1944-03-08",
        "location": "Monte Cassino, Italy",
        "note": "Dritte Schlacht um Monte Cassino"
    },
    {
        "id": "CgrWBr68rng",
        "nr": 699,
        "title": "Wochenschau 699: Anzio Landing (26.01.1944) | 8K HQ (4K UHD)",
        "event_en": "Anzio Landing",
        "event_de": "Anzio Landung",
        "date": "1944-01-26",
        "location": "Anzio, Italy",
        "note": "Alliierte landen bei Anzio (22.01.1944)"
    },
    {
        "id": "ULW1rl24JLM",
        "nr": 703,
        "title": "Wochenschau 703: Big Week (23.02.1944) | 8K HQ (4K UHD)",
        "event_en": "Big Week",
        "event_de": "Big Week",
        "date": "1944-02-23",
        "location": "Germany",
        "note": "Alliierte Luftoffensive gegen Luftwaffe"
    },
    {
        "id": "a-mad6-VBuU",
        "nr": 704,
        "title": "Wochenschau 704: Air Supremacy Lost (01.03.1944) | 8K HQ (4K UHD)",
        "event_en": "Air Supremacy Lost",
        "event_de": "Luftherrschaft verloren",
        "date": "1944-03-01",
        "location": "Germany",
        "note": "Alliierte gewinnen Lufthoheit"
    },
]

# === LIVESTREAM FIX ===
LIVESTREAM_ID = "lm4EcKHQ45o"
LIVESTREAM_NEW_TITLE = "📺 WochenschauTV 🔴 LIVE 24/7 | Deutsche Wochenschau | 4K Highest Quality"

def build_wochenschau_description(ep):
    """Build SEO-optimized description for Wochenschau draft."""
    nr = ep["nr"]
    event_en = ep["event_en"]
    event_de = ep["event_de"]
    date = ep["date"]
    location = ep["location"]
    note = ep["note"]
    
    # Parse date for display
    parts = date.split("-")
    date_display = f"{parts[2]}.{parts[1]}.{parts[0]}"
    year = parts[0]
    
    desc = f"""⚠️ HISTORISCHES DOKUMENT — Dieses Video dient ausschließlich der historischen Dokumentation und Bildung.
🎬 Deutsche Wochenschau Nr. {nr}: {event_en} | {event_de}
📅 {date_display} | 📍 {location}
{note}

Original WWII German newsreel, AI remastered in stunning 8K quality.
Historische Wochenschau aus dem Zweiten Weltkrieg, KI-restauriert in 8K HQ (4K UHD).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

🔍 Search: Deutsche Wochenschau {nr}, {event_en} {year}, WWII newsreel, Wochenschau {date_display}
🌍 Recherche: Wochenschau allemande, Noticiario alemán, Cinejornal alemão, जर्मन न्यूज़रील, Wochenschau Jerman

#Wochenschau #WWII #8K #History #PublicDomain"""
    return desc

WOCHENSCHAU_TAGS = [
    "wochenschau", "deutsche wochenschau", "wwii", "world war 2", "ww2",
    "8k", "4k uhd", "remastered", "restored", "AI enhanced",
    "historical footage", "newsreel", "vintage newsreel",
    "public domain", "history"
]

def main():
    youtube = get_youtube()
    mode = "--apply" in sys.argv
    
    print("=" * 60)
    print("DRAFT RENAME + LIVESTREAM FIX")
    print(f"Mode: {'APPLY (LIVE!)' if mode else 'DRY RUN (--apply to execute)'}")
    print("=" * 60)
    
    quota_used = 0
    
    # === 1) Rename 4 Drafts ===
    print("\n--- DRAFT RENAMES ---")
    for ep in DRAFT_UPDATES:
        vid_id = ep["id"]
        new_title = ep["title"]
        new_desc = build_wochenschau_description(ep)
        
        print(f"\n  [{vid_id}] Nr. {ep['nr']}")
        print(f"  → Title: {new_title}")
        print(f"  → Desc: {new_desc[:100]}...")
        print(f"  → Tags: {len(WOCHENSCHAU_TAGS)} tags")
        
        if mode:
            # First get current snippet to preserve what we need
            current = youtube.videos().list(part='snippet,status', id=vid_id).execute()
            quota_used += 1
            
            if not current.get('items'):
                print(f"  ❌ Video not found!")
                continue
            
            item = current['items'][0]
            snippet = item['snippet']
            
            # Update
            snippet['title'] = new_title
            snippet['description'] = new_desc
            snippet['tags'] = WOCHENSCHAU_TAGS
            snippet['categoryId'] = '27'  # Education
            
            try:
                youtube.videos().update(
                    part='snippet',
                    body={'id': vid_id, 'snippet': snippet}
                ).execute()
                quota_used += 50
                print(f"  ✅ UPDATED!")
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
        else:
            print(f"  [DRY RUN]")
    
    # === 2) Fix Livestream Title ===
    print("\n--- LIVESTREAM TITLE FIX ---")
    print(f"  [{LIVESTREAM_ID}]")
    print(f"  → New Title: {LIVESTREAM_NEW_TITLE}")
    
    if mode:
        # Get current livestream data
        current = youtube.videos().list(part='snippet,status', id=LIVESTREAM_ID).execute()
        quota_used += 1
        
        if current.get('items'):
            item = current['items'][0]
            snippet = item['snippet']
            old_title = snippet['title']
            print(f"  Old Title: {old_title}")
            
            # Only update title, keep everything else
            snippet['title'] = LIVESTREAM_NEW_TITLE
            
            try:
                youtube.videos().update(
                    part='snippet',
                    body={'id': LIVESTREAM_ID, 'snippet': snippet}
                ).execute()
                quota_used += 50
                print(f"  ✅ LIVESTREAM TITLE UPDATED!")
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
        else:
            print(f"  ❌ Livestream not found!")
    else:
        print(f"  [DRY RUN]")
    
    # === Summary ===
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Drafts to rename: {len(DRAFT_UPDATES)}")
    print(f"  Livestream title fix: 1")
    if mode:
        print(f"  Quota used: ~{quota_used} Units")
        print(f"  (4 reads + 4 writes + 1 read + 1 write = ~255 Units)")
    else:
        print(f"  Estimated quota: ~255 Units (5 x 50 writes + 5 reads)")
        print(f"\n  Run with --apply to execute!")
    print("=" * 60)

if __name__ == '__main__':
    main()
