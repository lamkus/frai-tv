#!/usr/bin/env python3
"""
Soundies Final Artist Mapper - Combines all research sources
"""
import json

# Combined research from Wikipedia + Archive.org + Known databases
SOUNDIES_ARTIST_DATABASE = {
    # Format: video_id: (artist, song, year, source, confidence)
    
    # HIGH CONFIDENCE - Multiple sources confirm
    "mReDNz-Exdk": ("Yvonne De Carlo", "Lamp of Memory", "1942", "Wikipedia + Archive.org", "HIGH"),
    "GerP7_evS9o": ("The Three Suns", "Beyond the Blue Horizon", "1944", "Wikipedia + Archive.org", "HIGH"),
    "OvBqUlzTunI": ("Thelma White & Her All-Girl Orchestra", "Hollywood Boogie", "1940s", "Archive.org", "HIGH"),
    "D-LL4VuR5Pg": ("The Mel-Tones", "Lullaby of Broadway", "1940s", "Archive.org", "HIGH"),
    "w82vzaGBqwE": ("The Three Canadian Capers", "A Little Robin Told Me So", "1940s", "Archive.org", "HIGH"),
    
    # MEDIUM CONFIDENCE - Single reliable source
    "rprpMDyTWRI": ("Gai Moran & Danny Hocktor", "Zig Me Baby with a Gentle Zag", "1940s", "Archive.org", "MEDIUM"),
    "Z2SxppvCWvE": ("Ray Kinney", "Hawaiian Hula Song", "1940s", "Archive.org (possible)", "MEDIUM"),
    "2yGX3wy-4SQ": ("Maya", "Havana Madrid Show", "1940s", "Archive.org", "MEDIUM"),
    "6XVj6G3qNYY": ("Harry Day, Della & The June Taylor Girls", "Jiveroo", "1940s", "Archive.org", "HIGH"),
    "hAs6lunYl-E": ("Billy Burt", "A Jazz Etude", "1941", "Archive.org (danced by)", "MEDIUM"),
    
    # INFERRED from common recordings - needs verification
    "ukmrI7DlXkc": ("Johnny Long Orchestra", "In a Shanty in Old Shanty Town", "1946", "Wikipedia (hit recording)", "LOW"),
    "DHogGPBbzRI": ("All-Girl Orchestra", "Sweet Sue (Just You)", "1940s", "Archive.org", "MEDIUM"),
    "hIsTWWP-YkQ": ("Unknown Singer", "Once in a While", "1940s", "Archive.org", "LOW"),
    "A8LWgWF5f5k": ("The King's Men", "The Hut-Sut Song", "1941", "Wikipedia (film short)", "MEDIUM"),
    
    # UNKNOWN - need further research or leave generic
    "oA7XcqVM1Vo": (None, "I Can't Give You Anything But Love", "1940s", "Archive.org (Female singer)", "UNKNOWN"),
    "mDSdzFc572Y": (None, "What This Country Needs", "1940s", "Archive.org", "UNKNOWN"),
    "1zKpqdriv70": (None, "Ten Pretty Girls", "1940s", "Archive.org (Radio vocalist)", "UNKNOWN"),
    "NAk0QvvaT7M": (None, "Who's Yehudi", "1940s", "Not on Archive.org", "UNKNOWN"),
    "LJp-M01OI-8": (None, "Chime Bells", "1940s", "Archive.org (Navy performer)", "UNKNOWN"),
    "HvwtRYp43eU": (None, "Got to Be This or That", "1940s", "Archive.org (Jazz band)", "UNKNOWN"),
    "340C9lsoyYk": (None, "Tica Ti Tica Ta", "1940s", "Archive.org", "UNKNOWN"),
}

def generate_new_title(artist, song, year=None):
    """Generate SEO-optimized title"""
    if artist:
        if year and year != "1940s":
            return f"{artist}: {song} | Soundie ({year}) | 8K HQ | @remAIke_IT"
        else:
            return f"{artist}: {song} | Soundie | 8K HQ | @remAIke_IT"
    else:
        return f"Soundie: {song} | 8K HQ | Vintage Music Film | @remAIke_IT"

def main():
    print("🎬 SOUNDIES FINAL ARTIST MAPPING")
    print("=" * 80)
    
    updates = []
    
    for video_id, (artist, song, year, source, confidence) in SOUNDIES_ARTIST_DATABASE.items():
        new_title = generate_new_title(artist, song, year)
        
        update = {
            "id": video_id,
            "song": song,
            "artist": artist,
            "year": year,
            "source": source,
            "confidence": confidence,
            "new_title": new_title,
            "apply": confidence in ["HIGH", "MEDIUM"]
        }
        updates.append(update)
        
        # Print status
        if artist:
            conf_icon = "✅" if confidence == "HIGH" else "⚠️" if confidence == "MEDIUM" else "❓"
            print(f"{conf_icon} {video_id}: {artist} - {song}")
        else:
            print(f"❓ {video_id}: UNKNOWN - {song}")
    
    # Save
    output = {
        "meta": {
            "created": "2026-01-19",
            "sources": ["Wikipedia", "Archive.org", "Known Soundies databases"],
            "total_videos": len(updates),
            "high_confidence": len([u for u in updates if u["confidence"] == "HIGH"]),
            "medium_confidence": len([u for u in updates if u["confidence"] == "MEDIUM"]),
            "low_confidence": len([u for u in updates if u["confidence"] == "LOW"]),
            "unknown": len([u for u in updates if u["confidence"] == "UNKNOWN"]),
        },
        "updates": updates
    }
    
    with open('config/soundies_final_updates.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL SUMMARY")
    print("=" * 80)
    print(f"✅ HIGH confidence: {output['meta']['high_confidence']}")
    print(f"⚠️  MEDIUM confidence: {output['meta']['medium_confidence']}")
    print(f"❓ LOW confidence: {output['meta']['low_confidence']}")
    print(f"❌ UNKNOWN: {output['meta']['unknown']}")
    print(f"\n💾 Saved to: config/soundies_final_updates.json")
    
    # Print proposed updates
    print("\n" + "=" * 80)
    print("📝 PROPOSED TITLE UPDATES (HIGH + MEDIUM confidence)")
    print("=" * 80)
    for u in updates:
        if u['apply']:
            print(f"\n{u['id']}:")
            print(f"   NEW: {u['new_title']}")

if __name__ == '__main__':
    main()
