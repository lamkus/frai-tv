"""
FINALER Wochenschau Download-Quellenplan
Konsolidiert alle Daten aus Archive.org (175+159 Ergebnisse) und net-film.ru (328 Einträge, 8 Seiten)
Erstellt: 2026-02-08
"""
import json
from datetime import datetime

# ============================================================================
# 47 FEHLENDE EPISODEN - VOLLSTÄNDIGE QUELLENANALYSE
# ============================================================================

MISSING_EPISODES = {
    # ========================================================================
    # ERA 1: VORKRIEG/POLENFELDZUG (1939) — 9 fehlend
    # Alle unter "UfA-Tonwoche" Titel, NICHT "Deutsche Wochenschau"
    # ========================================================================
    460: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-06-28",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Kein Online-Nachweis. Zwischen Nr.459 (Scapa Flow) und Nr.468 (Molotov-Ribbentrop). Bundesarchiv-Anfrage nötig."
    },
    461: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-07-05",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Sommer 1939, vor Kriegsausbruch. Keine Online-Quelle bekannt."
    },
    462: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-07-12",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    463: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-07-19",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    464: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-07-26",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    465: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-08-02",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    466: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-08-09",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    467: {
        "era": "1939 Vorkrieg",
        "date_est": "1939-08-16",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Woche vor Molotov-Ribbentrop-Pakt. Keine Online-Quelle bekannt."
    },
    469: {
        "era": "1939 Vorkrieg/Polenfeldzug",
        "date_est": "1939-08-30",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Tage vor Kriegsbeginn 01.09.1939! Extrem historisch wertvoll. Keine Online-Quelle."
    },

    # ========================================================================
    # ERA 2: SITZKRIEG/WESTFELDZUG (Jan-Jun 1940) — 17 fehlend
    # ========================================================================
    475: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-10-11",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.474 (Warschau-Kapitulation) und Nr.477 (Prien). Keine Online-Quelle."
    },
    476: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-10-18",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    478: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-11-01",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    479: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-11-08",
        "series": "UfA-Tonwoche",
        "sources": [
            {
                "type": "archive.org_extract",
                "identifier": "ufa-tonwoche-479-08.11.1939-herms-niel",
                "url": "https://archive.org/details/ufa-tonwoche-479-08.11.1939-herms-niel",
                "note": "NUR Musikextrakt: 'Wir fahren gegen Engelland' (Herms Niel), NICHT volle Episode"
            }
        ],
        "status": "PARTIAL",
        "note": "Bürgerbräukeller-Attentat auf Hitler! Nur Musikausschnitt online. Volle Episode: Bundesarchiv."
    },
    481: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-11-22",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    484: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-12-13",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.483 (Sport+U-Boote) und Nr.488 (Winter). Keine Online-Quelle."
    },
    485: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-12-20",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Weihnachten 1939 an der Front? Keine Online-Quelle."
    },
    486: {
        "era": "1940 Sitzkrieg",
        "date_est": "1939-12-27",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Jahresende 1939. Keine Online-Quelle."
    },
    487: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-01-03",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Neujahr 1940. Keine Online-Quelle."
    },
    489: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-01-17",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.488 und Nr.491. Keine Online-Quelle."
    },
    490: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-01-24",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    494: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-02-21",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Altmark-Vorfall (16.02.1940) könnte hier dokumentiert sein! Keine Online-Quelle."
    },
    495: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-02-28",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    498: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-03-20",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.497 (Heldengedenktag) und Nr.499 (Brenner-Treffen). Keine Online-Quelle."
    },
    500: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-04-03",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Kurz vor Operation Weserübung (09.04). Keine Online-Quelle."
    },
    501: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-04-10",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Beginn Weserübung? Könnte ersten Norwegen-Bericht enthalten. Keine Online-Quelle."
    },
    503: {
        "era": "1940 Sitzkrieg",
        "date_est": "1940-04-24",
        "series": "UfA-Tonwoche",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.502 (Dänemark) und Nr.504 (Norwegen). Keine Online-Quelle."
    },

    # ========================================================================
    # ERA 3: LUFTSCHLACHT/BARBAROSSA (1940-41) — 8 fehlend
    # Ab Nr.511 = "Die Deutsche Wochenschau"
    # ========================================================================
    535: {
        "era": "1940 Luftschlacht um England",
        "date_est": "1940-12-04",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Zwischen Nr.534 (Coventry) und Nr.536 (Bismarck). Keine Online-Quelle."
    },
    540: {
        "era": "1941 Dreimächtepakt",
        "date_est": "1941-01-08",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62772,
                "url": "https://www.net-film.ru/en/film-62772/",
                "duration": "21:24",
                "quality": "Full episode",
                "access": "Licensing required (commercial archive)"
            }
        ],
        "status": "FOUND",
        "note": "VOLLSTÄNDIGE Episode auf net-film.ru verfügbar!"
    },
    541: {
        "era": "1941 Dreimächtepakt",
        "date_est": "1941-01-15",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    546: {
        "era": "1941 Afrika-Korps/Balkan",
        "date_est": "1941-02-19",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "archive.org",
                "identifier": "19410219DieDeutscheWochenschauNr.54623m14s640x480",
                "url": "https://archive.org/details/19410219DieDeutscheWochenschauNr.54623m14s640x480",
                "download_url": "https://archive.org/download/19410219DieDeutscheWochenschauNr.54623m14s640x480/",
                "duration": "23:14",
                "quality": "640x480",
                "access": "FREE DOWNLOAD"
            }
        ],
        "status": "FOUND_FREE",
        "description": "Feldherrnhalle München Kriebel. Reichsmarschall Flieger West. Berghof. Mussolini-Franco. Japan Botschafter Oshima. Reichsfilmkammer Goebbels. Polizeisportfest. Max Schmeling Fallschirmjäger. SS Leibstandarte. Sizilien Afrika. Hilfskreuzer Atlantik.",
        "note": "GRATIS Download von Archive.org! 640x480 Qualität."
    },
    549: {
        "era": "1941 Afrika-Korps",
        "date_est": "1941-03-12",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62781,
                "url": "https://www.net-film.ru/en/film-62781/",
                "duration": "26:48",
                "quality": "Full episode",
                "access": "Licensing required"
            },
            {
                "type": "net-film.ru_wm",
                "film_id": 62780,
                "url": "https://www.net-film.ru/en/film-62780/",
                "duration": "08:37",
                "quality": "Working material",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND",
        "note": "Volle Episode + Arbeitsmaterial auf net-film.ru!"
    },
    551: {
        "era": "1941 Afrika-Korps",
        "date_est": "1941-03-26",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    558: {
        "era": "1941 Barbarossa-Vorbereitung",
        "date_est": "1941-05-14",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru_wm",
                "film_id": 62775,
                "url": "https://www.net-film.ru/en/film-62775/",
                "duration": "13:44",
                "quality": "Working material only",
                "access": "Licensing required"
            }
        ],
        "status": "PARTIAL",
        "note": "NUR Arbeitsmaterial auf net-film.ru. Keine volle Episode online."
    },
    559: {
        "era": "1941 Barbarossa-Vorbereitung",
        "date_est": "1941-05-21",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },

    # ========================================================================
    # ERA 4: OSTFRONT (1941-42) — 7 fehlend
    # ========================================================================
    560: {
        "era": "1941 Barbarossa-Vorbereitung",
        "date_est": "1941-05-28",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Kurz vor Barbarossa! Keine Online-Quelle."
    },
    563: {
        "era": "1941 Operation Barbarossa",
        "date_est": "1941-06-18",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62784,
                "url": "https://www.net-film.ru/en/film-62784/",
                "duration": "23:40",
                "quality": "Full episode",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND",
        "note": "VOLLSTÄNDIGE Episode! Tage VOR Barbarossa (22.06.1941). Historisch extrem wertvoll!"
    },
    580: {
        "era": "1941 Ostfront",
        "date_est": "1941-10-15",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62795,
                "url": "https://www.net-film.ru/en/film-62795/",
                "duration": "42:54",
                "quality": "Full episode, 4 parts",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND",
        "note": "VOLLSTÄNDIGE Episode auf net-film.ru! 42:54 Minuten, 4 Teile."
    },
    587: {
        "era": "1941 Ostfront",
        "date_est": "1941-12-03",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru_wm",
                "film_id": 62802,
                "url": "https://www.net-film.ru/en/film-62802/",
                "duration": "11:32",
                "quality": "Working material only, 2 parts",
                "access": "Licensing required"
            }
        ],
        "status": "PARTIAL",
        "note": "NUR Arbeitsmaterial (11:32). Volle Episode nicht online. Kurz vor Pearl Harbor!"
    },
    591: {
        "era": "1942 Ostfront Winter",
        "date_est": "1942-01-07",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Winter 1941/42 vor Moskau. Keine Online-Quelle."
    },
    597: {
        "era": "1942 Ostfront",
        "date_est": "1942-02-18",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },
    603: {
        "era": "1942 Ostfront Frühling",
        "date_est": "1942-04-01",
        "series": "Deutsche Wochenschau",
        "sources": [],
        "status": "NOT_FOUND",
        "note": "Keine Online-Quelle bekannt."
    },

    # ========================================================================
    # ERA 5: STALINGRAD (1942-43) — 4 fehlend
    # ========================================================================
    626: {
        "era": "1942 Stalingrad",
        "date_est": "1942-09-16",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62820,
                "url": "https://www.net-film.ru/en/film-62820/",
                "duration": "25:49",
                "quality": "Full episode, 3 parts",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND",
        "note": "VOLLSTÄNDIGE Episode! Schlacht um Stalingrad beginnt! Historisch enorm wichtig."
    },
    636: {
        "era": "1942 Stalingrad",
        "date_est": "1942-11-25",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "net-film.ru",
                "film_id": 62826,
                "url": "https://www.net-film.ru/en/film-62826/",
                "duration": "19:42",
                "quality": "Full episode, 2 parts",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND",
        "note": "VOLLSTÄNDIGE Episode! Einkesselung Stalingrad (19.11.1942). Historisch kritisch!"
    },
    643: {
        "era": "1943 Stalingrad-Kapitulation",
        "date_est": "1943-01-13",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "archive.org_compilation",
                "identifier": "diedeutschewochenschau646.2",
                "url": "https://archive.org/details/diedeutschewochenschau646.2",
                "download_url": "https://archive.org/download/diedeutschewochenschau646.2/",
                "files": ["die deutsche wochenschau 643.2", "die deutsche wochenschau 643"],
                "quality": "Standard (vermutlich 640x480)",
                "access": "FREE DOWNLOAD",
                "compilation_range": "Nr. 642-668 (66 Dateien)"
            }
        ],
        "status": "FOUND_FREE",
        "note": "GRATIS auf Archive.org! In Kompilation Nr. 642-668. Nahe Stalingrad-Kapitulation (02.02.1943)."
    },
    646: {
        "era": "1943 Totaler Krieg",
        "date_est": "1943-02-03",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "archive.org_compilation",
                "identifier": "diedeutschewochenschau646.2",
                "url": "https://archive.org/details/diedeutschewochenschau646.2",
                "download_url": "https://archive.org/download/diedeutschewochenschau646.2/",
                "quality": "Standard (vermutlich 640x480)",
                "access": "FREE DOWNLOAD",
                "compilation_range": "Nr. 642-668 (66 Dateien)"
            }
        ],
        "status": "FOUND_FREE",
        "note": "GRATIS auf Archive.org! In Kompilation Nr. 642-668. Nach Stalingrad-Kapitulation! Goebbels Sportpalastrede möglicherweise hier."
    },

    # ========================================================================
    # ERA 6: RÜCKZUG (1943-44) — 2 fehlend
    # ========================================================================
    664: {
        "era": "1943 Rückzug",
        "date_est": "1943-06-16",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "archive.org_compilation",
                "identifier": "diedeutschewochenschau646.2",
                "url": "https://archive.org/details/diedeutschewochenschau646.2",
                "download_url": "https://archive.org/download/diedeutschewochenschau646.2/",
                "quality": "Standard (vermutlich 640x480)",
                "access": "FREE DOWNLOAD",
                "compilation_range": "Nr. 642-668 (66 Dateien)"
            },
            {
                "type": "net-film.ru_wm",
                "film_id": 62846,
                "url": "https://www.net-film.ru/en/film-62846/",
                "duration": "07:15",
                "quality": "Working material only, 1 part",
                "access": "Licensing required"
            }
        ],
        "status": "FOUND_FREE",
        "note": "GRATIS auf Archive.org! In Kompilation Nr. 642-668. Zusätzlich: Arbeitsmaterial auf net-film.ru."
    },
    678: {
        "era": "1943 Rückzug",
        "date_est": "1943-09-22",
        "series": "Deutsche Wochenschau",
        "sources": [
            {
                "type": "archive.org_compilation",
                "identifier": "diedeutschewochenschau674_201907",
                "url": "https://archive.org/details/diedeutschewochenschau674_201907",
                "download_url": "https://archive.org/download/diedeutschewochenschau674_201907/",
                "quality": "Standard (vermutlich 640x480)",
                "access": "FREE DOWNLOAD",
                "compilation_range": "Nr. 669-695"
            }
        ],
        "status": "FOUND_FREE",
        "note": "GRATIS auf Archive.org! In Kompilation Nr. 669-695. Nach Sturz Mussolinis und Waffenstillstand Italien."
    },
}


def generate_final_plan():
    # Statistiken berechnen
    found_full = sum(1 for e in MISSING_EPISODES.values() if e["status"] in ("FOUND", "FOUND_FREE"))
    found_partial = sum(1 for e in MISSING_EPISODES.values() if e["status"] == "PARTIAL")
    not_found = sum(1 for e in MISSING_EPISODES.values() if e["status"] == "NOT_FOUND")
    
    plan = {
        "meta": {
            "generated": datetime.now().isoformat(),
            "title": "Wochenschau Download-Quellenplan — Weltweit erstes vollständiges Archiv",
            "channel": "@remAIke_IT (UCVFv6Egpl0LDvigpFbQXNeQ)",
            "total_episodes_range": "Nr. 459-755 (297 Nummern)",
            "currently_owned": 250,
            "missing": 47,
            "completion": "84.2%"
        },
        "summary": {
            "total_missing": 47,
            "found_full_episode": found_full,
            "found_partial_only": found_partial,
            "not_found_anywhere": not_found,
            "sources_searched": [
                "Archive.org (175 UfA-Tonwoche + 159 Deutsche Wochenschau = 334 Einträge)",
                "net-film.ru (328 Einträge, 8 Seiten komplett gescannt)",
                "Bundesarchiv (digitaler-lesesaal.bundesarchiv.de — Katalog vorhanden, Anfrage nötig)",
                "Periscope Film (2K/4K kommerzielle Lizenzierung)",
                "US National Archives (NARA — Kriegsbeute-Bestände)"
            ]
        },
        "action_plan": {
            "priority_1_free_download": {
                "description": "SOFORT herunterladen — Archive.org (kostenlos!)",
                "episodes": [546, 643, 646, 664, 678],
                "urls": [
                    "https://archive.org/details/19410219DieDeutscheWochenschauNr.54623m14s640x480",
                    "https://archive.org/details/diedeutschewochenschau646.2",
                    "https://archive.org/details/diedeutschewochenschau674_201907"
                ],
                "note": "Nr. 546 als Einzeldatei; Nr. 643+646+664 in Kompilation Nr.642-668; Nr. 678 in Kompilation Nr.669-695"
            },
            "priority_2_netfilm_licensing": {
                "description": "Bei net-film.ru lizenzieren — 6 volle Episoden verfügbar",
                "episodes": [540, 549, 563, 580, 626, 636],
                "total_duration_minutes": "~160 Min",
                "contact": "info@netfilm.store",
                "note": "Lizenzkosten anfragen. Russisches Staatsarchiv (RGAKFD) Material."
            },
            "priority_3_working_material": {
                "description": "Arbeitsmaterial von net-film.ru (unfertige Versionen, teils ohne Ton)",
                "episodes": [479, 558, 587],
                "note": "Nicht ideal für YouTube, aber besser als nichts. Teils nur Rohschnitt."
            },
            "priority_4_bundesarchiv": {
                "description": "Bundesarchiv-Anfrage für die verbleibenden 33 Episoden",
                "episodes": [460, 461, 462, 463, 464, 465, 466, 467, 469, 475, 476,
                            478, 481, 484, 485, 486, 487, 489, 490, 494, 495, 498,
                            500, 501, 503, 535, 541, 551, 559, 560, 591, 597, 603],
                "count": 33,
                "contact": "benutzung@bundesarchiv.de",
                "url": "https://www.bundesarchiv.de/DE/Navigation/Finden/Recherche-Online/recherche-online.html",
                "note": "Formale Bestellung nötig. Kosten: ca. 25-50€ pro Kopie. Bearbeitungszeit: 2-4 Wochen.",
                "strategy": "Sammelbestellung für alle 37 Nummern, Referenz auf Bestandssignatur Film R901/"
            },
            "priority_5_alternative_sources": {
                "description": "Alternative Quellen für besonders seltene Episoden",
                "sources": [
                    {
                        "name": "US National Archives (NARA)",
                        "url": "https://catalog.archives.gov/",
                        "search": "Deutsche Wochenschau OR UfA-Tonwoche",
                        "note": "Viel Material als Kriegsbeute beschlagnahmt. RG 242 (Foreign Records Seized)"
                    },
                    {
                        "name": "Imperial War Museum (IWM)",
                        "url": "https://www.iwm.org.uk/collections",
                        "note": "Britische Sammlung erbeuteter deutscher Wochenschauen"
                    },
                    {
                        "name": "Periscope Film",
                        "url": "https://www.periscopefilm.com/",
                        "note": "Kommerzielle Lizenzierung, 2K/4K Qualität, teuer"
                    },
                    {
                        "name": "Steven Spielberg Film and Video Archive (USHMM)",
                        "url": "https://collections.ushmm.org/search/",
                        "note": "US Holocaust Memorial Museum, einige Wochenschauen digitalisiert"
                    }
                ]
            }
        },
        "episodes_detail": {}
    }
    
    # Details für jede Episode
    for nr, info in sorted(MISSING_EPISODES.items()):
        plan["episodes_detail"][str(nr)] = info
    
    return plan


if __name__ == "__main__":
    plan = generate_final_plan()
    
    # Speichern
    out_path = "D:/remaike.TV/config/wochenschau_download_plan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    s = plan["summary"]
    a = plan["action_plan"]
    
    print("=" * 70)
    print("  🎬 WOCHENSCHAU DOWNLOAD-QUELLENPLAN — FINAL")
    print("=" * 70)
    print(f"  Fehlende Episoden gesamt:     {s['total_missing']}")
    print(f"  ✅ Volle Episode gefunden:    {s['found_full_episode']}")
    print(f"  ⚠️  Nur Arbeitsmaterial:       {s['found_partial_only']}")
    print(f"  ❌ Nicht gefunden:            {s['not_found_anywhere']}")
    print()
    print("  📋 AKTIONSPLAN:")
    print()
    print(f"  🟢 P1: Archive.org GRATIS Download:")
    for nr in a["priority_1_free_download"]["episodes"]:
        print(f"      → Nr. {nr}: {a['priority_1_free_download']['urls'][0]}")
    print()
    print(f"  🟡 P2: net-film.ru Lizenzierung ({len(a['priority_2_netfilm_licensing']['episodes'])} Episoden):")
    for nr in a["priority_2_netfilm_licensing"]["episodes"]:
        ep = MISSING_EPISODES[nr]
        url = ep["sources"][0]["url"]
        dur = ep["sources"][0]["duration"]
        print(f"      → Nr. {nr}: {url} ({dur})")
    print()
    print(f"  🟠 P3: Arbeitsmaterial ({len(a['priority_3_working_material']['episodes'])} Episoden):")
    for nr in a["priority_3_working_material"]["episodes"]:
        ep = MISSING_EPISODES[nr]
        if ep["sources"]:
            src = ep["sources"][0]
            print(f"      → Nr. {nr}: {src.get('url', 'Extrakt')} ({src.get('duration', 'k.A.')})")
        else:
            print(f"      → Nr. {nr}: Nur Extrakt auf Archive.org")
    print()
    print(f"  🔴 P4: Bundesarchiv-Anfrage ({a['priority_4_bundesarchiv']['count']} Episoden):")
    print(f"      Kontakt: {a['priority_4_bundesarchiv']['contact']}")
    episodes_str = ", ".join(str(n) for n in a['priority_4_bundesarchiv']['episodes'][:10])
    print(f"      Nummern: {episodes_str}, ...")
    print()
    print(f"  Gespeichert: {out_path}")
