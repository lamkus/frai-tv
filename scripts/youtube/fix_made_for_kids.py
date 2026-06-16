"""
Check and fix madeForKids=false for 4 videos.
YouTube API: selfDeclaredMadeForKids is writable via videos.update(part="status")
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

VIDEO_IDS = ["wAkUnHRxwT8", "SARofiBGJ2U", "Ucub3igzk2U", "MXE3TqsT2oE"]

yt = get_yt()

# Fetch current status
resp = yt.videos().list(part="status,snippet", id=",".join(VIDEO_IDS)).execute()

print("=== CURRENT STATUS ===")
for item in resp.get("items", []):
    vid = item["id"]
    title = item["snippet"]["title"]
    status = item["status"]
    mfk = status.get("madeForKids", "?")
    self_mfk = status.get("selfDeclaredMadeForKids", "?")
    privacy = status.get("privacyStatus", "?")
    print(f"  {vid}: madeForKids={mfk}, selfDeclared={self_mfk}, privacy={privacy}")
    print(f"    Title: {title[:70]}")

DRY_RUN = "--apply" not in sys.argv
if DRY_RUN:
    print("\nDRY RUN — pass --apply to fix")
    sys.exit(0)

print("\n=== FIXING ===")
success = 0
for item in resp.get("items", []):
    vid = item["id"]
    # Update: set selfDeclaredMadeForKids = false
    try:
        yt.videos().update(
            part="status",
            body={
                "id": vid,
                "status": {
                    "privacyStatus": item["status"]["privacyStatus"],
                    "selfDeclaredMadeForKids": False,
                    "embeddable": item["status"].get("embeddable", True),
                }
            }
        ).execute()
        print(f"  ✅ {vid}: madeForKids → false")
        success += 1
    except Exception as e:
        print(f"  ❌ {vid}: {e}")

print(f"\nFixed {success}/{len(VIDEO_IDS)} ({success*50} quota)")
