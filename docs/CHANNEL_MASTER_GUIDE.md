# 🎬 remAIke_IT - Channel Master Guide

> **Zentrale Dokumentation für Channel-Management, SEO & Monetarisierung**
> Zuletzt aktualisiert: 2026-01-14

---

## 📺 CHANNEL ÜBERSICHT

| Info | Wert |
|------|------|
| **Channel ID** | `UCVFv6Egpl0LDvigpFbQXNeQ` |
| **Handle** | `@remAIke_IT` |
| **Videos** | ~290 (271 public, 18 drafts) |
| **Hauptthema** | Public Domain Content in 8K |
| **USP** | "Best Online Version" - 8K AI-Upscaled |

---

## 🎯 CONTENT-KATEGORIEN

| Kategorie | Videos | Status | Playlist |
|-----------|--------|--------|----------|
| 💋 Betty Boop | 64 | ✅ Optimiert | ✅ |
| 🎵 Soundies | 39 | ✅ Music Category | ✅ |
| 🦆 Alfred J. Kwak | 22 | ✅ Komplett | ✅ |
| 🐰 Looney Tunes | 17 | ✅ | ✅ |
| 🦸 Superman/Fleischer | 15 | ✅ | ✅ |
| 🐱 Felix the Cat | 13 | ✅ | ✅ |
| 🎄 Christmas | 13 | ✅ | ✅ |
| 📽️ Dokumentationen | 13 | ✅ | ✅ |
| 👻 Casper | 9 | ✅ | ✅ |
| 🎬 Silent Era | 9 | ✅ | ✅ |
| 📰 Wochenschau | 6 | ✅ Trilingual | ✅ |
| 🤠 BraveStarr | 4 | 🔄 In Progress | ✅ |
| ⚔️ Asterix | 3 | ✅ | Pending |
| 🏎️ Ken Block/Gymkhana | 3 | ✅ | Pending |
| 💎 Misc Vintage | 29 | ✅ | ✅ |

---

## 📋 SEO-STANDARDS

### Titel-Format (max 70 Zeichen!)
```
[Content]: [Spezifisch] | 8K HQ
```

**Beispiele:**
- `Betty Boop (14/105): The Dancing Fool (1932) | 8K HQ`
- `Jiveroo (1940s) | Soundie | 8K HQ`
- `Wochenschau: Battle of France (22.07.1940) | 8K HQ (4K UHD)`

### Pflicht-Elemente
- ✅ **8K HQ (4K UHD)** im Wochenschau-Titel
- ❌ **KEIN @remAIke_IT im Titel!** (verschwendet Zeichen)
- ✅ Jahr in Klammern bei Filmen: `(1932)`
- ✅ Episode-Nummer bei Serien: `(14/105)`

### Beschreibungs-Template
```
WE HAVE THE BEST VERSION FOR YOU!
SHARE AND PUSH US TO GET THE WHOLE INTERNET UPGRADED :)

@remAIke_IT | www.remAIke.IT
www.FRai.TV - All videos organized....

[CONTENT-SPEZIFISCHE BESCHREIBUNG DE/EN/ES]

8K HQ Edition:
• stabilized archival source
• enhanced clarity for modern displays
• original visual and audio character preserved

LIKE • COMMENT • SUBSCRIBE @remAIke_IT

#[Hashtags]
```

---

## 🎵 YOUTUBE MUSIC OPTIMIERUNG

### Für Musik-Content (Soundies, etc.)
- **Category:** Muss `10` (Music) sein!
- **Tags:** `Official Audio`, `music video`, Genre-Tags
- **Titel:** Artist + Song Title klar erkennbar

### Category IDs
| ID | Kategorie | Für |
|----|-----------|-----|
| 1 | Film & Animation | Cartoons, Filme |
| 10 | Music | Soundies, Musikvideos |
| 22 | People & Blogs | Vlogs |
| 24 | Entertainment | Misc |
| 25 | News & Politics | Wochenschau, Doku |
| 27 | Education | Lehr-Content |

---

## 📰 HISTORISCHES MATERIAL

### Wochenschau-Standard
- ✅ Trilingual: DE/EN/ES
- ✅ Disclaimer: `⚠️ Historisches Archivmaterial`
- ✅ Category: `27` (Education) — NICHT News & Politics!
- ✅ Template: [docs/templates/WOCHENSCHAU_SEO_TEMPLATE.md](docs/templates/WOCHENSCHAU_SEO_TEMPLATE.md)

---

## 🛠️ SCRIPTS & TOOLS

### Channel-Analyse
| Script | Funktion |
|--------|----------|
| `fresh_channel_scan.py` | Kompletter Channel-Scan inkl. Drafts |
| `analyze_soundies.py` | Soundies SEO-Analyse |
| `analyze_playlist_assignments.py` | Playlist-Zuordnungen |

### SEO-Fixes
| Script | Funktion |
|--------|----------|
| `fix_soundies_category.py` | Category → Music |
| `fix_wochenschau_drafts.py` | Wochenschau Titel-Fix |
| `live_seo_optimizer.py` | Live SEO-Optimierung |

### Playlist-Management
| Script | Funktion |
|--------|----------|
| `create_wochenschau_playlist.py` | Playlist erstellen + Videos hinzufügen |
| `watchtime_playlist_updater_v3.py` | Watchtime-Optimierung |

---

## 💰 MONETARISIERUNGS-CHECKLISTE

### YouTube Partner Program
- [ ] 1.000 Subscriber
- [ ] 4.000 Watch Hours (12 Monate)
- [ ] Oder: 10 Mio Shorts Views (90 Tage)

### Optimierung für Revenue
1. **Längere Videos** (8+ Min) = Mehr Mid-Roll Ads
2. **Music Category** = YouTube Music Discovery
3. **Playlists** = Binge-Watching → Watch Time
4. **SEO** = Organic Discovery

### Content-Strategie
- 🎯 **High-Value**: Soundies (Music), Betty Boop (Nostalgie)
- 📈 **Wachstum**: BraveStarr, Alfred J. Kwak (Serien)
- 🌍 **International**: EN/ES Beschreibungen

---

## 📊 API QUOTA REGELN

```
┌─────────────────────────────────────────────────────┐
│  🔑 PUBLIC API FIRST! OAUTH NUR FÜR WRITE!          │
├─────────────────────────────────────────────────────┤
│  READ: Public API mit API_KEY                       │
│  WRITE: OAuth Token                                 │
│  DELETE: MANUELL IM STUDIO (0 Quota!)               │
│  Quota Reset: 08:00 UTC (09:00 MEZ)                 │
└─────────────────────────────────────────────────────┘
```

### Quota-Kosten
| Operation | Units |
|-----------|-------|
| videos.list | 1 |
| videos.update | 50 |
| playlistItems.insert | 50 |
| search.list | 100 ⚠️ |

---

## 📁 CONFIG-DATEIEN

| Datei | Inhalt |
|-------|--------|
| `config/youtube_oauth.json` | OAuth Credentials |
| `config/fresh_channel_scan.json` | Aktueller Channel-Stand |
| `config/playlist_master_schema.json` | Playlist-Definitionen |
| `config/playlist_assignments.json` | Video → Playlist Mapping |
| `config/wochenschau_playlist_final.json` | Wochenschau-Playlist |

---

## 🔗 WICHTIGE LINKS

- **YouTube Studio**: https://studio.youtube.com/channel/UCVFv6Egpl0LDvigpFbQXNeQ
- **FRai.TV**: https://www.frai.tv
- **remAIke.IT**: https://www.remaike.it

---

## 📚 WEITERE DOKUMENTATION

- [MANA_RULES.md](../MANA_RULES.md) - Copilot-Regeln
- [copilot-instructions.md](../.github/copilot-instructions.md) - API-Regeln
- [YOUTUBE_KNOWLEDGE_BASE.md](YOUTUBE_KNOWLEDGE_BASE.md) - Detailliertes YT-Wissen
- [YOUTUBE_ALGO_2026_PLAYBOOK.md](YOUTUBE_ALGO_2026_PLAYBOOK.md) - Algorithmus-Guide

---

*Maintained by Copilot • Last scan: 2026-01-14*
