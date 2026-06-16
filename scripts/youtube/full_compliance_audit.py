"""
FULL COMPLIANCE AUDIT — Alle Regeln aus dem Workspace prüfen.
Checked rules:
1. 8K/4K in title
2. @remAIke_IT NOT in title (new rule)
3. Max 70 chars title
4. CTA in description (LIKE/SUBSCRIBE)
5. www.remaike.IT link in description
6. YouTube channel link in description
7. Max 5 hashtags
8. Max 15 tags
9. Category correct per series
10. "sls" raw marker NOT in title
"""
import sqlite3, json, re

DB = r"D:\remaike.TV\tools\channel_manager\channel_manager.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get all public videos
cur.execute("""
    SELECT id, title, description, tags, category_id, series, privacy_status
    FROM videos 
    WHERE privacy_status = 'public'
    ORDER BY series, title
""")
videos = [dict(r) for r in cur.fetchall()]
print(f"📊 {len(videos)} public videos to audit\n")

# Category rules
CATEGORY_RULES = {
    'soundies': 10,       # Music
    'wochenschau': 27,    # Education
    'ken_block': 2,       # Autos
    # Everything else: 1 (Film & Animation)
}
DEFAULT_CAT = 1

issues = {
    'no_8k_in_title': [],
    'handle_in_title': [],
    'title_too_long': [],
    'no_cta_in_desc': [],
    'no_website_in_desc': [],
    'no_channel_link_in_desc': [],
    'too_many_hashtags': [],
    'too_many_tags': [],
    'wrong_category': [],
    'raw_sls_in_title': [],
    'no_description': [],
}

for v in videos:
    title = v['title'] or ''
    desc = v['description'] or ''
    tags = v['tags'] or ''
    cat = v['category_id']
    series = v['series'] or 'unknown'
    
    # 1. 8K or 4K in title?
    if '8K' not in title and '4K' not in title and '8k' not in title and '4k' not in title:
        issues['no_8k_in_title'].append(v)
    
    # 2. @remAIke_IT in title (should NOT be there per new rules)
    if '@remAIke_IT' in title or '@remaike' in title.lower():
        issues['handle_in_title'].append(v)
    
    # 3. Title too long (max 70 chars)
    if len(title) > 70:
        issues['title_too_long'].append(v)
    
    # 4. CTA in description
    desc_lower = desc.lower()
    has_cta = any(w in desc_lower for w in ['subscribe', 'abonnieren', 'like', '👆', '💬', '🔔'])
    if not has_cta:
        issues['no_cta_in_desc'].append(v)
    
    # 5. www.remaike.IT in description
    if 'remaike.it' not in desc_lower and 'remaike' not in desc_lower:
        issues['no_website_in_desc'].append(v)
    
    # 6. YouTube channel link in description
    if '@remaike_it' not in desc_lower and 'youtube.com/@remaike' not in desc_lower:
        issues['no_channel_link_in_desc'].append(v)
    
    # 7. Max 5 hashtags in description
    hashtags = re.findall(r'#\w+', desc)
    if len(hashtags) > 5:
        issues['too_many_hashtags'].append({**v, '_hashtag_count': len(hashtags)})
    
    # 8. Max 15 tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()] if tags else []
    if len(tag_list) > 15:
        issues['too_many_tags'].append({**v, '_tag_count': len(tag_list)})
    
    # 9. Category correct?
    expected_cat = CATEGORY_RULES.get(series, DEFAULT_CAT)
    if cat and int(cat) != expected_cat:
        issues['wrong_category'].append({**v, '_expected': expected_cat, '_actual': cat})
    
    # 10. "sls" raw marker in title
    if ' sls ' in title.lower() or title.lower().endswith(' sls') or '_sls_' in title.lower():
        issues['raw_sls_in_title'].append(v)
    
    # 11. No description at all
    if len(desc.strip()) < 50:
        issues['no_description'].append(v)

# ════════════════════════════════════════
# REPORT
# ════════════════════════════════════════
print("=" * 70)
print("📋 FULL COMPLIANCE AUDIT REPORT")
print("=" * 70)

for key, vids in issues.items():
    label = key.replace('_', ' ').upper()
    print(f"\n{'❌' if vids else '✅'} {label}: {len(vids)} videos")
    if vids and key == 'no_8k_in_title':
        print("   These videos have NO '8K' or '4K' in their title:")
        for v in vids:
            print(f"   - [{v['series']}] {v['title'][:80]}")
            print(f"     ID: {v['id']}")
    elif vids and key == 'handle_in_title':
        for v in vids:
            print(f"   - {v['title'][:80]}")
    elif vids and key == 'title_too_long':
        for v in vids[:10]:
            print(f"   - [{len(v['title'])} chars] {v['title'][:80]}")
        if len(vids) > 10:
            print(f"   ... and {len(vids)-10} more")
    elif vids and key == 'wrong_category':
        for v in vids[:10]:
            print(f"   - [{v['series']}] Cat {v['_actual']} → should be {v['_expected']}: {v['title'][:60]}")
    elif vids and key == 'too_many_tags':
        for v in vids[:10]:
            print(f"   - [{v['_tag_count']} tags] {v['title'][:60]}")
        if len(vids) > 10:
            print(f"   ... and {len(vids)-10} more")
    elif vids and key == 'too_many_hashtags':
        for v in vids[:10]:
            print(f"   - [{v['_hashtag_count']} hashtags] {v['title'][:60]}")
    elif vids and key == 'raw_sls_in_title':
        for v in vids:
            print(f"   - {v['title'][:80]}")
    elif vids and key in ('no_cta_in_desc', 'no_website_in_desc', 'no_channel_link_in_desc', 'no_description'):
        by_series = {}
        for v in vids:
            by_series.setdefault(v['series'] or 'unknown', []).append(v)
        for s, svids in sorted(by_series.items()):
            print(f"   {s}: {len(svids)} videos")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)
total_issues = sum(len(v) for v in issues.values())
print(f"Total issues found: {total_issues}")
print(f"Videos audited: {len(videos)}")
print(f"\nCritical (affects SEO/visibility):")
print(f"  No 8K in title:      {len(issues['no_8k_in_title'])}")
print(f"  No CTA in desc:      {len(issues['no_cta_in_desc'])}")
print(f"  No website link:     {len(issues['no_website_in_desc'])}")
print(f"  Wrong category:      {len(issues['wrong_category'])}")
print(f"\nWarnings:")
print(f"  Handle in title:     {len(issues['handle_in_title'])}")
print(f"  Title too long:      {len(issues['title_too_long'])}")
print(f"  Too many hashtags:   {len(issues['too_many_hashtags'])}")
print(f"  Too many tags:       {len(issues['too_many_tags'])}")
print(f"  Raw 'sls' in title:  {len(issues['raw_sls_in_title'])}")
print(f"  No/short description:{len(issues['no_description'])}")

# Save detailed report
report = {
    'total_videos': len(videos),
    'total_issues': total_issues,
    'summary': {k: len(v) for k, v in issues.items()},
    'no_8k_in_title': [{'id': v['id'], 'title': v['title'], 'series': v['series']} 
                        for v in issues['no_8k_in_title']],
    'wrong_category': [{'id': v['id'], 'title': v['title'], 'series': v['series'],
                         'actual': v['_actual'], 'expected': v['_expected']} 
                        for v in issues['wrong_category']],
    'too_many_tags': [{'id': v['id'], 'title': v['title'], 'tag_count': v['_tag_count']} 
                      for v in issues['too_many_tags']],
    'no_cta_videos': [{'id': v['id'], 'title': v['title'], 'series': v['series']}
                       for v in issues['no_cta_in_desc']],
    'handle_in_title': [{'id': v['id'], 'title': v['title']} 
                         for v in issues['handle_in_title']],
    'title_too_long': [{'id': v['id'], 'title': v['title'], 'length': len(v['title'])} 
                        for v in issues['title_too_long']],
}

with open(r'D:\remaike.TV\config\full_compliance_audit.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\n💾 Detailed report saved to config/full_compliance_audit.json")

conn.close()
