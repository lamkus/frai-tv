import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Youtube, Mail, ExternalLink, Instagram } from 'lucide-react';
import { InfoPopup } from '../ui/InfoPopup';

/**
 * Footer Component - Site footer for FRai.TV
 * FR always uppercase, ai always lowercase, .TV always uppercase
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();
  const [showImpressum, setShowImpressum] = useState(false);
  const [showDatenschutz, setShowDatenschutz] = useState(false);

  return (
    <footer className="bg-retro-darker border-t border-retro-gray mt-auto">
      <div className="max-w-screen-4k mx-auto px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24">
        {/* Main Footer */}
        <div className="py-8 md:py-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 sm:col-span-2 lg:col-span-1">
            <Link to="/" className="inline-block mb-4">
              <span className="font-display text-3xl text-accent-red">FRai</span>
              <span className="font-display text-xl text-retro-muted">.TV</span>
            </Link>
            <p className="text-fluid-sm text-retro-muted max-w-xs">
              FREE ai Enhanced TV – Deine persönliche Retro-Mediathek. Klassiker neu aufbereitet mit
              AI-Enhancement.
            </p>
          </div>

          {/* Legal Links - Jetzt als Popups! */}
          <div>
            <h4 className="font-semibold text-fluid-sm mb-4">Rechtliches</h4>
            <ul className="space-y-2">
              <li>
                <button
                  onClick={() => setShowImpressum(true)}
                  className="text-fluid-sm text-retro-muted hover:text-white transition-colors text-left"
                >
                  Impressum
                </button>
              </li>
              <li>
                <button
                  onClick={() => setShowDatenschutz(true)}
                  className="text-fluid-sm text-retro-muted hover:text-white transition-colors text-left"
                >
                  Datenschutz
                </button>
              </li>
            </ul>
          </div>

          {/* Social / Connect - remAIke.IT Clean Style */}
          <div>
            <h4 className="font-semibold text-fluid-sm mb-4">Verbinden</h4>
            <div className="flex gap-2">
              <a
                href="https://www.youtube.com/@FRai_TV"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                aria-label="YouTube"
              >
                <Youtube
                  size={18}
                  className="text-white/70 group-hover:text-red-500 transition-colors"
                />
              </a>
              <a
                href="https://www.instagram.com/frai.tv"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                aria-label="Instagram"
              >
                <Instagram
                  size={18}
                  className="text-white/70 group-hover:text-pink-400 transition-colors"
                />
              </a>
              <a
                href="https://www.tiktok.com/@frai.tv"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                aria-label="TikTok"
              >
                <svg
                  viewBox="0 0 24 24"
                  className="w-[18px] h-[18px] fill-white/70 group-hover:fill-white transition-colors"
                >
                  <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z" />
                </svg>
              </a>
              <a
                href="https://x.com/FRai_TV"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                aria-label="X"
              >
                <svg
                  viewBox="0 0 24 24"
                  className="w-[18px] h-[18px] fill-white/70 group-hover:fill-white transition-colors"
                >
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                </svg>
              </a>
              <a
                href="mailto:contact@frai.tv"
                className="p-2.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 transition-all group"
                aria-label="E-Mail"
              >
                <Mail
                  size={18}
                  className="text-white/70 group-hover:text-accent-gold transition-colors"
                />
              </a>
            </div>
          </div>

          {/* Powered By (nur Hinweis unten) */}
          <div>
            <h4 className="font-semibold text-fluid-sm mb-4">Powered by</h4>
            <div className="space-y-3">
              <a
                href="https://remAIke.IT"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-fluid-sm text-retro-muted hover:text-white transition-colors"
              >
                <ExternalLink size={12} />
                <span>remAIke.IT</span>
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="py-4 border-t border-retro-gray flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-retro-muted text-center sm:text-left">
            © {currentYear} FRai.TV – FREE ai Enhanced TV. Alle Rechte vorbehalten.
          </p>

          <div className="flex items-center gap-4 text-xs text-retro-muted">
            <button
              onClick={() => setShowImpressum(true)}
              className="hover:text-white transition-colors"
            >
              Impressum
            </button>
            <button
              onClick={() => setShowDatenschutz(true)}
              className="hover:text-white transition-colors"
            >
              Datenschutz
            </button>
          </div>
        </div>
      </div>

      {/* Impressum Modal */}
      <InfoPopup
        isOpen={showImpressum}
        onClose={() => setShowImpressum(false)}
        title="Impressum"
        size="lg"
      >
        <div className="space-y-6">
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <h3 className="text-accent-gold font-semibold mb-2">Diensteanbieter</h3>
            <p className="text-white font-medium">FRai.TV – FREE ai Enhanced TV</p>
            <div className="mt-3 pt-3 border-t border-white/10 text-sm text-gray-300">
              Maxim Seer
              <br />
              Copernicusstraße 1<br />
              10243 Berlin
              <br />
              Deutschland
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <h3 className="text-accent-gold font-semibold mb-2">Kontakt</h3>
            <p className="text-sm text-gray-300">
              E-Mail:{' '}
              <a href="mailto:contact@frai.tv" className="text-accent-cyan hover:underline">
                contact@frai.tv
              </a>
            </p>
          </div>

          <div className="text-xs text-gray-500">
            <p>
              Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV: Maxim Seer, Anschrift wie oben.
            </p>
          </div>
        </div>
      </InfoPopup>

      {/* Datenschutz Modal */}
      <InfoPopup
        isOpen={showDatenschutz}
        onClose={() => setShowDatenschutz(false)}
        title="Datenschutzerklärung"
        size="xl"
      >
        <div className="space-y-6">
          <div className="grid grid-cols-2 gap-3 mb-6">
            <div className="bg-white/5 p-3 rounded border border-white/10 text-center">
              <span className="block text-green-500 text-xl mb-1">✓</span>
              <span className="text-xs text-gray-400">DSGVO-konform</span>
            </div>
            <div className="bg-white/5 p-3 rounded border border-white/10 text-center">
              <span className="block text-amber-500 text-xl mb-1">🍪</span>
              <span className="text-xs text-gray-400">Nur notwendige Cookies</span>
            </div>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <h3 className="text-accent-gold font-semibold mb-2">1. Verantwortlicher</h3>
            <p className="text-sm text-gray-300">
              FRai.TV - Maxim Seer
              <br />
              Copernicusstraße 1, 10243 Berlin
              <br />
              E-Mail:{' '}
              <a href="mailto:datenschutz@frai.tv" className="text-accent-cyan hover:underline">
                datenschutz@frai.tv
              </a>
            </p>
          </div>

          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <h3 className="text-accent-gold font-semibold mb-2">2. Übersicht</h3>
            <p className="text-sm text-gray-300 mb-3">
              Wir verarbeiten Ihre Daten nur, soweit dies zur Bereitstellung unserer Dienste
              erforderlich ist.
            </p>
            <ul className="text-sm text-gray-400 space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Keine Analyse-Tools von Drittanbietern
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Keine Weitergabe an Dritte
              </li>
              <li className="flex items-center gap-2">
                <span className="text-green-500">✓</span> Serverstandort Deutschland (Strato)
              </li>
            </ul>
          </div>

          <div className="text-xs text-gray-500 mt-4">
            <p>
              Stand: Dezember 2025. Die vollständige Datenschutzerklärung finden Sie auf Anfrage.
            </p>
          </div>
        </div>
      </InfoPopup>
    </footer>
  );
}
