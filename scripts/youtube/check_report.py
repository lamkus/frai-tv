import json

with open('config/mega_fix_report_2026_02_18.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

ok = sum(1 for x in r['results'] if x['status'] == 'success')
err = sum(1 for x in r['results'] if x['status'] == 'error')
print(f"Applied: {ok} OK, {err} errors, {r['skipped']} already OK")
print(f"Quota used: {r['quota_used']} units")

if err:
    for x in r['results']:
        if x['status'] == 'error':
            print(f"  ERR: {x['id']}: {x.get('error', '?')}")

tc = 0
for x in r['results']:
    if x['status'] == 'success' and 'old_title' in x and x['old_title'] != x['new_title']:
        if tc < 8:
            print(f"  BEFORE: {x['old_title'][:70]}")
            print(f"  AFTER:  {x['new_title'][:70]}")
            print()
            tc += 1
