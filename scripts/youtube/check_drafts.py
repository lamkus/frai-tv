"""Check all private/unlisted videos and their current titles."""
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
CHANNEL_ID = "UCVFv6Egpl0LDvigpFbQXNeQ"
UPLOAD_PL = "UUVFv6Egpl0LDvigpFbQXNeQ"

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

# Get ALL videos from uploads playlist (includes private)
all_ids = []
next_token = None
while True:
    resp = yt.playlistItems().list(
        part="contentDetails,status",
        playlistId=UPLOAD_PL,
        maxResults=50,
        pageToken=next_token
    ).execute()
    for item in resp.get("items", []):
        vid = item["contentDetails"]["videoId"]
        privacy = item["status"]["privacyStatus"]
        all_ids.append((vid, privacy))
    next_token = resp.get("nextPageToken")
    if not next_token:
        break

print(f"Total videos in channel: {len(all_ids)}")
public = [(v,p) for v,p in all_ids if p == "public"]
private = [(v,p) for v,p in all_ids if p == "private"]
unlisted = [(v,p) for v,p in all_ids if p == "unlisted"]
print(f"  Public: {len(public)} | Private: {len(private)} | Unlisted: {len(unlisted)}")

# Fetch details for non-public videos
non_public = private + unlisted
if not non_public:
    print("\nNo private/unlisted videos found.")
else:
    print(f"\n{'='*70}")
    print(f"  PRIVATE / UNLISTED VIDEOS ({len(non_public)})")
    print(f"{'='*70}")
    
    ids = [v for v,p in non_public]
    for i in range(0, len(ids), 50):
        batch = ids[i:i+50]
        resp = yt.videos().list(
            part="snippet,status",
            id=",".join(batch)
        ).execute()
        for item in resp.get("items", []):
            vid = item["id"]
            title = item["snippet"]["title"]
            privacy = item["status"]["privacyStatus"]
            cat = item["snippet"]["categoryId"]
            tlen = len(title)
            
            # Check issues
            issues = []
            if tlen > 70: issues.append(f"LONG({tlen})")
            if "8K" not in title and "8k" not in title: issues.append("NO_8K")
            if "@remAI" in title: issues.append("@HANDLE")
            if "Best Online" in title: issues.append("OLD_NAME")
            if "(4K UHD)" in title: issues.append("OLD_SUFFIX")
            if "sls" in title.lower(): issues.append("SLS_IN_TITLE")
            
            status_icon = "🔒" if privacy == "private" else "👁️"
            issue_str = " ⚠️ " + ", ".join(issues) if issues else " ✅"
            print(f"\n  {status_icon} {vid} [{privacy}] cat={cat}")
            print(f"     [{tlen}] {title}")
            print(f"     {issue_str}")
