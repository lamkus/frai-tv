from __future__ import annotations

import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TARGETS = [
    "H_n_mS-eKps",
    "T-EsdXGhqog",
    "ezYIk8bReaE",
    "exukLdxugy8",
]

creds = Credentials.from_authorized_user_file("token.json")
yt = build("youtube", "v3", credentials=creds)

for vid in TARGETS:
    print(f"\n--- {vid} ---")
    ok = False
    for attempt in range(1, 6):
        try:
            item = yt.videos().list(part="status,snippet", id=vid).execute()["items"][0]
            status = item["status"]
            if status.get("embeddable", True):
                print("already embeddable")
                ok = True
                break
            status["embeddable"] = True
            yt.videos().update(part="status", body={"id": vid, "status": status}).execute()
            print("updated -> embeddable=True")
            ok = True
            break
        except Exception as exc:
            print(f"attempt {attempt} failed: {exc}")
            time.sleep(min(2 * attempt, 10))
    if not ok:
        print("FAILED after retries")
