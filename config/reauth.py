#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick re-auth script - opens browser, saves token."""
import sys, os, json
sys.stdout.reconfigure(line_buffering=True)

from google_auth_oauthlib.flow import InstalledAppFlow

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET = os.path.join(CONFIG_DIR, "client_secret.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.json")
OAUTH_PATH = os.path.join(CONFIG_DIR, "youtube_oauth.json")

SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

print("Opening browser for Google sign-in...", flush=True)
print("Select the remAIke_IT account!", flush=True)

flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET, SCOPES)
creds = flow.run_local_server(port=8090, prompt='consent', access_type='offline')

# Save youtube_oauth.json
oauth_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    "universe_domain": "googleapis.com",
    "account": "",
    "expiry": creds.expiry.isoformat() + "Z" if creds.expiry else ""
}
with open(OAUTH_PATH, 'w') as f:
    json.dump(oauth_data, f, indent=2)

# Save token.json
token_data = {
    "access_token": creds.token,
    "refresh_token": creds.refresh_token,
    "scope": " ".join(SCOPES),
    "token_type": "Bearer",
    "expiry_date": int(creds.expiry.timestamp() * 1000) if creds.expiry else 0
}
with open(TOKEN_PATH, 'w') as f:
    json.dump(token_data, f, indent=2)

print(f"Token saved to {TOKEN_PATH} and {OAUTH_PATH}", flush=True)
print("Done!", flush=True)
