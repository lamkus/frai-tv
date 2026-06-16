#!/usr/bin/env python3
"""Fix localizations for the 3 new uploads by setting defaultLanguage first."""
import sys, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = r"D:\remaike.TV\token.json"

def yt_client():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

yt = yt_client()
quota = 0

VIDEOS = [
    {
        "id": "pFCidUe6JV4",
        "defaultLanguage": "en",
        "localizations": {
            "de": {"title": "Wochenschau 605: Lübeck bombardiert (08.04.1942) | 8K HQ (4K UHD)",
                   "description": "Deutsche Wochenschau Nr. 605 — Luftangriff auf Lübeck (28./29.03.1942)"},
            "en": {"title": "Wochenschau 605: Lubeck Bombed (08.04.1942) | 8K HQ (4K UHD)",
                   "description": "German Newsreel Nr. 605 — RAF Bombing of Lübeck (March 28-29, 1942)"},
            "es": {"title": "Wochenschau 605: Bombardeo de Lübeck (08.04.1942) | 8K HQ",
                   "description": "Noticiero alemán Nr. 605 — Bombardeo de Lübeck"},
            "pt": {"title": "Wochenschau 605: Bombardeio de Lübeck (08.04.1942) | 8K HQ",
                   "description": "Cinejornal alemão Nr. 605 — Bombardeio de Lübeck"},
            "fr": {"title": "Wochenschau 605: Bombardement de Lübeck (08.04.1942) | 8K HQ",
                   "description": "Actualités allemandes Nr. 605 — Bombardement de Lübeck"},
            "ja": {"title": "ドイツニュース映画 605: リューベック爆撃 (1942) | 8K HQ",
                   "description": "ドイツニュース映画第605号 — リューベック爆撃"},
            "ru": {"title": "Вохеншау 605: Бомбардировка Любека (08.04.1942) | 8K HQ",
                   "description": "Немецкая кинохроника Nr. 605 — Бомбардировка Любека"},
        }
    },
    {
        "id": "Ima7UohPE4Y",
        "defaultLanguage": "en",
        "localizations": {
            "de": {"title": "Wochenschau 606: Baedeker-Angriffe (15.04.1942) | 8K HQ (4K UHD)",
                   "description": "Deutsche Wochenschau Nr. 606 — Baedeker-Angriffe auf englische Kulturstädte"},
            "en": {"title": "Wochenschau 606: Baedeker Raids (15.04.1942) | 8K HQ (4K UHD)",
                   "description": "German Newsreel Nr. 606 — Baedeker Raids on English historic cities"},
            "es": {"title": "Wochenschau 606: Ataques Baedeker (15.04.1942) | 8K HQ",
                   "description": "Noticiero alemán Nr. 606 — Ataques Baedeker"},
            "pt": {"title": "Wochenschau 606: Ataques Baedeker (15.04.1942) | 8K HQ",
                   "description": "Cinejornal alemão Nr. 606 — Ataques Baedeker"},
            "fr": {"title": "Wochenschau 606: Raids Baedeker (15.04.1942) | 8K HQ",
                   "description": "Actualités allemandes Nr. 606 — Raids Baedeker"},
            "ja": {"title": "ドイツニュース映画 606: ベデカー空襲 (1942) | 8K HQ",
                   "description": "ドイツニュース映画第606号 — ベデカー空襲"},
            "ru": {"title": "Вохеншау 606: Бедекерские налёты (15.04.1942) | 8K HQ",
                   "description": "Немецкая кинохроника Nr. 606 — Бедекерские налёты"},
        }
    },
    {
        "id": "SYY31eEbYiQ",
        "defaultLanguage": "de",
        "localizations": {
            "de": {"title": "Der 7. Sinn: Frauen am Steuer (1970er) | 8K HQ (4K UHD)",
                   "description": "Der 7. Sinn — Frauen am Steuer – Übung macht den Meister"},
            "en": {"title": "Der 7. Sinn: Women Drivers (1970s) | 8K HQ (4K UHD)",
                   "description": "Der 7. Sinn — Women Drivers – Practice Makes Perfect"},
            "fr": {"title": "Der 7. Sinn: Femmes au volant (1970s) | 8K HQ",
                   "description": "Der 7. Sinn — Femmes au volant – C'est en forgeant qu'on devient forgeron"},
            "es": {"title": "Der 7. Sinn: Mujeres al volante (1970s) | 8K HQ",
                   "description": "Der 7. Sinn — Mujeres al volante – La práctica hace al maestro"},
        }
    },
]

for vid in VIDEOS:
    vid_id = vid["id"]
    print(f"\n📹 {vid_id} — Setting defaultLanguage + localizations")

    try:
        # Step 1: Get current snippet + set defaultLanguage
        resp = yt.videos().list(part="snippet,localizations", id=vid_id).execute()
        quota += 1

        if not resp["items"]:
            print(f"   ❌ Not found")
            continue

        item = resp["items"][0]
        snippet = item["snippet"]
        snippet["defaultLanguage"] = vid["defaultLanguage"]

        # Set defaultLanguage via snippet update
        yt.videos().update(
            part="snippet",
            body={"id": vid_id, "snippet": snippet}
        ).execute()
        quota += 50
        print(f"   ✅ defaultLanguage = {vid['defaultLanguage']} (quota: {quota})")
        time.sleep(0.5)

        # Step 2: Now set localizations
        yt.videos().update(
            part="localizations",
            body={"id": vid_id, "localizations": vid["localizations"]}
        ).execute()
        quota += 50
        print(f"   ✅ {len(vid['localizations'])} localizations set (quota: {quota})")
        time.sleep(0.5)

    except Exception as e:
        print(f"   ❌ {e}")

print(f"\n{'='*50}")
print(f"Quota used: {quota}")
