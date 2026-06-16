
import json

PRIORITY_ORDER = [
    "Alfred J. Kwak",
    "Betty Boop",
    "Superman",
    "Popeye",
    "Felix the Cat",
    "Bravestarr",
    "Gulliver's Travels",
    "Soundies",
    "Wochenschau",
    "Misc"
]

def main():
    print("⚖️ Prioritizing Fix List by Series Importance (High Range)...")
    
    try:
        with open('config/channel_master_fix.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ config/channel_master_fix.json not found.")
        return

    # Helper for sort index
    def get_prio(item):
        series = item.get('series', 'Misc')
        try:
            return PRIORITY_ORDER.index(series)
        except ValueError:
            return 999 

    # Sort
    sorted_data = sorted(data, key=get_prio)
    
    # Save back
    with open('config/channel_master_fix_prioritized.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2)
        
    print(f"✅ Reordered {len(sorted_data)} tasks.")
    print("   Top 3 Series:", ", ".join([x['series'] for x in sorted_data[:3]]))
    print("   Output: config/channel_master_fix_prioritized.json")

    # Update execution script pointer
    ex_script = 'scripts/youtube/execute_global_fix.py'
    if os.path.exists(ex_script):
        with open(ex_script, 'r', encoding='utf-8') as f:
            code = f.read()
            
        new_code = code.replace('config/channel_master_fix.json', 'config/channel_master_fix_prioritized.json')
        
        with open(ex_script, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print(f"✅ Updated {ex_script} to use prioritized file.")

import os
if __name__ == "__main__":
    main()
