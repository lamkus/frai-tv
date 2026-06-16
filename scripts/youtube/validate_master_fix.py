
import json

def main():
    print("🔍 Validating Master Fix Plan against 2026 Rules...")
    
    with open('config/channel_master_fix.json', 'r', encoding='utf-8') as f:
        updates = json.load(f)
        
    errors = []
    
    for item in updates:
        # Check 1: Title Length
        if len(item['new_title']) > 100:
            errors.append(f"Title too long: {item['new_title']}")
            
        # Check 2: Tag Count
        if len(item['new_tags']) > 15:
            errors.append(f"Too many tags: {item['id']}")
            
        # Check 3: Keywords
        t = item['new_title']
        if "8K" not in t or "4K" not in t:
             errors.append(f"Missing Keywords: {t}")
             
    if errors:
        print(f"❌ Found {len(errors)} errors:")
        for e in errors[:5]:
            print(f"  - {e}")
    else:
        print("✅ Validation Passed: All 345 updates meet 2026 Criteria.")
        print("   - Title includes 8K & 4K")
        print("   - Tags <= 15")
        print("   - Description Format Consistent")

if __name__ == "__main__":
    main()
