import { useState, useEffect } from 'react';
import { Cookie, ExternalLink } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { initAnalytics, setAnalyticsConsent } from '../../lib/analytics';

/**
 * GDPR/Cookie Consent Modal - i18n enabled
 */
export default function GDPRModal() {
  const { t } = useTranslation();
  const [isVisible, setIsVisible] = useState(false);
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    // Prüfe ob bereits entschieden wurde
    const consent = getCookie('gdpr_accepted');
    if (consent === null || consent === undefined || consent === '') {
      // Noch keine Entscheidung getroffen
      setIsVisible(true);
    } else if (consent === 'true') {
      // Analytics aktivieren
      enableAnalytics();
      setAnalyticsConsent(true);
      initAnalytics();
    } else {
      setAnalyticsConsent(false);
    }
  }, []);

  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
  };

  const setCookie = (name, value, days) => {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/;SameSite=Lax`;
  };

  const enableAnalytics = () => {
    // Google Analytics aktivieren (falls gtag vorhanden)
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'granted',
      });
    }
  };

  const disableAnalytics = () => {
    // Google Analytics deaktivieren
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied',
      });
    }
  };

  const handleClose = (accepted) => {
    setIsClosing(true);

    if (accepted) {
      setCookie('gdpr_accepted', 'true', 365);
      enableAnalytics();
      setAnalyticsConsent(true);
      initAnalytics();
    } else {
      setCookie('gdpr_accepted', 'false', 30);
      disableAnalytics();
      setAnalyticsConsent(false);
    }

    // Fade-out Animation
    setTimeout(() => {
      setIsVisible(false);
      setIsClosing(false);
    }, 300);
  };

  if (!isVisible) return null;

  return (
    <div
      className={`fixed inset-0 flex items-center justify-center p-4 transition-opacity duration-300 ${
        isClosing ? 'opacity-0' : 'opacity-100'
      }`}
      style={{
        backgroundColor: 'rgba(0, 0, 0, 0.95)',
        zIndex: 9999,
      }}
    >
      {/* Modal Box */}
      <div
        className={`w-full max-w-[500px] rounded-xl p-6 transition-transform duration-300 ${
          isClosing ? 'scale-95' : 'scale-100'
        }`}
        style={{
          backgroundColor: '#1a1a1a',
          border: '2px solid #c9a962',
          borderRadius: '12px',
          boxShadow: '0 0 40px rgba(201, 169, 98, 0.3)',
        }}
      >
        {/* Header */}
        <div className="flex items-center justify-center gap-2 mb-5">
          <Cookie size={24} style={{ color: '#c9a962' }} />
          <h2
            className="text-xl font-display text-center"
            style={{ color: '#c9a962', fontSize: '20px' }}
          >
            {t('gdpr.title')}
          </h2>
        </div>

        {/* Body Text */}
        <p
          className="mb-5"
          style={{
            fontSize: '14px',
            lineHeight: '1.6',
            color: '#cccccc',
          }}
        >
          {t('gdpr.description')}
        </p>

        {/* Links */}
        <p
          className="mb-6 text-center"
          style={{
            fontSize: '13px',
            color: '#999999',
          }}
        >
          {t('gdpr.moreInfo')}{' '}
          <a
            href="/datenschutz"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 hover:underline"
            style={{ color: '#c9a962' }}
          >
            {t('gdpr.privacyPolicy')}
            <ExternalLink size={12} />
          </a>{' '}
          {t('gdpr.andIn')}{' '}
          <a
            href="/impressum"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 hover:underline"
            style={{ color: '#c9a962' }}
          >
            {t('imprint')}
            <ExternalLink size={12} />
          </a>
          .
        </p>

        {/* Buttons */}
        <div className="flex gap-3">
          {/* Decline Button */}
          <button
            onClick={() => handleClose(false)}
            className="flex-1 h-11 rounded-lg font-medium transition-all duration-200 hover:scale-[1.02]"
            style={{
              backgroundColor: 'transparent',
              border: '2px solid #666666',
              color: '#999999',
              borderRadius: '8px',
            }}
          >
            {t('gdpr.decline')}
          </button>

          {/* Accept Button */}
          <button
            onClick={() => handleClose(true)}
            className="flex-1 h-11 rounded-lg font-bold transition-all duration-200 hover:scale-[1.02]"
            style={{
              background: 'linear-gradient(135deg, #c9a962 0%, #a8893f 100%)',
              border: 'none',
              color: '#1a1a1a',
              borderRadius: '8px',
            }}
          >
            {t('gdpr.accept')}
          </button>
        </div>
      </div>
    </div>
  );
}
