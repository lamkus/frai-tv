import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Download, Share, Sparkles, Zap } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * PWA Install Prompt Component - Premium Gold Edition
 * Matches style of www.remaike.it Inquiry Modal
 */
export function InstallPrompt({ forceOpen = false, onClose: onParentClose } = {}) {
  const { t } = useTranslation();
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [platform, setPlatform] = useState('desktop');
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Detect Platform
    const ua = navigator.userAgent;
    const isIOS = /iPad|iPhone|iPod/.test(ua) && !window.MSStream;
    const isAndroid = /Android/.test(ua);

    setPlatform(isIOS ? 'ios' : isAndroid ? 'android' : 'desktop');

    // Check cooldown (7 days)
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    if (dismissed) {
      const days = (Date.now() - parseInt(dismissed, 10)) / (1000 * 60 * 60 * 24);
      if (days < 7) return;
    }

    // Show after delay
    const timer = setTimeout(() => setShowPrompt(true), 3000);

    // Capture install event
    const installHandler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', installHandler);

    // Listen for successful install
    const installedHandler = () => {
      setIsInstalled(true);
      setShowPrompt(false);
    };
    window.addEventListener('appinstalled', installedHandler);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('beforeinstallprompt', installHandler);
      window.removeEventListener('appinstalled', installedHandler);
    };
  }, []);

  const handleInstall = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === 'accepted') {
        setShowPrompt(false);
      }
      setDeferredPrompt(null);
    } else {
      handleDismiss();
    }
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
    // Call parent handler when used in a force open demo
    if (onParentClose) onParentClose();
  };

  if (isInstalled) return null;
  // Show when the browser triggers it OR when parent wants to force open for demo
  if (!showPrompt && !forceOpen) return null;

  return (
    <>
      {/* Premium Backdrop */}
      <div
        className="fixed inset-0 bg-black/80 backdrop-blur-md z-[100] transition-opacity duration-500"
        onClick={handleDismiss}
      />

      {/* Premium Bottom Sheet / Modal */}
      <div
        className={cn(
          'fixed bottom-0 left-0 right-0 z-[101]',
          'bg-gradient-to-br from-[#141414] to-[#0a0a0b]', // Premium Dark Gradient
          'border-t border-accent-gold/30', // Gold Border
          'shadow-[0_0_100px_rgba(201,169,98,0.15)]', // Gold Glow
          'transform transition-transform duration-500 ease-out',
          showPrompt ? 'translate-y-0' : 'translate-y-full'
        )}
      >
        <div className="max-w-4xl mx-auto p-6 sm:p-8">
          {/* Header Section */}
          <div className="flex items-start gap-5 mb-8">
            {/* Logo Box */}
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-gold to-[#a88b4a] flex items-center justify-center shrink-0 shadow-[0_0_30px_rgba(201,169,98,0.3)]">
              <Zap size={32} className="text-black fill-black" />
            </div>

            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2 flex items-center gap-2 text-accent-gold tracking-tight">
                <Sparkles size={20} className="text-accent-gold" />
                {t('installAppTitle')}
              </h2>
              <p className="text-sm text-retro-muted leading-relaxed max-w-2xl">
                {platform === 'ios' ? (
                  <>
                    {t('installAppDescIOS')} <strong className="text-white">{t('share')}</strong>{' '}
                    und wähle{' '}
                    <strong className="text-white">&quot;{t('addToHomeScreen')}&quot;</strong>.
                  </>
                ) : (
                  <>{t('installAppDescAndroid')}</>
                )}
              </p>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
            <FeatureBox icon="⚡" label="Instant Start" />
            <FeatureBox icon="🎬" label="Cinema Mode" />
            <FeatureBox icon="💾" label="Offline Ready" />
            <FeatureBox icon="🔔" label="Updates" />
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 sm:items-center sm:justify-between pt-6 border-t border-white/5">
            <button
              onClick={handleDismiss}
              className="text-sm text-retro-muted hover:text-white transition-colors px-2"
            >
              {t('remindLater')}
            </button>

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={handleDismiss}
                className="px-6 py-3 rounded-xl bg-[#1c1c1e] border border-[#2c2c2e] text-white font-medium hover:border-accent-gold hover:text-accent-gold transition-all duration-300"
              >
                {t('notNow')}
              </button>

              {platform === 'ios' ? (
                <button
                  onClick={handleDismiss}
                  className="px-8 py-3 rounded-xl bg-gradient-to-br from-accent-gold to-[#b8944a] text-black font-bold shadow-[0_4px_20px_rgba(201,169,98,0.3)] hover:shadow-[0_6px_30px_rgba(201,169,98,0.5)] hover:-translate-y-0.5 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Share size={18} />
                  {t('understood')}
                </button>
              ) : (
                <button
                  onClick={handleInstall}
                  className="px-8 py-3 rounded-xl bg-gradient-to-br from-accent-gold to-[#b8944a] text-black font-bold shadow-[0_4px_20px_rgba(201,169,98,0.3)] hover:shadow-[0_6px_30px_rgba(201,169,98,0.5)] hover:-translate-y-0.5 transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Download size={18} />
                  {t('installApp')}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function FeatureBox({ icon, label }) {
  return (
    <div className="bg-[#1c1c1e] border border-[#2c2c2e] rounded-xl p-4 text-center hover:border-accent-gold/50 transition-colors group">
      <div className="text-2xl mb-2 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <div className="text-xs font-medium text-retro-muted group-hover:text-white uppercase tracking-wider">
        {label}
      </div>
    </div>
  );
}

// Settings Page Button
export function InstallButton({ className = '' }) {
  const { t } = useTranslation();
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }
    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handler);
    window.addEventListener('appinstalled', () => setIsInstalled(true));
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    await deferredPrompt.userChoice;
    setDeferredPrompt(null);
  };

  if (isInstalled) {
    return (
      <div className={`flex items-center gap-3 text-accent-green ${className}`}>
        <div className="w-10 h-10 bg-accent-green/20 rounded-full flex items-center justify-center">
          ✓
        </div>
        <span>{t('appInstalled')}</span>
      </div>
    );
  }

  return (
    <button
      onClick={handleInstall}
      disabled={!deferredPrompt}
      className={`px-6 py-3 rounded-xl bg-gradient-to-br from-accent-gold to-[#b8944a] text-black font-bold shadow-[0_4px_20px_rgba(201,169,98,0.3)] hover:shadow-[0_6px_30px_rgba(201,169,98,0.5)] hover:-translate-y-0.5 transition-all duration-300 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      <Download size={20} />
      <span>{t('installApp')}</span>
    </button>
  );
}

export default InstallPrompt;
