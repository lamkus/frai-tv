"""Quick lookup for Wochenschau events/dates."""
import json

with open('config/wochenschau_complete_locations.json', 'r', encoding='utf-8') as f:
    locs = json.load(f)
with open('config/wochenschau_events.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

for nr in [701, 703, 706, 707, 708, 709, 710]:
    nr_str = str(nr)
    loc = locs.get(nr_str, {})
    evt = events.get(nr_str, {})
    date = loc.get('date', evt.get('date', '?'))
    event_en = evt.get('event_en', evt.get('event', '?'))
    location = loc.get('location', '?')
    print(f"Nr.{nr}:")
    print(f"  Date: {date}")
    print(f"  Event EN: {event_en}")
    print(f"  Location: {location}")
    print()
