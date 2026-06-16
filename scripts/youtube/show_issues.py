#!/usr/bin/env python3
"""Zeigt alle Videos mit Problemen und erstellt Fix-Plan"""

import json

with open('config/rename_audit_result.json', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("🔧 8K INKONSISTENT - Brauchen '8K HQ' statt nur '8K'")
print("=" * 70)
for v in data['issues']['inconsistent_8k']:
    print(f"  {v['id']}: {v['title'][:70]}")
print(f"\nTotal: {len(data['issues']['inconsistent_8k'])}")
print()

print("=" * 70)
print("❌ KEIN BRANDING @remAIke_IT")
print("=" * 70)
for v in data['issues']['no_branding']:
    print(f"  {v['id']}: {v['title'][:70]}")
print()

print("=" * 70)
print("⚠️ ZU LANG (>90 Zeichen)")
print("=" * 70)
for v in data['issues']['too_long'][:30]:
    print(f"  {v['id']}: {len(v['title'])} chars - {v['title'][:60]}...")
print(f"\nTotal: {len(data['issues']['too_long'])}")
