# -*- coding: utf-8 -*-
"""Generiert scripts/youtube/_classics_workflow.js mit eingebetteten Klassiker-Videos."""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
rows = json.load(open('config/other_videos.json', encoding='utf-8'))
EXC = ['betty boop', 'felix', 'popeye', 'casper', 'soundie', 'maulwurf', 'krtek', 'looney', 'dinner for one']
classics = [{'id': r['id'], 'title': r['title']} for r in rows
            if not any(k in r['title'].lower() for k in EXC) and r['title'].strip()]
DATA = json.dumps(classics, ensure_ascii=False)

RULES = (
    "You verify metadata for classic film/TV videos on a German restoration archive. "
    "For EACH video (given as 'id | current title'), identify the actual work and return per video:\n"
    "- canonical_title: a clean, correct title. FIX broken/truncated/garbage titles (e.g. '#1', cut-off names). Stay close to the channel style but accurate.\n"
    "- year: production year (empty string if unknown)\n"
    "- language: ISO code of the SPOKEN language (de for German productions, en for English; empty if silent)\n"
    "- is_public_domain: TRUE only if verifiably public domain. German TV/film productions such as 'Der 7. Sinn', 'Familie Heinz Becker', 'Drueben bei Lehmanns', 'Der kleene Punker' are COPYRIGHTED -> false. Be conservative: if unsure, false.\n"
    "- series_or_type: e.g. 'Der 7. Sinn', 'Spielfilm', 'Kurzfilm', 'Dokumentation'\n"
    "- desc_hook_de: one factual German sentence describing the work\n"
    "- confidence (high/medium/low) + notes\n"
    "Use web search to verify. Do NOT invent facts. Be accurate and conservative about copyright."
)

js = (
"export const meta = {\n"
"  name: 'classics-verify',\n"
"  description: 'Verify identity, year, language and public-domain status of classic film/TV videos',\n"
"  phases: [{ title: 'Verify' }],\n"
"}\n"
"const VIDEOS = " + DATA + ";\n"
"const BATCH = 6;\n"
"const batches = [];\n"
"for (let i = 0; i < VIDEOS.length; i += BATCH) batches.push(VIDEOS.slice(i, i + BATCH));\n"
"const ITEM = { id:{type:'string'}, canonical_title:{type:'string'}, year:{type:'string'}, language:{type:'string'}, is_public_domain:{type:'boolean'}, series_or_type:{type:'string'}, desc_hook_de:{type:'string'}, confidence:{type:'string',enum:['high','medium','low']}, notes:{type:'string'} };\n"
"const SCHEMA = { type:'object', properties:{ items:{ type:'array', items:{ type:'object', properties: ITEM, required:['id','canonical_title','language','is_public_domain','confidence'] } } }, required:['items'] };\n"
"const RULES = " + json.dumps(RULES) + ";\n"
"phase('Verify');\n"
"const res = await parallel(batches.map((b) => () => agent(RULES + '\\n\\nVideos:\\n' + b.map((v) => v.id + ' | ' + v.title).join('\\n'), { label: 'verify ' + b[0].id, phase: 'Verify', schema: SCHEMA })));\n"
"const flat = res.filter(Boolean).flatMap((r) => (r && r.items) ? r.items : []);\n"
"const pd = flat.filter((x) => x.is_public_domain).length;\n"
"return { count: flat.length, public_domain: pd, copyrighted: flat.length - pd, items: flat };\n"
)
open('scripts/youtube/_classics_workflow.js', 'w', encoding='utf-8').write(js)
print('Geschrieben:', len(classics), 'Klassiker -> scripts/youtube/_classics_workflow.js (', len(js), 'Bytes )')
