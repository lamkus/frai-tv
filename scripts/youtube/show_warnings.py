import json

audit = json.load(open('D:/remaike.TV/config/compliance_audit_2026_02_08.json', encoding='utf-8'))
for r in audit['results']:
    for w in r['warnings']:
        if 'MADE_FOR_KIDS' in w:
            print(f"MFK: {r['id']} | {r['title'][:65]}")
        if 'KENBLOCK_CATEGORY' in w:
            print(f"CAT: {r['id']} | {r['title'][:65]} | cat={r['category']}")
        if 'OLD_NAMING' in w:
            print(f"OLD: {r['id']} | {r['title'][:65]}")
