"""Verify all episodes can build HUD filters without errors."""
import sys, json
sys.path.insert(0, 'scripts/youtube')
from wochenschautv import load_episodes, scan_video_files, build_timeline_filters, _build_episode_keywords

config = json.load(open('config/wochenschautv_config.json'))
episodes = load_episodes()
matched_count, unmatched = scan_video_files(config, episodes)

available = [ep for ep in episodes if ep.get('file_path')]
print(f"Episodes loaded: {len(episodes)}")
print(f"Videos matched: {len(available)}")
print()

errors = []
for i, ep in enumerate(available):
    ep['_index'] = i + 1
    ep['_total'] = len(available)
    ep['_duration'] = 600  # placeholder

    # Set next episode
    if i + 1 < len(available):
        ep['_next_episode'] = available[i + 1]

    try:
        filters = build_timeline_filters(ep, config)
        kw = _build_episode_keywords(ep)
        num = ep['number']
        event = ep.get('event_en', '?')
        print(f"  Nr.{num}: {len(filters)} filters | {len(kw)} kw: {kw[:3]} | event: {event}")
    except Exception as e:
        errors.append((ep['number'], str(e)))
        num = ep['number']
        print(f"  Nr.{num}: ERROR: {e}")

print(f"\nVerified: {len(available)} episodes")
print(f"Errors: {len(errors)}")
if errors:
    for num, err in errors:
        print(f"  FAIL Nr.{num}: {err}")
else:
    print(f"ALL {len(available)} EPISODES BUILD SUCCESSFULLY!")
