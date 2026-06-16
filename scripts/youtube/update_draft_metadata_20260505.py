"""
Update metadata for the newest Wochenschau draft.
Safety: snippet-only update, keeps privacy unchanged.
Quota: videos.list (1) + videos.update (50) + videos.list verify (1) = 52 units.
"""

import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

OAUTH_PATH = Path("config/youtube_oauth.json")
VIDEO_ID = "Fwrlu1MbPpc"

NEW_TITLE = "Wochenschau: Stalingrad Pocket (02.12.1942) | 8K HQ (4K UHD)"

NEW_DESCRIPTION = """🎬 WOCHENSCHAU 639 (02.12.1942)
Stalingrad Kessel | Stalingrad Pocket

Diese Ausgabe der Deutschen Wochenschau dokumentiert die Lage im Kessel von Stalingrad Anfang Dezember 1942.
Ort: Stalingrad, Russia. Historischer Kontext: 300.000 Mann eingeschlossen.

This German newsreel episode documents the Stalingrad pocket in early December 1942.
Location: Stalingrad, Russia. Historical context: 300,000 troops encircled.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg
🇬🇧 German Newsreel, World War II, WWII
🇪🇸 Noticiero aleman, Segunda Guerra Mundial
🇫🇷 Actualites allemandes, Seconde Guerre mondiale
🇵🇹 Cinejornal alemao, Segunda Guerra Mundial
🇷🇺 Nemetskaya kinokhronika, Vtoraya mirovaya voyna
🇯🇵 Doitsu nyusu eiga, Dainiji sekai taisen
🇮🇳 German newsreel, Dvitiya vishva yuddh
🇨🇳 Deguo xinwen pian, erzhan
🇸🇦 German newsreel, alharb alealamiat althaania
🇮🇩 Berita Jerman, Perang Dunia II
🇻🇳 Tin tuc Duc, The chien thu hai
🇹🇷 Alman haber filmi, Ikinci Dunya Savasi
🇰🇷 Dogil nyuseuril, je2cha segye daejeon
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT
🌐 https://frai.tv

📜 Source: Public Domain (UFA 1940-1945)
⚠️ Educational and Historical Use Only
"""

NEW_TAGS = [
    "Wochenschau",
    "Deutsche Wochenschau",
    "German newsreel",
    "WWII",
    "World War II",
    "Stalingrad",
    "Stalingrad Pocket",
    "history",
    "historical footage",
    "public domain",
    "8K",
    "4K UHD",
    "remastered",
    "archival footage",
    "documentary",
]


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
    item = current["items"][0]
    privacy = item.get("status", {}).get("privacyStatus", "unknown")

    # Use a minimal snippet body to avoid stale localized/defaultLanguage fields
    # from older metadata overwriting the new description.
    snippet = {
        "title": NEW_TITLE,
        "description": NEW_DESCRIPTION,
        "tags": NEW_TAGS,
        "categoryId": "27",
    }

    yt.videos().update(part="snippet", body={"id": VIDEO_ID, "snippet": snippet}).execute()

    verify = yt.videos().list(part="snippet,status", id=VIDEO_ID).execute()["items"][0]
    vs = verify["snippet"]

    print(f"VIDEO_ID: {VIDEO_ID}")
    print(f"TITLE: {vs.get('title', '')}")
    print(f"DESC_LEN: {len(vs.get('description', ''))}")
    print(f"TAGS: {len(vs.get('tags', []))}")
    print(f"CATEGORY: {vs.get('categoryId', '')}")
    print(f"PRIVACY_UNCHANGED: {privacy} -> {verify.get('status', {}).get('privacyStatus', '')}")


if __name__ == "__main__":
    main()
