# 🎰 Jukebox Roulette - Technical Specification

> **Version:** 1.0 | **Erstellt:** 2026-01-15 | **Status:** IN DESIGN
> 
> Das Killer-Feature für FRai.TV: Retro-Jukebox trifft Casino-Roulette

---

## 🎯 Vision

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   ╔═══════════════════════════════════════════════════════════════════╗   │
│   ║                    🎰 JUKEBOX ROULETTE                             ║   │
│   ╠═══════════════════════════════════════════════════════════════════╣   │
│   ║                                                                    ║   │
│   ║      ┌─────────────────────────────────────────────────┐          ║   │
│   ║      │                                                 │          ║   │
│   ║      │              [JUKEBOX DISPLAY]                  │          ║   │
│   ║      │                                                 │          ║   │
│   ║      │     ╭──────────────────────────────────╮       │          ║   │
│   ║      │     │                                  │       │          ║   │
│   ║      │     │   🎬 VIDEO THUMBNAIL SLOT        │       │          ║   │
│   ║      │     │                                  │       │          ║   │
│   ║      │     │   [Spinning Animation]           │       │          ║   │
│   ║      │     │                                  │       │          ║   │
│   ║      │     ╰──────────────────────────────────╯       │          ║   │
│   ║      │                                                 │          ║   │
│   ║      │     "Betty Boop: Minnie the Moocher"           │          ║   │
│   ║      │              (1932) | 8K HQ                     │          ║   │
│   ║      │                                                 │          ║   │
│   ║      └─────────────────────────────────────────────────┘          ║   │
│   ║                                                                    ║   │
│   ║      ╭────────────────────────────────────────────────╮           ║   │
│   ║      │                                                │           ║   │
│   ║      │              🎡 ROULETTE WHEEL                 │           ║   │
│   ║      │                                                │           ║   │
│   ║      │         ┌───┐  ┌───┐  ┌───┐  ┌───┐            │           ║   │
│   ║      │         │ 🎭│  │ 🦸│  │ 🐱│  │ 🎵│            │           ║   │
│   ║      │         └───┘  └───┘  └───┘  └───┘            │           ║   │
│   ║      │    Betty  Super- Felix  Soun-                  │           ║   │
│   ║      │    Boop   man    Cat    dies                   │           ║   │
│   ║      │                                                │           ║   │
│   ║      │              [    ▲ POINTER    ]               │           ║   │
│   ║      ╰────────────────────────────────────────────────╯           ║   │
│   ║                                                                    ║   │
│   ║              ╔═══════════════════════════╗                        ║   │
│   ║              ║     🎲 SPIN! 🎲            ║                        ║   │
│   ║              ╚═══════════════════════════╝                        ║   │
│   ║                                                                    ║   │
│   ║   [Quick] [Era 🕰️] [Genre 🎬] [Mood 😊] [Golden Mix ⭐]           ║   │
│   ║                                                                    ║   │
│   ╚════════════════════════════════════════════════════════════════════╝   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎮 Core Mechanics

### 1. Spin Modes

| Mode | Icon | Beschreibung | Filter |
|------|------|--------------|--------|
| **Quick Spin** | 🎲 | 1 Random Video sofort | Alle Videos |
| **Era Spin** | 🕰️ | Wähle Jahrzehnt | `1920s`, `1930s`, `1940s`, etc. |
| **Genre Spin** | 🎬 | Wähle Kategorie | Betty Boop, Superman, Soundies, etc. |
| **Mood Spin** | 😊 | Wähle Stimmung | Funny, Adventure, Musical, Spooky |
| **Golden Mix** | ⭐ | Watchtime-optimiert | Top 50 + Ungesehene |

### 2. Spin Animation Sequence

```
1. USER CLICKS SPIN
   ↓
2. WHEEL STARTS SPINNING (ease-in, accelerate)
   → Sound: "vinyl spin up" whoosh
   ↓
3. THUMBNAILS BLUR-SCROLL (slot machine effect)
   → 20-40 thumbnails fly by vertically
   ↓
4. WHEEL DECELERATES (physics: friction + bounce)
   → Sound: "click click click" ticks
   ↓
5. WHEEL STOPS (pointer lands on segment)
   → Sound: "ding!" bell
   ↓
6. THUMBNAIL LOCKS (zoom-in + glow)
   → Sound: "record drop" vinyl thunk
   ↓
7. AUTO-PLAY COUNTDOWN (3...2...1...)
   → Or click "Play Now" / "Spin Again"
```

### 3. Roulette Wheel Design

```
         🎭 Betty Boop
           ╱     ╲
      🦸 Superman   🐱 Felix
         │           │
    🎵 Soundies ───┼─── 🎄 Christmas
         │           │
      📰 Wochenschau  🐤 Alfred J. Kwak
           ╲     ╱
         🎬 Looney Tunes
              │
            ▼ POINTER
```

**Segment Properties:**
- Segment-Größe = proportional zur Video-Anzahl
- Farbe = Kategorie-Farbe (aus bestehendem Design)
- Icon = Kategorie-Icon
- Glow-Effekt bei Hover

---

## 🛠️ Technical Implementation

### Component Structure

```
src/components/jukebox/
├── JukeboxRoulette.jsx        # Main container
├── RouletteWheel.jsx          # Spinning wheel with segments
├── VideoSlot.jsx              # Thumbnail slot machine
├── SpinButton.jsx             # Big SPIN button
├── ModeSelector.jsx           # Quick/Era/Genre/Mood/Golden
├── SpinResult.jsx             # Result display + actions
├── QueuePanel.jsx             # Upcoming videos queue
└── hooks/
    ├── useSpinPhysics.js      # Wheel physics (velocity, friction)
    ├── useVideoSelector.js    # Random selection logic
    └── useSoundEffects.js     # Audio feedback
```

### State Model

```javascript
const jukeboxState = {
  // Current mode
  mode: 'quick' | 'era' | 'genre' | 'mood' | 'golden',
  
  // Mode filters
  selectedEra: '1930s' | null,
  selectedGenre: 'betty-boop' | null,
  selectedMood: 'funny' | null,
  
  // Spin state
  isSpinning: false,
  spinVelocity: 0,
  wheelRotation: 0,  // degrees
  
  // Result
  selectedVideo: null,
  selectionHistory: [],
  
  // Queue
  queue: [],
  autoplayEnabled: true,
  
  // Audio
  soundEnabled: true,
  volume: 0.7
};
```

### Spin Algorithm

```javascript
// useVideoSelector.js
function selectVideo(videos, mode, filters, history) {
  // 1. Apply mode filter
  let pool = filterByMode(videos, mode, filters);
  
  // 2. Exclude recently played (last 10)
  pool = pool.filter(v => !history.slice(-10).includes(v.id));
  
  // 3. Weight by "freshness" (prefer unwatched)
  const weighted = pool.map(v => ({
    video: v,
    weight: v.watched ? 1 : 3  // 3x more likely if unwatched
  }));
  
  // 4. Random weighted selection
  return weightedRandom(weighted);
}

// Wheel physics
function useSpinPhysics() {
  const [rotation, setRotation] = useState(0);
  const [velocity, setVelocity] = useState(0);
  
  const spin = () => {
    const initialVelocity = 800 + Math.random() * 400; // 800-1200 deg/s
    setVelocity(initialVelocity);
  };
  
  useFrame((delta) => {
    if (velocity > 0) {
      setRotation(r => r + velocity * delta);
      setVelocity(v => Math.max(0, v - FRICTION * delta));
      
      // Click sound at segment boundaries
      if (crossedSegmentBoundary(rotation)) {
        playTickSound();
      }
    }
  });
  
  return { rotation, velocity, spin, isSpinning: velocity > 0 };
}
```

### CSS Animations

```css
/* Wheel spin */
.roulette-wheel {
  transition: transform 0.1s linear;
}

.roulette-wheel.spinning {
  animation: none; /* Controlled by JS physics */
}

/* Slot machine thumbnails */
.video-slot-reel {
  display: flex;
  flex-direction: column;
  animation: slot-spin 0.1s steps(1) infinite;
}

@keyframes slot-spin {
  0% { transform: translateY(0); }
  100% { transform: translateY(-100px); }
}

/* Result lock-in */
.video-locked {
  animation: lock-in 0.5s ease-out;
}

@keyframes lock-in {
  0% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); opacity: 1; }
}

/* Glow effect */
.segment-active {
  filter: drop-shadow(0 0 20px var(--category-color));
}
```

### Sound Design

| Event | Sound | File |
|-------|-------|------|
| Spin Start | Vinyl whoosh | `spin-start.mp3` |
| Wheel Tick | Soft click | `tick.mp3` |
| Wheel Stop | Bell ding | `ding.mp3` |
| Video Lock | Record drop | `vinyl-drop.mp3` |
| Queue Add | Soft pop | `pop.mp3` |

---

## 📱 Mobile UX

### Touch Gestures

```
┌─────────────────────────────┐
│                             │
│   SWIPE UP on wheel         │ → Spin!
│                             │
│   TAP segment               │ → Select category
│                             │
│   LONG PRESS video          │ → Add to queue
│                             │
│   SWIPE LEFT on result      │ → Spin again
│                             │
│   SWIPE RIGHT on result     │ → Play now
│                             │
└─────────────────────────────┘
```

### Responsive Layout

```
DESKTOP (>1024px)           TABLET (768-1024px)         MOBILE (<768px)
┌──────────────────┐        ┌──────────────────┐        ┌──────────────┐
│ [Jukebox] [Wheel]│        │    [Jukebox]     │        │  [Jukebox]   │
│                  │        │    [Wheel]       │        │              │
│    [Modes]       │        │    [Modes]       │        │  [Wheel]     │
│                  │        │    [SPIN]        │        │              │
│    [Queue]       │        │    [Queue]       │        │  [Modes]     │
│                  │        │                  │        │  [SPIN]      │
└──────────────────┘        └──────────────────┘        └──────────────┘
```

---

## 🎨 Visual Design

### Color Palette (from existing categories)

```javascript
const CATEGORY_COLORS = {
  'betty-boop': '#FF69B4',      // Hot Pink
  'superman': '#0066CC',         // Superman Blue
  'felix-cat': '#FFD700',        // Gold
  'soundies': '#9932CC',         // Purple
  'alfred-kwak': '#32CD32',      // Lime Green
  'looney-tunes': '#FF4500',     // Orange Red
  'christmas': '#228B22',        // Forest Green
  'wochenschau': '#708090',      // Slate Gray
  'bravestarr': '#8B4513',       // Saddle Brown
};
```

### Jukebox Style

```
RETRO DINER AESTHETIC:
- Chrome/metallic accents
- Neon glow effects
- Art Deco curves
- Warm amber lighting
- Vinyl record textures
```

---

## 📋 Implementation Phases

### Phase 1: Core Spin (8h)
- [ ] `JukeboxRoulette.jsx` container
- [ ] `RouletteWheel.jsx` with segments
- [ ] Basic spin physics
- [ ] Random video selection
- [ ] Quick Spin mode

### Phase 2: Slot Animation (6h)
- [ ] `VideoSlot.jsx` slot machine
- [ ] Thumbnail blur-scroll effect
- [ ] Lock-in animation
- [ ] Result display

### Phase 3: Modes (4h)
- [ ] `ModeSelector.jsx`
- [ ] Era filter (decade picker)
- [ ] Genre filter (category picker)
- [ ] Mode-specific selection logic

### Phase 4: Polish (6h)
- [ ] Sound effects
- [ ] Mobile touch gestures
- [ ] Queue system
- [ ] Golden Mix algorithm

### Phase 5: Integration (4h)
- [ ] Homepage widget
- [ ] Nav link
- [ ] Analytics tracking
- [ ] A11y audit

---

## 🔗 Integration Points

### Homepage

```jsx
// pages/HomePage.jsx
<HeroBillboard />
<JukeboxRouletteWidget mode="compact" />  // Mini version
<ContentRow category="continue-watching" />
<ContentRow category="betty-boop" />
```

### Navigation

```jsx
// Neuer Nav-Link
<NavLink to="/roulette" icon="🎰">
  Jukebox Roulette
</NavLink>
```

### Dedicated Page

```jsx
// pages/RoulettePage.jsx
<JukeboxRoulette fullscreen />
```

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Spin-to-Play Rate | > 70% |
| Avg. Spins per Session | > 3 |
| Queue Usage | > 30% of users |
| Mobile Spin Rate | Same as desktop |
| Time on Roulette Page | > 2 min |

---

## 🚀 Go-Live Checklist

- [ ] All modes functional
- [ ] Mobile responsive
- [ ] Sound effects optional (mute button)
- [ ] Keyboard accessible (Space = Spin)
- [ ] Screen reader announces results
- [ ] Analytics events tracking
- [ ] Performance < 100ms spin start
- [ ] Works offline (PWA)

---

*Spec Version 1.0 | 2026-01-15 | FRai.TV Jukebox Roulette*
