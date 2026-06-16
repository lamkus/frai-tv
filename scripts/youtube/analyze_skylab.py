"""Analyze Skylab video in detail and fix title/metadata."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
VID = "sp1AzW-_rV0"

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

yt = get_yt()
resp = yt.videos().list(
    part="snippet,contentDetails,status,statistics,localizations",
    id=VID
).execute()

item = resp["items"][0]
s = item["snippet"]
st = item["status"]
cd = item["contentDetails"]

print("="*70)
print(f"  VIDEO: {VID}")
print("="*70)
print(f"  Title:       {s['title']}")
print(f"  Description: {s.get('description','')[:500]}")
print(f"  Tags:        {s.get('tags', [])}")
print(f"  Category:    {s['categoryId']}")
print(f"  Published:   {s['publishedAt']}")
print(f"  Duration:    {cd['duration']}")
print(f"  Privacy:     {st['privacyStatus']}")
print(f"  MadeForKids: {st.get('madeForKids')}")
print(f"  DefaultLang: {s.get('defaultLanguage','(none)')}")
print(f"  Locs:        {list(item.get('localizations',{}).keys())}")
print(f"  Embeddable:  {st.get('embeddable')}")
print()

# Full description
print("--- FULL DESCRIPTION ---")
print(s.get("description","(empty)"))
print("--- END ---")
