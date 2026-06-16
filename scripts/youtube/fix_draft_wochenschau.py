#!/usr/bin/env python3
"""Fix 3 Draft Wochenschau videos with raw filenames: Nr.553, Nr.554, Nr.752"""
import os, json, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/../..')

# OAuth
creds = Credentials.from_authorized_user_file('token.json')
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
yt = build('youtube', 'v3', credentials=creds)
print('OAuth OK')

DRAFTS = [
    {
        'id': 'cBaedrKsyuE',
        'nr': 553,
        'date': '09.04.1941',
        'event_en': 'Balkans Campaign',
        'event_de': 'Balkanfeldzug',
        'location': 'Balkans',
    },
    {
        'id': 'st3OhIheE_0',
        'nr': 554,
        'date': '16.04.1941',
        'event_en': 'Belgrade Falls',
        'event_de': 'Belgrad gefallen',
        'location': 'Belgrade, Yugoslavia',
    },
    {
        'id': 'tzqJDt8ASiE',
        'nr': 752,
        'date': '31.01.1945',
        'event_en': 'Auschwitz Liberated',
        'event_de': 'Auschwitz befreit',
        'location': 'Auschwitz, Poland',
    },
]

WS_TAGS = [
    'wochenschau', 'deutsche wochenschau', 'german newsreel', 'WWII',
    'World War 2', 'newsreel', '8K', '4K UHD', 'remastered', 'restored',
    'AI enhanced', 'historical footage', 'public domain', 'vintage newsreel',
    'WW2 footage',
]

results = []
for d in DRAFTS:
    nr = d['nr']
    title_en = f"Wochenschau {nr}: {d['event_en']} ({d['date']}) | 8K HQ (4K UHD)"
    title_de = f"Wochenschau {nr}: {d['event_de']} ({d['date']}) | 8K HQ (4K UHD)"

    desc = (
        f"Wochenschau {nr}: {d['event_en']} ({d['date']}) | 8K HQ (4K UHD)\n"
        f"Deutsche Wochenschau Nr. {nr} - {d['event_de']}. "
        f"Original WWII German newsreel from {d['date']}, AI-remastered in stunning 8K quality.\n\n"
        "HISTORISCHES DOKUMENT - Dieses Video zeigt Original-Material der "
        "NS-Propaganda-Wochenschau. Es dient ausschliesslich der historischen "
        "Dokumentation und Bildung. Die dargestellten Inhalte spiegeln NICHT die "
        "Meinung des Uploaders wider.\n\n"
        f"Location: {d['location']}\n\n"
        "--------------------------------------------\n"
        "LIKE if you found this valuable!\n"
        "COMMENT your thoughts!\n"
        "SUBSCRIBE for more vintage content!\n"
        "--------------------------------------------\n"
        "Web: www.remaike.IT\n"
        "YouTube: https://www.youtube.com/@remAIke_IT\n\n"
        "#Wochenschau #WWII #8K #History #PublicDomain"
    )

    desc_de = desc.replace(d['event_en'], d['event_de'])
    title_short = f"Wochenschau {nr}: {d['event_en']} ({d['date']}) | 8K HQ"

    body = {
        'id': d['id'],
        'snippet': {
            'title': title_en,
            'description': desc,
            'tags': WS_TAGS,
            'categoryId': '27',
            'defaultLanguage': 'de',
        },
        'localizations': {
            'de': {'title': title_de, 'description': desc_de},
            'en': {'title': title_en, 'description': desc},
            'fr': {'title': title_short, 'description': desc},
            'es': {'title': title_short, 'description': desc},
            'pt': {'title': title_short, 'description': desc},
        },
    }

    try:
        resp = yt.videos().update(part='snippet,localizations', body=body).execute()
        new_title = resp['snippet']['title']
        print(f'  OK Nr.{nr}: {new_title}')
        results.append({'nr': nr, 'id': d['id'], 'status': 'OK', 'title': new_title})
    except Exception as e:
        print(f'  FAIL Nr.{nr}: {e}')
        results.append({'nr': nr, 'id': d['id'], 'status': 'ERROR', 'error': str(e)})
    time.sleep(0.5)

ok = sum(1 for r in results if r['status'] == 'OK')
err = sum(1 for r in results if r['status'] != 'OK')
print(f'\nRESULTS: {ok} updated, {err} errors')
print(f'QUOTA USED: {len(results) * 50} units')

# Save report
with open('config/fix_draft_ws_report.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
