# -*- coding: utf-8 -*-
"""Klassiker-Applier aus config/classics_verified.json (Workflow-verifiziert).
Setzt korrigierten Titel, PD-bewusste Beschreibung (kein PD-Claim auf urheberrechtliche!),
defaultLanguage (Auto-Dub), recordingDate, categoryId. Überspringt 'nicht anfassen' + low-confidence.
DRY default; --apply schreibt. Resume-/quota-sicher (config/classics_progress.json).
"""
import io, sys, json, os, re, time, urllib.request, urllib.parse, urllib.error
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'); sys.stdout.reconfigure(line_buffering=True)
APPLY = '--apply' in sys.argv
o = json.load(open('config/youtube_oauth.json', encoding='utf-8'))
ITEMS = json.load(open('config/classics_verified.json', encoding='utf-8'))
SKIP = set(json.load(open('config/classics_skip.json', encoding='utf-8'))) if os.path.exists('config/classics_skip.json') else set()
SUB = 'https://www.youtube.com/@remAIke_IT?sub_confirmation=1'

def title_of(x):
    t = (x.get('canonical_title') or '').strip()
    if '8K' not in t:
        cand = t + ' | 8K HQ (4K UHD)'
        if len(cand) <= 100: t = cand
        elif len(t + ' | 8K') <= 100: t = t + ' | 8K'
    return t[:100]

def desc_of(x):
    t = title_of(x); hook = (x.get('desc_hook_de') or '').strip()
    pd = x.get('is_public_domain'); typ = x.get('series_or_type') or 'Klassiker'
    head = f'{re.sub(r"\\s*\\|.*$","",t)} – in 8K (4K UHD) KI-restauriert von remAIke.TV.'
    blocks = [head[:125]]
    if hook: blocks.append(hook)
    blocks.append('Originalmaterial: Public Domain.' if pd else 'Historische Restauration · remAIke.TV.')
    blocks.append(f'Alle Klassiker kostenlos auf frai.TV:\nhttps://frai.tv\n\nAbonnieren:\n{SUB}')
    tag = re.sub(r'[^A-Za-z0-9]', '', typ)[:20] or 'Klassiker'
    blocks.append(f'#{tag} #Klassiker #8K #remAIke')
    return '\n\n'.join(blocks)[:4900]

def token():
    return json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token',
        urllib.parse.urlencode({'client_id':o['client_id'],'client_secret':o['client_secret'],
        'refresh_token':o['refresh_token'],'grant_type':'refresh_token'}).encode())).read())['access_token']
tok = token() if APPLY else None
PROG='config/classics_progress.json'
done=set(json.load(open(PROG))) if os.path.exists(PROG) else set()

todo=[x for x in ITEMS if x['id'] not in SKIP and x.get('confidence') in ('high','medium')]
skip_low=[x for x in ITEMS if x.get('confidence')=='low']
print(f'[PLAN] {len(ITEMS)} verifiziert | {len(todo)} anwendbar (high+medium) | {len(skip_low)} low übersprungen | {len(SKIP)} nicht-anfassen')

ok=skip=err=0; quota=False
for x in todo:
    vid=x['id']
    if vid in done: skip+=1; continue
    title=title_of(x); lang=(x.get('language') or 'en').strip() or 'en'
    typ=(x.get('series_or_type') or '').lower()
    cat='27' if ('doku' in typ or 'nasa' in (x.get('desc_hook_de','') or '').lower()) else '1'
    body={'id':vid,'snippet':{'title':title,'description':desc_of(x),'tags':[x.get('series_or_type') or 'Klassiker','Klassiker','8K','remAIke.TV'][:8],
        'categoryId':cat,'defaultLanguage':lang,'defaultAudioLanguage':lang}}
    yr=(x.get('year') or '').strip()
    if re.match(r'^\d{4}$', yr): body['recordingDetails']={'recordingDate':f'{yr}-01-01T00:00:00Z'}
    part='snippet,recordingDetails' if 'recordingDetails' in body else 'snippet'
    if not APPLY:
        if ok<8: print('  [DRY] '+vid+' pd='+str(x.get('is_public_domain'))+' lang='+lang+' | '+title[:55])
        ok+=1; continue
    try:
        urllib.request.urlopen(urllib.request.Request(f'https://www.googleapis.com/youtube/v3/videos?part={part}',
            data=json.dumps(body).encode('utf-8'),headers={'Authorization':f'Bearer {tok}','Content-Type':'application/json'},method='PUT'))
        done.add(vid); ok+=1
        if ok%10==0: print(f'  [{ok}] geschrieben'); json.dump(sorted(done),open(PROG,'w'))
        time.sleep(0.35)
        if ok%100==0: tok=token()
    except urllib.error.HTTPError as e:
        b=e.read().decode()
        if 'quotaExceeded' in b: print(f'[QUOTA] nach {ok} - resume morgen'); quota=True; break
        err+=1; print(f'  [ERR] {vid}: {b[:80]}')
json.dump(sorted(done),open(PROG,'w'))
print(f'\n=== {"APPLY" if APPLY else "DRY"}: {ok} {"geschrieben" if APPLY else "(dry)"}, {skip} skip, {err} Fehler{" (QUOTA)" if quota else ""} ===')
