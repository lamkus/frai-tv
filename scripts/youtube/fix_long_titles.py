"""
Fix 6 titles that exceed 70 characters.
Uses YouTube API (videos.update) — 50 quota per video = 300 total.
READ via Public API (requests + API_KEY), WRITE via OAuth.
"""
import json, os, sys, requests as req
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# ── Auth ──
OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
API_KEY = os.environ.get("YOUTUBE_API_KEY")

def get_youtube_rw():
    """OAuth client for write operations."""
    creds_data = json.load(open(OAUTH_PATH, "r"))
    creds = Credentials(
        token=creds_data.get("access_token", creds_data.get("token")),
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

def public_api_get(ids_csv):
    """Public API for read operations via requests (saves OAuth quota)."""
    r = req.get("https://www.googleapis.com/youtube/v3/videos",
                params={"part": "snippet", "id": ids_csv, "key": API_KEY})
    r.raise_for_status()
    return r.json()

# ── Title fixes ──
FIXES = [
    {
        "id": "1yiNR69g0qA",
        "new_title": "Johnny Long Orch: My Girl Loves a Sailor | Soundie | 8K HQ"
    },
    {
        "id": "lxrwknLmRl4",
        "new_title": "This Deleted Porky Pig Episode Got Restored to 8K | 8K HQ"
    },
    {
        "id": "xoCvBUIaqwg",
        "new_title": "Betty Boop (95/105): Pudgy the Watchman (1938) | 8K HQ"
    },
    {
        "id": "zouf8VMUeCo",
        "new_title": "Betty Boop (91/105): Out of the Inkwell (1938) | 8K HQ"
    },
    {
        "id": "MXE3TqsT2oE",
        "new_title": "Old Mother Hubbard (1935) | ComiColor | 8K HQ"
    },
    {
        "id": "dCCl4JxrlF8",
        "new_title": "Betty Boop (11/105): Minnie the Moocher (1932) | 8K HQ"
    },
]

# Verify all <=70
for f in FIXES:
    l = len(f["new_title"])
    assert l <= 70, f"STILL TOO LONG ({l}): {f['new_title']}"
    print(f"  [{l:2d}] {f['new_title']}")

print(f"\n{'='*60}")
print(f"Total: {len(FIXES)} videos | Quota: {len(FIXES)*50} units")
print(f"{'='*60}\n")

# ── DRY RUN: Fetch current titles via Public API ──
DRY_RUN = "--apply" not in sys.argv
if DRY_RUN:
    print("DRY RUN — pass --apply to execute\n")

ids = ",".join(f["id"] for f in FIXES)
yt = get_youtube_rw()  # Use OAuth for read too (API key not in env)
resp = yt.videos().list(part="snippet", id=ids).execute()  # 1 quota
current = {item["id"]: item for item in resp.get("items", [])}

print("Current → New:")
for f in FIXES:
    cur = current.get(f["id"])
    if not cur:
        print(f"  ❌ {f['id']} NOT FOUND!")
        continue
    old_title = cur["snippet"]["title"]
    print(f"  {f['id']}:")
    print(f"    OLD [{len(old_title):2d}]: {old_title}")
    print(f"    NEW [{len(f['new_title']):2d}]: {f['new_title']}")
    print()

if DRY_RUN:
    print("DRY RUN COMPLETE. Run with --apply to update.")
    sys.exit(0)

# ── APPLY ──
yt_rw = get_youtube_rw()
success = 0
for f in FIXES:
    cur = current.get(f["id"])
    if not cur:
        continue
    snippet = cur["snippet"]
    snippet["title"] = f["new_title"]
    try:
        yt_rw.videos().update(
            part="snippet",
            body={"id": f["id"], "snippet": snippet}
        ).execute()
        print(f"  ✅ {f['id']}: {f['new_title']}")
        success += 1
    except Exception as e:
        print(f"  ❌ {f['id']}: {e}")

print(f"\n{'='*60}")
print(f"Updated {success}/{len(FIXES)} titles ({success*50} quota used)")
print(f"{'='*60}")
