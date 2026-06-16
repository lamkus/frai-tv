#!/usr/bin/env python3
"""Fix livestream description — everything is wrong."""
import os, re, json, sys
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

def get_episode_info():
    """Read current concat file and event data."""
    with open('logs/stream_concat.txt', 'r') as f:
        lines = f.readlines()
    
    episodes = []
    for line in lines:
        line = line.strip()
        if line.startswith('file ') and 'wochenschau' in line.lower():
            m = re.search(r'nr(\d+)', line, re.IGNORECASE)
            if not m:
                m = re.search(r'(\d{3,4})', line)
            if m:
                episodes.append(int(m.group(1)))
    
    with open('config/wochenschau_events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    events = data.get('events', data)
    
    return episodes, events

def main():
    episodes, events = get_episode_info()
    
    print(f"Episodes in stream: {len(episodes)}")
    print(f"First: Nr. {episodes[0]}, Last: Nr. {episodes[-1]}")
    print(f"459 blocked: {459 not in episodes}")
    print(f"513 blocked: {513 not in episodes}")
    
    # Get year range
    dates = []
    for nr in episodes:
        key = str(nr)
        if key in events:
            dates.append(events[key]['date'])
    years = sorted(set(d[:4] for d in dates)) if dates else ['1939', '1945']
    year_range = f"{years[0]}–{years[-1]}"
    
    # Build episode list for description (first 10)
    episode_lines = []
    for nr in episodes[:10]:
        key = str(nr)
        if key in events:
            e = events[key]
            episode_lines.append(f"  ▸ Nr. {nr}: {e['event_en']} ({e['date'][:4]})")
        else:
            episode_lines.append(f"  ▸ Nr. {nr}")
    
    episode_list = "\n".join(episode_lines)
    
    # Build Nr range string
    all_nrs = sorted(episodes)
    nr_range = f"Nr. {all_nrs[0]}–{all_nrs[-1]}"
    
    # === NEW DESCRIPTION ===
    new_description = f"""⚠️ HISTORISCHES DOKUMENT — Inhalte dienen ausschließlich der historischen Dokumentation und Bildung.

📺 WochenschauTV — 24/7 Deutsche Wochenschau Livestream in 4K Highest Quality
🔴 {len(episodes)} Episoden in chronologischer Rotation ({year_range})
📋 Episoden: {nr_range} (ohne gesperrte Nummern)

Original WWII German newsreel, AI remastered and restored for modern screens.
Historische Deutsche Wochenschau aus dem Zweiten Weltkrieg, KI-restauriert und in 4K gestreamt.

📋 EPISODE ROTATION:
{episode_list}
  ... und {len(episodes) - 10} weitere Episoden

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE wenn dir der Stream gefällt!
💬 KOMMENTIERE deine Gedanken!
🔔 ABONNIERE für mehr historisches Material!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

🔍 Deutsche Wochenschau, WWII newsreel, Zweiter Weltkrieg, World War 2, historical footage, vintage newsreel, archive footage
🌍 Cinejornal alemão, Noticiario alemán, Actualités allemandes, जर्मन न्यूज़रील, Wochenschau Jerman

#Wochenschau #WWII #History #4K #PublicDomain"""
    
    # === NEW TAGS (4K focused, NOT 8K) ===
    new_tags = [
        "4k", "4k uhd", "highest quality", "AI enhanced",
        "WochenschauTV", "archive footage", "deutsche wochenschau",
        "historical footage", "newsreel", "public domain",
        "remastered", "restored", "wochenschau",
        "world war 2", "wwii"
    ]
    
    print(f"\n=== NEW TITLE (unchanged) ===")
    print("📺 WochenschauTV 🔴 LIVE 24/7 | Deutsche Wochenschau | 4K Highest Quality")
    print(f"\n=== NEW DESCRIPTION ===")
    print(new_description)
    print(f"\n=== NEW TAGS ({len(new_tags)}) ===")
    print(new_tags)
    
    mode = "--apply" in sys.argv
    
    if mode:
        youtube = get_youtube()
        
        # Get current snippet
        current = youtube.videos().list(part='snippet,status', id='lm4EcKHQ45o').execute()
        if not current.get('items'):
            print("ERROR: Livestream not found!")
            return
        
        snippet = current['items'][0]['snippet']
        old_desc = snippet.get('description', '')
        
        print(f"\n--- OLD DESCRIPTION (first 3 lines) ---")
        for line in old_desc.split('\n')[:3]:
            print(f"  {line}")
        
        # Update
        snippet['description'] = new_description
        snippet['tags'] = new_tags
        # Title already correct from previous update
        
        youtube.videos().update(
            part='snippet',
            body={'id': 'lm4EcKHQ45o', 'snippet': snippet}
        ).execute()
        
        print("\n✅ LIVESTREAM DESCRIPTION + TAGS UPDATED!")
        print("Quota used: ~51 Units (1 read + 1 write)")
    else:
        print(f"\n[DRY RUN] — run with --apply to execute")
        print(f"Quota cost: ~51 Units")

if __name__ == '__main__':
    main()
