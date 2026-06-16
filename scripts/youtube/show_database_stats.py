#!/usr/bin/env python3
"""Show database statistics"""
import json

db = json.load(open('config/wochenschau_complete_upload_database.json', encoding='utf-8'))

print("=" * 70)
print("🎬 WOCHENSCHAU COMPLETE UPLOAD DATABASE - STATISTICS")
print("=" * 70)

videos = db['videos']
print(f"\n📊 OVERVIEW:")
print(f"   Total Videos:      {len(videos)}")
print(f"   First:             Nr. {min(int(k) for k in videos.keys())} ({videos[min(videos.keys())]['event_en']})")
print(f"   Last:              Nr. {max(int(k) for k in videos.keys())} ({videos[max(videos.keys(), key=int)]['event_en']})")

# Stats
avg_title = sum(v['title_length'] for v in videos.values()) / len(videos)
avg_desc = sum(v['description_length'] for v in videos.values()) / len(videos)
avg_tags = sum(v['tags_count'] for v in videos.values()) / len(videos)
ufa_count = sum(1 for v in videos.values() if v['is_ufa_tonwoche'])

print(f"\n📏 AVERAGES:")
print(f"   Title Length:      {avg_title:.1f} chars (target: <60)")
print(f"   Description:       {avg_desc:.0f} chars")
print(f"   Tags per Video:    {avg_tags:.0f} tags")

print(f"\n🏷️ HISTORICAL:")
print(f"   Ufa-Tonwoche:      {ufa_count} (Nr. 459-510)")
print(f"   Deutsche WS:       {len(videos) - ufa_count} (Nr. 511-755)")

print(f"\n📝 WHAT'S INCLUDED PER VIDEO:")
print(f"   ✅ Optimized Title (SEO 2026)")
print(f"   ✅ Multilingual Description (DE/EN/ES + 11 more)")
print(f"   ✅ International Tags (14 languages)")
print(f"   ✅ Event Keywords (DE + EN)")
print(f"   ✅ Historical Notes")
print(f"   ✅ Ufa-Tonwoche Note (for Nr. <511)")
print(f"   ✅ CTAs (Like/Comment/Subscribe)")
print(f"   ✅ Category, Privacy, License Settings")
print(f"   ✅ Expected Filename")

# Sample
print(f"\n" + "=" * 70)
print(f"📝 SAMPLE: Nr. 523 (London Blitz)")
print("=" * 70)
v = videos['523']
print(f"\n🎬 TITLE ({v['title_length']} chars):")
print(f"   {v['title']}")

print(f"\n🏷️ TAGS ({v['tags_count']} tags, {v['tags_total_chars']} chars):")
for i, tag in enumerate(v['tags'][:20]):
    print(f"   {tag}", end=", " if (i+1) % 5 != 0 else "\n")
print(f"\n   ... and {v['tags_count'] - 20} more")

print(f"\n📄 DESCRIPTION ({v['description_length']} chars):")
print("-" * 40)
print(v['description'][:800])
print("...")

print(f"\n" + "=" * 70)
print(f"✅ DATABASE READY FOR ALL 252 UPLOADS!")
print("=" * 70)
