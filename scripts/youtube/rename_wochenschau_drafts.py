"""
Rename Wochenschau drafts to proper SEO-compliant titles.
Updates title, description, tags for 7 new Wochenschau uploads.

STOP-GATE: Only updates metadata, does NOT change privacyStatus.
"""
import json, sys, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', 
    ['https://www.googleapis.com/auth/youtube.force-ssl'])
youtube = build('youtube', 'v3', credentials=creds)

# ── Rename plan ──────────────────────────────────────────────────────────────
RENAMES = [
    {
        "id": "WAKX3d__J8E",
        "nr": 701,
        "title": "Wochenschau 701: Battle of Monte Cassino (09.02.1944) | 8K HQ (4K UHD)",
        "date": "09.02.1944",
        "location": "Monte Cassino, Italy",
        "event": "Fierce fighting at Monte Cassino as Allied forces attempt to break through the Gustav Line in central Italy."
    },
    {
        "id": "f6iafERcG6M",
        "nr": 703,
        "title": "Wochenschau 703: German Industry & Home Front (23.02.1944) | 8K HQ (4K UHD)",
        "date": "23.02.1944",
        "location": "Germany",
        "event": "Reports from the German home front, war industry production, and civilian life during total war mobilization."
    },
    {
        "id": "FU9uhmbyyas",
        "nr": 706,
        "title": "Wochenschau 706: Hungary Under Occupation (15.03.1944) | 8K HQ (4K UHD)",
        "date": "15.03.1944",
        "location": "Budapest, Hungary",
        "event": "German forces occupy Hungary in Operation Margarethe. Scenes from Budapest and military operations."
    },
    {
        "id": "xZ8hbztqcQI",
        "nr": 707,
        "title": "Wochenschau 707: Crimea Campaign (22.03.1944) | 8K HQ (4K UHD)",
        "date": "22.03.1944",
        "location": "Crimea",
        "event": "Fighting intensifies on the Crimean Peninsula as Soviet forces press their offensive against Axis positions."
    },
    {
        "id": "XYH4X8I4L-8",
        "nr": 708,
        "title": "Wochenschau 708: Eastern Front Offensive (29.03.1944) | 8K HQ (4K UHD)",
        "date": "29.03.1944",
        "location": "Eastern Front",
        "event": "Major Soviet spring offensive operations along the Eastern Front. German defensive positions under heavy pressure."
    },
    {
        "id": "jRYN8RQVHj4",
        "nr": 709,
        "title": "Wochenschau 709: Crimea Battles (05.04.1944) | 8K HQ (4K UHD)",
        "date": "05.04.1944",
        "location": "Crimea",
        "event": "Continued fighting on the Crimean Peninsula. Soviet forces advance toward Sevastopol."
    },
    {
        "id": "Lqk_6Rp9YLw",
        "nr": 710,
        "title": "Wochenschau 710: Crimea Evacuation (12.04.1944) | 8K HQ (4K UHD)",
        "date": "12.04.1944",
        "location": "Crimea",
        "event": "The battle for Crimea reaches its final phase. German and Romanian forces face encirclement near Sevastopol."
    },
]

# ── Standard tags for all Wochenschau ────────────────────────────────────────
BASE_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "WWII", "World War II",
    "vintage newsreel", "historical footage", "8K", "4K", "remastered",
    "restored", "AI enhanced", "public domain", "history", "documentary",
    "WW2 footage"
]

# ── Description template ────────────────────────────────────────────────────
def build_description(item):
    nr = item["nr"]
    date = item["date"]
    loc = item["location"]
    event = item["event"]
    
    return f"""Deutsche Wochenschau Nr. {nr} ({date}) - Original WWII newsreel, AI remastered in stunning 8K quality.
{event}

Location: {loc}

This newsreel is a historical document from World War II, presented for educational and documentary purposes only. The views expressed in this footage do not reflect the opinions of the uploader.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #WWII #8K #History #PublicDomain
"""

# ── Apply updates ────────────────────────────────────────────────────────────
DRY_RUN = "--apply" not in sys.argv

if DRY_RUN:
    print("=" * 70)
    print("  DRY RUN - Use --apply to actually update YouTube")
    print("=" * 70)

results = []
for item in RENAMES:
    vid = item["id"]
    new_title = item["title"]
    desc = build_description(item)
    
    # Add episode-specific tags
    tags = BASE_TAGS + [
        f"Wochenschau {item['nr']}",
        item["location"],
        item["date"][:4],  # year
    ]
    
    print(f"\n{'='*60}")
    print(f"  Nr.{item['nr']} ({vid})")
    print(f"  OLD: deutsche wochenschau nr{item['nr']} ... ARCHIVE PROTECTED")
    print(f"  NEW: {new_title}")
    print(f"  Tags: {len(tags)} tags")
    
    if DRY_RUN:
        print(f"  [DRY RUN] Would update")
        results.append({"id": vid, "nr": item["nr"], "title": new_title, "status": "dry_run"})
    else:
        try:
            # Get current snippet (needed to preserve categoryId etc)
            current = youtube.videos().list(part="snippet,status", id=vid).execute()
            if not current.get("items"):
                print(f"  [ERROR] Video not found!")
                results.append({"id": vid, "nr": item["nr"], "status": "not_found"})
                continue
            
            snippet = current["items"][0]["snippet"]
            snippet["title"] = new_title
            snippet["description"] = desc
            snippet["tags"] = tags
            snippet["categoryId"] = "27"  # Education
            
            # Update - ONLY snippet, NOT status (no privacy change!)
            youtube.videos().update(
                part="snippet",
                body={"id": vid, "snippet": snippet}
            ).execute()
            
            print(f"  [OK] Updated successfully")
            results.append({"id": vid, "nr": item["nr"], "title": new_title, "status": "updated"})
        except Exception as e:
            print(f"  [ERROR] {e}")
            results.append({"id": vid, "nr": item["nr"], "status": f"error: {e}"})

print(f"\n{'='*60}")
print(f"Results: {len([r for r in results if r.get('status') == 'updated' or r.get('status') == 'dry_run'])}/{len(RENAMES)} OK")

# Save results
with open("config/wochenschau_rename_result.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"Results saved to config/wochenschau_rename_result.json")

# Quota info
if not DRY_RUN:
    # 7 videos.list (1 each = 7) + 7 videos.update (50 each = 350) = 357 total
    print(f"\nQuota used: ~357 units (7x list@1 + 7x update@50)")
