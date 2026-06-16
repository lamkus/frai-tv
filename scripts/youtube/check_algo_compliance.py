#!/usr/bin/env python3
"""
Prüft Channel gegen YouTube 2026 Algorithm Research
Basierend auf: YOUTUBE_ALGORITHM_2026.md, YOUTUBE_ALGO_2026_PLAYBOOK.md
"""

import json

print("="*70)
print("📊 CHANNEL CHECK GEGEN YOUTUBE 2026 ALGORITHM RESEARCH")
print("="*70)

with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n📅 Scan Datum: {data['fetched_at']}")
print(f"📺 Videos: {data['total_videos']} total, {data['public']} public")

# === CHECKS basierend auf Research ===

issues = {
    'critical': [],
    'warning': [],
    'good': []
}

long_titles = []
no_cta = []
no_hashtags = []
no_chapters = []
bad_title_format = []
excessive_tags = []

for v in data['videos']:
    vid = v['id']
    title = v['snippet']['title']
    desc = v['snippet'].get('description', '')
    tags = v['snippet'].get('tags', [])
    
    # 1. Titel-Länge (max 70 empfohlen)
    if len(title) > 70:
        long_titles.append((vid, len(title), title[:50]))
    
    # 2. CTA in Description (Research: CTAs bei 60-70% aber auch in Desc)
    cta_keywords = ['subscribe', 'like', 'comment', 'abonnier', 'kommentar', '👆', '💬', '🔔']
    has_cta = any(kw.lower() in desc.lower() for kw in cta_keywords)
    if not has_cta:
        no_cta.append((vid, title[:40]))
    
    # 3. Hashtags (Research: 2-3 hashtags PFLICHT, nicht mehr!)
    hashtag_count = desc.count('#')
    if hashtag_count == 0:
        no_hashtags.append((vid, title[:40]))
    
    # 4. Chapters/Timestamps (Research: Wichtig für Satisfaction)
    has_chapters = '0:00' in desc or 'CHAPTERS' in desc.upper()
    # Nur für längere Videos relevant - Skip für jetzt
    
    # 5. Titel-Format Check (Research: Keyword am ANFANG)
    # Gute Formate: "Betty Boop:", "Wochenschau:", "Alfred J. Kwak"
    good_prefixes = ['betty boop', 'wochenschau', 'alfred', 'felix', 'soundie', 
                     'superman', 'porky', 'looney', 'popeye', 'casper']
    title_lower = title.lower()
    has_good_prefix = any(title_lower.startswith(p) or f': {p}' in title_lower[:30] for p in good_prefixes)
    
    # 6. Excessive Tags (Research: Max 15, "MINIMAL role")
    if len(tags) > 15:
        excessive_tags.append((vid, len(tags), title[:40]))

# === REPORT ===
print("\n" + "="*70)
print("🚨 KRITISCHE ISSUES (gegen YouTube 2026 Algorithm)")
print("="*70)

print(f"\n📏 TITEL >70 ZEICHEN: {len(long_titles)}")
if long_titles:
    print("   (YouTube Research: Mobile-scannable, 50-70 chars optimal)")
    for vid, length, title in long_titles[:5]:
        print(f"   • [{length}] {title}...")
    if len(long_titles) > 5:
        print(f"   ... und {len(long_titles)-5} weitere")

print(f"\n❌ OHNE HASHTAGS: {len(no_hashtags)}")
if no_hashtags:
    print("   (YouTube 2026: 2-3 Hashtags PFLICHT, erscheinen ÜBER Description)")
    for vid, title in no_hashtags[:5]:
        print(f"   • {vid}: {title}...")

print(f"\n📢 OHNE CTA IN DESC: {len(no_cta)}")
if no_cta:
    print("   (Research: CTAs sind wichtig für Engagement Signals)")
    for vid, title in no_cta[:5]:
        print(f"   • {vid}: {title}...")

print(f"\n🏷️ EXCESSIVE TAGS (>15): {len(excessive_tags)}")
if excessive_tags:
    print("   (YouTube: 'MINIMAL role' - Excessive = SPAM VIOLATION)")
    for vid, count, title in excessive_tags[:5]:
        print(f"   • [{count} tags] {title}...")

# === POSITIVE CHECKS ===
print("\n" + "="*70)
print("✅ YOUTUBE 2026 COMPLIANCE SCORE")
print("="*70)

total = data['public']
title_ok = total - len(long_titles)
hashtag_ok = total - len(no_hashtags)
cta_ok = total - len(no_cta)
tags_ok = total - len(excessive_tags)

print(f"""
📏 Titel <=70 chars:    {title_ok}/{total} ({title_ok*100//total}%)
🏷️ Hashtags vorhanden:  {hashtag_ok}/{total} ({hashtag_ok*100//total}%)
📢 CTA in Description:  {cta_ok}/{total} ({cta_ok*100//total}%)
🔖 Tags <=15:           {tags_ok}/{total} ({tags_ok*100//total}%)
""")

# Overall Score
score = (title_ok/total * 30 + hashtag_ok/total * 20 + cta_ok/total * 30 + tags_ok/total * 20)
print(f"🎯 OVERALL COMPLIANCE: {score:.1f}/100")

if score < 80:
    print("\n⚠️ EMPFEHLUNG: Weitere Optimierungen nötig!")
else:
    print("\n✅ Channel ist gut optimiert für YouTube 2026 Algorithm!")

print("\n" + "="*70)
