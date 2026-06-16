#!/usr/bin/env python3
"""Vollständige Analyse ALLER Videos inkl. Drafts, Shorts, etc."""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"

# OAuth laden
oauth = json.loads((CONFIG / "youtube_oauth.json").read_text(encoding="utf-8"))
creds = Credentials(
    token=oauth.get("token"),
    refresh_token=oauth.get("refresh_token"),
    token_uri=oauth.get("token_uri"),
    client_id=oauth.get("client_id"),
    client_secret=oauth.get("client_secret"),
    scopes=oauth.get("scopes"),
)
if creds.expired:
    creds.refresh(Request())
    oauth["token"] = creds.token
    (CONFIG / "youtube_oauth.json").write_text(json.dumps(oauth, indent=2), encoding="utf-8")

youtube = build("youtube", "v3", credentials=creds)

# Channel ID holen
ch = youtube.channels().list(part="contentDetails", mine=True).execute()
uploads_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# ALLE Videos holen (auch private/unlisted)
all_videos = []
next_token = None
while True:
    resp = youtube.playlistItems().list(
        part="snippet,status,contentDetails",
        playlistId=uploads_id,
        maxResults=50,
        pageToken=next_token
    ).execute()
    all_videos.extend(resp.get("items", []))
    next_token = resp.get("nextPageToken")
    if not next_token:
        break

print(f"Total Videos gefunden: {len(all_videos)}")

# Nach Status gruppieren
public = [v for v in all_videos if v["status"]["privacyStatus"] == "public"]
private = [v for v in all_videos if v["status"]["privacyStatus"] == "private"]
unlisted = [v for v in all_videos if v["status"]["privacyStatus"] == "unlisted"]

print(f"Public: {len(public)}")
print(f"Private (Entwuerfe): {len(private)}")
print(f"Unlisted: {len(unlisted)}")

# Shorts finden
print("\n" + "=" * 60)
print("SHORTS / KURZE VIDEOS")
print("=" * 60)
shorts = []
for v in all_videos:
    title = v["snippet"]["title"].lower()
    if "#short" in title or "short" in title or "shorts" in title:
        shorts.append(v)
        status = v["status"]["privacyStatus"]
        print(f"  [{status}] {v['snippet']['title'][:55]}")

if not shorts:
    print("  (Keine Shorts gefunden mit 'short' im Titel)")

# Soundies prüfen
print("\n" + "=" * 60)
print("SOUNDIE VIDEOS")
print("=" * 60)
soundies = []
for v in all_videos:
    title = v["snippet"]["title"].lower()
    if "soundi" in title:
        soundies.append(v)
        status = v["status"]["privacyStatus"]
        vid = v["contentDetails"]["videoId"]
        print(f"  [{status}] {vid} | {v['snippet']['title'][:45]}")

# BraveStarr prüfen  
print("\n" + "=" * 60)
print("BRAVESTARR VIDEOS")
print("=" * 60)
bravestarr = []
for v in all_videos:
    title = v["snippet"]["title"].lower()
    if "brave" in title or "bravestar" in title:
        bravestarr.append(v)
        status = v["status"]["privacyStatus"]
        vid = v["contentDetails"]["videoId"]
        print(f"  [{status}] {vid} | {v['snippet']['title'][:45]}")

# ALLE Private/Entwürfe
print("\n" + "=" * 60)
print("ALLE ENTWUERFE (PRIVATE)")
print("=" * 60)
for v in private:
    vid = v["contentDetails"]["videoId"]
    print(f"  {vid} | {v['snippet']['title'][:55]}")

# Speichern für weitere Verarbeitung
full_data = {
    "total": len(all_videos),
    "public": len(public),
    "private": len(private),
    "unlisted": len(unlisted),
    "shorts_count": len(shorts),
    "soundies_count": len(soundies),
    "bravestarr_count": len(bravestarr),
    "all_videos": [
        {
            "id": v["contentDetails"]["videoId"],
            "title": v["snippet"]["title"],
            "status": v["status"]["privacyStatus"],
            "publishedAt": v["snippet"].get("publishedAt", "")
        }
        for v in all_videos
    ]
}
(CONFIG / "full_channel_scan.json").write_text(json.dumps(full_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n[Gespeichert] config/full_channel_scan.json")
