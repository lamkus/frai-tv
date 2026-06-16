#!/usr/bin/env python3
"""Re-authenticate OAuth and save fresh token.json only after success."""
import os
import shutil
from datetime import datetime
from pathlib import Path

import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
TOKEN_PATH = Path("token.json")

def main():
    started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"OAuth refresh started: {started}")
    print("Existing token.json will stay untouched until Google callback succeeds.")

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "config/client_secret.json", SCOPES
    )

    creds = flow.run_local_server(
        host="127.0.0.1",
        port=0,
        authorization_prompt_message=(
            "Open this URL in your browser and approve YouTube access:\n{url}\n"
        ),
        success_message="OAuth complete. You can close this browser tab and return to VS Code.",
        open_browser=True,
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true",
    )

    if not creds or not creds.valid:
        raise RuntimeError("OAuth completed but credentials are not valid")
    if not creds.refresh_token:
        raise RuntimeError("OAuth completed without refresh_token; consent was not granted")

    backup_path = None
    if TOKEN_PATH.exists():
        backup_path = Path(f"token.json.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(TOKEN_PATH, backup_path)

    tmp_path = Path("token.json.tmp")
    tmp_path.write_text(creds.to_json(), encoding="utf-8")

    # Re-read before replacing to prove the file is parseable.
    check = Credentials.from_authorized_user_file(str(tmp_path), SCOPES)
    if not check.valid or not check.refresh_token:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError("New token failed validation before replacement")

    os.replace(tmp_path, TOKEN_PATH)
    print("Fresh token.json saved and validated.")
    if backup_path:
        print(f"Previous token backed up to {backup_path}")
    print(f"Expiry: {check.expiry}")
    print(f"Scopes: {', '.join(check.scopes or SCOPES)}")

if __name__ == "__main__":
    main()
