#!/usr/bin/env python3
"""Apply a single SEO update JSON to YouTube"""
import json
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def main():
    if len(sys.argv) < 2:
        print("Usage: apply_single_update.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    with open(json_file, encoding="utf-8") as f:
        payload = json.load(f)

    opt = payload.get("optimized_seo") or payload.get("optimized")
    if not opt:
        print("No optimized_seo or optimized found in JSON.")
        sys.exit(1)

    video_id = payload["video_id"]

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

    current = youtube.videos().list(part="snippet", id=video_id).execute()
    if not current["items"]:
        print(f"Video not found: {video_id}")
        sys.exit(1)

    snippet = current["items"][0]["snippet"]
    snippet["title"] = opt["title"]
    snippet["description"] = opt["description"]
    snippet["tags"] = opt.get("tags", snippet.get("tags", []))
    category_id = opt.get("categoryId") or opt.get("category")
    snippet["categoryId"] = category_id if category_id else snippet.get("categoryId")

    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": snippet},
    ).execute()

    print(f"Updated: {video_id}")


if __name__ == "__main__":
    main()
