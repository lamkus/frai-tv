"""Check fix history"""
import json

# Fix report Feb 13
with open('config/fix_uploads_2026_02_13_report.json', 'r', encoding='utf-8') as f:
    report13 = json.load(f)
r13 = report13.get('results', [])
print(f"Fixed on 2026-02-13: {len(r13)} videos")
for r in r13:
    print(f"  {r['id']}: {r.get('old_title','?')[:50]} -> {r['title'][:50]}")

# Fix report Feb 12
print()
with open('config/fix_uploads_report_2026_02_12.json', 'r', encoding='utf-8') as f:
    report12 = json.load(f)
if isinstance(report12, dict):
    r12 = report12.get('results', [])
    print(f"Fixed on 2026-02-12: {len(r12)} videos")
    for r in r12:
        rid = r.get('id', '?')
        rtitle = r.get('title', r.get('new_title', '?'))
        rold = r.get('old_title', '?')
        print(f"  {rid}: {rold[:40]} -> {rtitle[:40]}")
elif isinstance(report12, list):
    print(f"Fixed on 2026-02-12: {len(report12)} items")

# Check new_uploads_audit
print()
with open('config/new_uploads_audit.json', 'r', encoding='utf-8') as f:
    audit = json.load(f)
if isinstance(audit, dict):
    keys = list(audit.keys())
    print(f"new_uploads_audit: {len(keys)} entries")
    for k in keys[:5]:
        v = audit[k]
        if isinstance(v, dict):
            print(f"  {k}: {v.get('title','?')[:60]} ({v.get('privacy','?')})")
elif isinstance(audit, list):
    print(f"new_uploads_audit: {len(audit)} items")
