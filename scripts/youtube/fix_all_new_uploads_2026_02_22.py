#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
  FIX ALL NEW UPLOADS — COMPREHENSIVE SEO + COMPLIANCE UPDATE
  Date: 2026-02-22
═══════════════════════════════════════════════════════════════════

  Phase 1: 4 raw Wochenschau (PRIVATE) — full metadata build
  Phase 2: 16 raw Alfred J. Kwak (PRIVATE) — full metadata build  
  Phase 3: 2-3 public videos with remaining issues
  
  Total: ~22 videos × 50 = ~1.100 Quota Units

Usage:
  python scripts/youtube/fix_all_new_uploads_2026_02_22.py              # Dry-run
  python scripts/youtube/fix_all_new_uploads_2026_02_22.py --apply      # Write to YouTube
  python scripts/youtube/fix_all_new_uploads_2026_02_22.py --phase 1    # Only WS
  python scripts/youtube/fix_all_new_uploads_2026_02_22.py --phase 2    # Only Alfred
  python scripts/youtube/fix_all_new_uploads_2026_02_22.py --phase 3    # Only public fixes
"""
import sys, json, time, os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = Path(r"D:\remaike.TV\token.json")
DRY = "--apply" not in sys.argv
PHASE_FILTER = None
for i, arg in enumerate(sys.argv):
    if arg == "--phase" and i + 1 < len(sys.argv):
        PHASE_FILTER = int(sys.argv[i + 1])

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def yt_client():
    creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds.expired:
        creds.refresh(Request())
        with open(TOKEN, "w") as f:
            f.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)


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

WS_DISC = ("⚠️ HISTORISCHES DOKUMENT — Dieses Video zeigt Original-Material "
           "der NS-Propaganda-Wochenschau. Es dient ausschließlich der historischen "
           "Dokumentation und Bildung. Die dargestellten Inhalte spiegeln NICHT "
           "die Meinung des Uploaders wider.")

WS_TAGS_BASE = [
    "Wochenschau", "Deutsche Wochenschau", "Newsreel", "World War II", "WWII",
    "WW2", "History", "Documentary", "8K", "remastered", "restored",
    "public domain", "vintage newsreel", "historical footage", "AI enhanced"
]

ALFRED_TAGS_BASE = [
    "Alfred J. Kwak", "Alfred Jodokus Kwak", "Alfred Quack",
    "Herman van Veen", "1989", "Zeichentrick", "classic cartoon",
    "8K", "4K UHD", "remastered", "restored", "Deutsch"
]

def ws_locs(nr, ev_en, ev_de, date):
    """5-language localizations for Wochenschau."""
    return {
        "en": {"title": f"Newsreel {nr}: {ev_en} ({date}) | 8K HQ (4K UHD)",
               "description": f"German Weekly Newsreel (Deutsche Wochenschau) No. {nr} from {date}. Topic: {ev_en}. AI remastered in stunning 8K quality.\n\n⚠️ Historical archive material — for documentation and educational purposes only."},
        "de": {"title": f"Wochenschau {nr}: {ev_de} ({date}) | 8K HQ (4K UHD)",
               "description": f"Deutsche Wochenschau Nr. {nr} vom {date}. Thema: {ev_de}. In 8K restauriert.\n\n⚠️ Historisches Archivmaterial — dient der Dokumentation und Bildung."},
        "es": {"title": f"Noticiario {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"Noticiario alemán Nr. {nr} del {date}. Tema: {ev_en}. Restaurado en 8K.\n\n⚠️ Material de archivo histórico — con fines documentales y educativos."},
        "fr": {"title": f"Actualités {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"Actualités allemandes Nr. {nr} du {date}. Sujet: {ev_en}. Restauré en 8K.\n\n⚠️ Matériel d'archives historiques — à des fins documentaires et éducatives."},
        "ja": {"title": f"ニュース映画 {nr}: {ev_en} ({date}) | 8K HQ",
               "description": f"ドイツ週間ニュース Nr.{nr} ({date})。テーマ: {ev_en}。8K復元。\n\n⚠️ 歴史的資料 — ドキュメンタリーおよび教育目的のみ。"},
    }

def alfred_locs(ep_nr, title_de):
    """DE+EN localizations for Alfred J. Kwak."""
    return {
        "de": {
            "title": f"Alfred J. Kwak (E{ep_nr:02d}) {title_de} | DE | 8K HQ (4K UHD)",
            "description": f"Alfred J. Kwak / Alfred Jodokus Quak — Episode {ep_nr}: {title_de}. Die beliebte Zeichentrickserie (1989) in 8K restauriert."
        },
        "en": {
            "title": f"Alfred J. Kwak (E{ep_nr:02d}) {title_de} | DE | 8K HQ (4K UHD)",
            "description": f"Alfred J. Kwak — Episode {ep_nr}: {title_de}. The beloved animated series (1989), AI remastered in stunning 8K quality. German audio."
        }
    }

def ws_desc(nr, date, ev_de, ev_en, location, hist_note):
    """Full Wochenschau description."""
    return f"""{WS_DISC}

🎬 WOCHENSCHAU {nr} | {date} | {ev_en}
Deutsche Wochenschau Nr. {nr} vom {date}. Thema: {ev_de} / {ev_en}.

{hist_note}

📍 Ort: {location}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇩🇪 DEUTSCH:
Die Deutsche Wochenschau Nr. {nr} vom {date}.
⚠️ Historisches Archivmaterial - dient der Dokumentation und Bildung.

🇬🇧 ENGLISH:
German Weekly Newsreel No. {nr}, dated {date}.
Original theatrical newsreel with contemporary footage and audio.
⚠️ Historical archive material - for documentation and educational purposes.

🇪🇸 ESPAÑOL:
Noticiero Semanal Alemán Nr. {nr}, del {date}.
⚠️ Material de archivo histórico - con fines documentales y educativos.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📺 8K HQ Edition:
• AI-Stabilized archival source
• Enhanced clarity for modern displays
• Original visual and audio character preserved

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌍 SEARCH IN YOUR LANGUAGE:
🇩🇪 Deutsche Wochenschau, Zweiter Weltkrieg, {ev_de}
🇬🇧 German Newsreel, World War II, WWII, {ev_en}
🇪🇸 Noticiero alemán, Segunda Guerra Mundial
🇫🇷 Actualités allemandes, Seconde Guerre mondiale
🇵🇹 Cinejornal alemão, Segunda Guerra Mundial
🇷🇺 Немецкая кинохроника, Вторая мировая война
🇯🇵 ドイツニュース映画, 第二次世界大戦
🇮🇳 जर्मन न्यूज़रील, द्वितीय विश्व युद्ध
🇨🇳 德国新闻片, 二战
🇸🇦 النشرة الإخبارية الألمانية
🇮🇩 Berita Jerman, Perang Dunia II
🇻🇳 Tin tức Đức, Thế chiến thứ hai
🇹🇷 Alman haber filmi, İkinci Dünya Savaşı
🇰🇷 독일 뉴스릴, 제2차 세계대전
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{CTA}

📜 Source: Public Domain (Bundesarchiv / German Federal Archives)

#Wochenschau #WWII #WW2 #8K #History"""

def alfred_desc(ep_nr, title_de):
    """Full Alfred J. Kwak description."""
    return f"""Alfred J. Kwak (E{ep_nr:02d}) {title_de} | Deutsch | 8K HQ (4K UHD)

🎬 Alfred J. Kwak / Alfred Jodokus Quak — die beliebte Zeichentrickserie (1989).
Episode {ep_nr} von 52: "{title_de}"

🇩🇪 Die komplette Episode in deutscher Sprache, AI-remastered in atemberaubender 8K Qualität.
Ein Meisterwerk von Herman van Veen, das Generationen begeistert hat.

🇬🇧 The complete episode in German, AI-remastered in stunning 8K quality.
A masterpiece by Herman van Veen that has enchanted generations.

🕐 CHAPTERS:
0:00 Intro

{CTA}

#AlfredJKwak #Zeichentrick #8K #ClassicCartoon #Deutsch"""


# ═══════════════════════════════════════════════════════════
# PHASE 1: WOCHENSCHAU (4 raw private uploads)
# ═══════════════════════════════════════════════════════════

PHASE1_WOCHENSCHAU = [
    {
        "id": "2HZx5FumOo8",
        "title": "Wochenschau 552: Belgrade Coup (02.04.1941) | 8K HQ (4K UHD)",
        "category": "27",
        "tags": WS_TAGS_BASE + ["1941", "Belgrade", "Yugoslavia", "Belgrade Coup", "Balkan"],
        "desc": ws_desc("552", "02.04.1941", "Belgrad Putsch", "Belgrade Coup",
                        "Belgrade, Yugoslavia", "Putsch gegen den Achsenbeitritt Jugoslawiens (27.03.1941). "
                        "König Peter II. übernimmt die Macht — Beginn der Vergeltungsoperation."),
        "locs": ws_locs("552", "Belgrade Coup", "Belgrad Putsch", "02.04.1941"),
        "phase": 1,
    },
    {
        "id": "Yhz7gsTVqNA",
        "title": "Wochenschau 567: Smolensk Pocket (16.07.1941) | 8K HQ (4K UHD)",
        "category": "27",
        "tags": WS_TAGS_BASE + ["1941", "Smolensk", "Russia", "Eastern Front", "Operation Barbarossa"],
        "desc": ws_desc("567", "16.07.1941", "Smolensk Kessel", "Smolensk Pocket",
                        "Smolensk, Russia", "Die Schlacht um Smolensk beginnt (10.07.1941). "
                        "Deutsche Truppen schließen den Kessel um die Stadt — ein Wendepunkt an der Ostfront."),
        "locs": ws_locs("567", "Smolensk Pocket", "Smolensk Kessel", "16.07.1941"),
        "phase": 1,
    },
    {
        "id": "suxhPHyaQHU",
        "title": "Wochenschau 569: Kiev Encirclement (30.07.1941) | 8K HQ (4K UHD)",
        "category": "27",
        "tags": WS_TAGS_BASE + ["1941", "Kiev", "Ukraine", "Eastern Front", "Operation Barbarossa"],
        "desc": ws_desc("569", "30.07.1941", "Kiew Einkreisung", "Kiev Encirclement",
                        "Kyiv, Ukraine", "Beginn der Kiew-Operation. Die Wehrmacht beginnt die Einkreisung "
                        "der ukrainischen Hauptstadt — eine der größten Kesselschlachten der Geschichte."),
        "locs": ws_locs("569", "Kiev Encirclement", "Kiew Einkreisung", "30.07.1941"),
        "phase": 1,
    },
    {
        "id": "6Mh7zjUCmHw",
        "title": "Wochenschau 749: Ardennes Fails (10.01.1945) | 8K HQ (4K UHD)",
        "category": "27",
        "tags": WS_TAGS_BASE + ["1945", "Ardennes", "Belgium", "Battle of the Bulge", "Western Front"],
        "desc": ws_desc("749", "10.01.1945", "Ardennen scheitert", "Ardennes Fails",
                        "Ardennes, Belgium", "Die Ardennenoffensive scheitert (Dezember 1944 - Januar 1945). "
                        "Der letzte große deutsche Gegenangriff im Westen bricht zusammen."),
        "locs": ws_locs("749", "Ardennes Fails", "Ardennen scheitert", "10.01.1945"),
        "phase": 1,
    },
]


# ═══════════════════════════════════════════════════════════
# PHASE 2: ALFRED J. KWAK (private, raw "sls ARCHIVE" titles)
# File Nr → Broadcast Nr mapping applied!
# ═══════════════════════════════════════════════════════════

PHASE2_ALFRED = [
    # File 6 → Broadcast 6 (same)
    {"id": "8vH0m4Af1Hk", "ep": 6, "title_de": "Olympiade", "phase": 2},
    # File 7 → Broadcast 7 (same)
    {"id": "RFPKjY2AQDg", "ep": 7, "title_de": "Abenteuer auf hoher See", "phase": 2},
    # File 9 → Broadcast 9 (same)
    {"id": "LQFhE9PUgB4", "ep": 9, "title_de": "Ein gefährliches Geschenk", "phase": 2},
    # File 12 → Broadcast 12 (same)
    {"id": "0lphM8tc95M", "ep": 12, "title_de": "Die geheimnisvolle Königin", "phase": 2},
    # File 13 → Broadcast 13 (same) — DUPE of k0rYJmDH2kc which is public
    {"id": "Zb88QyQcUK4", "ep": 13, "title_de": "Haltet den Dieb!", "phase": 2},
    # File 14 → Broadcast 14 (same)
    {"id": "xkYPbDSepCY", "ep": 14, "title_de": "Skrupellose Geschäfte", "phase": 2},
    # File 15 → Broadcast 15 (same)
    {"id": "k_sQAu1YbWY", "ep": 15, "title_de": "Die Explosion", "phase": 2},
    # File 19 → Broadcast 19 (same)
    {"id": "ghhyzR9NSLE", "ep": 19, "title_de": "Rettet die Wale!", "phase": 2},
    # File 20 → Broadcast 20 (same)
    {"id": "oWZ5BmJVsxI", "ep": 20, "title_de": "Der Alptraum", "phase": 2},
    # File 29 → Broadcast 29 (same)
    {"id": "rC7bAjq0tLY", "ep": 29, "title_de": "Die Burengänse", "phase": 2},
    # File 31 → Broadcast 31 (same)
    {"id": "NvwmtSLyCE4", "ep": 31, "title_de": "Die Bohrinsel", "phase": 2},
    # File 32 → Broadcast 32 (same)
    {"id": "CmdyjVrJghc", "ep": 32, "title_de": "Atlantis", "phase": 2},
    # File 36 → Broadcast 37 (SHIFTED!)
    {"id": "Dg6eQNIY_Ys", "ep": 37, "title_de": "Die Entführung", "phase": 2},
    # File 41 → Broadcast 43 (SHIFTED!)
    {"id": "alOAM7jqMHY", "ep": 43, "title_de": "Groß-Wasserland", "phase": 2},
    # File 42 → Broadcast 44 (SHIFTED!) 
    {"id": "wZkHuISjOyE", "ep": 44, "title_de": "Die Überschwemmung", "phase": 2},
    # File 43 → Broadcast 48 (SHIFTED!)
    {"id": "8aeRL4PwSVI", "ep": 48, "title_de": "Eine Partie Golf", "phase": 2},
    # File 44 → Broadcast 49 (SHIFTED!)
    {"id": "RLfihGmp26w", "ep": 49, "title_de": "Der Regenbogen", "phase": 2},
    # File 45 → Broadcast 50 (SHIFTED!)
    {"id": "t1uRzra4Kb0", "ep": 50, "title_de": "Das Casino", "phase": 2},
]


# ═══════════════════════════════════════════════════════════
# PHASE 3: PUBLIC videos with remaining issues
# ═══════════════════════════════════════════════════════════

PHASE3_PUBLIC = [
    # WS 511: cat 25→27, missing "(4K UHD)" in title
    {
        "id": "3rB80OGKzrg",
        "title": "Wochenschau 511: Paris Falls (19.06.1940) | 8K HQ (4K UHD)",
        "category": "27",
        "tags": WS_TAGS_BASE + ["1940", "Paris", "France", "Paris Falls", "Western Front"],
        "locs": ws_locs("511", "Paris Falls", "Paris fällt", "19.06.1940"),
        "desc": None,  # keep existing, just fix cat + title
        "phase": 3,
    },
    # Skeleton Dance SHORT — private raw title
    {
        "id": "21iqU9NKJL0",
        "title": "The Skeleton Dance (1929) | Disney Silly Symphony | 8K HQ (4K UHD)",
        "category": "1",
        "tags": ["Skeleton Dance", "Disney", "Silly Symphony", "1929", "Ub Iwerks",
                 "vintage animation", "classic cartoon", "8K", "4K UHD",
                 "public domain", "Walt Disney", "Halloween", "remastered"],
        "desc": f"""🎬 The Skeleton Dance (1929) — the very first Disney Silly Symphony!
Directed by Walt Disney and animated by Ub Iwerks, this groundbreaking short
features skeletons dancing in a graveyard to spooky music.

A milestone of animation history, restored in stunning 8K quality.

🇩🇪 Der Skelett-Tanz (1929) — die allererste Disney Silly Symphony!
Regie: Walt Disney, Animation: Ub Iwerks. Ein Meilenstein der Animationsgeschichte.

{CTA}

#Disney #SillySymphony #8K #VintageAnimation #PublicDomain""",
        "locs": {
            "en": {"title": "The Skeleton Dance (1929) | Disney Silly Symphony | 8K HQ (4K UHD)",
                   "description": "The Skeleton Dance (1929) — the very first Disney Silly Symphony! AI remastered in 8K."},
            "de": {"title": "Der Skelett-Tanz (1929) | Disney Silly Symphony | 8K HQ (4K UHD)",
                   "description": "Der Skelett-Tanz (1929) — die allererste Disney Silly Symphony! In 8K restauriert."},
        },
        "phase": 3,
    },
]


# ═══════════════════════════════════════════════════════════
# EXPAND Alfred entries to full video objects
# ═══════════════════════════════════════════════════════════

def expand_alfred(entries):
    """Convert compact Alfred entries to full video dicts."""
    expanded = []
    for e in entries:
        ep = e["ep"]
        title_de = e["title_de"]
        yt_title = f"Alfred J. Kwak (E{ep:02d}) {title_de} | DE | 8K HQ (4K UHD)"
        expanded.append({
            "id": e["id"],
            "title": yt_title,
            "category": "1",
            "tags": ALFRED_TAGS_BASE + [title_de, f"Episode {ep}", f"E{ep:02d}"],
            "desc": alfred_desc(ep, title_de),
            "locs": alfred_locs(ep, title_de),
            "phase": e["phase"],
        })
    return expanded


# ═══════════════════════════════════════════════════════════
# EXECUTION ENGINE
# ═══════════════════════════════════════════════════════════

def apply_update(yt, video):
    """Apply a single video update. Returns quota used."""
    vid_id = video["id"]

    snippet = {
        "title": video["title"],
        "categoryId": video["category"],
        "tags": video["tags"],
        "defaultLanguage": "de",
    }
    
    if video.get("desc"):
        snippet["description"] = video["desc"]
    
    body = {"id": vid_id, "snippet": snippet}
    
    # Add localizations if present
    if video.get("locs"):
        body["localizations"] = video["locs"]
        parts = "snippet,localizations"
    else:
        parts = "snippet"

    try:
        # First fetch current to preserve description if not changing
        if not video.get("desc"):
            current = yt.videos().list(part="snippet", id=vid_id).execute()
            if current.get("items"):
                snippet["description"] = current["items"][0]["snippet"]["description"]

        yt.videos().update(part=parts, body=body).execute()
        return 50, "OK"
    except Exception as e:
        return 0, str(e)


def main():
    mode = "APPLY" if not DRY else "DRY-RUN"
    
    # Build full video list
    all_videos = []
    if PHASE_FILTER is None or PHASE_FILTER == 1:
        all_videos.extend(PHASE1_WOCHENSCHAU)
    if PHASE_FILTER is None or PHASE_FILTER == 2:
        all_videos.extend(expand_alfred(PHASE2_ALFRED))
    if PHASE_FILTER is None or PHASE_FILTER == 3:
        all_videos.extend(PHASE3_PUBLIC)
    
    total_quota = len(all_videos) * 50
    
    print("=" * 70)
    print(f"  FIX ALL NEW UPLOADS [{mode}]")
    print(f"  Videos: {len(all_videos)} | Quota: ~{total_quota} units")
    if PHASE_FILTER:
        print(f"  Phase filter: {PHASE_FILTER}")
    print("=" * 70)
    print()

    # Show plan
    for phase_num in [1, 2, 3]:
        phase_videos = [v for v in all_videos if v["phase"] == phase_num]
        if not phase_videos:
            continue
        phase_names = {1: "WOCHENSCHAU (private)", 2: "ALFRED J. KWAK (private)", 3: "PUBLIC FIXES"}
        print(f"── Phase {phase_num}: {phase_names[phase_num]} ({len(phase_videos)} videos) ──")
        for v in phase_videos:
            print(f"  [{v['id']}] → {v['title']}")
        print()

    if DRY:
        print(">>> Add --apply to execute changes <<<")
        print(f">>> Estimated quota: {total_quota} units <<<")
        
        # Save dry-run report
        report = {
            "date": "2026-02-22",
            "mode": "dry_run",
            "total_videos": len(all_videos),
            "estimated_quota": total_quota,
            "videos": [{"id": v["id"], "title": v["title"], "phase": v["phase"]} for v in all_videos]
        }
        report_path = Path("config/fix_all_uploads_2026_02_22_plan.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\nPlan saved: {report_path}")
        return

    # APPLY MODE
    yt = yt_client()
    quota_used = 0
    results = []

    for i, v in enumerate(all_videos, 1):
        print(f"[{i}/{len(all_videos)}] Phase {v['phase']} | {v['id']}")
        print(f"  → {v['title']}")
        
        quota, status = apply_update(yt, v)
        quota_used += quota
        results.append({
            "id": v["id"],
            "title": v["title"],
            "phase": v["phase"],
            "status": status,
            "quota": quota
        })
        
        if status == "OK":
            print(f"  ✅ UPDATED (+{quota} quota)")
        else:
            print(f"  ❌ ERROR: {status}")
        
        # Rate limit: 1 sec between calls
        if i < len(all_videos):
            time.sleep(1)

    # Summary
    ok = len([r for r in results if r["status"] == "OK"])
    err = len([r for r in results if r["status"] != "OK"])
    
    print()
    print("=" * 70)
    print(f"  RESULTS: {ok} updated, {err} errors")
    print(f"  QUOTA USED: {quota_used} units")
    print("=" * 70)
    
    # Save report
    report = {
        "date": "2026-02-22",
        "mode": "applied",
        "total_videos": len(all_videos),
        "quota_used": quota_used,
        "ok": ok,
        "errors": err,
        "results": results
    }
    report_path = Path("config/fix_all_uploads_2026_02_22_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
