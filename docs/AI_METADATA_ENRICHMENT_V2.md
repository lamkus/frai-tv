# AI-Metadata Enrichment v2 – Design Document

**ID:** CDARCH-20260103-002
**Status:** DESIGN
**Priority:** P1

## 1. Problemstellung
Die aktuelle Metadaten-Anreicherung (v1) basiert primär auf Heuristiken und einfachen Regex-Patterns. Die KI-Integration ist vorhanden, aber nicht standardmäßig aktiv und liefert nur grundlegende Kategorien. Für eine "High-End Mediathek" (Joyn/Netflix-Niveau) fehlen tiefergehende Informationen wie Besetzung, Regie, Altersfreigabe und eine konsistente Mehrsprachigkeit.

## 2. Ziele (v2)
- **Tiefen-Metadaten**: Extraktion von Regisseur, Cast, Genre, Farbe/SW-Status.
- **Mehrsprachigkeit (i18n)**: Automatische Generierung von Titeln und Beschreibungen in DE, EN, FR.
- **SEO-Optimierung**: Generierung von Meta-Titeln und Beschreibungen für die Plattform.
- **Content Rating**: Zuweisung von FSK-Einstufungen basierend auf Inhaltsanalyse.
- **Kosteneffizienz**: Nutzung der OpenAI Batch API (50% Ersparnis) für Massen-Updates.
- **Vision-Support**: Analyse von Thumbnails (GPT-4o-vision) zur Verifizierung von Stummfilm-Status oder Qualität.

## 3. Datenstruktur (Schema v2)

```json
{
  "id": "ytId",
  "metadata": {
    "director": "String",
    "cast": ["String"],
    "genres": ["String"],
    "color": "B&W | Color",
    "rating": "FSK 0 | FSK 6 | FSK 12 | FSK 16",
    "imdbId": "String (optional)",
    "originalLanguage": "String"
  },
  "i18n": {
    "de": { "title": "String", "description": "String" },
    "en": { "title": "String", "description": "String" },
    "fr": { "title": "String", "description": "String" }
  },
  "seo": {
    "metaTitle": "String",
    "metaDescription": "String",
    "keywords": ["String"]
  }
}
```

## 4. Implementierungsplan

### Phase 1: Prompt Engineering & Schema-Validierung
- Entwicklung eines komplexen System-Prompts für GPT-4o.
- Integration von `zod` zur Validierung der KI-Antworten.

### Phase 2: Batch Processing Script
- Neues Script `scripts/ai-enrichment-v2.mjs`.
- Unterstützung für den OpenAI Batch-Modus (Upload .jsonl -> Download Results).

### Phase 3: Frontend Integration
- Anpassung der `VideoDetailPage.jsx` zur Anzeige der neuen Metadaten (Cast, Director).
- Integration der i18n-Daten in den `useApp` Context.

### Phase 4: Vision Integration (Optional/P2)
- Thumbnail-Analyse zur Erkennung von Text-Overlays oder spezifischen Stilen.

## 5. Debatte: Kosten vs. Nutzen
**Lead Architect (15):** Batch API ist ein Muss für Skalierbarkeit.
**Product Management (3):** Mehrsprachigkeit erhöht die Reichweite massiv.
**SEO (4):** Eigene Meta-Tags pro Video verbessern das Ranking gegenüber YouTube-Embeds.

**Ergebnis:** Fokus auf Batch-Processing und i18n. Vision-Support wird als P2 eingestuft.
