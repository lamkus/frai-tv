import { useState, useEffect } from 'react';

/**
 * Hook to check if YouTube consent was given
 */
export function useYouTubeConsent() {
  const [hasConsent, setHasConsent] = useState(() => {
    try {
      const consent = localStorage.getItem('remaike_cookie_consent');
      if (consent) {
        const parsed = JSON.parse(consent);
        return parsed.youtube === true;
      }
    } catch (e) {
      // Ignore parse errors
    }
    return false;
  });

  useEffect(() => {
    const handleConsentChange = () => {
      try {
        const consent = localStorage.getItem('remaike_cookie_consent');
        if (consent) {
          const parsed = JSON.parse(consent);
          setHasConsent(parsed.youtube === true);
        }
      } catch (e) {
        // Ignore
      }
    };

    window.addEventListener('cookieConsentChanged', handleConsentChange);
    window.addEventListener('storage', handleConsentChange);

    return () => {
      window.removeEventListener('cookieConsentChanged', handleConsentChange);
      window.removeEventListener('storage', handleConsentChange);
    };
  }, []);

  return hasConsent;
}
