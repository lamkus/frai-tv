#!/usr/bin/env python3
"""Manual OAuth fallback: paste redirected loopback URL/code, save token.json."""
import os
import shutil
import urllib.parse
from datetime import datetime
from pathlib import Path

import google_auth_oauthlib.flow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
REDIRECT_URI = "http://127.0.0.1:8090/"
TOKEN_PATH = Path("token.json")

def extract_code(value):
    value = value.strip()
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urllib.parse.urlparse(value)
        params = urllib.parse.parse_qs(parsed.query)
        codes = params.get("code")
        if not codes:
            raise ValueError("No code parameter found in pasted URL")
        return codes[0]
    return value

def main():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "config/client_secret.json",
        SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    print("Open this URL in your browser:")
    print(auth_url)
    print()
    print("After approving, the browser may show an unreachable localhost page.")
    print("Copy the FULL address bar URL (or only the code= value) and paste it below.")
    pasted = input("Redirect URL or code: ").strip()
    code = extract_code(pasted)

    flow.fetch_token(code=code)
    creds = flow.credentials
    if not creds or not creds.valid or not creds.refresh_token:
        raise RuntimeError("OAuth returned invalid credentials")

    backup = None
    if TOKEN_PATH.exists():
        backup = Path(f"token.json.bak_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(TOKEN_PATH, backup)

    tmp_path = Path("token.json.tmp")
    tmp_path.write_text(creds.to_json(), encoding="utf-8")
    check = Credentials.from_authorized_user_file(str(tmp_path), SCOPES)
    if not check.valid or not check.refresh_token:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError("New token failed validation before replacement")
    os.replace(tmp_path, TOKEN_PATH)

    print("Fresh token.json saved and validated")
    if backup:
        print(f"Previous token backed up to {backup}")
    print(f"Expiry: {check.expiry}")
    print(f"Scopes: {', '.join(check.scopes or SCOPES)}")

if __name__ == "__main__":
    main()
