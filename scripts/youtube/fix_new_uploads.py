#!/usr/bin/env python3
"""
Fix 9 new uploads — comprehensive SEO + compliance update.

  4 PRIVATE (raw uploads): Full metadata build (title, desc, tags, cat, locs)
  5 PUBLIC (live):         Fix metadata issues (title, desc, hashtags, cat, locs)

Usage:
  python fix_new_uploads.py          # dry run
  python fix_new_uploads.py --apply  # write to YouTube API (~450 quota)
"""
import sys, json, time, re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = r"D:\remaike.TV\token.json"
DRY = "--apply" not in sys.argv

def yt_client():
    creds = Credentials.from_authorized_user_file(TOKEN)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

yt = yt_client()

# ═══════════════════════════════════════════════════════════
# BUILDING BLOCKS
# ═══════════════════════════════════════════════════════════

CTA = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more vintage content in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

WS_DISC = ("⚠️ HISTORICAL DOCUMENT — This newsreel is original wartime propaganda, "
           "presented for educational and documentary purposes only. The content "
           "reflects the ideology of its era and does not represent the views of the uploader.")

def ws_locs(nr, ev_en, ev_de, date):
    """Standard 5-language localizations for Wochenschau."""
    return {
        "en": {"title": f"Newsreel {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"German Newsreel (Deutsche Wochenschau) No. {nr} from {date}. Topic: {ev_en}. Restored in 8K."},
        "de": {"title": f"Wochenschau {nr}: {ev_de} ({date}) | 8K HQ",
               "description": f"Deutsche Wochenschau Nr. {nr} vom {date}. Thema: {ev_de}. In 8K restauriert."},
        "es": {"title": f"Noticiario {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"Noticiario alemán Nr. {nr} del {date}. Tema: {ev_en}. Restaurado en 8K."},
        "fr": {"title": f"Actualités {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"Actualités allemandes Nr. {nr} du {date}. Sujet: {ev_en}. Restauré en 8K."},
        "ja": {"title": f"ニュース映画 {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"ドイツ週間ニュース Nr.{nr} ({date})。テーマ: {ev_en}。8K復元。"},
    }

# ═══════════════════════════════════════════════════════════
# PER-VIDEO FIX PLAN
# ═══════════════════════════════════════════════════════════

VIDEOS = [
    # ─── 1. WS 491 (PRIVATE) ───────────────────────────────
    {
        "id": "W1zYu-fTejs",
        "title": "Wochenschau 491: Phoney War (31.01.1940) | 8K HQ",
        "category": "27",
        "tags": ["Wochenschau", "Deutsche Wochenschau", "Newsreel", "1940",
                 "Phoney War", "Sitzkrieg", "WWII", "World War II", "8K",
                 "public domain", "history", "historical document", "propaganda"],
        "desc": f"""{WS_DISC}

Deutsche Wochenschau Nr. 491 vom 31. Januar 1940. Thema: Sitzkrieg / Phoney War.

Diese Wochenschau zeigt die Berichterstattung während der Phase des "Sitzkriegs" — der ruhigen Periode an der Westfront vor dem deutschen Westfeldzug im Mai 1940.

📍 Ort: Deutschland

{CTA}

#Wochenschau #WWII #8K #History #PublicDomain""",
        "locs": ws_locs("491", "Phoney War", "Sitzkrieg", "31.01.1940"),
    },
    # ─── 2. WS 496 (PRIVATE) ───────────────────────────────
    {
        "id": "3FstojEXJ5k",
        "title": "Wochenschau 496: Winter War Ends (06.03.1940) | 8K HQ",
        "category": "27",
        "tags": ["Wochenschau", "Deutsche Wochenschau", "Newsreel", "1940",
                 "Winter War", "Winterkrieg", "Finland", "WWII", "World War II",
                 "8K", "public domain", "history", "historical document"],
        "desc": f"""{WS_DISC}

Deutsche Wochenschau Nr. 496 vom 6. März 1940. Thema: Ende des Winterkriegs.

Der sowjetisch-finnische Winterkrieg endet. Die Wochenschau berichtet über den Friedensschluss und die politischen Folgen im Norden Europas.

📍 Ort: Helsinki, Finnland

{CTA}

#Wochenschau #WWII #8K #History #PublicDomain""",
        "locs": ws_locs("496", "Winter War Ends", "Winterkrieg endet", "06.03.1940"),
    },
    # ─── 3. WS 504 (PRIVATE) ───────────────────────────────
    {
        "id": "n-_DEeOSKz0",
        "title": "Wochenschau 504: Battle of Narvik (01.05.1940) | 8K HQ",
        "category": "27",
        "tags": ["Wochenschau", "Deutsche Wochenschau", "Newsreel", "1940",
                 "Battle of Narvik", "Narvik", "Norway", "WWII", "World War II",
                 "8K", "public domain", "history", "historical document"],
        "desc": f"""{WS_DISC}

Deutsche Wochenschau Nr. 504 vom 1. Mai 1940. Thema: Kampf um Narvik.

Die Wochenschau berichtet über die Kämpfe um den strategisch wichtigen norwegischen Hafen Narvik während des Norwegenfeldzugs. Deutsche Gebirgsjäger und Marinekräfte kämpfen gegen alliierte Truppen.

📍 Ort: Narvik, Norwegen

{CTA}

#Wochenschau #WWII #8K #History #PublicDomain""",
        "locs": ws_locs("504", "Battle of Narvik", "Kampf um Narvik", "01.05.1940"),
    },
    # ─── 4. Skeleton Dance SHORT (PRIVATE) ─────────────────
    {
        "id": "21iqU9NKJL0",
        "title": "The Skeleton Dance (1929) | Disney | 8K HQ",
        "category": "1",
        "tags": ["Skeleton Dance", "Disney", "Silly Symphony", "1929",
                 "Ub Iwerks", "vintage animation", "classic cartoon", "8K",
                 "public domain", "Walt Disney", "Halloween", "skeleton"],
        "desc": f"""The Skeleton Dance (1929) — the very first Disney Silly Symphony! Directed by Walt Disney and animated by Ub Iwerks. A group of skeletons dance and play music in a graveyard at midnight.

Originally released on August 22, 1929, this was the first entry in the "Silly Symphonies" series that would go on to produce 75 cartoons. This iconic short pioneered the synchronization of animation with music.

Restored and upscaled to 8K quality.

{CTA}

#Disney #SillySymphony #8K #PublicDomain #VintageAnimation""",
        "locs": {
            "en": {"title": "The Skeleton Dance (1929) | Disney | 8K HQ",
                   "description": "Disney's first Silly Symphony (1929). Skeletons dance in a graveyard. Restored in 8K."},
            "de": {"title": "Der Skelett-Tanz (1929) | Disney | 8K HQ",
                   "description": "Disneys erste Silly Symphony von 1929. Skelette tanzen auf einem Friedhof. In 8K restauriert."},
            "es": {"title": "La Danza de los Esqueletos (1929) | Disney | 8K HQ",
                   "description": "Primera Silly Symphony de Disney de 1929. Esqueletos bailan en un cementerio. Restaurado en 8K."},
            "fr": {"title": "La Danse des Squelettes (1929) | Disney | 8K HQ",
                   "description": "Première Silly Symphony de Disney (1929). Des squelettes dansent dans un cimetière. Restauré en 8K."},
            "ja": {"title": "骸骨の踊り (1929) | ディズニー | 8K HQ",
                   "description": "1929年のディズニー初のシリーシンフォニー。墓地で骸骨が踊る。8Kで復元。"},
        },
    },

    # ═══════════════════════════════════════════════════════
    # PUBLIC VIDEOS — preserve existing desc, fix issues
    # ═══════════════════════════════════════════════════════

    # ─── 5. WS 511 (PUBLIC) — cat 25→27, hashtags, links ──
    {
        "id": "3rB80OGKzrg",
        "title": None,  # keep current: "Wochenschau 511: Paris Falls (Jun 1940) | 8K"
        "category": "27",
        "tags": ["Wochenschau", "Deutsche Wochenschau", "Newsreel", "1940",
                 "Paris Falls", "WWII", "World War II", "8K", "public domain",
                 "history", "newsreel", "restored footage", "German Newsreel"],
        "desc_ops": [
            # Remove excessive hashtags at end
            ("regex_sub", r"\n*#\w+(\s+#\w+)*\s*$", "\n\n#Wochenschau #WWII #8K #History #PublicDomain"),
            # Fix links: frai.tv → remaike.IT
            ("replace", "📺 More at: https://frai.tv | @remAIke_IT", "🌐 www.remaike.IT\n📺 https://www.youtube.com/@remAIke_IT"),
        ],
        "locs": ws_locs("511", "Paris Falls", "Paris fällt", "19.06.1940"),
    },
    # ─── 6. Burlesque (PUBLIC) — title, hashtags, tags ─────
    {
        "id": "YHlhhiAfxEA",
        "title": "Rare 1955 Burlesque Footage | Icons You've Never Seen | 8K",
        "category": "1",
        "tags": ["burlesque", "1955", "Teaserama", "Tempest Storm",
                 "Betty Page", "pinup", "vintage dance", "cabaret",
                 "showgirl", "8K", "restored", "remastered", "1950s",
                 "public domain", "classic film"],
        "desc_ops": [
            # Replace spammy hashtag section with clean version
            ("regex_sub", r"\n*#\w+(\s+#\w+)*\s*$", "\n\n#Burlesque #1950s #8K #Vintage #PublicDomain"),
            # Ensure CTA links exist (add after existing subscribe line if missing)
            ("ensure_links",),
        ],
        "locs": {
            "en": {"title": "Rare 1955 Burlesque Footage | 8K HQ",
                   "description": "Rare burlesque footage from Teaserama (1955) featuring Tempest Storm & Betty Page. Restored in 8K."},
            "de": {"title": "Seltene Burlesque-Aufnahmen (1955) | 8K HQ",
                   "description": "Seltene Burlesque-Aufnahmen aus Teaserama (1955) mit Tempest Storm & Betty Page. In 8K restauriert."},
            "es": {"title": "Imágenes Raras del Burlesque (1955) | 8K HQ",
                   "description": "Raras imágenes del burlesque de Teaserama (1955). Restaurado en 8K."},
            "fr": {"title": "Images Rares du Burlesque (1955) | 8K HQ",
                   "description": "Rares images de burlesque de Teaserama (1955). Restauré en 8K."},
            "ja": {"title": "貴重なバーレスク映像 (1955) | 8K HQ",
                   "description": "1955年テーザラマの貴重なバーレスク映像。8K品質で修復。"},
        },
    },
    # ─── 7. Fast & Furious (PUBLIC) — @handle, links, hashtags ──
    {
        "id": "3UBF9ycZwJU",
        "title": "The 8K ORIGINAL Fast & Furious from 1954! \U0001f3ce\ufe0f",  # keep emoji, remove @handle
        "category": "1",
        "tags": ["Fast and Furious", "1954 movie", "8K restored", "Classic cars",
                 "Hot rod", "Racing movie", "Public domain", "Vintage racing",
                 "Fast & Furious origin", "Hidden gem", "Movie trivia",
                 "Did you know", "classic film", "B-movie", "car chase"],
        "desc_ops": [
            # Fix hashtags (13→5)
            ("regex_sub", r"\n*#\w+(\s+#\w+)*\s*$", "\n\n#FastAndFurious #1954 #8K #ClassicCars #PublicDomain"),
            # Ensure proper links
            ("ensure_links",),
        ],
        "locs": {
            "en": {"title": "The ORIGINAL Fast & Furious from 1954! | 8K HQ",
                   "description": "The original 'Fast and the Furious' from 1954 — the classic racing film. Restored in 8K."},
            "de": {"title": "Das ORIGINAL Fast & Furious von 1954! | 8K HQ",
                   "description": "Das Original 'Fast and the Furious' von 1954. In 8K restauriert."},
            "es": {"title": "¡El ORIGINAL Fast & Furious de 1954! | 8K HQ",
                   "description": "El original 'Fast and the Furious' de 1954. Restaurado en 8K."},
            "fr": {"title": "L'ORIGINAL Fast & Furious de 1954 ! | 8K HQ",
                   "description": "L'original 'Fast and the Furious' de 1954. Restauré en 8K."},
            "ja": {"title": "1954年のオリジナル ワイルド・スピード! | 8K HQ",
                   "description": "1954年のオリジナル「Fast and the Furious」。8Kで復元。"},
        },
    },
    # ─── 8. New Year's Eve (PUBLIC) — only localizations ───
    {
        "id": "2CwXPhUDC7U",
        "title": None,  # keep current
        "category": None,  # keep current
        "tags": None,  # keep current
        "locs": {
            "en": {"title": "New Year's Eve 1951-1952 | Colorized | 8K HQ",
                   "description": "Colorized home movies from New Year's Eve 1951-1952. Restored in 8K quality."},
            "de": {"title": "Silvester 1951-1952 | Koloriert | 8K HQ",
                   "description": "Kolorierte Heimaufnahmen von Silvester 1951-1952. In 8K Qualität restauriert."},
            "es": {"title": "Nochevieja 1951-1952 | Colorizado | 8K HQ",
                   "description": "Películas caseras colorizadas de Nochevieja 1951-1952. Restaurado en 8K."},
            "fr": {"title": "Nouvel An 1951-1952 | Colorisé | 8K HQ",
                   "description": "Films familiaux colorisés du Nouvel An 1951-1952. Restauré en 8K."},
            "ja": {"title": "大晦日 1951-1952 | カラー化 | 8K HQ",
                   "description": "1951-1952年の大晦日のカラー化家庭映像。8Kで復元。"},
        },
    },
    # ─── 9. Day of the Earth (PUBLIC) — @handle, title len, hashtags, links
    {
        "id": "XAyK1yy_e-M",
        "title": "Day of the Earth (1951) | Vintage Documentary | 8K HQ",
        "category": "1",
        "tags": None,  # keep current (already 15)
        "desc_ops": [
            # Fix hashtags
            ("regex_sub", r"\n*#\w+(\s+#\w+)*\s*$", ""),  # remove scattered hashtags
            # Replace old links block with proper CTA
            ("replace",
             "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎬 www.FRai.TV – Classic films organized by category\n📺 Subscribe for daily vintage classics in 4K/8K quality!\n🔔 Turn on notifications to never miss a new upload!",
             CTA + "\n\n#Documentary #1951 #8K #Vintage #PublicDomain"),
        ],
        "locs": {
            "en": {"title": "Day of the Earth (1951) | Documentary | 8K HQ",
                   "description": "Vintage documentary from 1951 exploring Earth sciences. Restored in 8K quality."},
            "de": {"title": "Tag der Erde (1951) | Dokumentarfilm | 8K HQ",
                   "description": "Vintage-Dokumentarfilm von 1951 über Erdwissenschaften. In 8K restauriert."},
            "es": {"title": "Día de la Tierra (1951) | Documental | 8K HQ",
                   "description": "Documental vintage de 1951 sobre ciencias de la Tierra. Restaurado en 8K."},
            "fr": {"title": "Jour de la Terre (1951) | Documentaire | 8K HQ",
                   "description": "Documentaire vintage de 1951 sur les sciences de la Terre. Restauré en 8K."},
            "ja": {"title": "地球の日 (1951) | ドキュメンタリー | 8K HQ",
                   "description": "1951年の地球科学ドキュメンタリー。8Kで復元。"},
        },
    },
]

# ═══════════════════════════════════════════════════════════
# EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════

print("=" * 70)
print(f"FIX NEW UPLOADS — {'DRY RUN' if DRY else '🔴 APPLY MODE'}")
print(f"Videos: {len(VIDEOS)}")
print("=" * 70)

# Fetch current state (1 quota unit)
all_ids = [v["id"] for v in VIDEOS]
resp = yt.videos().list(part="snippet,status,localizations", id=",".join(all_ids)).execute()
current = {item["id"]: item for item in resp.get("items", [])}
print(f"\nFetched {len(current)} videos (1 quota)\n")

quota = 1
fixed = 0
errors = 0

for vfix in VIDEOS:
    vid = vfix["id"]
    if vid not in current:
        print(f"⚠️  {vid} NOT FOUND (deleted?)\n")
        continue

    item = current[vid]
    snip = item["snippet"]
    privacy = item["status"]["privacyStatus"]
    cur_title = snip["title"]
    cur_desc = snip["description"]
    cur_tags = snip.get("tags", [])
    cur_cat = snip["categoryId"]
    cur_locs = item.get("localizations", {})

    changes = []

    # ── TITLE ──
    new_title = vfix.get("title") or cur_title
    if new_title != cur_title:
        changes.append(f"Title: '{cur_title[:50]}' → '{new_title[:50]}'")

    # ── DESCRIPTION ──
    new_desc = cur_desc
    if "desc" in vfix:
        new_desc = vfix["desc"]
        changes.append("Desc: FULL REWRITE")
    elif "desc_ops" in vfix:
        for op in vfix["desc_ops"]:
            if op[0] == "regex_sub":
                before = new_desc
                new_desc = re.sub(op[1], op[2], new_desc)
                if new_desc != before:
                    changes.append(f"Desc: regex '{op[1][:30]}...'")
            elif op[0] == "replace":
                if op[1] in new_desc:
                    new_desc = new_desc.replace(op[1], op[2])
                    changes.append(f"Desc: replaced '{op[1][:40]}...'")
            elif op[0] == "ensure_links":
                if "www.remaike.IT" not in new_desc:
                    new_desc = new_desc.rstrip() + f"\n\n{CTA}"
                    changes.append("Desc: added CTA+links")

    # ── CATEGORY ──
    new_cat = vfix.get("category") or cur_cat
    if new_cat != cur_cat:
        changes.append(f"Category: {cur_cat} → {new_cat}")

    # ── TAGS ──
    new_tags = vfix.get("tags") or cur_tags
    # Remove any # prefixes from tags
    new_tags = [t.lstrip("#") for t in new_tags]
    # Remove @remAIke_IT from tags
    new_tags = [t for t in new_tags if t != "@remAIke_IT"]
    if len(new_tags) > 15:
        new_tags = new_tags[:15]
    if set(new_tags) != set(cur_tags):
        changes.append(f"Tags: {len(cur_tags)} → {len(new_tags)}")

    # ── LOCALIZATIONS ──
    new_locs = dict(cur_locs)
    if "locs" in vfix and vfix["locs"]:
        for lang, data in vfix["locs"].items():
            if lang not in new_locs:
                new_locs[lang] = data
        added = len(new_locs) - len(cur_locs)
        if added > 0:
            changes.append(f"Locs: +{added} ({len(cur_locs)}→{len(new_locs)})")

    # ── PRINT ──
    icon = "🔒" if privacy == "private" else "🌐"
    print(f"{icon} {vid} [{privacy}] {new_title[:55]}")
    if not changes:
        print("   ✅ Already compliant\n")
        continue
    for c in changes:
        print(f"   → {c}")

    # ── BUILD UPDATE BODY ──
    body = {
        "id": vid,
        "snippet": {
            "title": new_title,
            "description": new_desc,
            "categoryId": new_cat,
            "tags": new_tags,
        },
    }
    parts = ["snippet"]
    if len(new_locs) > len(cur_locs):
        body["localizations"] = new_locs
        parts.append("localizations")

    # ── APPLY ──
    if not DRY:
        try:
            yt.videos().update(part=",".join(parts), body=body).execute()
            quota += 50
            fixed += 1
            print(f"   ✅ UPDATED (quota: {quota})")
            time.sleep(1.5)
        except Exception as e:
            errors += 1
            msg = str(e)
            if "quotaExceeded" in msg:
                print(f"   ❌ QUOTA EXCEEDED — stopping!")
                break
            print(f"   ❌ ERROR: {msg[:120]}")
    else:
        fixed += 1
    print()

print("=" * 70)
if DRY:
    print(f"DRY RUN — Would fix {fixed} videos (~{fixed * 50 + 1} quota)")
    print("Run: python fix_new_uploads.py --apply")
else:
    print(f"DONE — Fixed: {fixed} | Errors: {errors} | Quota: {quota}")
print("=" * 70)
