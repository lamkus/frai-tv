#!/usr/bin/env python3
"""List recent uploads (last N days) with description length and status"""
import json
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def main():
    days = 2
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    with open("config/youtube_oauth.json") as f:
        oauth = json.load(f)

    creds = Credentials(
        token=oauth["token"],
        refresh_token=oauth["refresh_token"],
        token_uri=oauth["token_uri"],
        client_id=oauth["client_id"],
        client_secret=oauth["client_secret"],
    )

    youtube = build("youtube", "v3", credentials=creds)

    channel = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    recent_ids = []
    next_page = None
    while True:
        pl = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=50,
            pageToken=next_page
        ).execute()

        for item in pl.get("items", []):
            published_raw = item["contentDetails"].get("videoPublishedAt")
            if not published_raw:
                continue
            published = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
            if published >= cutoff:
                recent_ids.append(item["contentDetails"]["videoId"])
        next_page = pl.get("nextPageToken")
        if not next_page:
            break

    print(f"Recent uploads (last {days} days): {len(recent_ids)}")
    if not recent_ids:
        return

    for i in range(0, len(recent_ids), 50):
        batch = recent_ids[i:i+50]
        vids = youtube.videos().list(
            part="snippet,status,contentDetails",
            id=",".join(batch)
        ).execute()

        for v in vids.get("items", []):
            snip = v["snippet"]
            status = v["status"]["privacyStatus"]
            desc_len = len(snip.get("description", ""))
            print(f"[{v['id']}] {snip['title']}")
            print(f"  Status: {status} | Desc length: {desc_len} | Duration: {v['contentDetails']['duration']}")


if __name__ == "__main__":
    main()
