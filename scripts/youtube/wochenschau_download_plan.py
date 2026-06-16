"""
Wochenschau Download-Quellenplan Generator
Parst Archive.org API-Daten und net-film.ru Katalog
Erstellt: 2026-02-08
"""
import json
import re
import os
from datetime import datetime

# Unsere 47 fehlenden Nummern
MISSING = [460, 461, 462, 463, 464, 465, 466, 467, 469, 475, 476, 478, 479, 481,
           484, 485, 486, 487, 489, 490, 494, 495, 498, 500, 501, 503, 535, 540,
           541, 546, 549, 551, 558, 559, 560, 563, 580, 587, 591, 597, 603, 626,
           636, 643, 646, 664, 678]

# ============================================================================
# Archive.org Funde (aus API-Abfrage 2026-02-08)
# Format: identifier -> Nummer(n) + Beschreibung
# ============================================================================
ARCHIVE_ORG_EPISODES = {
    # Deulig-Tonwoche (Vorgänger, eigene Nummerierung)
    "1932-02-24-Deulig-Tonwoche-008-1": {"nr": None, "series": "Deulig-Tonwoche", "date": "1932-02-24", "num": 8},
    "1933-04-26-Deulig-Tonwoche-069": {"nr": None, "series": "Deulig-Tonwoche", "date": "1933-04-26", "num": 69},
    "1933-08-02-Deulig-Tonwoche083": {"nr": None, "series": "Deulig-Tonwoche", "date": "1933-08-02", "num": 83},
    "1933-10-11-Deulig-Tonwoche-093": {"nr": None, "series": "Deulig-Tonwoche", "date": "1933-10-11", "num": 93},
    "1933-11-13-Deulig-Tonwoche-098": {"nr": None, "series": "Deulig-Tonwoche", "date": "1933-11-13", "num": 98},
    "1938-10-05-Deulig-Tonwoche-353": {"nr": None, "series": "Deulig-Tonwoche", "date": "1938-10-05", "num": 353},
    
    # UfA-Tonwoche (Hauptserie bis Nr. 511)
    "1935-03-20-UfA-Tonwoche-237": {"nr": 237, "series": "UfA-Tonwoche", "date": "1935-03-20"},
    "1936-08-18-UfA-Tonwoche-311": {"nr": 311, "series": "UfA-Tonwoche", "date": "1936-08-18"},
    "1937-09-22-UfA-Tonwoche-368": {"nr": 368, "series": "UfA-Tonwoche", "date": "1937-09-22"},
    "1938-05-10-UfA-TonWoche-Nr.401": {"nr": 401, "series": "UfA-Tonwoche", "date": "1938-05-10"},
    "1938-11-15-UfA-Tonwoche-428": {"nr": 428, "series": "UfA-Tonwoche", "date": "1938-11-15"},
    "1939-03-22-UfA-Tonwoche-446": {"nr": 446, "series": "UfA-Tonwoche", "date": "1939-03-22"},
    "1939-04-25-UfA-Tonwoche-451": {"nr": 451, "series": "UfA-Tonwoche", "date": "1939-04-25"},
    "1939-06-21-UfA-Tonwoche-459": {"nr": 459, "series": "UfA-Tonwoche", "date": "1939-06-21"},
    "1939-08-23-UfA-Tonwoche-468": {"nr": 468, "series": "UfA-Tonwoche", "date": "1939-08-23"},
    "1939-09-07-UfA-Tonwoche-470": {"nr": 470, "series": "UfA-Tonwoche", "date": "1939-09-07"},
    "1939-09-14-UfA-Tonwoche-471": {"nr": 471, "series": "UfA-Tonwoche", "date": "1939-09-14"},
    "1939-09-20-UfA-Tonwoche-472": {"nr": 472, "series": "UfA-Tonwoche", "date": "1939-09-20"},
    "1939-09-21-UfA-Tonwoche-473": {"nr": 473, "series": "UfA-Tonwoche", "date": "1939-09-27"},
    "1939-10-04-UfA-Tonwoche-474": {"nr": 474, "series": "UfA-Tonwoche", "date": "1939-10-04"},
    "1939-10-25-UfA-Tonwoche-477": {"nr": 477, "series": "UfA-Tonwoche", "date": "1939-10-25"},
    "1939-11-14-UfA-Tonwoche-480": {"nr": 480, "series": "UfA-Tonwoche", "date": "1939-11-14"},
    "1939-11-29-UfA-Tonwoche-482": {"nr": 482, "series": "UfA-Tonwoche", "date": "1939-11-29"},
    "1939-12-06-UfA-Tonwoche-483": {"nr": 483, "series": "UfA-Tonwoche", "date": "1939-12-06"},
    "1940-01-10-UfA-Tonwoche-488": {"nr": 488, "series": "UfA-Tonwoche", "date": "1940-01-10"},
    "1940-01-31-UfA-Tonwoche": {"nr": 491, "series": "UfA-Tonwoche", "date": "1940-01-31"},
    "1940-02-07-UfA-Tonwoche-492": {"nr": 492, "series": "UfA-Tonwoche", "date": "1940-02-07"},
    "1940-03-06-UfA-Tonwoche-496": {"nr": 496, "series": "UfA-Tonwoche", "date": "1940-03-06"},
    "1940-03-13-UfA-Tonwoche-497": {"nr": 497, "series": "UfA-Tonwoche", "date": "1940-03-13"},
    "1940-03-27-UfA-Tonwoche-499": {"nr": 499, "series": "UfA-Tonwoche", "date": "1940-03-27"},
    "1940-04-17-UfA-Tonwoche-502": {"nr": 502, "series": "UfA-Tonwoche", "date": "1940-04-17"},
    "1940-05-03-UfA-Tonwoche-504": {"nr": 504, "series": "UfA-Tonwoche", "date": "1940-05-03"},
    "1940-05-08-UfA-Tonwoche-505": {"nr": 505, "series": "UfA-Tonwoche", "date": "1940-05-08"},
    "1940-05-15-UfA-Tonwoche-506_2": {"nr": 506, "series": "UfA-Tonwoche", "date": "1940-05-15"},
    "1940-05-23-UfA-Tonwoche-507": {"nr": 507, "series": "UfA-Tonwoche", "date": "1940-05-22"},
    "1940-06-12-UfA-Tonwoche-510": {"nr": 510, "series": "UfA-Tonwoche", "date": "1940-06-12"},
    
    # Die Deutsche Wochenschau (ab Nr. 511)
    "1940-06-20-Die-Deutsche-Wochenschau-511": {"nr": 511, "series": "Deutsche Wochenschau", "date": "1940-06-20"},
    "1940-06-26-Die-Deutsche-Wochenschau-Nr.512": {"nr": 512, "series": "Deutsche Wochenschau", "date": "1940-06-26"},
    "1940-07-03-Die-Deutsche-Wochenschau-513": {"nr": 513, "series": "Deutsche Wochenschau", "date": "1940-07-03"},
    "1940-07-22-Die-Deutsche-Wochenschau-516": {"nr": 516, "series": "Deutsche Wochenschau", "date": "1940-07-22"},
    "1940-08-01-die-deutsche-wochenschau-nr.-51722m-45s-720x-544-512kb": {"nr": 517, "series": "Deutsche Wochenschau", "date": "1940-08-01"},
    "1940-08-23-Die-Deutsche-Wochenschau-520": {"nr": 520, "series": "Deutsche Wochenschau", "date": "1940-08-23"},
    "1940-09-18-Die-Deutsche-Wochenschau-524": {"nr": 524, "series": "Deutsche Wochenschau", "date": "1940-09-18"},
    "1940-09-25-Die-Deutsche-Wochenschau-525": {"nr": 525, "series": "Deutsche Wochenschau", "date": "1940-09-25"},
    "1940-10-09-Die-Deutsche-Wochenschau-527": {"nr": 527, "series": "Deutsche Wochenschau", "date": "1940-10-09"},
    "1940-10-16-Die-Deutsche-Wochenschau-528-2": {"nr": 528, "series": "Deutsche Wochenschau", "date": "1940-10-16"},
    "1940-10-30-Die-Deutsche-Wochenschau-530": {"nr": 530, "series": "Deutsche Wochenschau", "date": "1940-10-30"},
    "1940-11-06-Die-Deutsche-Wochenschau-531": {"nr": 531, "series": "Deutsche Wochenschau", "date": "1940-11-06"},
    "1940-11-20-Die-Deutsche-Wochenschau-533": {"nr": 533, "series": "Deutsche Wochenschau", "date": "1940-11-20"},
    "1940-11-28-Die-Deutsche-Wochenschau-534": {"nr": 534, "series": "Deutsche Wochenschau", "date": "1940-11-28"},
    "1940-12-18-Die-Deutsche-Wochenschau-537": {"nr": 537, "series": "Deutsche Wochenschau", "date": "1940-12-18"},
    "1940-12-25-Die-Deutsche-Wochenschau-538": {"nr": 538, "series": "Deutsche Wochenschau", "date": "1940-12-25"},
    "1941-01-22-Die-Deutsche-Wochenschau-542": {"nr": 542, "series": "Deutsche Wochenschau", "date": "1941-01-22"},
    "1941-01-29-Die-Deutsche-Wochenschau-Nr.543": {"nr": 543, "series": "Deutsche Wochenschau", "date": "1941-01-29"},
    "1941-02-05-Die-Deutsche-Wochenschau-544": {"nr": 544, "series": "Deutsche Wochenschau", "date": "1941-02-05"},
    "1941-02-12-Die-Deutsche-Wochenschau-545": {"nr": 545, "series": "Deutsche Wochenschau", "date": "1941-02-12"},
    "1941-02-26-Die-Deutsche-Wochenschau-547": {"nr": 547, "series": "Deutsche Wochenschau", "date": "1941-02-26"},
    
    # Sonderausgaben (extra identifiers mit Auflösung im Namen)
    "19410219DieDeutscheWochenschauNr.54623m14s640x480": {"nr": 546, "series": "Deutsche Wochenschau", "date": "1941-02-19", "quality": "640x480"},
    "19401211DieDeutscheWochenschauNr.53626m33s640x480FRUntertitel": {"nr": 536, "series": "Deutsche Wochenschau", "date": "1940-12-11", "quality": "640x480", "note": "FR Untertitel"},
    
    # Tobis Wochenschau
    "1940-05-22-Tobis-Wochenschau-22": {"nr": None, "series": "Tobis Wochenschau", "date": "1940-05-22", "num": 22, "note": "Sedan content"},
}

# ============================================================================
# Net-Film.ru Funde (328 Ausgaben, Seiten 1-2 gescannt)
# ============================================================================
NETFILM_EPISODES = {
    # Page 1 (sorted by appearance)
    511: {"film_id": 62753, "duration": "31:47", "year": 1940},
    514: {"film_id": 62754, "duration": "34:25", "year": 1940},
    515: {"film_id": 62755, "duration": "30:36", "year": 1940},
    519: {"film_id": 62756, "duration": "21:51", "year": 1940},
    520: {"film_id": 62757, "duration": "30:32", "year": 1940},
    521: {"film_id": 62758, "duration": "27:33", "year": 1940},
    523: {"film_id": 62759, "duration": "23:25", "year": 1940},
    524: {"film_id": 62760, "duration": "30:19", "year": 1940},
    531: {"film_id": 62761, "duration": "21:59", "year": 1940},
    532: {"film_id": 62762, "duration": "22:02", "year": 1940},
    537: {"film_id": 62763, "duration": "15:18", "year": 1940},
    538: {"film_id": 62764, "duration": "24:37", "year": 1940},
    542: {"film_id": 62766, "duration": "19:11", "year": 1941},
    544: {"film_id": 62765, "duration": "18:11", "year": 1941},
    549: {"film_id": 62781, "duration": "26:48", "year": 1941},  # ← MISSING! 
    561: {"film_id": 62783, "duration": "26:59", "year": 1941},
    563: {"film_id": 62784, "duration": "23:40", "year": 1941},  # ← MISSING!
    652: {"film_id": 62835, "duration": "20:27", "year": 1943},
    653: {"film_id": 72113, "duration": "20:35", "year": 1943},
    # Page 2
    527: {"film_id": 62776, "duration": "27:10", "year": 1940},
    529: {"film_id": 62770, "duration": "27:01", "year": 1940},
    540: {"film_id": 62772, "duration": "21:24", "year": 1941},  # ← MISSING!
    547: {"film_id": 62778, "duration": "27:35", "year": 1941},
    548: {"film_id": 62779, "duration": "27:24", "year": 1941},
    557: {"film_id": 62773, "duration": "20:51", "year": 1941},
    577: {"film_id": 62793, "duration": "31:14", "year": 1941},
    579: {"film_id": 62774, "duration": "36:59", "year": 1941},
    # Working material versions (additional)
    # 544-2, 549-2, 553-2, 558-2, 565-2, 566-2, 567-2, 569-2, 573-2, 575-2, 576-2, 578-2, 583-2
}

# Working material nur auf net-film.ru (teils für fehlende Nummern!)
NETFILM_WORKING_MATERIAL = {
    544: {"film_id": 62777, "duration": "03:24", "note": "Working material"},
    549: {"film_id": 62780, "duration": "08:37", "note": "Working material"},  # ← MISSING!
    553: {"film_id": None, "duration": "31:31", "note": "Working material"},
    558: {"film_id": 62775, "duration": "13:44", "note": "Working material"},  # ← MISSING!
    565: {"film_id": 62786, "duration": "10:30", "note": "Working material"},
    566: {"film_id": 62787, "duration": "29:20", "note": "Working material"},
    567: {"film_id": 62788, "duration": "14:07", "note": "Working material"},
    569: {"film_id": 62789, "duration": "10:22", "note": "Working material"},
    573: {"film_id": 62790, "duration": "14:59", "note": "Working material"},
    575: {"film_id": 62792, "duration": "10:49", "note": "Working material"},
    576: {"film_id": 62767, "duration": "26:41", "note": "Working material"},
    578: {"film_id": 62794, "duration": "01:15", "note": "Working material"},
    583: {"film_id": 62771, "duration": "16:22", "note": "Working material"},
}

# ============================================================================
# Archive.org Beschreibungen (historischer Kontext aus API)
# ============================================================================
ARCHIVE_DESCRIPTIONS = {
    459: "Archivbilder zeigen die Deutsche Kriegs-Flotte heute und vor ihrer Versenkung vor 20 Jahren in Scapa Flow. Kunstflugvorfuehrung in Frankreich. Rennfahren in Indianapolis. Tag der Kriegsmarine in Italien. Grosser Gaukulturtag in Danzig. Schalke 04 gewinnt gegen Admiral Wien 9:0.",
    468: "Fahrt der Marine-HJ auf der Donau von Passau nach Budapest. Grosse italienische Manoever in Turin. Polen: Danzig als Freistaat. Munitionsdepot errichtet. Nichtangriffspakt zwischen Reichs- und Sowjetregierung.",
    470: "Danzig zum Freistaat abgeschnitten. Beisetzung des Joseph Wessel. Flucht Volksdeutscher aus polnischen Gebieten. Polnische Artillerie attackiert deutsche Wohnhaeuser. Siegeszug deutscher Truppen.",
    471: "Generalfeldmarschall Goering. Truppen interniert. Der Fuehrer befindet sich bei seinen Truppen. Die Polen begreifen, fuer Englands Machtinteressen missbraucht worden zu sein.",
    472: "Frauen nehmen Platz der eingezogenen Maenner ein. DRK-Helferinnen. Deutsche Artisten unter KdF. Ueberquerung des Flusses Sang.",
    473: "Polenfeldzug: schwerste Entscheidungskaempfe in der 3. Woche. Luftwaffe bringt Polen zum Rueckzug.",
    474: "Staatsbegraebnis fuer Generaloberst von Fritsch. Buendnisse mit Russland, Tuerkei und Italien. Juden als internationales Verbrechergesindel. Warschau kapituliert 27. September.",
    477: "Konferenz der nordischen Staaten in Stockholm. U-Boot Kapitan Prien kehrt zurueck. Empfang in Berlin. Wunschkonzert im Radio.",
    480: "Japanischer Aussenminister Nomura. Amerika nach Neutralitaetsgesetz. Marine-Dienst.",
    482: "Japan grosse Uebungsmanoever. Vormilitaerische Erziehung der Hitler-Jugend. NSV in allen Gauen. Posen.",
    483: "Sport-Wandlung. Nationale Sportkaempfe Japan unter Kaiser Hirohito. Deutsch-Rumaenischer Handelsvertrag. Englische Hunger-Blockade. U-Boote siegreich.",
    488: "Zusammenwirkens der verschiedensten Waffen. Infanterist als Traeger des Kampfes.",
    491: "Harter Winter in Holland. Eisbrecher. Skiuebungen trotz Krieg. Goebbels besucht Westfront. Pioniere Behelfsbruecke. U-Boot Erfolge. Admiral Doenitz.",
    492: "Deutscher Wintersport vorbildlich. Hitler-Rede 30. Januar im Sportpalast. Angriffsuebung Infanterie-Bataillon. Ring um England durch Luftwaffe.",
    493: "Leipziger Fruehjahrs-Messe. Finnisch-russischer Krieg. Deutschland Schweizerische Nachbarschaft.",
    496: "Grossfeuer Japan. Barcelona Jahrestag Befreiung. Musketiere des Duce in Rom. Roosevelt-Gesandter in Europa. Leipziger Kriegsmesse. U-Boot Heimkehr. Torpedo-Boote Nordsee.",
    497: "Harter Winter Japan. Hochwild bayerische Alpen. Skiwettkampf Garmisch-Partenkirchen. Heldengedenktag. U-Boot 80.000t versenkt.",
    499: "Begegnung Fuehrer-Duce am Brennerpass. Neuaufbau Ostmark. Frauen in Produktion. U-Boot Werft. Messerschmitt-Jaeger. Scapa Flow Flieger.",
    502: "Deutsche Truppen landen in Daenemark (Kopenhagen). Flugblaetterabwurf. Operation Weseruebung. Platzkonzert.",
    504: "Uebungen am Westwall. Ribbentrop Regierungserklaerung. Norwegenfront, Vernichtung norwegischer Widerstandsnester. Festung Oscarborg.",
    505: "Reichsarbeitskammer 1. Mai Krupp-Werke. Metallspenden. Norwegen-Operationen. Kampf zu Lande und zur See.",
    506: "Beginn Westfeldzug 10. Mai. Luxemburg, Belgien. Panzer, Sturmpioniere, Fallschirmjaeger. Fort Eben-Emael. Rotterdam Kapitulation.",
    507: "Fallschirmjaeger Rotterdam und Dordrecht. Uebergang ueber die Maas. Rotterdam Verteidigung bricht zusammen. Kapitulation hollaendische Armee. Bombengeschwader gegen Belgien. Fort Luettich.",
    510: "Duenkirchen: Kampf- und Stukaverbaende. Flak und Schnellboote. Flucht der Englaender. Besuch des Fuehrers. Kriegserklaerung Italiens. Luftangriffe bei Paris.",
    511: "Schlacht um Frankreich. Le Havre. Amiens. Kaempfe Sommegebiet. Hissung Hakenkreuzfahne Versailles. Einnahme Paris. Eiffelturm. Kapitulation Frankreichs.",
    512: "Strassburg, Metz, Verdun wieder deutsch. Kapitulation. Compiegne Waffenstillstand.",
    513: "Rueckblick Frankreich-Feldzug. Transport-Organisation. Flandern. Englische Bombenangriffe auf deutsche Staedte. Vergeltung.",
    516: "Italienischer Vormarsch franzoesische Alpen. Ostafrika. Gibraltar. Fuehrerrede 19. Juli. Berlin empfaengt heimkehrende Division.",
    517: "BDM Koerperschulung. Kunstausstellung Muenchen. Panzerproduktion. Kanalinseln Guernsey Jersey. U-Boote. Feindflug gegen England.",
    520: "28. Deutsche Ostmesse Koenigsberg. Duengemittel. Flak-Geschuetze. Marschallstaebe. Italienische Bomber Somali. Fernartillerie Kanalgebiet.",
    524: "Reichsarbeitsdienst Wartheland. Elsass-Lothringen Fluechtlinge. Minensperren Norwegen. Bombenangriff Berlin. Luftangriff London.",
    525: "Norwegisches Arbeitsmaidenlager. Ungarn Siebenbuergen. Serrano Suner Berlin. Seeminenherstellung. Goering Kampfgeschwader. Stukas England.",
    527: "Amerikanische Wehrpflicht Roosevelt. Japanischer Angriff Tschungking. Hitler-Mussolini Brenner. Luxemburg NS-Kundgebung. Bordeaux. Sidi Barrani. Liverpool.",
    528: "Bauvorhaben Rom. Konzert Madrid Stierkampfarena. Tangerzone Spanien. Bulgarien Dobrudscha. Bessarabien-Deutsche. Warschau Parade. Dover Artillerie.",
    530: "KdF-Seebad Ruegen. Danzig-Westpreussen. Rumaenien Oelfelder. Hitler-Franco Hendaye. Hitler-Mussolini Florenz.",
    531: "Kartoffelernte. Autobahnbau. Segelfliegerlager. SA Marienburg. Generalgouvernement Krakau. Nordafrika Italien. Burmastrasse Japan. Richthofen-Geschwader. Coventry.",
    533: "Mandschukuo. Japan Indochina. NS-Bewegung Amsterdam. Molotow Berlin. Siedlungen Warthegau. Kinderlandverschickung. Langemarck. Kuestenbatterie England.",
    534: "Erdbeben Rumaenien. Nordafrika Italien. Bessarabien-Deutsche Umsiedlung. Ciano Obersalzberg. Ungarn/Rumaenien/Slowakei Dreimaechte. Wien Ausstellung. Coventry Luftangriff. U-Boot Kretschmer 200.000t.",
    536: "Goebbels Oslo. Bauarbeiten Generalgouvernement. Volksweihnacht. Wehrmachtswunschkonzert. Birmingham. Schlachtschiff Bismarck.",
    537: "Genesungsheim. Generalfeldmarschall Brauchitsch. Parade Bukarest. Strassenbau Norwegen. Paris-Strassburg Eisenbahn. Winterhilfswerk. Volksweihnacht. U-Boot Bau. Fuehrer-Rede.",
    538: "Japan Burmastrasse. Spanische Fluechtlingskinder. Warschau Strassenbahn. Norwegen Flugplaetze. Neue Reichskanzlei. Gewehrfabrikation Steyr. Volksweihnacht. Kanalinseln.",
    542: "Japan Kaiserhaus 2600 Jahre. Sowjetisches Grenzabkommen Moskau. Schneefaelle Europa. Lofoten Marine. Kronborg Helsingoer. NSB Utrecht. Goering 48. Geburtstag. Galland Kanalgebiet.",
    543: "Christian Sinding. Norweger Arbeitseinsatz Deutschland. Generalgouvernement Wiederaufbau. Lehar Paris. HJ Kaernten. Japanische Offiziersabordnung. Condor Fw200. Malta Luftangriff. U-Boot Aequator.",
    544: "Trauerfeier Guertner. Ungarischer Honved-Minister. Japan Offiziersabordnung. Fieseler Storch. Condor Fw200 Schottland. Hilfskreuzer Tropen. Hitler Sportpalast 8. Jahrestag.",
    545: "Beisetzung Graf Czaky Budapest. Japan Botschafter Kurosu. Axmann Norwegen. Wintersport Oslo. Raeumboote Kanalkueste. Nordafrika Fliegerstaffel.",
    546: "Feldherrnhalle Muenchen Kriebel. Reichsmarschall Flieger West. Berghof. Mussolini-Franco. Japan Botschafter Oshima. Reichsfilmkammer Goebbels. Polizeisportfest. Max Schmeling Fallschirmjaeger. SS Leibstandarte. Sizilien Afrika. Hilfskreuzer Atlantik.",
    547: "Ordensburg Sonthofen. Grossappell Deutsche Arbeitsfront. Tag der Polizei. Bildhauer Arno Breker. Soldaten Paris. Ski-WM Cortina. Sanitaetssoldaten. Fw200 Atlantik.",
}

# ============================================================================
# ERGEBNIS-GENERIERUNG
# ============================================================================

def generate_download_plan():
    results = {
        "generated": datetime.now().isoformat(),
        "summary": {},
        "missing_episodes": {},
        "archive_org_available": {},
        "netfilm_available": {},
        "historical_descriptions": {},
        "download_urls": {}
    }
    
    # Archive.org Nummern extrahieren
    archive_numbers = set()
    for ident, info in ARCHIVE_ORG_EPISODES.items():
        if info.get("nr"):
            archive_numbers.add(info["nr"])
            results["archive_org_available"][str(info["nr"])] = {
                "identifier": ident,
                "url": f"https://archive.org/details/{ident}",
                "download": f"https://archive.org/download/{ident}/",
                "date": info["date"],
                "series": info["series"]
            }
    
    # Net-film.ru Nummern
    netfilm_numbers = set(NETFILM_EPISODES.keys())
    netfilm_wm_numbers = set(NETFILM_WORKING_MATERIAL.keys())
    
    for nr, info in NETFILM_EPISODES.items():
        results["netfilm_available"][str(nr)] = {
            "url": f"https://www.net-film.ru/en/film-{info['film_id']}/",
            "duration": info["duration"],
            "year": info["year"],
            "type": "full"
        }
    
    for nr, info in NETFILM_WORKING_MATERIAL.items():
        key = f"{nr}_wm"
        if info.get("film_id"):
            results["netfilm_available"][key] = {
                "url": f"https://www.net-film.ru/en/film-{info['film_id']}/",
                "duration": info["duration"],
                "type": "working_material"
            }
    
    # Beschreibungen
    for nr, desc in ARCHIVE_DESCRIPTIONS.items():
        results["historical_descriptions"][str(nr)] = desc
    
    # Fehlende Episoden analysieren
    found_archive = 0
    found_netfilm = 0
    found_netfilm_wm = 0
    not_found = 0
    
    for nr in MISSING:
        sources = []
        if nr in archive_numbers:
            sources.append("archive.org")
            found_archive += 1
        if nr in netfilm_numbers:
            sources.append("net-film.ru")
            found_netfilm += 1
        if nr in netfilm_wm_numbers:
            sources.append("net-film.ru (working material)")
            found_netfilm_wm += 1
        
        status = "FOUND" if sources else "NOT_FOUND"
        if not sources:
            not_found += 1
            sources = ["Bundesarchiv (Kopienbestellung)", "Archive.org (weitere Suche noetig)"]
            status = "SEARCH_NEEDED"
        
        # Era bestimmen
        if nr < 470: era = "1939 Vorkrieg/Polenfeldzug"
        elif nr < 512: era = "1940 Sitzkrieg/Westfeldzug"  
        elif nr < 560: era = "1940-41 Luftschlacht/Barbarossa"
        elif nr < 610: era = "1941-42 Ostfront"
        elif nr < 660: era = "1942-43 Stalingrad"
        elif nr < 700: era = "1943-44 Rueckzug"
        else: era = "1944-45 Endphase"
        
        # Download URL wenn verfuegbar
        download_url = None
        if nr in archive_numbers:
            for ident, info in ARCHIVE_ORG_EPISODES.items():
                if info.get("nr") == nr:
                    download_url = f"https://archive.org/details/{ident}"
                    break
        
        results["missing_episodes"][str(nr)] = {
            "status": status,
            "era": era,
            "sources": sources,
            "download_url": download_url,
            "description": ARCHIVE_DESCRIPTIONS.get(nr, "")
        }
    
    # Summary
    results["summary"] = {
        "total_missing": len(MISSING),
        "found_on_archive_org": found_archive,
        "found_on_netfilm": found_netfilm,
        "found_on_netfilm_wm_only": found_netfilm_wm,
        "still_not_found": not_found,
        "archive_org_total_episodes": len(archive_numbers),
        "netfilm_total_episodes": len(netfilm_numbers),
        "netfilm_total_catalog": 328,
        "netfilm_pages_remaining": "3, 4, 5 (noch nicht gescannt)",
        "completion_percentage": round((250 / 297) * 100, 1),
        "target": "297 Episoden (Nr. 459-755) fuer weltweit erstes vollstaendiges Archiv"
    }
    
    return results


if __name__ == "__main__":
    plan = generate_download_plan()
    
    # Speichern
    out_path = "D:/remaike.TV/config/wochenschau_download_plan.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    # Ausgabe
    s = plan["summary"]
    print("=" * 60)
    print("  WOCHENSCHAU DOWNLOAD-QUELLENPLAN")
    print("=" * 60)
    print(f"  Fehlende Episoden: {s['total_missing']}")
    print(f"  Gefunden auf Archive.org: {s['found_on_archive_org']}")
    print(f"  Gefunden auf Net-Film.ru: {s['found_on_netfilm']}")
    print(f"  Nur Working Material: {s['found_on_netfilm_wm_only']}")
    print(f"  Noch nicht gefunden: {s['still_not_found']}")
    print(f"  Gesamtfortschritt: {s['completion_percentage']}%")
    print()
    
    print("=== FEHLENDE MIT DOWNLOAD-QUELLE ===")
    for nr_str, info in sorted(plan["missing_episodes"].items(), key=lambda x: int(x[0])):
        nr = int(nr_str)
        icon = "✅" if info["status"] == "FOUND" else "🔍"
        src = ", ".join(info["sources"][:2])
        print(f"  {icon} Nr. {nr:3d} | {info['era'][:30]:30s} | {src}")
    
    print(f"\n  Gespeichert: {out_path}")
