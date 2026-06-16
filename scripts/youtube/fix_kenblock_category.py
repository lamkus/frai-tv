"""
Fix Ken Block / Getaway category (should be Autos & Vehicles = 2)
and clean up remaining old title patterns.
4 videos, 200 quota.
"""
import json, sys
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
        scopes=creds_data.get("scopes", ["https://www.googleapis.com/auth/youtube"])
    )
    if creds.expired:
        creds.refresh(Request())
        creds_data["access_token"] = creds.token
        json.dump(creds_data, open(OAUTH_PATH, "w"), indent=2)
    return build("youtube", "v3", credentials=creds)

# Videos to fix: title + category
FIXES = {
    "JzJrH43etPA": {
        "title": "Ken Block: Gymkhana 3 (2010) | DC Shoes | 8K HQ",
        "categoryId": "2",
    },
    "90UleF637FA": {
        "title": "Ken Block: Gymkhana 1 (2008) | World First | 8K HQ",
        "categoryId": "2",
    },
    "LOTXPLYeRAc": {
        "title": "Getaway in Stockholm 2 | Full Film | 8K HQ",
        "categoryId": "2",
    },
    "NcfUWqlfSm0": {
        "title": "Getaway in Stockholm 1 | Porsche 911 | 8K HQ",
        "categoryId": "2",
    },
}

# Validate
for vid, fix in FIXES.items():
    t = fix["title"]
    assert len(t) <= 70, f"TOO LONG: {t}"
    print(f"  [{len(t):2d}] {vid}: {t} (cat→{fix['categoryId']})")

print(f"\nTotal: {len(FIXES)} | Quota: {len(FIXES)*50+1}")

DRY_RUN = "--apply" not in sys.argv
yt = get_yt()

# Fetch current
ids = ",".join(FIXES.keys())
resp = yt.videos().list(part="snippet", id=ids).execute()
current = {item["id"]: item for item in resp.get("items", [])}

print("\nCurrent → New:")
for vid, fix in FIXES.items():
    item = current.get(vid)
    if not item:
        print(f"  ❌ {vid}: NOT FOUND")
        continue
    old_t = item["snippet"]["title"]
    old_c = item["snippet"]["categoryId"]
    print(f"  {vid}:")
    print(f"    title: [{len(old_t)}] {old_t[:70]}")
    print(f"       → [{len(fix['title'])}] {fix['title']}")
    print(f"    cat:   {old_c} → {fix['categoryId']}")

if DRY_RUN:
    print("\nDRY RUN — pass --apply")
    sys.exit(0)

success = 0
for vid, fix in FIXES.items():
    item = current.get(vid)
    if not item:
        continue
    snippet = item["snippet"]
    snippet["title"] = fix["title"]
    snippet["categoryId"] = fix["categoryId"]
    try:
        yt.videos().update(part="snippet", body={"id": vid, "snippet": snippet}).execute()
        print(f"  ✅ {vid}: {fix['title']} (cat={fix['categoryId']})")
        success += 1
    except Exception as e:
        print(f"  ❌ {vid}: {e}")

print(f"\nUpdated {success}/{len(FIXES)} ({success*50} quota)")
