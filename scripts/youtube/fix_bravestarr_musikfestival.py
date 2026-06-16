#!/usr/bin/env python3
"""BraveStarr Musikfestival KOMPLETT korrigieren"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import json
from pathlib import Path

oauth = json.loads(Path("config/youtube_oauth.json").read_text(encoding="utf-8"))
creds = Credentials(
    token=oauth.get("token"),
    refresh_token=oauth.get("refresh_token"),
    token_uri=oauth.get("token_uri"),
    client_id=oauth.get("client_id"),
    client_secret=oauth.get("client_secret"),
    scopes=oauth.get("scopes"),
)

youtube = build("youtube", "v3", credentials=creds)

vid = "XU7yM4H5vrY"

# Korrekte Beschreibung für Episode 1 - Das Musikfestival
CORRECT_DESCRIPTION = """🤠 BraveStarr - Komplette Serie in 8K | Folge 1 von 65

📺 "Das Musikfestival" - Deutsche Erstausstrahlung

═══════════════════════════════════════════════
🌟 ÜBER BRAVESTARR
═══════════════════════════════════════════════

BraveStarr ist eine amerikanische Space-Western-Zeichentrickserie von Filmation (1987-1988). Die Serie spielt im 23. Jahrhundert auf dem Wüstenplaneten New Texas.

👤 HAUPTCHARAKTERE:
• Marshal BraveStarr - Galaktischer Marshal mit Tierkräften
• Thirty/Thirty - Sein Equestroid-Partner (Pferd-Cyborg)  
• Deputy Fuzz - Kleiner pelziger Hilfsdeputy
• Judge J.B. McBride - Richterin und BraveStarrs Verbündete
• Shaman - BraveStarrs mystischer Mentor
• Tex Hex - Hauptantagonist mit magischen Kräften
• Stampede - Uralter Broncosaur, Anführer der Schurken

⚡ BRAVESTARRS KRÄFTE:
• 👁️ Eyes of the Hawk (Adleraugen)
• 👂 Ears of the Wolf (Wolfsohren)
• 💪 Strength of the Bear (Bärenstärke)
• 🏃 Speed of the Puma (Pumaschnelligkeit)

═══════════════════════════════════════════════
🎬 ÜBER DIESE VERSION
═══════════════════════════════════════════════
• 8K AI-Upscaling (4K UHD verfügbar)
• Deutsche Synchronfassung
• Restauriert & Remastered

📌 ABONNIEREN für mehr klassische Zeichentrickserien!

#BraveStarr #Filmation #80sCartoon #SpaceWestern #Deutsch #8K #Retro #Nostalgie #Zeichentrick #remAIke
"""

# Korrekte Tags für Episode 1
CORRECT_TAGS = [
    "BraveStarr", "Bravestarr", "Das Musikfestival",
    "Filmation", "1987", "Episode 1", "Folge 1",
    "Space Western", "New Texas", "Marshal BraveStarr",
    "Thirty Thirty", "Tex Hex", "Stampede", "Shaman",
    "80s cartoon", "80er Zeichentrick", "Deutsch", "German",
    "8K", "4K UHD", "remastered", "AI upscaled", "remAIke",
    "Pat Fraley", "Charlie Adler", "Ed Gilbert",
    "classic cartoon", "nostalgia", "retro", "Mattel"
]

resp = youtube.videos().list(part="snippet", id=vid).execute()
if resp.get("items"):
    snippet = resp["items"][0]["snippet"]
    
    # Alles korrigieren
    snippet["title"] = "8K Bravestarr - Das Musikfestival | Erste Folge (1/65) | Deutsch | 4K HQ | @remAIke_IT"
    snippet["description"] = CORRECT_DESCRIPTION
    snippet["tags"] = CORRECT_TAGS
    
    youtube.videos().update(
        part="snippet",
        body={"id": vid, "snippet": snippet}
    ).execute()
    
    print("KORRIGIERT!")
    print("- Titel: Das Musikfestival | Erste Folge (1/65)")
    print("- Beschreibung: Folge 1 von 65")
    print("- Tags: Episode 1, Folge 1, Das Musikfestival")
else:
    print("Video nicht gefunden!")
