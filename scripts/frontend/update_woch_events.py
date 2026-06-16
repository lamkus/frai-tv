# -*- coding: utf-8 -*-
"""Aktualisiert die WOCHENSCHAU_EVENTS-Sektion in projectorData.js (de/en/note/loc/date)
aus config/wochenschau_verified.json. Diese Sektion speist OG-Titel/Keywords/JSON-LD/Body
der Watch-Pages + die /wochenschau-Hub-Seite. Idempotent. --dry zeigt nur Zahlen.
"""
import io, sys, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--dry' in sys.argv
PD = 'code/frontend/src/data/projectorData.js'
VER = {str(v['nr']): v for v in json.load(open('config/wochenschau_verified.json', encoding='utf-8'))}

def jsesc(s):
    return (s or '').replace('\\', '\\\\').replace("'", "\\'").replace('\r', '').replace('\n', ' ').strip()

src = open(PD, encoding='utf-8').read()
# Event-Blöcke: "  <nr>: { ... de: ... en: ... loc: ... },"  (keine verschachtelten {})
ev_re = re.compile(r"(\n\s*)(\d+):\s*\{((?:[^{}]|'(?:[^'\\]|\\.)*')*?)\},", re.DOTALL)
upd = [0]

def repl(m):
    indent, nr, body = m.group(1), m.group(2), m.group(3)
    if nr not in VER or 'de:' not in body or 'loc:' not in body:
        return m.group(0)
    v = VER[nr]
    de = jsesc(v.get('event_keyword_de', ''))
    en = jsesc(v.get('event_keyword_en') or v.get('event_keyword_de', ''))
    note = jsesc((v.get('content_summary_de', '') or '')[:200])
    th = v.get('primary_theaters') or []
    date = v.get('verified_date', '')
    nb = body
    nb = re.sub(r"de:\s*'(?:[^'\\]|\\.)*'", lambda _: "de: '%s'" % de, nb, count=1)
    nb = re.sub(r"en:\s*'(?:[^'\\]|\\.)*'", lambda _: "en: '%s'" % en, nb, count=1)
    if re.search(r"note:\s*'(?:[^'\\]|\\.)*'", nb):
        nb = re.sub(r"note:\s*'(?:[^'\\]|\\.)*'", lambda _: "note: '%s'" % note, nb, count=1)
    if date and re.search(r"date:\s*'[^']*'", nb):
        nb = re.sub(r"date:\s*'[^']*'", lambda _: "date: '%s'" % date, nb, count=1)
    if th and re.search(r"loc:\s*'(?:[^'\\]|\\.)*'", nb):
        nb = re.sub(r"loc:\s*'(?:[^'\\]|\\.)*'", lambda _: "loc: '%s'" % jsesc(th[0]), nb, count=1)
    upd[0] += 1
    return "%s%s: {%s}," % (indent, nr, nb)

new_src = ev_re.sub(repl, src)
print('WOCHENSCHAU_EVENTS aktualisiert:', upd[0])
if not DRY:
    open(PD, 'w', encoding='utf-8').write(new_src)
    print('-> geschrieben')
else:
    print('(dry)')
