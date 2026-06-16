"""
Apply SEO metadata to 4 draft videos.
NEVER changes privacyStatus — videos stay PRIVATE.
Quota cost: 4 × videos.update = 4 × 50 = 200 Units
"""
import json, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN = 'token.json'
creds = Credentials.from_authorized_user_file(TOKEN, ['https://www.googleapis.com/auth/youtube.force-ssl'])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
    with open(TOKEN, 'w') as f:
        f.write(creds.to_json())
    print('Token refreshed OK')

yt = build('youtube', 'v3', credentials=creds)

# ═══════════════════════════════════════════════════════════
# SEO UPDATES — privacyStatus bleibt UNVERÄNDERT (private)
# ═══════════════════════════════════════════════════════════

UPDATES = [
    # ─── 1. Der kleene Punker (1992) ───
    {
        'id': 'w17Gyr4r5A8',
        'title': 'Der kleene Punker (1992) | Kinderfilm | 8K HQ (4K UHD)',
        'categoryId': '1',  # Film & Animation
        'tags': [
            'Der kleene Punker', 'Kinderfilm', '1992', 'German film',
            'Deutscher Film', 'Berlin', '8K', '4K UHD', 'remastered',
            'restored', 'AI enhanced', 'classic', 'Punk', 'Kinder',
            'public domain'
        ],
        'description': """🎬 Der kleene Punker (1992) — Deutscher Kinderfilm in 8K restauriert.
Ein Berliner Junge taucht in die Punk-Szene ein — Kult-Kinderfilm der 90er Jahre, liebevoll in 8K remastered.

🎥 Originaltitel: Der kleene Punker
📅 Jahr: 1992
🎭 Genre: Kinderfilm / Komödie
🇩🇪 Sprache: Deutsch
⏱️ Laufzeit: ca. 79 Minuten

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this classic!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Kinderfilm #DeutscherFilm #8K #Remastered #PublicDomain"""
    },

    # ─── 2. Drüben bei Lehmanns (1970) S01E01 ───
    {
        'id': 'WV9o9YtlQbQ',
        'title': 'Drüben bei Lehmanns (E01) Neueröffnung (1970) | 8K HQ (4K UHD)',
        'categoryId': '24',  # Entertainment
        'tags': [
            'Drüben bei Lehmanns', 'ARD', 'Familienserie', '1970',
            'West-Berlin', 'Brigitte Mira', 'Walter Gross', 'Gustav Knuth',
            '8K', '4K UHD', 'remastered', 'restored', 'AI enhanced',
            'classic TV', 'German TV series'
        ],
        'description': """🎬 Drüben bei Lehmanns — ARD-Vorabendserie (1970), restauriert in 8K.
Paul und Else Lehmann betreiben einen kleinen Laden in West-Berlin. Episode 1: Neueröffnung.

📺 Serie: Drüben bei Lehmanns (ARD/SFB, 1970–1971)
🎬 Regie: Herbert Ballmann | Drehbuch: Rolf Schulz
🎭 Genre: Familienserie / Drama
👥 Darsteller: Walter Gross, Brigitte Mira, Gustav Knuth, Erika Rehhahn
📅 Erstausstrahlung: 12. September 1970
⏱️ Episode 1 von 26: "Neueröffnung"

Paul und Else Lehmann sind Inhaber eines kleinen Lebensmittelladens in einem West-Berliner Wohnviertel. Beide zeichnen sich durch große Hilfsbereitschaft aus und kümmern sich nebenbei um die kleinen und großen Sorgen ihrer Kunden und Nachbarn.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this classic!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#DeutscheFernsehserie #WestBerlin #8K #Remastered #ClassicTV"""
    },

    # ─── 3. Der 7. Sinn: Frauen am Steuer ───
    {
        'id': 'm7QBaZuR-Rw',
        'title': 'Der 7. Sinn: Frauen am Steuer (1966-2005) | 8K HQ (4K UHD)',
        'categoryId': '27',  # Education — korrekt!
        'tags': [
            'Der 7. Sinn', 'Verkehrserziehung', 'ARD', 'WDR',
            'Frauen am Steuer', 'Egon Hoegen', 'Verkehrssicherheit',
            '8K', '4K UHD', 'remastered', 'restored', 'AI enhanced',
            'classic TV', 'road safety', 'German TV'
        ],
        'description': """🎬 Der 7. Sinn — Frauen am Steuer: Übung macht den Meister | ARD-Verkehrserziehung in 8K restauriert.
Legendäre TV-Sendung zur Verkehrssicherheit (1966–2005), gesprochen von Egon Hoegen.

📺 Sendereihe: Der 7. Sinn (ARD/WDR, 1966–2005)
🎭 Genre: Verkehrserziehung / Bildung
🎙️ Sprecher: Egon Hoegen
🏢 Produktion: WDR / Cine Relation GmbH
📅 Ausgestrahlt: 1966–2005 (ca. 40 Jahre!)
⏱️ Folge: "Frauen am Steuer – Übung macht den Meister"

Der 7. Sinn war die "Mutter aller Verkehrserziehungssendungen" — wöchentlich wurden Tipps zum richtigen Verhalten im Straßenverkehr präsentiert, mit über 45 internationalen Preisen ausgezeichnet.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you found this valuable!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#Der7Sinn #Verkehrserziehung #8K #ClassicTV #PublicDomain"""
    },

    # ─── 4. Familie Heinz Becker S01E01 ───
    {
        'id': 'TQ3VQ66XNjg',
        'title': 'Familie Heinz Becker (S01E01) Der Dia-Abend (1992) | 8K HQ (4K UHD)',
        'categoryId': '24',  # Entertainment
        'tags': [
            'Familie Heinz Becker', 'Gerd Dudenhöffer', 'Heinz Becker',
            'Saarland', 'Comedy', 'Sitcom', 'ARD', 'WDR', '1992',
            '8K', '4K UHD', 'remastered', 'restored', 'AI enhanced',
            'German comedy'
        ],
        'description': """🎬 Familie Heinz Becker — Kult-Sitcom mit Gerd Dudenhöffer, restauriert in 8K.
Staffel 1, Folge 1: "Der Dia-Abend" (Erstausstrahlung: 23. März 1992).

📺 Serie: Familie Heinz Becker (ARD/WDR/SR, 1992–2004)
🎬 Idee: Gerd Dudenhöffer | Regie: Martin Kliemann
🎭 Genre: Comedy / Sitcom
👥 Darsteller: Gerd Dudenhöffer, Marianne Riedel-Weber, Gregor Weber
📅 Erstausstrahlung: 23. März 1992
⏱️ Staffel 1, Folge 1 von 42: "Der Dia-Abend"
🏆 Deutscher Comedypreis 2004 — Beste Comedy-Serie

Heinz Becker, der legendäre saarländische Spießer, entstammt der seit 1982 von Gerd Dudenhöffer verkörperten Bühnenfigur. Die Serie spielt in Bexbach und zeigt den Alltag der Familie Becker — Vater Heinz, Mutter Hilde und Sohn Stefan — im rheinfränkischen Dialekt.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👆 LIKE if you enjoyed this classic!
💬 COMMENT your thoughts!
🔔 SUBSCRIBE for more restored classics!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 www.remaike.IT
📺 https://www.youtube.com/@remAIke_IT

#FamilieHeinzBecker #GerdDudenhöffer #8K #DeutscheComedy #Remastered"""
    },
]

# ═══════════════════════════════════════════════════════════
# APPLY — privacyStatus stays UNCHANGED!
# ═══════════════════════════════════════════════════════════

print(f"\n{'='*60}")
print(f"APPLYING SEO TO {len(UPDATES)} DRAFT VIDEOS")
print(f"⚠️  privacyStatus: UNCHANGED (stays private)")
print(f"Quota cost: {len(UPDATES)} × 50 = {len(UPDATES) * 50} Units")
print(f"{'='*60}\n")

ok, fail = 0, 0
for u in UPDATES:
    try:
        # First GET current video to preserve all existing fields
        current = yt.videos().list(part='snippet,status', id=u['id']).execute()
        if not current.get('items'):
            print(f"  ❌ {u['id']}: NOT FOUND")
            fail += 1
            continue

        item = current['items'][0]
        snippet = item['snippet']
        status = item['status']

        # Update snippet fields
        snippet['title'] = u['title']
        snippet['description'] = u['description']
        snippet['tags'] = u['tags']
        snippet['categoryId'] = u['categoryId']

        # Apply — do NOT touch status/privacyStatus
        result = yt.videos().update(
            part='snippet',
            body={'id': u['id'], 'snippet': snippet}
        ).execute()

        print(f"  ✅ {u['id']}: {u['title']}")
        print(f"     Category: {u['categoryId']} | Tags: {len(u['tags'])} | Privacy: {status['privacyStatus']} (UNCHANGED)")
        ok += 1

    except Exception as e:
        print(f"  ❌ {u['id']}: {e}")
        fail += 1

print(f"\n{'='*60}")
print(f"DONE: {ok} updated | {fail} failed")
print(f"⚠️  All videos remain PRIVATE — user publishes manually!")
print(f"{'='*60}")
