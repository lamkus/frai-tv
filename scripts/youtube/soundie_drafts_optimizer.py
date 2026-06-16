#!/usr/bin/env python3
"""Soundie Drafts Optimizer - Private Soundies veröffentlichungsfertig machen

Optimiert:
1. Titel im Format: Soundie: [Song Name] (Year) | 8K HQ | Vintage Music | @remAIke_IT
2. YouTube Music Tags
3. Beschreibung mit Serieninfos
"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import json
import re
import time
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def get_youtube():
    oauth = load_json(CONFIG / "youtube_oauth.json")
    creds = Credentials(
        token=oauth.get("token"),
        refresh_token=oauth.get("refresh_token"),
        token_uri=oauth.get("token_uri"),
        client_id=oauth.get("client_id"),
        client_secret=oauth.get("client_secret"),
        scopes=oauth.get("scopes"),
    )
    if creds.expired:
        creds.refresh(Request())
        oauth["token"] = creds.token
        save_json(CONFIG / "youtube_oauth.json", oauth)
    return build("youtube", "v3", credentials=creds)

# YouTube Music optimierte Tags
SOUNDIE_TAGS = [
    "Soundie", "Soundies", "1940s", "Panoram", "jukebox",
    "Mills Novelty Company", "music video", "vintage music",
    "swing era", "big band", "jazz", "Official Audio",
    "music", "song", "official video", "vintage music video",
    "classic music", "retro music", "jazz music", "swing music",
    "1940s music", "big band music", "boogie woogie",
    "rhythm and blues", "jazz standard", "golden age music",
    "8K", "4K UHD", "restored", "remastered", "remAIke"
]

# Song-spezifische Tags
SONG_KNOWLEDGE = {
    "heaven help a sailor": {
        "title": "Heaven Help a Sailor on a Night Like This",
        "tags": ["sailor song", "navy", "romantic"]
    },
    "jiveroo": {
        "title": "Jiveroo",
        "tags": ["jive", "dance", "swing dance"]
    },
    "shanty": {
        "title": "In a Shanty in Old Shanty Town",
        "tags": ["shanty town", "jazz standard", "1932"]
    },
    "anything but love": {
        "title": "I Cant Give You Anything But Love",
        "tags": ["Jimmy McHugh", "Dorothy Fields", "jazz standard", "1928"]
    },
    "hollywood boogie": {
        "title": "Hollywood Boogie",
        "tags": ["Hadda Brooks", "Queen of Boogie", "boogie woogie", "piano", "R&B"]
    },
    "what this country needs": {
        "title": "What This Country Needs",
        "tags": ["comedy", "novelty song"]
    },
    "jazz etude": {
        "title": "A Jazz Etude",
        "tags": ["jazz", "instrumental", "etude"]
    },
    "ten pretty girls": {
        "title": "Ten Pretty Girls",
        "tags": ["girls", "dance", "showgirls"]
    },
    "hawaiian": {
        "title": "Hawaiian Hula Song",
        "tags": ["Hawaiian", "hula", "tropical", "ukulele", "island music"]
    },
    "zig me baby": {
        "title": "Zig Me Baby with a Gentle Zag",
        "tags": ["novelty", "dance", "swing"]
    },
    "yehudi": {
        "title": "Whos Yehudi",
        "tags": ["Yehudi Menuhin", "comedy", "novelty"]
    },
    "robin told me": {
        "title": "A Little Robin Told Me So",
        "tags": ["robin", "bird", "romantic", "spring"]
    },
    "beyond the blue horizon": {
        "title": "Beyond the Blue Horizon",
        "tags": ["Leo Robin", "Richard Whiting", "1930", "Jeanette MacDonald"]
    },
    "havana madrid": {
        "title": "Havana Madrid Show",
        "tags": ["Havana", "Madrid", "Latin", "Cuban", "nightclub"]
    },
    "got to be": {
        "title": "Got to Be This or That",
        "tags": ["Benny Goodman", "swing", "big band"]
    }
}

SOUNDIE_DESCRIPTION = """🎵 Soundie: {song_title} | Vintage Music Film (1940s)

═══════════════════════════════════════════════════════════
🎬 WAS SIND SOUNDIES?
═══════════════════════════════════════════════════════════

Soundies waren kurze Musikfilme (3 Minuten), die von 1940-1947 
für Panoram Jukeboxen produziert wurden - die Vorläufer der 
modernen Musikvideos!

• 🎥 Produziert von Mills Novelty Company
• 📺 Gezeigt auf Panoram Visual Jukeboxen
• 🎵 Die ersten "Musikvideos" der Geschichte
• ⭐ Mit legendären Jazz & Swing Künstlern

═══════════════════════════════════════════════════════════
🌟 ÜBER DIESE VERSION
═══════════════════════════════════════════════════════════

• 8K AI-Upscaling (4K UHD verfügbar)
• Restauriert & Remastered
• Best Quality Online

📌 ABONNIEREN für mehr Vintage Musik!

▶️ Soundies Playlist: [Link zur Playlist]

#Soundie #Soundies #1940s #VintageMusic #Jazz #Swing #BigBand 
#JukeboxFilm #Panoram #ClassicMusic #RetroMusic #remAIke
"""

def extract_song_name(title):
    """Extrahiert Songnamen aus Titel"""
    # Entferne "soundie" prefix und "sls 8K HQ" suffix
    clean = re.sub(r'^soundie\s*', '', title, flags=re.IGNORECASE)
    clean = re.sub(r'\s*sls\s*8K\s*HQ.*$', '', clean, flags=re.IGNORECASE)
    clean = clean.strip()
    return clean

def find_song_info(title):
    """Findet Song-Infos aus Knowledge Base"""
    title_lower = title.lower()
    for key, info in SONG_KNOWLEDGE.items():
        if key in title_lower:
            return info
    return None

def create_new_title(raw_title):
    """Erstellt optimierten Titel"""
    song_name = extract_song_name(raw_title)
    
    # Versuche besseren Namen aus Knowledge Base
    info = find_song_info(raw_title)
    if info:
        song_name = info["title"]
    else:
        # Capitalize words
        song_name = " ".join(word.capitalize() for word in song_name.split())
    
    return f"Soundie: {song_name} | 8K HQ (4K UHD) | Vintage Music Film | @remAIke_IT"

def create_tags(raw_title):
    """Erstellt optimierte Tags"""
    tags = SOUNDIE_TAGS.copy()
    
    info = find_song_info(raw_title)
    if info:
        tags.extend(info.get("tags", []))
    
    # Deduplizieren
    seen = set()
    result = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            result.append(tag)
    
    # Limitieren auf 500 chars
    kept = []
    for tag in result:
        if len(",".join(kept + [tag])) <= 500:
            kept.append(tag)
    return kept

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--publish", action="store_true", help="Auch veroeffentlichen (public)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("SOUNDIE DRAFTS OPTIMIZER")
    print("YouTube Music optimiert!")
    print("=" * 60)
    
    youtube = get_youtube()
    scan = load_json(CONFIG / "full_channel_scan.json")
    
    # Nur private Soundies (Entwürfe)
    soundies = [v for v in scan["all_videos"] 
                if "soundi" in v["title"].lower() and v["status"] == "private"]
    
    print(f"\n[Gefunden] {len(soundies)} private Soundie-Entwuerfe")
    
    results = []
    
    for i, snd in enumerate(soundies, 1):
        vid = snd["id"]
        old_title = snd["title"]
        
        new_title = create_new_title(old_title)
        new_tags = create_tags(old_title)
        
        song_info = find_song_info(old_title)
        song_name = song_info["title"] if song_info else extract_song_name(old_title)
        new_desc = SOUNDIE_DESCRIPTION.format(song_title=song_name)
        
        print(f"\n[{i}/{len(soundies)}] {old_title[:45]}...")
        print(f"   Neu: {new_title[:50]}...")
        print(f"   Tags: {len(new_tags)}")
        
        result = {
            "id": vid,
            "old_title": old_title,
            "new_title": new_title,
            "tags": len(new_tags),
            "action": "pending"
        }
        
        if args.apply:
            try:
                resp = youtube.videos().list(part="snippet,status", id=vid).execute()
                if resp.get("items"):
                    item = resp["items"][0]
                    snippet = item["snippet"]
                    status = item["status"]
                    
                    snippet["title"] = new_title
                    snippet["description"] = new_desc
                    snippet["tags"] = new_tags
                    
                    # Optional: Veröffentlichen
                    if args.publish:
                        status["privacyStatus"] = "public"
                        youtube.videos().update(
                            part="snippet,status",
                            body={"id": vid, "snippet": snippet, "status": status}
                        ).execute()
                        result["action"] = "PUBLISHED"
                        print(f"   [OK] Veroeffentlicht!")
                    else:
                        youtube.videos().update(
                            part="snippet",
                            body={"id": vid, "snippet": snippet}
                        ).execute()
                        result["action"] = "UPDATED"
                        print(f"   [OK] Aktualisiert (bleibt privat)")
                else:
                    result["action"] = "NOT_FOUND"
            except HttpError as e:
                if "quotaExceeded" in str(e):
                    result["action"] = "QUOTA"
                    print("   [STOP] Quota!")
                    results.append(result)
                    break
                result["action"] = f"ERROR: {e}"
                print(f"   [ERROR] {e}")
            
            time.sleep(0.5)
        else:
            result["action"] = "DRY-RUN"
        
        results.append(result)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "total": len(soundies),
        "results": results
    }
    save_json(CONFIG / "soundie_drafts_report.json", report)
    print(f"\n[Report] {CONFIG / 'soundie_drafts_report.json'}")
    
    if not args.apply:
        print("\n[DRY-RUN] Mit --apply ausfuehren!")
        print("          Mit --apply --publish auch veroeffentlichen!")

if __name__ == "__main__":
    main()
