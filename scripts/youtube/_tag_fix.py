"""
Add Pflicht-Tags (remastered, restored, AI enhanced, upscaled, classic) 
to all public videos that are missing them.
Also adds category-specific tags per rules.

QUOTA: ~51 Units per video (1 list + 1 update per 50-batch)
BUG FIX from 2026-02-10: Only use part="snippet" — NEVER include "status"!
"""
import json, os, sys
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = r"D:\remaike.TV\token.json"
CLIENT = r"D:\remaike.TV\config\client_secret.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
UPLOAD_PL = "UUVFv6Egpl0LDvigpFbQXNeQ"

# Pflicht-Tags für ALLE Videos
PFLICHT_ALL = ["remastered", "restored", "AI enhanced", "upscaled", "classic"]

# Category-specific tags
CAT_TAGS = {
    "cartoon": ["classic cartoon", "vintage cartoon", "retro animation"],
    "film": ["full movie", "public domain", "free movie"],
    "series": ["full episode", "complete episode"],
    "soundie": ["vintage music", "jazz", "swing", "1940s music"],
    "wochenschau": ["vintage newsreel", "WW2 footage", "historical footage"],
}

def get_youtube():
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN, 'w') as f:
            f.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def detect_category(title, tags_lower):
    """Detect content category from title/tags for category-specific tags."""
    t = title.lower()
    cats = []
    
    # Cartoon detection
    cartoon_series = ["betty boop", "felix", "superman", "popeye", "casper", 
                      "looney tunes", "merrie melodies", "alfred", "kwak", "quack",
                      "bravestarr", "maulwurf", "krtek", "ferdy", "tom and jerry",
                      "woody woodpecker", "bugs bunny", "daffy duck"]
    if any(s in t for s in cartoon_series):
        cats.append("cartoon")
    
    # Film detection (full-length movies)
    films = ["nosferatu", "metropolis", "caligari", "white zombie", "charade",
             "grim game", "phantom of the opera", "häxan", "blackmail",
             "voyage", "dinner for one", "boxing cats", "arrival of a train",
             "soviet experiment", "a trip to the moon"]
    if any(s in t for s in films):
        cats.append("film")
    
    # Series detection  
    if any(s in t for s in ["episode", "e0", "e1", "e2", "e3", "folge", "(1/", "(2/", "(3/"]):
        cats.append("series")
    
    # Soundie
    if "soundie" in t:
        cats.append("soundie")
    
    # Wochenschau
    if "wochenschau" in t:
        cats.append("wochenschau")
    
    return cats

def main():
    yt = get_youtube()
    
    # Step 1: Fetch ALL video IDs from upload playlist
    print("📡 Fetching all video IDs from upload playlist...")
    video_ids = []
    next_token = None
    while True:
        resp = yt.playlistItems().list(
            part="contentDetails",
            playlistId=UPLOAD_PL,
            maxResults=50,
            pageToken=next_token
        ).execute()
        for item in resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        next_token = resp.get("nextPageToken")
        if not next_token:
            break
    print(f"  Found {len(video_ids)} videos total")
    
    # Step 2: Fetch snippets in batches of 50 — ONLY part="snippet"!
    print("\n📊 Checking tags on all videos...")
    need_fix = []
    
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        resp = yt.videos().list(
            part="snippet",  # ← BUG FIX: ONLY snippet, never status!
            id=",".join(batch)
        ).execute()
        
        for item in resp.get("items", []):
            vid = item["id"]
            snippet = item["snippet"]
            title = snippet.get("title", "")
            existing_tags = [t.lower() for t in snippet.get("tags", [])]
            
            # Check which Pflicht-Tags are missing
            missing = [t for t in PFLICHT_ALL if t.lower() not in existing_tags]
            
            # Check category-specific tags
            cats = detect_category(title, existing_tags)
            cat_missing = []
            for cat in cats:
                for tag in CAT_TAGS.get(cat, []):
                    if tag.lower() not in existing_tags:
                        cat_missing.append(tag)
            
            if missing or cat_missing:
                need_fix.append({
                    "id": vid,
                    "title": title,
                    "snippet": snippet,
                    "missing_pflicht": missing,
                    "missing_cat": cat_missing,
                    "categories": cats,
                    "current_tag_count": len(snippet.get("tags", []))
                })
    
    print(f"\n📋 {len(need_fix)} videos need tag updates")
    if not need_fix:
        print("✅ All videos have Pflicht-Tags!")
        return
    
    # Show preview
    print("\n--- PREVIEW (first 10) ---")
    for v in need_fix[:10]:
        print(f"  [{v['id']}] {v['title'][:50]}...")
        print(f"    Missing Pflicht: {v['missing_pflicht']}")
        if v['missing_cat']:
            print(f"    Missing Category ({v['categories']}): {v['missing_cat']}")
        print(f"    Current tags: {v['current_tag_count']}")
    
    if len(need_fix) > 10:
        print(f"  ... and {len(need_fix) - 10} more")
    
    total_quota = len(need_fix) * 50 + (len(need_fix) // 50 + 1)
    print(f"\n💰 Estimated quota: ~{total_quota} Units ({len(need_fix)} × 50 update + reads)")
    
    # Step 3: Apply fixes
    print("\n🔧 Applying tag fixes...")
    fixed = 0
    errors = 0
    
    for v in need_fix:
        tags = list(v["snippet"].get("tags", []))
        
        # Add missing Pflicht tags
        for tag in v["missing_pflicht"]:
            if tag not in tags:
                tags.append(tag)
        
        # Add missing category tags (respect max 15)
        for tag in v["missing_cat"]:
            if len(tags) < 15 and tag not in tags:
                tags.append(tag)
        
        # Enforce max 15 tags
        if len(tags) > 15:
            tags = tags[:15]
        
        # Build update body — ONLY snippet, no status!
        body = {
            "id": v["id"],
            "snippet": {
                "title": v["snippet"]["title"],
                "description": v["snippet"]["description"],
                "tags": tags,
                "categoryId": v["snippet"]["categoryId"]
            }
        }
        
        try:
            yt.videos().update(
                part="snippet",
                body=body
            ).execute()
            fixed += 1
            print(f"  ✅ [{fixed}/{len(need_fix)}] {v['title'][:50]}... (+{len(v['missing_pflicht'])} pflicht, +{len(v['missing_cat'])} cat)")
        except Exception as e:
            err_str = str(e)
            if "quotaExceeded" in err_str:
                print(f"\n  ❌ QUOTA EXHAUSTED after {fixed} fixes!")
                errors += 1
                break
            else:
                print(f"  ❌ Error on {v['id']}: {err_str[:100]}")
                errors += 1
    
    print(f"\n📊 RESULT: {fixed} fixed, {errors} errors, {len(need_fix) - fixed - errors} remaining")
    print(f"💰 Quota used: ~{fixed * 50 + (len(video_ids) // 50 + 1)} Units")

if __name__ == "__main__":
    main()
