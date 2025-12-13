import { useState, useEffect } from 'react';
import { Cookie, Shield, ExternalLink, BarChart3 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { setAnalyticsConsent } from '../../lib/analytics';

/**
 * CookieConsent - DSGVO-compliant cookie consent banner
 *
 * Required before loading YouTube embeds!
 * Stores consent in localStorage.
 * Integrates with Analytics system for tracking consent.
 */
export default function CookieConsent() {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [analyticsEnabled, setAnalyticsEnabled] = useState(true);

  useEffect(() => {
    // Check if consent was already given
    const consent = localStorage.getItem('remaike_cookie_consent');
    if (!consent) {
      // Small delay for better UX
      const timer = setTimeout(() => setIsVisible(true), 1000);
      return () => clearTimeout(timer);
    } else {
      // Apply existing consent to analytics
      try {
        const parsed = JSON.parse(consent);
        setAnalyticsConsent(parsed.analytics ?? false);
      } catch {
        // ignore parse errors
      }
    }
  }, []);

  const handleAcceptAll = () => {
    const consent = {
      necessary: true,
      functional: true,
      youtube: true,
      analytics: true,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('remaike_cookie_consent', JSON.stringify(consent));
    setAnalyticsConsent(true);
    setIsVisible(false);
    window.dispatchEvent(new Event('cookieConsentChanged'));
  };

  const handleAcceptNecessary = () => {
    const consent = {
      necessary: true,
      functional: false,
      youtube: false,
      analytics: false,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('remaike_cookie_consent', JSON.stringify(consent));
    setAnalyticsConsent(false);
    setIsVisible(false);
    window.dispatchEvent(new Event('cookieConsentChanged'));
  };

  const handleAcceptCustom = () => {
    const consent = {
      necessary: true,
      functional: true,
      youtube: true,
      analytics: analyticsEnabled,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('remaike_cookie_consent', JSON.stringify(consent));
    setAnalyticsConsent(analyticsEnabled);
    setIsVisible(false);
    window.dispatchEvent(new Event('cookieConsentChanged'));
  };

  const handleCustomize = () => {
    setShowDetails(!showDetails);
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]" />

      {/* Banner */}
      <div
        className={cn(
          'fixed bottom-0 left-0 right-0 z-[101]',
          'bg-retro-darker border-t border-retro-gray/50',
          'transform transition-transform duration-500',
          isVisible ? 'translate-y-0' : 'translate-y-full'
        )}
      >
        <div className="max-w-6xl mx-auto p-4 sm:p-6 md:p-8">
          {/* Header */}
          <div className="flex items-start gap-4 mb-4">
            <div className="p-3 bg-accent-red/20 rounded-lg shrink-0">
              <Cookie className="text-accent-red" size={24} />
            </div>
            <div className="flex-1">
              <h2 className="text-fluid-xl font-semibold mb-2 flex items-center gap-2">
                <Shield size={20} className="text-accent-cyan" />
                Datenschutz & Cookies
              </h2>
              <p className="text-fluid-sm text-retro-muted leading-relaxed">
                Diese Website nutzt YouTube-Embeds zur Videowiedergabe. Dabei werden Daten an
                YouTube/Google übertragen. Wir verwenden <strong>youtube-nocookie.com</strong> für
                datenschutzfreundlicheres Embedding. Zusätzlich speichern wir lokale Präferenzen
                (Watchlist, Verlauf) in deinem Browser.
              </p>
            </div>
          </div>

          {/* Details (expandable) */}
          {showDetails && (
            <div className="bg-retro-dark/50 rounded-lg p-4 mb-4 space-y-3">
              <div className="flex items-center justify-between py-2 border-b border-retro-gray/30">
                <div>
                  <p className="font-medium">Notwendige Cookies</p>
                  <p className="text-sm text-retro-muted">Session, Theme-Einstellungen</p>
                </div>
                <span className="text-xs bg-green-600/20 text-green-400 px-2 py-1 rounded">
                  Immer aktiv
                </span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-retro-gray/30">
                <div>
                  <p className="font-medium">Funktionale Cookies</p>
                  <p className="text-sm text-retro-muted">Watchlist, Verlauf, Wiedergabeposition</p>
                </div>
                <span className="text-xs bg-accent-cyan/20 text-accent-cyan px-2 py-1 rounded">
                  Optional
                </span>
              </div>

              <div className="flex items-center justify-between py-2 border-b border-retro-gray/30">
                <div>
                  <p className="font-medium">YouTube-Embeds</p>
                  <p className="text-sm text-retro-muted">
                    Videos über youtube-nocookie.com einbetten
                  </p>
                </div>
                <span className="text-xs bg-accent-cyan/20 text-accent-cyan px-2 py-1 rounded">
                  Optional
                </span>
              </div>

              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-2">
                  <BarChart3 size={16} className="text-accent-cyan" />
                  <div>
                    <p className="font-medium">Analytics (lokal)</p>
                    <p className="text-sm text-retro-muted">
                      Nutzungsstatistiken lokal im Browser speichern
                    </p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={analyticsEnabled}
                    onChange={(e) => setAnalyticsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-retro-gray/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-cyan"></div>
                </label>
              </div>

              <a
                href="https://policies.google.com/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-accent-cyan hover:underline mt-2"
              >
                Google Datenschutzerklärung
                <ExternalLink size={14} />
              </a>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
            <button
              onClick={handleCustomize}
              className="text-fluid-sm text-retro-muted hover:text-white transition-colors underline-offset-4 hover:underline"
            >
              {showDetails ? 'Details ausblenden' : 'Details anzeigen'}
            </button>

            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
              <button onClick={handleAcceptNecessary} className="btn btn-secondary text-fluid-sm">
                Nur Notwendige
              </button>
              {showDetails && (
                <button onClick={handleAcceptCustom} className="btn btn-secondary text-fluid-sm">
                  Auswahl bestätigen
                </button>
              )}
              <button onClick={handleAcceptAll} className="btn btn-primary text-fluid-sm">
                Alle akzeptieren
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
