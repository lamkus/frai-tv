# FRai.TV - Android TWA (Trusted Web Activity) Setup

## Voraussetzungen

1. **Node.js** 18+ installiert
2. **Java JDK** 11+ installiert
3. **Android SDK** mit Build Tools

## Schritt 1: Bubblewrap CLI installieren

```bash
npm install -g @anthropic/anthropic @anthropic/bubblewrap-cli
```

## Schritt 2: Android SDK einrichten

```bash
# Android SDK Pfad setzen (Windows)
$env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"

# Oder über Android Studio Command Line Tools installieren
```

## Schritt 3: TWA generieren

```bash
cd code/frontend
npx @anthropic/anthropic-anthropic bubblewrap init --manifest="https://frai.tv/manifest.json"
```

Oder mit lokaler Konfiguration:

```bash
npx @anthropic/bubblewrap-cli build
```

## Schritt 4: APK/AAB erstellen

```bash
npx @anthropic/bubblewrap-cli build
```

Dies erstellt:
- `app-release-signed.apk` - APK für direkte Installation
- `app-release-bundle.aab` - Android App Bundle für Play Store

## Schritt 5: Digital Asset Links verifizieren

Die Datei `.well-known/assetlinks.json` muss auf frai.tv verfügbar sein:

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": {
    "namespace": "android_app",
    "package_name": "tv.frai.app",
    "sha256_cert_fingerprints": [
      "YOUR_SHA256_FINGERPRINT"
    ]
  }
}]
```

### SHA256 Fingerprint erhalten:

```bash
keytool -list -v -keystore android.keystore -alias android -storepass YOUR_PASSWORD
```

## Schritt 6: Google Play Console

1. [Google Play Console](https://play.google.com/console) öffnen
2. Neue App erstellen
3. App Bundle (`.aab`) hochladen
4. Store-Eintrag ausfüllen
5. Content-Rating abschließen
6. Zur Überprüfung einreichen

## Store-Metadaten

### App-Name
**FRai.TV - Retro Streaming**

### Kurzbeschreibung (80 Zeichen)
Public Domain Klassiker in 8K: Cartoons, Stummfilme & Nostalgie gratis streamen.

### Vollständige Beschreibung
FRai.TV ist deine kostenlose Streaming-Plattform für Public Domain Klassiker.

✨ **Features:**
• 146+ remasterisierte Videos in bis zu 8K Qualität
• Klassische Cartoons: Superman, Popeye, Betty Boop, Felix the Cat
• Stummfilm-Meisterwerke: Charlie Chaplin, Buster Keaton, Fritz Lang
• Horror-Klassiker, Sci-Fi & Dokumentationen
• Komplett kostenlos - keine Werbung, kein Abo

🎬 **Kategorien:**
• Animation & Cartoons
• Stummfilm-Ära
• Classic Horror
• Film Noir
• Dokumentationen
• Weihnachtsklassiker

📱 **App-Features:**
• Dark Mode für angenehmes Schauen
• Fortsetzung beim letzten Standpunkt
• Offline-fähig (PWA)
• Watchlist & Verlauf
• Suche & Filter

Entdecke die goldene Ära des Kinos - remastered in moderner Qualität!

### Screenshots benötigt
- Phone: 1080x1920 (Portrait) - mindestens 2
- Tablet 7": 1200x1600 - optional
- Tablet 10": 1600x2560 - optional

### Kategorien
- Primär: Entertainment
- Sekundär: Video Players & Editors

### Content Rating
- Alle Altersstufen (USK 0, PEGI 3)
- Kein User Generated Content
- Keine In-App-Käufe
- Keine Werbung

## Keystore erstellen (einmalig)

```bash
keytool -genkeypair -alias android -keyalg RSA -keysize 2048 -validity 10000 -keystore android.keystore
```

**WICHTIG:** Keystore sicher aufbewahren! Verlust = keine Updates möglich.

## Troubleshooting

### Chrome Custom Tabs statt TWA
- assetlinks.json prüfen
- SHA256 Fingerprint stimmt nicht

### App stürzt ab
- minSdkVersion prüfen (23+)
- Android WebView aktualisieren

### Icon fehlt
- maskable Icon unter 512x512 mit safe zone
- PNG und SVG bereitstellen
