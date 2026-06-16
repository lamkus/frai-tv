"""
Fix remaining title issues found by compliance audit:
- 15 titles too long (>70 chars)
- 7 with @remAIke_IT/@remAI... in title
- 6 with old naming patterns (Best Online Versio...)
All overlapping — total unique ~17 videos.

Uses OAuth for read+write.
"""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

OAUTH_PATH = "D:/remaike.TV/config/youtube_oauth.json"
AUDIT_FILE = "D:/remaike.TV/config/compliance_audit_2026_02_08.json"

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

# Load audit results
audit = json.load(open(AUDIT_FILE, encoding="utf-8"))
problem_videos = [r for r in audit["results"] if r["issues"]]

print(f"Found {len(problem_videos)} videos with critical issues\n")

# Manual title fixes
FIXES = {
    # Too long + @handle
    "Ucub3igzk2U": "Dick Whittington's Cat (1935) | ComiColor | 8K HQ",
    "1mVWh_B6_00": "Little Lambkins (1940) | Fleischer Color Classic | 8K HQ",
    "fVp_aVBZhak": "Gabby: King for a Day (1940) | Fleischer Cartoon | 8K HQ",
    "PzbAE96bG1Q": "Hawaiian Birds (1936) | Fleischer Color Classic | 8K HQ",
    "Zu_iBCd5NJc": "Biological Warfare: What You Should Know (1952) | 8K HQ",

    # Too long only
    "xzZ9yB5lJ9s": "Ferdy: Die abenteuerliche Rettung Bambini | Deutsch | 8K HQ",
    "4VO2weDCfi0": "The Little Stranger (1936) | Fleischer Color Classic | 8K HQ",
    "hvdNZy8AciI": "Casper (15/55): True Boo (1952) | 8K HQ",
    "3gzbxznJ_PM": "Popeye Movie Marathon | Fleischer Studios | Best 4K | 8K HQ",
    "EpzJcD6zkvs": "Suzy Snowflake (1953) | Christmas Short | 8K HQ",
    "U-WD47NSgAE": "Coca‑Cola Christmas Trucks — Holidays Are Coming (1995) | 8K HQ",
    "WSjkAZkPbKs": "EPIC Coca‑Cola Christmas Trucks (1995) | 8K HQ",
    "yIQCHpjp4NE": "Batman & Robin Meet Santa Claus (1966) | 8K HQ",
    "YbC2JynVCRA": "A Bill of Divorcement — Barrymore & Hepburn (1932) | 8K HQ",
    "dGD2CeoZX68": "A Christmas Carol (1984) | George C. Scott | 8K HQ",

    # @handle only (title length OK but @remAI... in title)
    "Sk2IIXPV5ig": "Betty Boop (35/105): Big Boss (1933) | 8K HQ",
    "_oZqwtQDg2c": "Betty Boop (9/105): Any Rags (1932) | 8K HQ",
}

# Validate all <=70 chars
print("Planned fixes:")
for vid, new_title in FIXES.items():
    l = len(new_title)
    ok = "✅" if l <= 70 else "❌"
    has_handle = "⚠️@" if '@remAI' in new_title else ""
    print(f"  {ok} [{l:2d}] {vid}: {new_title} {has_handle}")
    assert l <= 70, f"STILL TOO LONG: {new_title}"
    assert '@remAI' not in new_title, f"STILL HAS @handle: {new_title}"

print(f"\nTotal: {len(FIXES)} fixes | Quota: {len(FIXES) * 50 + 1} units")

# ── Execute ──
DRY_RUN = "--apply" not in sys.argv
if DRY_RUN:
    print("\nDRY RUN — pass --apply to execute")
    # Verify current titles
    yt = get_yt()
    ids = ",".join(FIXES.keys())
    resp = yt.videos().list(part="snippet", id=ids).execute()
    current = {item["id"]: item["snippet"]["title"] for item in resp.get("items", [])}
    print("\nCurrent → New:")
    for vid, new_title in FIXES.items():
        old = current.get(vid, "???")
        print(f"  {vid}:")
        print(f"    OLD [{len(old):2d}]: {old}")
        print(f"    NEW [{len(new_title):2d}]: {new_title}")
    sys.exit(0)

# APPLY
yt = get_yt()
ids_csv = ",".join(FIXES.keys())

# Fetch in batches of 50
all_items = {}
id_list = list(FIXES.keys())
for i in range(0, len(id_list), 50):
    batch = id_list[i:i+50]
    resp = yt.videos().list(part="snippet", id=",".join(batch)).execute()
    for item in resp.get("items", []):
        all_items[item["id"]] = item

success = 0
for vid, new_title in FIXES.items():
    item = all_items.get(vid)
    if not item:
        print(f"  ❌ {vid}: NOT FOUND")
        continue
    snippet = item["snippet"]
    old_title = snippet["title"]
    snippet["title"] = new_title
    try:
        yt.videos().update(part="snippet", body={"id": vid, "snippet": snippet}).execute()
        print(f"  ✅ {vid}: {new_title}")
        success += 1
    except Exception as e:
        print(f"  ❌ {vid}: {e}")

print(f"\n{'='*60}")
print(f"Updated {success}/{len(FIXES)} titles ({success * 50} quota used)")
print(f"{'='*60}")
