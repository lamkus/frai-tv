#!/usr/bin/env python3
"""BraveStarr Drafts Optimizer - Private BraveStarr Episoden optimieren"""
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

# Episode Mapping
EPISODES = {
    "e02": (2, "Fallen Idol", "September 15, 1987"),
    "e04": (4, "Skuzz and Fuzz", "September 17, 1987"),
}

BRAVESTARR_TAGS = [
    "BraveStarr", "Bravestarr", "Filmation", "1987",
    "Space Western", "New Texas", "Marshal BraveStarr",
    "Thirty Thirty", "Tex Hex", "Stampede", "Shaman",
    "80s cartoon", "80er Zeichentrick", "Deutsch", "German",
    "8K", "4K UHD", "remastered", "AI upscaled", "remAIke",
    "Pat Fraley", "Charlie Adler", "Ed Gilbert",
    "Eyes of the Hawk", "Strength of the Bear",
    "classic cartoon", "nostalgia", "retro", "Mattel"
]

DESCRIPTION_TEMPLATE = """🤠 BraveStarr - Folge {ep_num} von 65 | 8K Deutsch

📺 "{ep_title}" - Original: {air_date}

═══════════════════════════════════════════════
🌟 ÜBER BRAVESTARR
═══════════════════════════════════════════════

BraveStarr ist eine Space-Western-Serie von Filmation (1987-1988).
Planet New Texas im 23. Jahrhundert.

👤 HAUPTCHARAKTERE:
• Marshal BraveStarr - Galaktischer Marshal
• Thirty/Thirty - Equestroid-Partner  
• Tex Hex - Hauptantagonist
• Shaman - Mystischer Mentor

⚡ BRAVESTARRS KRÄFTE:
• 👁️ Eyes of the Hawk | 👂 Ears of the Wolf
• 💪 Strength of the Bear | 🏃 Speed of the Puma

═══════════════════════════════════════════════
📋 KOMPLETTE SERIE
═══════════════════════════════════════════════
▶️ BraveStarr Playlist abonnieren!

#BraveStarr #Filmation #80sCartoon #SpaceWestern #Deutsch #8K #remAIke
"""

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    print("=" * 60)
    print("BRAVESTARR DRAFTS OPTIMIZER")
    print("=" * 60)
    
    youtube = get_youtube()
    scan = load_json(CONFIG / "full_channel_scan.json")
    
    # Private BraveStarr
    drafts = [v for v in scan["all_videos"] 
              if "bravestar" in v["title"].lower() and v["status"] == "private"]
    
    print(f"\n[Gefunden] {len(drafts)} private BraveStarr-Entwuerfe")
    
    for draft in drafts:
        vid = draft["id"]
        old_title = draft["title"]
        
        print(f"\n  {vid} | {old_title}")
        
        # Episode erkennen
        ep_match = re.search(r'e(\d+)', old_title.lower())
        if ep_match:
            ep_key = f"e{ep_match.group(1).zfill(2)}"
            if ep_key in EPISODES:
                ep_num, ep_title, air_date = EPISODES[ep_key]
                
                new_title = f"BraveStarr ({ep_num}/65): {ep_title} (1987) | 8K HQ | Deutsch | @remAIke_IT"
                new_desc = DESCRIPTION_TEMPLATE.format(
                    ep_num=ep_num, ep_title=ep_title, air_date=air_date
                )
                new_tags = BRAVESTARR_TAGS + [f"Episode {ep_num}", f"Folge {ep_num}"]
                
                print(f"    -> Episode {ep_num}: {ep_title}")
                print(f"    -> Neuer Titel: {new_title[:50]}...")
                
                if args.apply:
                    try:
                        resp = youtube.videos().list(part="snippet", id=vid).execute()
                        if resp.get("items"):
                            snippet = resp["items"][0]["snippet"]
                            snippet["title"] = new_title
                            snippet["description"] = new_desc
                            snippet["tags"] = new_tags[:30]
                            
                            youtube.videos().update(
                                part="snippet",
                                body={"id": vid, "snippet": snippet}
                            ).execute()
                            print(f"    [OK] Aktualisiert!")
                        time.sleep(0.5)
                    except HttpError as e:
                        print(f"    [ERROR] {e}")
            else:
                print(f"    [SKIP] Episode {ep_key} nicht in Knowledge Base")
        else:
            print(f"    [SKIP] Keine Episode erkannt")
    
    if not args.apply:
        print("\n[DRY-RUN] Mit --apply ausfuehren!")

if __name__ == "__main__":
    main()
