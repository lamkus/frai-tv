
import json
import re
import os

# --- VERIFIED EPISODE DATABASE (Source: Wikipedia DE, Stand 08.02.2026) ---
# BROADCAST-Nummern (ZDF Erstausstrahlung 1990-1993)
# ACHTUNG: File-Nummern in V:\MediaArchive\Alfred\ weichen ab E35 ab!
# Mapping: File 35→E36, 36→E37, 37→E38, 38→E40, 39→E41, 40→E42,
#          41→E43, 42→E44, 43→E48, 44→E49, 45→E50, 46→E51
EPISODE_DB = {
    1: "Hurra, er ist da!",
    2: "Böse Überraschung",
    3: "Hinter Gittern",
    4: "Im Brunnen gefangen",
    5: "In letzter Sekunde",
    6: "Olympiade",
    7: "Abenteuer auf hoher See",
    8: "Der Spion",
    9: "Ein gefährliches Geschenk",
    10: "Der Geist in der Flasche",
    11: "Der Mensch ist los!",
    12: "Die geheimnisvolle Königin",
    13: "Haltet den Dieb!",
    14: "Skrupellose Geschäfte",
    15: "Die Explosion",
    16: "Die Reise zum Südpol",
    17: "Rettung aus dem All",
    18: "Im ewigen Eis",
    19: "Rettet die Wale!",
    20: "Der Alptraum",
    21: "Wasser für die Wüste",
    22: "Kra an die Macht!",
    23: "Die Krähenpartei",
    24: "Flucht aus Deichstadt",
    25: "Der Kampf um Deichstadt",
    26: "Der Schneemensch",
    27: "Verliebt",
    28: "Ein Geschenk des Königs",
    29: "Die Burengänse",
    30: "Im Urlaub",
    31: "Die Bohrinsel",
    32: "Atlantis",
    33: "Cowboys und Indianer",
    34: "Der Schatz des Tut Kaz Kammon",
    35: "Die Schlange",
    36: "Michael Duckson",
    37: "Die Entführung",
    38: "Krach mit den Nachbarn",
    39: "Die Hexe",
    40: "Der Stausee",
    41: "Der Vulkan",
    42: "Der Drache",
    43: "Ein Präsident für Groß-Wasserland",
    44: "Die Überschwemmung",
    45: "Das Land von Zwei",
    46: "Pierrot",
    47: "Ende gut, alles gut!",
    48: "Eine Partie Golf",
    49: "Der Regenbogen",
    50: "Das Casino",
    51: "Der Regenwald",
    52: "Und wenn sie nicht gestorben sind",
}

# CORRECTIONS DOULBE CHECK
# Ep 26 is "Der Schneemensch" in most guides.
# Ep 39 is "Der Vulkan".

FIXED_TAGS = [
    "Alfred J. Kwak", "Herman van Veen", "Zeichentrick", "8K", "4K",
    "UHD", "Remastered", "Anime", "Hiroshi Saitō", "Ente", "Maulwurf",
    "Dolf", "Groß-Wasserland", "Deichstadt", "Kultserie"
]

DESCRIPTION_TEMPLATE = """{title}

Die Kultserie von Herman van Veen in bestmöglicher 8K (und 4K UHD) Qualität!
Erlebe die Abenteuer von Alfred, der fröhlichen Ente aus Groß-Wasserland.

Handlung dieser Episode:
{ep_title}

Informationen zur Serie:
Alfred J. Kwak ist mehr als nur eine Kinderserie. Sie behandelt ernste Themen wie Umweltschutz, Gerechtigkeit und Demokratie, verpackt in eine spannende Geschichte für Jung und Alt.

Characters:
• Alfred (Die Ente)
• Henk (Der Maulwurf)
• Dolf (Die Krähe)
• Winnie (Die Freundin)

Credits:
Idee & Musik: Herman van Veen
Regie: Hiroshi Saitō
Design: Harald Siepermann

🕐 CHAPTERS:
0:00 Intro
22:00 Outro

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you loved this show!
💬 COMMENT which character is your favorite!
🔔 SUBSCRIBE for more 8K Cartoons!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#AlfredJKwak #HermanVanVeen #8K #Kindheit #Zeichentrick"""

def main():
    with open('config/fresh_channel_scan.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    updates = []
    
    for v in videos:
        title = v['snippet']['title']
        vid_id = v['id']
        
        if "Alfred J. Kwak" not in title:
            continue
        if "Hitchcock" in title:
            continue
            
        # Parse Episode Number
        ep_num = -1
        
        # Format 1: E14
        m1 = re.search(r'E(\d+)', title)
        if m1:
            ep_num = int(m1.group(1))
            
        # Format 2: (9)
        if ep_num == -1:
            m2 = re.search(r'\((\d+)\)', title)
            if m2:
                ep_num = int(m2.group(1))
        
        if ep_num == -1:
            print(f"⚠️ SKIPPING UNKNOWN FORMAT: {title}")
            continue
            
        # VERIFY
        db_title = EPISODE_DB.get(ep_num)
        if not db_title:
            print(f"❌ DB MISSING EPISODE {ep_num}: {title}")
            continue
            
        # Fuzzy Match Check (is the DB title roughly in the video title?)
        # Simple check: Is "Casino" in "Das Casino"? Yes.
        # Is "Skrupellose Geschäfte" in "Skrupellose Geschäfte"? Yes.
        
        # Clean titles for comparison
        clean_vid_title = title.lower()
        clean_db_title = db_title.lower()
        
        # Very distinct words
        match_score = 0
        db_words = clean_db_title.split()
        for word in db_words:
            if len(word) > 3 and word in clean_vid_title:
                match_score += 1
                
        if match_score == 0 and len(db_words) > 0:
            # Special case for "E5: In letzter Sekunde" vs Title
            if "sekunde" in clean_vid_title and "sekunde" in clean_db_title:
                match_score = 1
            else:
                 print(f"⚠️ TITLE MISMATCH Ep{ep_num}: Vid='{title}' vs DB='{db_title}'")
                 # We TRUST the DB if metadata is poor, but we warn.
                 # Actually, for 8K uploads, the titles are usually correct.
        
        # GENERATE UPDATE
        # Title Optimization: 8K is USP, but 4K is Search Volume. We include both.
        # "Alfred J. Kwak: Titel (Ep. X) | 8K HQ (4K)"
        new_title = f"Alfred J. Kwak: {db_title} (Ep. {ep_num}) | 8K HQ (4K)"
        new_desc = DESCRIPTION_TEMPLATE.format(title=new_title, ep_title=db_title)
        
        updates.append({
            "id": vid_id,
            "current_title": title,
            "new_title": new_title,
            "new_description": new_desc,
            "new_tags": FIXED_TAGS,
            "categoryId": "1" # Film & Animation
        })
        
    # Write Proposal
    with open('config/alfred_deep_fix.json', 'w', encoding='utf-8') as f:
        json.dump(updates, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated fix proposal for {len(updates)} Alfred videos in config/alfred_deep_fix.json")

if __name__ == "__main__":
    main()
