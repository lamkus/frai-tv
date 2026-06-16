# remAIke.TV – V3.0 / “2030 Style” (Level 3) Guide

This document distills current design-system and web-platform directions into a practical v3.0 style target for remAIke.TV.

Sources used for grounding:
- Material 3 (M3 Expressive): emotion-driven UX, adaptive components, color/motion/typography/shape systems.
- Fluent 2: cohesive modern component language; productivity-friendly UI patterns.
- Apple HIG: hierarchy, harmony, and consistency; “materials” as a mental model.
- MDN + web.dev: View Transitions API, Media Session API, PWA/offline service worker patterns.

## V3.0 North Star
A “cinematic library” experience that feels like a native media app:
- Content-first, minimal chrome, strong hierarchy.
- Seamless state changes (reduced cognitive load).
- Reliable, predictable behavior (no mystery caches).
- Progressive enhancement: advanced visuals never block playback.

## Visual Language (2030 look)
### 1) Hierarchy
- Make content the hero; controls elevate above content (clear layers).
- Prefer fewer, stronger surfaces over many thin outlines.

### 2) Materials
- Think “layers” (base canvas → content surface → elevated controls).
- Use translucency/backdrop blur only where it improves comprehension.

### 3) Typography
- Large, confident headlines; calm metadata.
- Prefer stable line lengths and consistent truncation for titles.

### 4) Color + Contrast
- Use color for meaning (focus/selection/active playback), not decoration.
- Always preserve readability (especially on artwork thumbnails).

### 5) Motion
- Motion is functional: orientation + continuity.
- Respect `prefers-reduced-motion` and keep transitions interruptible.

## Interaction Language (2030 feel)
### 1) “Scenes”, not pages
- Treat navigation changes as “scene transitions”.
- Use native View Transitions when available; fallback must be instant.

### 2) Media as a first-class OS citizen
- Use Media Session:
  - Lock-screen/media-center metadata (title/artwork)
  - Hardware media key handlers (play/pause/seek)

### 3) Remote/TV readiness
- Visible focus states, consistent tab order.
- No hover-only critical affordances.

## Performance & Reliability (mandatory for ‘future’)
### 1) Main-thread budget
- Avoid high-frequency state updates that re-render large trees.
- Prefer “update only on change” polling; suspend work in background tabs.

### 2) Progressive enhancement
- If a feature uses GPU-heavy work (e.g., WebGPU ambience):
  - feature-detect
  - disable on `prefers-reduced-motion`, `save-data`, low-power contexts
  - never block player

### 3) Caching is explicit
- Service worker caches must be versioned.
- Data caching should be deliberate and easy to invalidate.

## V3.0 Implementation Roadmap (minimal scope, maximum impact)
1) Seamless navigation
- View Transitions on key “card → detail/player” paths.

2) Player becomes device-native
- Media Session metadata/action handlers.

3) Reliability polish
- Reduce unnecessary polling and re-render churn.
- Ensure SW update path doesn’t trap users on stale bundles.

## Definition of Done (v3.0)
- Transitions feel smooth and never trap focus.
- Player shows correct lock-screen metadata and responds to media keys.
- No common flows trigger long tasks / ‘page unresponsive’ dialogs.
- Offline/online behavior is predictable and testable.
