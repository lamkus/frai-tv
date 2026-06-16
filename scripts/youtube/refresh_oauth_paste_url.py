#!/usr/bin/env python3
"""
Callback-freie OAuth-Auffrischung.

Warum: Bei Firewall/AV/IPv6-Issues erreicht der Browser-Callback den lokalen
Python-Server NICHT. Dieser Flow vermeidet das Problem komplett:

1. Skript baut Auth-URL und oeffnet sie im Browser
2. Du loggst dich ein und erlaubst Zugriff
3. Browser landet auf http://localhost/?code=...&scope=... (Seite NICHT erreichbar - egal!)
4. Du kopierst die KOMPLETTE Adresszeile aus dem Browser
5. Skript extrahiert den ?code=... Parameter und tauscht ihn gegen ein Token

Speichert token.json atomar erst NACH erfolgreichem Token-Tausch.
"""
import json
import os
import shutil
import sys
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
CLIENT_SECRET = Path("config/client_secret.json")
TOKEN_PATH = Path("token.json")
REDIRECT_URI = "http://localhost"  # Muss EXAKT mit registrierter URI matchen


def extract_code(raw):
    raw = raw.strip().strip('"').strip("'")
    if raw.startswith("http"):
        parsed = urllib.parse.urlparse(raw)
        params = urllib.parse.parse_qs(parsed.query)
        if "error" in params:
            raise SystemExit(f"OAuth error: {params['error'][0]}")
        if "code" not in params:
            raise SystemExit("URL enthaelt keinen ?code= Parameter")
        return params["code"][0]
    if "code=" in raw:
        return raw.split("code=", 1)[1].split("&", 1)[0]
    return raw


def main():
    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Fehlt: {CLIENT_SECRET}")

    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    print("=" * 70)
    print("OAuth Refresh (paste-URL flow)")
    print("=" * 70)
    print()
    print("1) Browser oeffnet jetzt diese URL (oder manuell kopieren):")
    print()
    print(auth_url)
    print()
    print("2) Google-Login + 'Erlauben' klicken.")
    print("3) Browser leitet auf http://localhost/?code=... weiter.")
    print("   Die Seite zeigt 'Diese Seite ist nicht erreichbar' - das ist OK!")
    print("4) Kopiere die KOMPLETTE Adresszeile aus dem Browser.")
    print()

    try:
        webbrowser.open(auth_url, new=2)
    except Exception:
        pass

    raw = input("URL hier einfuegen (oder nur den code= Wert) und Enter:\n> ")
    code = extract_code(raw)
    print(f"\nCode extrahiert ({len(code)} chars). Tausche gegen Token...")

    flow.fetch_token(code=code)
    creds = flow.credentials

    if not creds or not creds.valid:
        raise SystemExit("Token-Tausch lieferte ungueltige Credentials")
    if not creds.refresh_token:
        raise SystemExit("Kein refresh_token - consent wurde nicht erteilt")

    # Backup vorhandenes Token
    backup_path = None
    if TOKEN_PATH.exists():
        backup_path = Path(f"token.json.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        shutil.copy2(TOKEN_PATH, backup_path)

    # Atomic write via tmp + replace
    tmp = Path("token.json.tmp")
    tmp.write_text(creds.to_json(), encoding="utf-8")
    check = Credentials.from_authorized_user_file(str(tmp), SCOPES)
    if not check.valid or not check.refresh_token:
        tmp.unlink(missing_ok=True)
        raise SystemExit("Validierung des neuen Tokens fehlgeschlagen")

    os.replace(tmp, TOKEN_PATH)

    print()
    print("=" * 70)
    print("OK - token.json aktualisiert")
    print(f"Expiry:        {check.expiry}")
    print(f"Refresh token: {'JA' if check.refresh_token else 'NEIN'}")
    print(f"Scopes:        {', '.join(check.scopes or SCOPES)}")
    if backup_path:
        print(f"Backup:        {backup_path}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(1)
