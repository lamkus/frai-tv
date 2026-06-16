"""Check all Maulwurf videos in detail."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"

def get_yt():
    creds_data = json.load(open(OAUTH_PATH))
    creds = Credentials(
        token=creds_data.get("access_token"),
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
    )
    if creds.expired:
        creds.refresh(Request())
        creds_data["access_token"] = creds.token
        json.dump(creds_data, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)

yt = get_yt()

# search.list costs 100 quota - use snapshot instead
snap = json.load(open("config/channel_snapshot_2026_02_06.json", encoding="utf-8"))
all_vids = snap.get("all_videos", [])
maulwurf_ids = [v["id"] for v in all_vids if "maulwurf" in v.get("title","").lower() or "krtek" in v.get("title","").lower()]

print(f"Found {len(maulwurf_ids)} Maulwurf videos in snapshot")

# Fetch live details (1 quota)
resp = yt.videos().list(
    part="snippet,status,contentDetails,statistics,localizations",
    id=",".join(maulwurf_ids)
).execute()

for item in resp.get("items", []):
    s = item["snippet"]
    st = item["status"]
    loc = item.get("localizations", {})
    stats = item.get("statistics", {})
    cd = item["contentDetails"]
    
    print("=" * 70)
    print(f"  ID:       {item['id']} | {st['privacyStatus']}")
    print(f"  Title:    {s['title']}")
    print(f"  Cat:      {s['categoryId']}")
    print(f"  Duration: {cd['duration']}")
    print(f"  Views:    {stats.get('viewCount','?')} | Likes: {stats.get('likeCount','?')}")
    print(f"  DefLang:  {s.get('defaultLanguage','(none)')}")
    print(f"  Locs:     {list(loc.keys())}")
    print(f"  MFK:      {st.get('madeForKids')}")
    print(f"  Tags:     {len(s.get('tags',[]))} tags")
    
    # Check localization titles
    for lang in ['en', 'de', 'es', 'fr', 'pt']:
        if lang in loc:
            print(f"    [{lang}] {loc[lang].get('title','?')}")
    
    # Check description for key elements
    desc = s.get("description", "")
    checks = {
        "CTA": any(x in desc for x in ['LIKE', 'SUBSCRIBE']),
        "Website": 'remaike' in desc.lower(),
        "YT Link": '@remAIke_IT' in desc,
        "Hashtags": len([w for w in desc.split() if w.startswith('#')]),
    }
    print(f"  Checks:   {checks}")
    
    # CRITICAL: Is "Maulwurf" correctly identified?
    print(f"  NOTE:     Original = CZECH (Krtek by Zdenek Miler), NOT German!")
    print(f"            Content is 90%+ SILENT (pantomime) = universally accessible")
    
    # Show first 300 chars of desc
    print(f"  Desc[:300]:")
    for line in desc[:300].split("\n"):
        print(f"    {line}")
    print()
