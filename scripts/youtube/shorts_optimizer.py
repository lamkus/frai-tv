#!/usr/bin/env python3
"""Shorts Optimizer - Virale Hits optimieren!

Shorts brauchen:
- #Shorts im Titel (WICHTIG für YouTube Shorts Algorithmus!)
- Kurze, catchy Tags
- Trending Keywords
"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
import json
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

# Shorts Knowledge Base
SHORTS_TAGS = {
    "teaserama": [
        "Shorts", "vintage", "1950s", "burlesque", "pinup",
        "Bettie Page", "Tempest Storm", "retro", "classic",
        "dance", "showgirl", "8K", "restored", "HD",
        "glamour", "nostalgia", "oldies", "golden age",
        "viral", "trending", "aesthetic", "remAIke"
    ],
    "christmas": [
        "Shorts", "Christmas", "Winter", "Holiday", "Snow",
        "vintage", "1950s", "classic", "retro", "nostalgia",
        "animation", "cartoon", "8K", "restored", "remAIke"
    ],
    "pearl_harbor": [
        "Shorts", "Pearl Harbor", "1942", "WWII", "history",
        "documentary", "vintage", "war", "historical",
        "8K", "restored", "remAIke"
    ],
    "default": [
        "Shorts", "vintage", "classic", "retro", "8K",
        "restored", "HD", "remAIke", "nostalgia", "viral"
    ]
}

def optimize_short_title(title):
    """Fügt #Shorts hinzu wenn nicht vorhanden"""
    if "#shorts" not in title.lower():
        return title.rstrip() + " #Shorts"
    return title

def get_short_tags(title):
    """Wählt passende Tags basierend auf Titel"""
    title_lower = title.lower()
    
    if "teaserama" in title_lower or "bettie" in title_lower or "tempest" in title_lower:
        base = SHORTS_TAGS["teaserama"].copy()
        if "bettie" in title_lower:
            base.extend(["Bettie Page", "Betty Page", "pinup queen"])
        if "tempest" in title_lower:
            base.extend(["Tempest Storm", "burlesque queen"])
        if "trudy" in title_lower:
            base.append("Trudy Wayne")
        if "cherry" in title_lower:
            base.append("Cherry Knight")
        if "chris" in title_lower:
            base.append("Chris La Chris")
        if "icky" in title_lower:
            base.append("Icky Lynn")
        return base
    
    if "christmas" in title_lower or "winter" in title_lower or "snow" in title_lower:
        return SHORTS_TAGS["christmas"]
    
    if "pearl" in title_lower or "harbor" in title_lower:
        return SHORTS_TAGS["pearl_harbor"]
    
    return SHORTS_TAGS["default"]

def limit_tags(tags, max_chars=500):
    seen = set()
    result = []
    for tag in tags:
        key = tag.lower()
        if key not in seen and len(tag) > 1:
            seen.add(key)
            result.append(tag)
    
    kept = []
    for tag in result:
        if len(",".join(kept + [tag])) <= max_chars:
            kept.append(tag)
    return kept

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    
    print("=" * 60)
    print("SHORTS OPTIMIZER - Virale Hits!")
    print("=" * 60)
    
    youtube = get_youtube()
    scan = load_json(CONFIG / "full_channel_scan.json")
    
    shorts = [v for v in scan["all_videos"] if "short" in v["title"].lower()]
    
    print(f"\n[Gefunden] {len(shorts)} Shorts")
    
    results = []
    
    for i, short in enumerate(shorts, 1):
        vid = short["id"]
        title = short["title"]
        status = short["status"]
        
        print(f"\n[{i}/{len(shorts)}] {title[:50]}...")
        print(f"   Status: {status}")
        
        new_title = optimize_short_title(title)
        has_hashtag = "#shorts" in title.lower()
        
        if not has_hashtag:
            print(f"   + Hashtag #Shorts hinzufuegen")
        
        new_tags = limit_tags(get_short_tags(title))
        print(f"   Tags: {len(new_tags)}")
        
        result = {
            "id": vid,
            "old_title": title,
            "new_title": new_title,
            "status": status,
            "tags_count": len(new_tags),
            "action": "pending"
        }
        
        if args.apply:
            try:
                resp = youtube.videos().list(part="snippet", id=vid).execute()
                if resp.get("items"):
                    snippet = resp["items"][0]["snippet"]
                    needs_update = False
                    
                    if not has_hashtag:
                        snippet["title"] = new_title
                        needs_update = True
                    
                    current_tags = snippet.get("tags", [])
                    if len(current_tags) < 15:
                        snippet["tags"] = new_tags
                        needs_update = True
                    
                    if needs_update:
                        youtube.videos().update(
                            part="snippet",
                            body={"id": vid, "snippet": snippet}
                        ).execute()
                        result["action"] = "UPDATED"
                        print(f"   [OK] Aktualisiert!")
                    else:
                        result["action"] = "SKIPPED"
                        print(f"   [SKIP] Bereits optimiert")
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
        "total": len(shorts),
        "results": results
    }
    save_json(CONFIG / "shorts_optimizer_report.json", report)
    print(f"\n[Report] {CONFIG / 'shorts_optimizer_report.json'}")
    
    if not args.apply:
        print("\n[DRY-RUN] Mit --apply ausfuehren!")

if __name__ == "__main__":
    main()
