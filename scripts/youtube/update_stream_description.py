"""
update_stream_description.py
Updates the live broadcast description to include community engagement CTA
and the episode archive status. Run whenever description needs refresh.
"""
import json, os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOKEN     = os.path.join(BASE_DIR, 'token.json')
STATE_F   = os.path.join(BASE_DIR, 'config', 'broadcast_state.json')
EVENTS_F  = os.path.join(BASE_DIR, 'config', 'wochenschau_events.json')

D_DIR = os.path.join(BASE_DIR, 'wochenschau_rendered')
E_DIR = r'E:\wochenschau_rendered'

# Count rendered
rendered = set()
for d in [D_DIR, E_DIR]:
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith('.mp4') and 'Nr' in f:
                try: rendered.add(int(f.split('Nr')[1].split('_')[0]))
                except: pass

with open(EVENTS_F, 'r', encoding='utf-8') as f:
    raw = json.load(f)
    events = raw.get('events', raw)
total_known = len([k for k in events.keys() if str(k).isdigit()])

with open(STATE_F) as f:
    state = json.load(f)
bid = state['broadcast_id']

# ── SEO-optimised description with community CTA ──────────────────────────────
# First 2 lines = visible in YouTube search (high-value keywords!)
NEW_DESC = f"""🎬 Deutsche Wochenschau 1939–1945 | AI Remastered 8K Documentary Archive | 24/7 Stream
WWII Newsreels restored to stunning 4K UHD — history as it was filmed, uncut and uncensored.

⚠️ HISTORISCHES DOKUMENT | HISTORICAL DOCUMENT
Dieses Material dient ausschließlich der historischen Dokumentation und Bildung.
Die dargestellten Inhalte spiegeln NICHT die Meinung des Uploaders wider.
This content does NOT reflect the views of the uploader. Educational purposes only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 ARCHIV-STATUS | ARCHIVE STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Im Stream verfügbar | Currently streaming:  {len(rendered)} Wochenschau-Ausgaben
🔄 Gesamtarchiv geplant | Full archive target:  {total_known} Ausgaben (1939–1945)
📦 Im Aufbau | In progress:               {total_known - len(rendered)} Ausgaben noch ausstehend

WIR BAUEN DAS VOLLSTÄNDIGE ARCHIV AUF!
Welche Ausgabe wollt ihr als nächstes sehen?
👇 KOMMENTIERT: "Nr. XXX" oder "Datum: TT.MM.JJJJ"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💬 COMMUNITY – MITMACHEN & MITGESTALTEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🗳️ Welche Wochenschau-Ausgabe fehlt euch?
   → Kommentiert die Nummer oder das Datum!
📚 Historische Fragen oder Ergänzungen?
   → Schreibt sie in die Kommentare!
🔍 Ihr sucht eine bestimmte Schlachtszene / Ereignis?
   → Wir priorisieren eure Wünsche!

Dieses Archiv lebt durch eure Nachfrage. Je mehr ihr anfragt,
desto schneller wird die nächste Folge verfügbar.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you value preserved history!
💬 COMMENT which episode you want next!
🔔 SUBSCRIBE – new episodes added regularly!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Wochenschau #WWII #8K #Geschichte #History #PublicDomain #4K #Remastered #Documentary #WW2"""

# ── Apply via API ─────────────────────────────────────────────────────────────
creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN, 'w') as f:
        f.write(creds.to_json())
yt = build('youtube', 'v3', credentials=creds)

# Fetch current snippet (keep scheduledStartTime etc)
r = yt.liveBroadcasts().list(part='snippet', id=bid).execute()
snippet = r['items'][0]['snippet']
snippet['description'] = NEW_DESC

yt.liveBroadcasts().update(part='snippet', body={'id': bid, 'snippet': snippet}).execute()

print(f'✅ Broadcast {bid} description updated.')
print(f'   Archive status shown: {len(rendered)}/{total_known} episodes rendered')
print(f'   Community CTA: aktiv')
