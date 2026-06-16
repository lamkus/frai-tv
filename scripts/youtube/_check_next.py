import json
eps = json.load(open('config/episode_durations.json'))
locs = json.load(open('config/wochenschau_complete_locations.json'))
for i, e in enumerate(eps):
    if 513 <= e['nr'] <= 520:
        loc = locs.get(str(e['nr']), {})
        print(f"  [{i}] Nr. {e['nr']}: {loc.get('event_en','?')} | {e['path']}")
