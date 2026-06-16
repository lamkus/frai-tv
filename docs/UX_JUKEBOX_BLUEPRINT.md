# FRai.TV — High‑End UX Blueprint (Jukebox Roulette + Netflix‑Grade)

**Goal:** Premium streaming feel with “Jukebox Roulette” as signature interaction.

---

## 1) Above‑the‑Fold Layout (Hero + Jukebox)

```
┌─────────────────────────────────────────────────────────────────┐
│ HERO (70%)                               JUKEBOX (30%)          │
│ ┌───────────────┐  Title + CTA + Preview  ┌───────────────────┐  │
│ │ Poster/Loop   │  • Play Now             │ Jukebox Roulette  │  │
│ │ 8–12s clip    │  • Add to List          │ [Spin Now]        │  │
│ └───────────────┘  • Series/Episode info  │ Mode: Quick/Gold  │  │
│                    • Meta (Year, 8K)      │ Filter: Era/Mood  │  │
│                                            [Spin Again]       │  │
└─────────────────────────────────────────────────────────────────┘
```

**Hero content priorities**
1. Title (big)
2. CTA “Play Now”
3. Jukebox Spin
4. Series/Episode meta
5. Description (1–2 lines)

---

## 2) Mid‑Page Rails (Content Rows)
- **Continue Watching**
- **Jukebox Picks (Today)**
- **New in Library**
- **Series Spotlight** (Alfred / Betty / Soundies)
- **Hidden Gems**

**Rail behavior:** hover preview, quick add to list, keyboard‑nav focus ring.

---

## 3) Sticky Player (Bottom)
- “Now Playing” + title + thumbnail
- Play/Pause, Skip, Spin Next
- Minimal footprint, fades in/out with playback.

---

## 4) Design Tokens (High‑End Visual)

**Colors**
- Background: `#0A0A0A`
- Panels: `#1A1A1A`
- Accent: `#C9A962`
- Muted Text: `#7A7A7A`
- Primary Text: `#EDEDED`

**Typography**
- Display: Bebas Neue
- UI: Inter

**Motion**
- Hover glow: 120–180ms
- Panel transitions: 240–300ms
- Jukebox spin: 600–900ms (ease‑out)

---

## 5) Jukebox Roulette — Logic Rules

**Quick‑Spin**
- Random pick from full catalog
- Exclude last 5 played

**Golden Mix**
- 40% Top performers
- 40% New uploads
- 20% Hidden gems

**Era / Mood Filters**
- Era limits pool (e.g., 1930s/40s/50s)
- Mood limits pool (Comedy / Noir / Music / Newsreel)

**No‑Repeat Guard**
- 20‑video cooldown per device

---

## 6) UX Copy (Micro‑Text)
- Spin CTA: **“Spin Now”**
- Secondary: **“Spin Again”**
- Quick mode: **“Quick‑Spin”**
- Golden: **“Golden Mix”**
- Empty rail: **“No picks yet — spin the Jukebox!”**

---

## 7) Component List (Implementation Map)
- `HeroSpotlight`
- `JukeboxPanel`
- `JukeboxSpinButton`
- `RailRow`
- `RailCard`
- `StickyPlayer`
- `FilterPills` (Era / Mood)
- `MiniBadge` (8K, Year)

---

## 8) Phased Rollout

**Phase 1 (1–2 weeks)**
- Hero + Jukebox Quick‑Spin
- 4 main rails
- Sticky Player

**Phase 2**
- Golden Mix
- Era/Mood filters
- Smart previews

**Phase 3**
- Personalized mix (watch history)
- Adaptive hero based on last session

---

## 9) Success Metrics
- Jukebox Spin → Play conversion > 35%
- Avg session duration +30%
- Repeat visits +20% over 30 days

---

If you want, I can translate this into a concrete UI task list and component tickets.
