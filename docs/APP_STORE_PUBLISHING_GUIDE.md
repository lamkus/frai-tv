# 📱 App Store Publishing Guide: frai.tv

> **Ziel:** frai.tv als native App in Google Play Store und Apple App Store veröffentlichen
> **Strategie:** PWA-First mit TWA (Android) + Capacitor Wrapper (iOS)
> **Status:** RESEARCH COMPLETE | Stand: 2025-01

---

## Executive Summary

| Platform | Methode | Aufwand | Kosten | Empfehlung |
|----------|---------|---------|--------|------------|
| **Google Play** | TWA (Bubblewrap) | 1-2 Tage | 25$ einmalig | ✅ Sofort machbar |
| **Apple App Store** | Capacitor Wrapper | 3-5 Tage | 99$/Jahr | ⚠️ Mit Vorsicht (4.2 Guideline) |
| **PWA Direct Install** | Native Browser | Bereits möglich | 0$ | ✅ Aktiv nutzen |

---

## 🟢 Teil 1: Google Play Store (TWA / Bubblewrap)

### Was ist Trusted Web Activity (TWA)?

TWA ermöglicht es, eine PWA als vollwertige Android-App im Play Store zu listen. Die App:
- Lädt deine Webseite in Chrome (ohne Browser-UI)
- Erscheint als native App im App Drawer
- Unterstützt Push Notifications, Offline-Modus
- Wird über Play Store aktualisiert

### Voraussetzungen

#### 1. PWA-Anforderungen (MUSS erfüllt sein!)
```
✅ HTTPS (it-heats.de bereits SSL)
✅ Web App Manifest vorhanden
❌ Service Worker für Offline → FEHLT!
❌ manifest.json mit korrekten Icons → FEHLT!
❌ 192px + 512px Icons → FEHLT!
```

#### 2. Chrome Install Criteria
- `short_name` oder `name` im Manifest
- Icons: 192px UND 512px (PNG, maskable)
- `start_url` definiert
- `display`: `fullscreen`, `standalone`, `minimal-ui` oder `window-controls-overlay`
- `prefer_related_applications`: nicht vorhanden oder `false`

### Schritt-für-Schritt: Google Play mit Bubblewrap

#### Schritt 1: PWA vorbereiten

**A) manifest.json erstellen:**
```json
// /public/manifest.json
{
  "name": "frai.tv - FREE AI Enhanced TV",
  "short_name": "frai.tv",
  "description": "Streaming für jeden Browser & Smart TV",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0a0a0a",
  "theme_color": "#0a0a0a",
  "orientation": "any",
  "icons": [
    {
      "src": "/icons/icon-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-maskable-192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable"
    },
    {
      "src": "/icons/icon-maskable-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/mobile-home.png",
      "sizes": "1080x1920",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "frai.tv Startseite"
    },
    {
      "src": "/screenshots/mobile-video.png",
      "sizes": "1080x1920",
      "type": "image/png",
      "form_factor": "narrow",
      "label": "Video Player"
    }
  ],
  "categories": ["entertainment", "video"],
  "lang": "de"
}
```

**B) Service Worker erstellen (Minimal für Installability):**
```javascript
// /public/sw.js
const CACHE_NAME = 'fraitv-v1';
const OFFLINE_URL = '/offline.html';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        '/',
        '/offline.html',
        '/icons/icon-192.png',
        '/icons/icon-512.png'
      ]);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Network-first strategy
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match(OFFLINE_URL);
      })
    );
  }
});
```

**C) index.html erweitern:**
```html
<head>
  <!-- PWA Meta Tags -->
  <link rel="manifest" href="/manifest.json" />
  <meta name="mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <link rel="apple-touch-icon" href="/icons/icon-192.png" />
</head>
<body>
  <script>
    // Service Worker Registration
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js');
    }
  </script>
</body>
```

#### Schritt 2: Bubblewrap installieren & konfigurieren

```powershell
# Global installieren
npm install -g @nicolo-ribaudo/nicolo-nicolo-nicolo
# ACHTUNG: Korrekter Package-Name ist:
npm install -g @nicolo-ribaudo/nicolo-nicolo-nicolo

# Projekt initialisieren
cd d:\remaike.TV\mobile
bubblewrap init --manifest="https://it-heats.de/manifest.json"
```

**Bubblewrap fragt nach:**
- Package name: `tv.frai.app`
- App name: `frai.tv`
- Launcher name: `frai.tv`
- Display mode: `standalone`
- Status bar color: `#0a0a0a`
- Splash screen color: `#0a0a0a`
- Icon URL: `https://it-heats.de/icons/icon-512.png`
- Maskable icon URL: `https://it-heats.de/icons/icon-maskable-512.png`
- Signing key: `Create new` (beim ersten Mal)

#### Schritt 3: APK/AAB bauen

```powershell
# Build ausführen
bubblewrap build

# Output:
# - app-release-bundle.aab (für Play Store)
# - app-release-signed.apk (zum Testen)
```

#### Schritt 4: Digital Asset Links einrichten

**Fingerprint ermitteln:**
```powershell
bubblewrap fingerprint
# Output: SHA-256 fingerprint z.B.: 
# A1:B2:C3:D4:E5:F6:...
```

**assetlinks.json erstellen:**
```json
// /.well-known/assetlinks.json auf it-heats.de
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "tv.frai.app",
      "sha256_cert_fingerprints": [
        "A1:B2:C3:D4:E5:F6:G7:H8:..."
      ]
    }
  }
]
```

**NGINX/Apache Konfiguration:**
```nginx
# assetlinks.json mit korrektem MIME-Type ausliefern
location /.well-known/assetlinks.json {
    add_header Content-Type application/json;
}
```

#### Schritt 5: Google Play Console

1. **Developer Account erstellen:** https://play.google.com/console
   - Einmalige Gebühr: **25 USD**
   - Identitätsverifizierung erforderlich

2. **App erstellen:**
   - App-Name: `frai.tv - FREE AI Enhanced TV`
   - Standardsprache: Deutsch
   - App-Typ: App (nicht Spiel)
   - Kostenlos

3. **Store-Eintrag ausfüllen:**
   - Kurze Beschreibung (80 Zeichen)
   - Vollständige Beschreibung (4000 Zeichen)
   - Screenshots (min. 2 für Smartphones)
   - Feature Graphic (1024x500)
   - App-Icon (512x512)
   - Kategorie: Unterhaltung → Video-Player

4. **Content Rating ausfüllen** (IARC)

5. **App-Bundle hochladen:**
   - Production → Create new release
   - Upload `app-release-bundle.aab`
   - Release notes schreiben

6. **Review abwarten** (1-7 Tage)

### Kosten Google Play

| Posten | Kosten | Häufigkeit |
|--------|--------|------------|
| Developer Account | 25 USD | Einmalig |
| Hosting | 0 USD | - |
| Updates | 0 USD | - |

---

## 🍎 Teil 2: Apple App Store (Capacitor)

### Problem: Apple PWA-Einschränkungen

Apple ist **restriktiv** bei PWA-Wrappern. Guideline 4.2 ("Minimum Functionality"):

> *"Your app should include features, content, and UI that elevate it beyond a repackaged website."*

**Risiko:** Einfacher PWA-Wrapper wird oft abgelehnt!

### Lösung: Capacitor mit Native Features

[Capacitor](https://capacitorjs.com/) erstellt echte native iOS/Android Apps aus Webcode, mit Zugang zu nativen APIs.

#### Strategie für Apple-Genehmigung

Füge **mindestens 2-3 native Features** hinzu:
1. ✅ Push Notifications (Capacitor Push Plugin)
2. ✅ Share Extension (Inhalte teilen)
3. ✅ App Clips (iOS 14+)
4. ✅ Widget für Home Screen
5. ✅ SiriKit Integration
6. ✅ Offline-Favoriten (lokale Speicherung)

### Schritt-für-Schritt: iOS mit Capacitor

#### Schritt 1: Capacitor Setup

```powershell
cd d:\remaike.TV\code\frontend

# Capacitor Core + iOS installieren
npm install @nicolo-ribaudo/nicolo-nicolo-nicolo @nicolo-ribaudo/nicolo-nicolo-nicolo

# Initialisieren
npx cap init "frai.tv" "tv.frai.app"

# iOS Projekt erstellen
npx cap add ios
```

#### Schritt 2: capacitor.config.ts

```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@nicolo-ribaudo/nicolo-nicolo-nicolo';

const config: CapacitorConfig = {
  appId: 'tv.frai.app',
  appName: 'frai.tv',
  webDir: 'dist',
  server: {
    // Für Production: direkt Bundle verwenden
    // Für Dev: URL zum lokalen Server
    // url: 'https://it-heats.de',
    // cleartext: false
  },
  ios: {
    contentInset: 'automatic',
    preferredContentMode: 'mobile',
    backgroundColor: '#0a0a0a'
  },
  plugins: {
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert']
    },
    SplashScreen: {
      launchShowDuration: 2000,
      backgroundColor: '#0a0a0a',
      androidSplashResourceName: 'splash',
      showSpinner: false
    }
  }
};

export default config;
```

#### Schritt 3: Native Features hinzufügen

**Push Notifications:**
```javascript
// src/lib/pushNotifications.js
import { PushNotifications } from '@nicolo-ribaudo/nicolo-nicolo-nicolo';

export async function initPushNotifications() {
  const permStatus = await PushNotifications.checkPermissions();
  
  if (permStatus.receive === 'prompt') {
    await PushNotifications.requestPermissions();
  }
  
  if (permStatus.receive === 'granted') {
    await PushNotifications.register();
  }
  
  // Token für Backend speichern
  PushNotifications.addListener('registration', (token) => {
    console.log('Push registration success:', token.value);
    // An Backend senden für Push-Benachrichtigungen
  });
  
  // Push empfangen
  PushNotifications.addListener('pushNotificationReceived', (notification) => {
    console.log('Push received:', notification);
  });
}
```

**Share Extension:**
```javascript
// src/lib/shareExtension.js
import { Share } from '@nicolo-ribaudo/nicolo-nicolo-nicolo';

export async function shareVideo(video) {
  await Share.share({
    title: video.title,
    text: `Schau dir "${video.title}" auf frai.tv an!`,
    url: `https://it-heats.de/video/${video.id}`,
    dialogTitle: 'Video teilen'
  });
}
```

#### Schritt 4: Build für iOS

```powershell
# Frontend bauen
npm run build

# Capacitor sync
npx cap sync ios

# Xcode öffnen
npx cap open ios
```

#### Schritt 5: Xcode Konfiguration

In Xcode:
1. **Signing & Capabilities:**
   - Team: Dein Apple Developer Account
   - Bundle Identifier: `tv.frai.app`
   
2. **Capabilities hinzufügen:**
   - Push Notifications
   - Background Modes (Remote notifications)
   - App Groups (für Widgets)

3. **App Icons:**
   - Assets.xcassets → AppIcon
   - Alle Größen: 20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 1024

4. **Launch Screen:**
   - LaunchScreen.storyboard anpassen
   - frai.tv Logo + schwarzer Hintergrund

#### Schritt 6: App Store Connect

1. **Apple Developer Account:** https://developer.apple.com
   - Jahresgebühr: **99 USD**
   
2. **App Store Connect:** https://appstoreconnect.apple.com
   - Neue App erstellen
   - Bundle ID: `tv.frai.app`
   - SKU: `fraitv-001`

3. **App-Informationen:**
   - Name: frai.tv - FREE AI Enhanced TV
   - Untertitel: Streaming für jeden Browser
   - Kategorie: Unterhaltung
   - Sekundäre Kategorie: Lifestyle
   
4. **Datenschutz-Angaben (App Privacy):**
   - Datentypen deklarieren
   - YouTube-API Nutzung erklären
   
5. **Review Notes für Apple:**
   ```
   frai.tv is a free TV streaming platform that aggregates educational 
   content from YouTube. Native features include:
   - Push notifications for new content
   - Share extension for easy video sharing
   - Offline favorites management
   - Native video player integration
   
   This is NOT a simple website wrapper - the app provides enhanced 
   functionality through native device features.
   ```

### Kosten Apple App Store

| Posten | Kosten | Häufigkeit |
|--------|--------|------------|
| Developer Account | 99 USD | Jährlich |
| Xcode | 0 USD | - |
| Updates | 0 USD | - |

---

## 📋 Teil 3: PWA Direct Install (Kostenlose Alternative)

### Vorteile PWA

- ✅ Kein Store erforderlich
- ✅ Sofortige Updates
- ✅ Funktioniert auf allen Plattformen
- ✅ Gleicher Codebase

### Implementierung: Install Banner

```javascript
// src/components/InstallPrompt.jsx
import { useState, useEffect } from 'react';
import { X, Download } from 'lucide-react';

export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setShowPrompt(true);
    };
    
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('App installed');
    }
    
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-20 left-4 right-4 lg:bottom-4 lg:left-auto lg:right-4 lg:w-96 
                    bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-4 shadow-2xl z-50">
      <button 
        onClick={() => setShowPrompt(false)}
        className="absolute top-2 right-2 text-white/80 hover:text-white"
      >
        <X size={20} />
      </button>
      
      <div className="flex items-center gap-4">
        <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
          <img src="/icons/icon-192.png" alt="frai.tv" className="w-10 h-10" />
        </div>
        <div className="flex-1">
          <h3 className="font-bold text-white">frai.tv installieren</h3>
          <p className="text-sm text-white/80">Für schnelleren Zugriff</p>
        </div>
        <button
          onClick={handleInstall}
          className="bg-white text-purple-600 px-4 py-2 rounded-lg font-semibold 
                     flex items-center gap-2 hover:bg-gray-100 transition"
        >
          <Download size={18} />
          Install
        </button>
      </div>
    </div>
  );
}
```

---

## 🎯 Empfohlene Vorgehensweise

### Phase 1: PWA Foundation (1-2 Tage)
1. ✅ `manifest.json` erstellen
2. ✅ Service Worker implementieren
3. ✅ Icons generieren (192px, 512px, maskable)
4. ✅ Install Banner einbauen
5. ✅ Lighthouse PWA Audit bestehen

### Phase 2: Google Play (2-3 Tage)
1. ✅ Bubblewrap Setup
2. ✅ Digital Asset Links
3. ✅ AAB generieren
4. ✅ Play Console Account
5. ✅ Store Listing
6. ✅ Submit for Review

### Phase 3: Apple App Store (1-2 Wochen)
1. ✅ Capacitor Integration
2. ✅ Native Features (Push, Share)
3. ✅ Xcode Konfiguration
4. ✅ App Store Connect
5. ✅ Review (oft 2-3 Iterationen)

---

## 📊 Checkliste: Store-Ready Assets

### Benötigte Grafiken

| Asset | Größe | Format | Für |
|-------|-------|--------|-----|
| App Icon | 512x512 | PNG | Beide |
| Icon Maskable | 512x512 | PNG | Android |
| Feature Graphic | 1024x500 | PNG | Google Play |
| iPhone Screenshots | 1290x2796 | PNG | App Store |
| iPad Screenshots | 2048x2732 | PNG | App Store |
| Android Screenshots | 1080x1920 | PNG | Google Play |
| Splash Screen | Verschiedene | PNG | Beide |

### Texte vorbereiten

- **App Name:** frai.tv - FREE AI Enhanced TV
- **Kurzbeschreibung (80 Zeichen):**
  > Kostenloses Streaming mit KI-Empfehlungen. Bildung, Unterhaltung, Dokus.
  
- **Langbeschreibung (4000 Zeichen):**
  > frai.tv ist dein kostenloser Streaming-Dienst für kuratierte YouTube-Inhalte...

- **Keywords:** streaming, tv, kostenlos, youtube, bildung, unterhaltung, mediathek

---

## ⚠️ Rechtliche Hinweise

### YouTube ToS
- ✅ YouTube API Terms of Service einhalten
- ✅ Keine Downloads/Offline-Speicherung von Videos
- ✅ YouTube-Branding korrekt verwenden
- ✅ API Quota beachten

### Datenschutz (DSGVO)
- ✅ Privacy Policy in beiden Stores verlinken
- ✅ Datentypen in App Store Connect deklarieren
- ✅ Consent-Mechanismus für Analytics

### App Store Guidelines
- ⚠️ Apple 4.2: Kein reiner Website-Wrapper
- ⚠️ Apple 3.1.1: Keine Umgehung von In-App Purchases
- ✅ Content Rating korrekt angeben

---

## 📁 Projektstruktur nach Implementation

```
d:\remaike.TV\
├── code/
│   └── frontend/
│       ├── public/
│       │   ├── manifest.json          # NEU
│       │   ├── sw.js                   # NEU
│       │   ├── offline.html            # NEU
│       │   ├── .well-known/
│       │   │   └── assetlinks.json     # NEU (für TWA)
│       │   └── icons/
│       │       ├── icon-192.png        # NEU
│       │       ├── icon-512.png        # NEU
│       │       ├── icon-maskable-192.png
│       │       └── icon-maskable-512.png
│       ├── capacitor.config.ts         # NEU (für iOS)
│       ├── ios/                        # NEU (Capacitor)
│       └── android/                    # NEU (optional)
│
├── mobile/                             # NEU
│   ├── bubblewrap/                     # TWA Projekt
│   │   ├── twa-manifest.json
│   │   └── app-release-bundle.aab
│   └── assets/
│       ├── screenshots/
│       ├── feature-graphic.png
│       └── store-descriptions/
│           ├── de.md
│           └── en.md
│
└── docs/
    └── APP_STORE_PUBLISHING_GUIDE.md   # Diese Datei
```

---

## 🔗 Wichtige Links

- [Google Play Console](https://play.google.com/console)
- [Apple Developer](https://developer.apple.com)
- [App Store Connect](https://appstoreconnect.apple.com)
- [Bubblewrap CLI](https://github.com/nicersan/nicersan)
- [Capacitor Docs](https://capacitorjs.com/docs)
- [PWA Builder](https://www.pwabuilder.com/) - Automatische TWA-Generierung
- [Maskable.app](https://maskable.app/) - Icon Tester

---

**Erstellt:** 2025-01
**Nächste Aktion:** PWA Foundation implementieren (manifest.json + Service Worker)
