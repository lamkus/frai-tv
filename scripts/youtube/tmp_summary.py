"""Final compliance summary"""
import json

with open('config/fresh_audit_2026_02_08.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

public = [v for v in data['all_videos'] if v['privacy'] == 'public']

print('=' * 60)
print('FINAL AUDIT RESULTS - 2026-02-08')
print('=' * 60)
print(f'  Total public: {len(public)}')
print(f'  Avg Score: {data["avg_score"]}')
print(f'  Score 100: {sum(1 for v in public if v["score"] == 100)}')
print(f'  Score 95+: {sum(1 for v in public if v["score"] >= 95)}')
print(f'  Score 90+: {sum(1 for v in public if v["score"] >= 90)}')
print(f'  Score <90: {sum(1 for v in public if v["score"] < 90)}')

print()
print('COMPLIANCE SCORECARD:')
print(f'  8K in title:       {sum(1 for v in public if v["has_8k"])}/{len(public)}')
print(f'  Full format:       {sum(1 for v in public if v["has_full_format"])}/{len(public)}')
print(f'  CTA:               {sum(1 for v in public if v["has_cta"])}/{len(public)}')
print(f'  Website link:      {sum(1 for v in public if v["has_website"])}/{len(public)}')
print(f'  Channel link:      {sum(1 for v in public if v["has_channel_link"])}/{len(public)}')
hashtags_ok = sum(1 for v in public if 0 < v['hashtag_count'] <= 5)
print(f'  Hashtags (1-5):    {hashtags_ok}/{len(public)}')
print(f'  Too many hashtags: {sum(1 for v in public if v["hashtag_count"] > 5)}/{len(public)}')
at_in_title = sum(1 for v in public if '@remAIke' in v['title'].lower() or '@remaike' in v['title'].lower())
print(f'  @channel in title: {at_in_title}/{len(public)}')

print()
problems = [v for v in public if v['score'] < 100]
print(f'Videos NOT at 100: {len(problems)}')
for v in sorted(problems, key=lambda x: x['score']):
    all_iss = v['issues'] + v['warnings']
    iss_str = '; '.join(all_iss)[:80]
    print(f"  [{v['score']:3d}] {v['title'][:50]:50s} | {iss_str}")

# Top views
print()
top = sorted(public, key=lambda x: x['views'], reverse=True)[:10]
print('TOP 10 BY VIEWS:')
for v in top:
    print(f"  {v['views']:>6} views | [{v['score']}] {v['title'][:55]}")
