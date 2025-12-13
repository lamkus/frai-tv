/**
 * frai.tv - TV Remote Navigation Hook
 *
 * Ermöglicht Navigation mit TV-Fernbedienung:
 * - Pfeiltasten: Navigation zwischen fokussierbaren Elementen
 * - Enter/OK: Aktivieren des fokussierten Elements
 * - Back/Escape: Zurück-Navigation
 *
 * Kompatibel mit:
 * - Android TV
 * - Fire TV
 * - Samsung Tizen
 * - LG webOS
 * - Standard-Tastaturen
 */

import { useEffect, useCallback, useRef } from 'react';

// TV Remote Key Codes (variieren je nach Plattform)
const TV_KEYS = {
  // Standard Arrow Keys
  ArrowUp: 'up',
  ArrowDown: 'down',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  Enter: 'select',
  ' ': 'select', // Space
  Escape: 'back',
  Backspace: 'back',

  // Samsung Tizen
  10009: 'back', // Return
  10252: 'select', // PlayPause

  // LG webOS
  461: 'back', // Back

  // Android TV (zusätzlich zu Standard)
  66: 'select', // Enter
  23: 'select', // DPAD_CENTER
};

/**
 * Findet alle fokussierbaren Elemente im Container
 */
function getFocusableElements(container = document) {
  const focusableSelectors = [
    'a[href]:not([disabled]):not([tabindex="-1"])',
    'button:not([disabled]):not([tabindex="-1"])',
    'input:not([disabled]):not([tabindex="-1"])',
    'select:not([disabled]):not([tabindex="-1"])',
    'textarea:not([disabled]):not([tabindex="-1"])',
    '[tabindex]:not([tabindex="-1"]):not([disabled])',
    '[role="button"]:not([disabled]):not([tabindex="-1"])',
    '[role="link"]:not([disabled]):not([tabindex="-1"])',
    '[data-focusable="true"]',
  ];

  return Array.from(container.querySelectorAll(focusableSelectors.join(','))).filter((el) => {
    // Nur sichtbare Elemente
    const style = window.getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null;
  });
}

/**
 * Berechnet die nächste fokussierbare Position basierend auf Richtung
 */
function getNextFocusElement(currentElement, direction, container = document) {
  const elements = getFocusableElements(container);
  if (elements.length === 0) return null;

  const currentIndex = elements.indexOf(currentElement);
  const currentRect = currentElement?.getBoundingClientRect();

  if (!currentRect || currentIndex === -1) {
    // Kein aktuelles Element - erstes/letztes auswählen
    if (direction === 'down' || direction === 'right') {
      return elements[0];
    }
    return elements[elements.length - 1];
  }

  // Für horizontale Navigation (Tabs, Kategorien)
  if (direction === 'left' || direction === 'right') {
    // Elemente auf gleicher Y-Position filtern (gleiche Zeile)
    const sameRowElements = elements.filter((el) => {
      const rect = el.getBoundingClientRect();
      return Math.abs(rect.top - currentRect.top) < 50;
    });

    const rowIndex = sameRowElements.indexOf(currentElement);
    if (direction === 'right' && rowIndex < sameRowElements.length - 1) {
      return sameRowElements[rowIndex + 1];
    }
    if (direction === 'left' && rowIndex > 0) {
      return sameRowElements[rowIndex - 1];
    }
  }

  // Für vertikale Navigation
  if (direction === 'up' || direction === 'down') {
    // Elemente sortieren nach Y-Position
    const sorted = [...elements].sort((a, b) => {
      const rectA = a.getBoundingClientRect();
      const rectB = b.getBoundingClientRect();
      return rectA.top - rectB.top;
    });

    const sortedIndex = sorted.indexOf(currentElement);

    if (direction === 'down') {
      // Nächstes Element in nächster Zeile finden
      for (let i = sortedIndex + 1; i < sorted.length; i++) {
        const rect = sorted[i].getBoundingClientRect();
        if (rect.top > currentRect.bottom - 10) {
          // Nächste Zeile - Element mit ähnlicher X-Position bevorzugen
          const candidates = sorted.filter((el, idx) => {
            const r = el.getBoundingClientRect();
            return idx > sortedIndex && Math.abs(r.top - rect.top) < 30;
          });

          if (candidates.length > 0) {
            // Finde das Element mit der ähnlichsten X-Position
            return candidates.reduce((best, el) => {
              const bestRect = best.getBoundingClientRect();
              const elRect = el.getBoundingClientRect();
              const bestDist = Math.abs(bestRect.left - currentRect.left);
              const elDist = Math.abs(elRect.left - currentRect.left);
              return elDist < bestDist ? el : best;
            });
          }
          return sorted[i];
        }
      }
    }

    if (direction === 'up') {
      for (let i = sortedIndex - 1; i >= 0; i--) {
        const rect = sorted[i].getBoundingClientRect();
        if (rect.bottom < currentRect.top + 10) {
          // Vorherige Zeile
          const candidates = sorted.filter((el, idx) => {
            const r = el.getBoundingClientRect();
            return idx < sortedIndex && Math.abs(r.bottom - rect.bottom) < 30;
          });

          if (candidates.length > 0) {
            return candidates.reduce((best, el) => {
              const bestRect = best.getBoundingClientRect();
              const elRect = el.getBoundingClientRect();
              const bestDist = Math.abs(bestRect.left - currentRect.left);
              const elDist = Math.abs(elRect.left - currentRect.left);
              return elDist < bestDist ? el : best;
            });
          }
          return sorted[i];
        }
      }
    }
  }

  // Fallback: Einfache Index-Navigation
  if (direction === 'down' || direction === 'right') {
    return elements[(currentIndex + 1) % elements.length];
  }
  if (direction === 'up' || direction === 'left') {
    return elements[(currentIndex - 1 + elements.length) % elements.length];
  }

  return null;
}

/**
 * TV Navigation Hook
 *
 * @param {Object} options
 * @param {Function} options.onBack - Callback für Back-Taste
 * @param {HTMLElement} options.containerRef - Container für Navigation
 * @param {boolean} options.enabled - Navigation aktiviert
 */
export function useTVNavigation({ onBack, containerRef, enabled = true } = {}) {
  const lastFocusedRef = useRef(null);

  // Focus-Ring-Style für TV
  useEffect(() => {
    if (!enabled) return;

    // CSS für TV-Fokus-Ring hinzufügen
    const style = document.createElement('style');
    style.id = 'tv-navigation-styles';
    style.textContent = `
      /* TV Navigation Focus Styles */
      *:focus {
        outline: none !important;
      }
      
      *:focus-visible,
      [data-tv-focused="true"] {
        outline: 3px solid #f59e0b !important;
        outline-offset: 4px !important;
        box-shadow: 0 0 0 6px rgba(245, 158, 11, 0.3) !important;
        transition: outline 0.15s ease, box-shadow 0.15s ease !important;
      }
      
      /* Scroll-Verhalten für fokussierte Elemente */
      *:focus-visible {
        scroll-margin: 100px;
      }
      
      /* Größere Klickflächen für TV */
      @media (min-width: 1280px) {
        button, a, [role="button"] {
          min-height: 48px;
          min-width: 48px;
        }
      }
    `;

    if (!document.getElementById('tv-navigation-styles')) {
      document.head.appendChild(style);
    }

    return () => {
      style.remove();
    };
  }, [enabled]);

  // Key Handler
  const handleKeyDown = useCallback(
    (event) => {
      if (!enabled) return;

      // Key-Code normalisieren
      const key = event.key || event.keyCode;
      const action = TV_KEYS[key];

      if (!action) return;

      event.preventDefault();

      const container = containerRef?.current || document;
      const currentElement = document.activeElement;

      switch (action) {
        case 'up':
        case 'down':
        case 'left':
        case 'right': {
          const nextElement = getNextFocusElement(currentElement, action, container);
          if (nextElement) {
            nextElement.focus({ preventScroll: false });
            nextElement.scrollIntoView({
              behavior: 'smooth',
              block: 'nearest',
              inline: 'nearest',
            });
            lastFocusedRef.current = nextElement;
          }
          break;
        }

        case 'select': {
          // Element aktivieren
          if (currentElement && currentElement !== document.body) {
            currentElement.click();
          }
          break;
        }

        case 'back': {
          if (onBack) {
            onBack();
          } else {
            // Standard: History back
            window.history.back();
          }
          break;
        }

        default:
          break;
      }
    },
    [enabled, onBack, containerRef]
  );

  // Event Listener registrieren
  useEffect(() => {
    if (!enabled) return;

    window.addEventListener('keydown', handleKeyDown);

    // Initial-Fokus setzen wenn kein Element fokussiert
    const initFocus = () => {
      if (!document.activeElement || document.activeElement === document.body) {
        const container = containerRef?.current || document;
        const firstFocusable = getFocusableElements(container)[0];
        if (firstFocusable) {
          firstFocusable.focus();
        }
      }
    };

    // Verzögert, damit DOM geladen ist
    const timer = setTimeout(initFocus, 100);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      clearTimeout(timer);
    };
  }, [enabled, handleKeyDown, containerRef]);

  // Utility-Funktionen exponieren
  return {
    focusFirst: () => {
      const container = containerRef?.current || document;
      const first = getFocusableElements(container)[0];
      if (first) first.focus();
    },
    focusLast: () => {
      const container = containerRef?.current || document;
      const elements = getFocusableElements(container);
      const last = elements[elements.length - 1];
      if (last) last.focus();
    },
    restoreFocus: () => {
      if (lastFocusedRef.current) {
        lastFocusedRef.current.focus();
      }
    },
  };
}

/**
 * HOC für fokussierbare Komponenten auf TV
 */
export function withTVFocus(Component) {
  return function TVFocusableComponent(props) {
    return <Component {...props} tabIndex={props.tabIndex ?? 0} data-focusable="true" />;
  };
}

export default useTVNavigation;
