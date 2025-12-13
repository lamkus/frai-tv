# PWA Icons für frai.tv

## Benötigte Icons

Diese Icons müssen erstellt werden für PWA/App Store Veröffentlichung:

### Standard Icons (PNG, transparent)
- `icon-72.png` - 72x72
- `icon-96.png` - 96x96
- `icon-128.png` - 128x128
- `icon-144.png` - 144x144
- `icon-152.png` - 152x152
- `icon-192.png` - 192x192 ⭐ **Required für PWA**
- `icon-384.png` - 384x384
- `icon-512.png` - 512x512 ⭐ **Required für PWA**

### Maskable Icons (mit Safe Zone für Android Adaptive Icons)
- `icon-maskable-192.png` - 192x192
- `icon-maskable-512.png` - 512x512

### Shortcut Icons
- `shortcut-browse.png` - 96x96
- `shortcut-watchlist.png` - 96x96
- `shortcut-search.png` - 96x96

### Badge Icon (für Push Notifications)
- `badge-72.png` - 72x72 (monochrom)

## Design Guidelines

### Standard Icons
- frai.tv Logo zentriert
- Schwarzer Hintergrund (#0a0a0a)
- Logo mit Gradient (Purple #a855f7 → Pink #ec4899)

### Maskable Icons
- **Safe Zone:** 80% des Icons (40% Padding rundum)
- Logo muss in der inneren 80% sein
- Schwarzer Hintergrund (#0a0a0a)
- Wird von Android automatisch zugeschnitten

## Tools zum Erstellen

1. **Figma/Sketch:** Design erstellen, exportieren
2. **PWA Builder:** https://www.pwabuilder.com/imageGenerator
3. **Maskable.app:** https://maskable.app/ (Testen)
4. **Real Favicon Generator:** https://realfavicongenerator.net/

## Generierung mit CLI

```bash
# Mit sharp-cli
npm install -g sharp-cli
sharp -i logo.svg -o icon-192.png resize 192 192
sharp -i logo.svg -o icon-512.png resize 512 512
```

---

**WICHTIG:** Ohne diese Icons funktioniert die PWA-Installation nicht!
