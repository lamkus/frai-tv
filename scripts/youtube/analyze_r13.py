"""Analyze R13 and multi-issue videos"""
import json

with open('config/full_compliance_issues_2026_02_17.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

r13 = [v for v in data['fixable'] if any('R13' in i for i in v['issues'])]
print(f"R13 (missing pflicht-tags) videos: {len(r13)}")
for v in r13:
    print(f"  {v['id']}: [{v['privacy']}] {v['title'][:65]}")

print()
multi = [v for v in data['fixable'] if len(v['issues']) > 1]
print(f"Videos with MULTIPLE issues: {len(multi)}")
for v in multi:
    print(f"  {v['id']}: {v['title'][:50]}")
    for i in v['issues']:
        print(f"    - {i}")
