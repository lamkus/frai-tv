"""
Check live localization status for all channel videos.
Reports which videos have defaultLanguage set and which have localizations.

Quota: ~8 units (READ only, batches of 50)
"""
import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds_data = json.load(open('config/youtube_oauth.json'))
creds = Credentials(
    token=creds_data['access_token'],
    refresh_token=creds_data['refresh_token'],
    token_uri=creds_data['token_uri'],
    client_id=creds_data['client_id'],
    client_secret=creds_data['client_secret']
)
yt = build('youtube', 'v3', credentials=creds)

# Load snapshot for video IDs
snapshot = json.load(open('config/channel_snapshot_2026_02_06.json', encoding='utf-8'))
all_vids = [v for v in snapshot['all_videos'] if v['privacy'] == 'public']
video_ids = [v['id'] for v in all_vids]

print(f"Checking {len(video_ids)} public videos for localizations...\n")

has_default_lang = 0
has_localizations = 0
no_default_lang = []
with_localizations = []
lang_counts = {}

for i in range(0, len(video_ids), 50):
    batch = video_ids[i:i+50]
    resp = yt.videos().list(
        part='snippet,localizations',
        id=','.join(batch)
    ).execute()
    for v in resp.get('items', []):
        dl = v['snippet'].get('defaultLanguage', '')
        locs = v.get('localizations', {})
        title = v['snippet']['title'][:55]
        
        if dl:
            has_default_lang += 1
        else:
            no_default_lang.append({'id': v['id'], 'title': title})
        
        if locs and len(locs) > 0:
            has_localizations += 1
            with_localizations.append({
                'id': v['id'],
                'title': title,
                'defaultLanguage': dl,
                'localization_langs': list(locs.keys())
            })
            for lang in locs.keys():
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

print(f"=== LOCALIZATION STATUS ===")
print(f"Total public videos:      {len(video_ids)}")
print(f"Has defaultLanguage:      {has_default_lang} ({has_default_lang/len(video_ids)*100:.1f}%)")
print(f"Missing defaultLanguage:  {len(no_default_lang)} ({len(no_default_lang)/len(video_ids)*100:.1f}%)")
print(f"Has any localizations:    {has_localizations} ({has_localizations/len(video_ids)*100:.1f}%)")
print(f"No localizations:         {len(video_ids) - has_localizations}")

if with_localizations:
    print(f"\n📋 Videos WITH localizations ({len(with_localizations)}):")
    for v in with_localizations:
        print(f"  {v['id']} | {v['defaultLanguage']:>5} | langs: {','.join(v['localization_langs'])} | {v['title']}")

if lang_counts:
    print(f"\n🌍 Language distribution:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count} videos")

# First 10 without defaultLanguage
print(f"\n❌ First 10 WITHOUT defaultLanguage:")
for v in no_default_lang[:10]:
    print(f"  {v['id']} | {v['title']}")

# Save report
report = {
    'total_public': len(video_ids),
    'has_default_language': has_default_lang,
    'missing_default_language': len(no_default_lang),
    'has_localizations': has_localizations,
    'videos_with_localizations': with_localizations,
    'no_default_language_ids': [v['id'] for v in no_default_lang],
}
with open('config/localization_status_2026_02_06.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f"\n✅ Saved: config/localization_status_2026_02_06.json")
