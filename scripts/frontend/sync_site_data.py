# -*- coding: utf-8 -*-
"""Synchronisiert frai.tv (code/frontend/src/data/projectorData.js) mit den korrigierten
YouTube-Canonicals: ersetzt t (Titel) + desc je Video aus wochenschau_canonical.json (per wNum)
und alfred_canonical.json (per Episode). Andere Videos bleiben unberührt (Phase 3).
Idempotent: nur abweichende Felder werden ersetzt. --dry zeigt nur Zahlen.
"""
import io, sys, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--dry' in sys.argv
PD = 'code/frontend/src/data/projectorData.js'

woch = {str(c['nr']): c for c in json.load(open('config/wochenschau_canonical.json', encoding='utf-8'))}
alf = {int(c['ep']): c for c in json.load(open('config/alfred_canonical.json', encoding='utf-8'))}
alf_eps = json.load(open('config/alfred_episodes.json', encoding='utf-8'))

def jsesc(s):
    return (s or '').replace('\\', '\\\\').replace("'", "\\'").replace('\r', '').replace('\n', '\\n')

def norm(s):
    s = (s or '').lower().replace('ß', 'ss').replace('ä', 'a').replace('ö', 'o').replace('ü', 'u')
    return re.sub(r'[^a-z0-9]', '', s)

def alfred_ep_for(title):
    full = norm(title); best = None; bl = 0
    for e in alf_eps:
        tn = norm(e['title_de'])
        if len(tn) >= 4 and tn in full and len(tn) > bl:
            best = e['ep']; bl = len(tn)
    return best

src = open(PD, encoding='utf-8').read()
# Objektblöcke: { id: '...', ... },
block_re = re.compile(r"\{\s*id:\s*'([^']+)',(.*?)\n(\s*)\},", re.DOTALL)
upd_woch = upd_alf = skip = 0

def repl(m):
    global upd_woch, upd_alf, skip
    vid, body, indent = m.group(1), m.group(2), m.group(3)
    wnum = re.search(r"wNum:\s*(\d+)", body)
    cat = re.search(r"cat:\s*'([^']*)'", body)
    cur_t = re.search(r"t:\s*'((?:[^'\\]|\\.)*)'", body)
    canon = None
    if wnum and wnum.group(1) in woch:
        canon = woch[wnum.group(1)]; kind = 'woch'
    elif (cat and 'alfred' in cat.group(1).lower()) or (cur_t and 'kwak' in cur_t.group(1).lower()):
        ep = alfred_ep_for(cur_t.group(1) if cur_t else '')
        if ep and ep in alf:
            canon = alf[ep]; kind = 'alf'
    if not canon:
        skip += 1
        return m.group(0)
    nt = jsesc(canon['title']); nd = jsesc(canon['description'])
    # Lambda-Replacement: liefert den String LITERAL (re.sub verarbeitet sonst Backslashes im Replacement)
    new_body = re.sub(r"t:\s*'(?:[^'\\]|\\.)*'", lambda _: "t: '%s'" % nt, body, count=1)
    if re.search(r"desc:\s*'(?:[^'\\]|\\.)*'", new_body):
        new_body = re.sub(r"desc:\s*'(?:[^'\\]|\\.)*'", lambda _: "desc: '%s'" % nd, new_body, count=1)
    else:  # kein desc-Feld -> nach t einfügen
        new_body = re.sub(r"(t:\s*'(?:[^'\\]|\\.)*',)", lambda mm: "%s\n    desc: '%s'," % (mm.group(1), nd), new_body, count=1)
    if kind == 'woch': upd_woch += 1
    else: upd_alf += 1
    return "{ id: '%s',%s\n%s}," % (vid, new_body, indent)

new_src = block_re.sub(repl, src)
print(f'Wochenschau aktualisiert: {upd_woch} | Alfred: {upd_alf} | unberührt: {skip}')
if not DRY:
    open(PD, 'w', encoding='utf-8').write(new_src)
    print('-> geschrieben:', PD)
else:
    print('(dry-run, nichts geschrieben)')
