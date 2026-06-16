"""
Rename a single private YouTube draft using OAuth.
Safety: only updates snippet fields and does not touch privacyStatus.
Quota: videos.list (1) + videos.update (50) = 51 units.
"""

import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_PATH = Path("config/youtube_oauth.json")
VIDEO_ID = "iql1XOHf0t0"
NEW_TITLE = "Wochenschau: Warsaw Victory (04.10.1939) | 8K HQ (4K UHD)"


def main() -> None:
    oauth_data = json.loads(OAUTH_PATH.read_text(encoding="utf-8"))
    creds = Credentials(
        token=oauth_data.get("access_token") or oauth_data.get("token"),
        refresh_token=oauth_data.get("refresh_token"),
        token_uri=oauth_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=oauth_data.get("client_id"),
        client_secret=oauth_data.get("client_secret"),
        scopes=oauth_data.get("scopes"),
    )

    yt = build("youtube", "v3", credentials=creds)

    current = yt.videos().list(part="snippet,status", id=VIDEO_ID).execute()
    items = current.get("items", [])
    if not items:
        raise RuntimeError(f"Video not found: {VIDEO_ID}")

    item = items[0]
    snippet = item["snippet"]
    privacy = item.get("status", {}).get("privacyStatus", "unknown")
    old_title = snippet.get("title", "")

    snippet["title"] = NEW_TITLE

    yt.videos().update(part="snippet", body={"id": VIDEO_ID, "snippet": snippet}).execute()

    print(f"VIDEO_ID: {VIDEO_ID}")
    print(f"OLD_TITLE: {old_title}")
    print(f"NEW_TITLE: {NEW_TITLE}")
    print(f"PRIVACY_UNCHANGED: {privacy}")


if __name__ == "__main__":
    main()
