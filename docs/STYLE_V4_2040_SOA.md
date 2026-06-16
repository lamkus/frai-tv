# STYLE_V4_2040_SOA.md

> **SOA = “State Of the Art” (2040)** for remAIke.TV UI/UX + platform engineering.
> Secondary meaning (engineering): **service-oriented boundaries** inside the app (clear modules, stable interfaces).

## North Star
A “cinematic library” that behaves like a native media app:
- Fast, interruption-free playback
- Predictable updates (no cache surprises)
- Device-native controls (media keys, lock screen, casting later)
- Measurable performance and reliability

## Pillars (2040)

### 1) Native Media Controls
- Media Session metadata and action handlers
- Playback position state where supported
- Clean pause/play semantics across YouTube/embed/self-hosted modes

### 2) Predictable Updates (Cache Discipline)
- Every deploy must invalidate the right caches deterministically
- Service worker versioning is explicit and testable
- No “ghost bugs” from stale assets

### 3) Performance Budgets (Real Targets)
- Reduce main-thread churn (polling, re-renders, layout thrash)
- Prefer event-driven updates over tight timers where possible
- Establish budgets (examples):
  - Input responsiveness: avoid long tasks > 200ms during playback UI
  - Re-render frequency: only when state actually changes

### 4) Observability by Default
- Clear, low-noise logs around playback lifecycle and failures
- Simple breadcrumbs for: open → play → pause → seek → end → close
- Track “page unresponsive” risk factors (CPU-heavy loops, intervals)

### 5) Progressive Enhancement (No Hard Dependencies)
- Modern APIs must fail safe:
  - View Transitions: opt-in and reduced-motion aware
  - Media Session: feature detection + graceful fallback
  - Position state: optional

### 6) Accessibility + Resilience
- Keyboard-first flows always work (including the player)
- Reduced-motion respected
- Avoid critical UI that depends only on animation/gesture

## Executable Roadmap

### Now (v4.0 baseline)
- Media Session in the player (metadata + play/pause/seek handlers)
- PlaybackState + position state updates
- Document + track cache-busting policy

### Next (v4.x)
- Hardening: service worker update UX (ensure users actually receive new builds)
- Player event-driven progress updates where possible (reduce polling further)
- E2E coverage around player open/close and basic controls

### Later (v5)
- Casting/remote playback (only if product wants it)
- Optional GPU “art layer” (strictly decorative; never blocks playback)

## “Definition of Done” (SOA)
A feature is “2040-ready” when:
- It improves UX without breaking older browsers
- It’s measurable (perf/reliability impact is visible)
- It has safe fallbacks and respects reduced-motion
- It does not add cache ambiguity
