import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, ExternalLink, Shield, Cookie, Database, Lock } from 'lucide-react';

/**
 * Datenschutz / Privacy Policy Page for FRai.TV
 *
 * Privacy policy required by GDPR (DSGVO)
 */
export default function DatenschutzPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-retro-darker py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-retro-muted hover:text-white mb-8 transition-colors"
        >
          <ArrowLeft size={20} />
          <span>{t('privacyPage.backToHome')}</span>
        </Link>

        {/* Header */}
        <div className="mb-12">
          <h1 className="text-fluid-4xl font-display text-white mb-4">{t('privacyPage.title')}</h1>
          <p className="text-retro-muted">{t('privacyPage.subtitle')}</p>
          <p className="text-retro-muted text-sm mt-2">{t('privacyPage.lastUpdated')}</p>
        </div>

        {/* Quick Overview */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-12">
          <div className="bg-retro-dark/50 rounded-lg p-4 border border-retro-gray text-center">
            <Shield className="w-8 h-8 text-green-500 mx-auto mb-2" />
            <p className="text-xs text-retro-muted">{t('privacyPage.gdprCompliant')}</p>
          </div>
          <div className="bg-retro-dark/50 rounded-lg p-4 border border-retro-gray text-center">
            <Cookie className="w-8 h-8 text-amber-500 mx-auto mb-2" />
            <p className="text-xs text-retro-muted">{t('privacyPage.necessaryCookies')}</p>
          </div>
          <div className="bg-retro-dark/50 rounded-lg p-4 border border-retro-gray text-center">
            <Database className="w-8 h-8 text-blue-500 mx-auto mb-2" />
            <p className="text-xs text-retro-muted">{t('privacyPage.localStorage')}</p>
          </div>
          <div className="bg-retro-dark/50 rounded-lg p-4 border border-retro-gray text-center">
            <Lock className="w-8 h-8 text-purple-500 mx-auto mb-2" />
            <p className="text-xs text-retro-muted">{t('privacyPage.noSharing')}</p>
          </div>
        </div>

        {/* Content */}
        <div className="prose prose-invert max-w-none space-y-8">
          {/* Verantwortlicher */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">1. Verantwortlicher</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-light mb-2">
                <strong>FRai.TV</strong> – FREE ai Enhanced TV
              </p>
              <p className="text-retro-light">
                Maxim Seer
                <br />
                Copernicusstraße 1<br />
                10243 Berlin
                <br />
                Deutschland
              </p>
              <p className="text-retro-light mt-4">
                E-Mail:{' '}
                <a href="mailto:datenschutz@frai.tv" className="text-accent-cyan hover:underline">
                  datenschutz@frai.tv
                </a>
              </p>
            </div>
          </section>

          {/* Übersicht Datenverarbeitung */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              2. Übersicht der Datenverarbeitung
            </h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed mb-4">
                FRai.TV ist eine datenschutzfreundliche Video-Mediathek. Wir verarbeiten Ihre Daten
                nur, soweit dies zur Bereitstellung unserer Dienste erforderlich ist.
              </p>
              <h3 className="text-lg font-semibold text-white mb-3">Was wir NICHT tun:</h3>
              <ul className="text-retro-muted text-sm space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  Keine Analyse-Tools von Drittanbietern (kein Google Analytics)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  Keine Weitergabe Ihrer Daten an Dritte
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  Keine personalisierte Werbung
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">✓</span>
                  Keine Erstellung von Nutzerprofilen ohne Ihre Zustimmung
                </li>
              </ul>
            </div>
          </section>

          {/* Lokale Speicherung */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              3. Lokale Datenspeicherung (Browser)
            </h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed mb-4">
                Zur Verbesserung Ihrer Nutzungserfahrung speichern wir folgende Daten ausschließlich
                lokal in Ihrem Browser (LocalStorage):
              </p>
              <ul className="text-retro-muted text-sm space-y-3">
                <li>
                  <strong className="text-white">Merkliste:</strong> Videos, die Sie zur späteren
                  Ansicht vorgemerkt haben
                </li>
                <li>
                  <strong className="text-white">Wiedergabeverlauf:</strong> Zuletzt angesehene
                  Videos für &quot;Weiterschauen&quot;
                </li>
                <li>
                  <strong className="text-white">Einstellungen:</strong> Ihre Präferenzen (z.B.
                  Lautstärke, Theme)
                </li>
                <li>
                  <strong className="text-white">Cookie-Zustimmung:</strong> Ob Sie YouTube-Embeds
                  akzeptiert haben
                </li>
              </ul>
              <p className="text-retro-muted text-sm mt-4 p-3 bg-retro-darker rounded">
                <strong>Wichtig:</strong> Diese Daten verlassen niemals Ihren Browser und werden
                nicht an unsere oder fremde Server übertragen.
              </p>
            </div>
          </section>

          {/* YouTube Embeds */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">4. YouTube-Einbettungen</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed mb-4">
                FRai.TV bettet Videos von YouTube ein. Wir verwenden dabei den
                <strong className="text-white"> erweiterten Datenschutzmodus</strong>
                (youtube-nocookie.com), der das Tracking reduziert.
              </p>
              <h3 className="text-lg font-semibold text-white mb-3">Was bedeutet das?</h3>
              <ul className="text-retro-muted text-sm space-y-2">
                <li>• Videos werden erst nach Ihrer expliziten Zustimmung geladen</li>
                <li>
                  • YouTube setzt keine Cookies, bevor Sie auf &quot;Video laden&quot; klicken
                </li>
                <li>• Beim Abspielen eines Videos wird eine Verbindung zu YouTube hergestellt</li>
                <li>• YouTube kann dabei Ihre IP-Adresse und Nutzungsdaten erheben</li>
              </ul>
              <div className="mt-4 p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                <p className="text-amber-200 text-sm">
                  <strong>Hinweis:</strong> Für Details zur Datenverarbeitung durch YouTube beachten
                  Sie bitte die
                  <a
                    href="https://policies.google.com/privacy"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent-cyan hover:underline ml-1"
                  >
                    Datenschutzerklärung von Google
                    <ExternalLink size={12} className="inline ml-1" />
                  </a>
                </p>
              </div>
            </div>
          </section>

          {/* Hosting */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">5. Hosting</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed">
                Diese Website wird in Deutschland gehostet. Der Server-Standort ist Deutschland
                (EU). Bei jedem Zugriff werden folgende Daten in Server-Logfiles gespeichert:
              </p>
              <ul className="text-retro-muted text-sm mt-4 space-y-1">
                <li>• IP-Adresse (anonymisiert nach 7 Tagen)</li>
                <li>• Datum und Uhrzeit der Anfrage</li>
                <li>• Aufgerufene Seite</li>
                <li>• Browser und Betriebssystem</li>
                <li>• Referrer-URL (woher Sie kamen)</li>
              </ul>
              <p className="text-retro-muted text-sm mt-4">
                <strong className="text-white">Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. f DSGVO
                (berechtigtes Interesse an der Sicherheit und Optimierung des Angebots)
              </p>
            </div>
          </section>

          {/* Ihre Rechte */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">6. Ihre Rechte</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed mb-4">
                Sie haben gemäß DSGVO folgende Rechte:
              </p>
              <div className="grid gap-3">
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Auskunftsrecht (Art. 15):</strong>
                  <p className="text-retro-muted text-sm">
                    Welche Daten wir über Sie gespeichert haben
                  </p>
                </div>
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Berichtigung (Art. 16):</strong>
                  <p className="text-retro-muted text-sm">Korrektur unrichtiger Daten</p>
                </div>
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Löschung (Art. 17):</strong>
                  <p className="text-retro-muted text-sm">
                    Entfernung Ihrer Daten (&quot;Recht auf Vergessenwerden&quot;)
                  </p>
                </div>
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Einschränkung (Art. 18):</strong>
                  <p className="text-retro-muted text-sm">Einschränkung der Verarbeitung</p>
                </div>
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Widerspruch (Art. 21):</strong>
                  <p className="text-retro-muted text-sm">Widerspruch gegen die Verarbeitung</p>
                </div>
                <div className="p-3 bg-retro-darker rounded">
                  <strong className="text-white">Datenübertragbarkeit (Art. 20):</strong>
                  <p className="text-retro-muted text-sm">
                    Export Ihrer Daten in maschinenlesbarem Format
                  </p>
                </div>
              </div>
              <p className="text-retro-muted text-sm mt-4">
                Zur Ausübung Ihrer Rechte wenden Sie sich an:
                <a
                  href="mailto:datenschutz@frai.tv"
                  className="text-accent-cyan hover:underline ml-1"
                >
                  datenschutz@frai.tv
                </a>
              </p>
            </div>
          </section>

          {/* Lokale Daten löschen */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">7. Lokale Daten löschen</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed mb-4">
                Sie können alle lokal gespeicherten Daten jederzeit selbst löschen:
              </p>
              <ol className="text-retro-muted text-sm space-y-2 list-decimal list-inside">
                <li>Öffnen Sie die Browser-Einstellungen</li>
                <li>Gehen Sie zu &quot;Datenschutz&quot; oder &quot;Websitedaten&quot;</li>
                <li>Suchen Sie nach &quot;frai.tv&quot; oder &quot;it-heats.de&quot;</li>
                <li>Löschen Sie die gespeicherten Daten</li>
              </ol>
              <p className="text-retro-muted text-sm mt-4">
                Alternativ können Sie in den
                <Link to="/settings" className="text-accent-cyan hover:underline mx-1">
                  Einstellungen
                </Link>
                alle Daten mit einem Klick zurücksetzen.
              </p>
            </div>
          </section>

          {/* Beschwerderecht */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">8. Beschwerderecht</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed">
                Sie haben das Recht, sich bei einer Datenschutz-Aufsichtsbehörde zu beschweren. Die
                für uns zuständige Behörde ist:
              </p>
              <div className="mt-4 p-4 bg-retro-darker rounded">
                <p className="text-retro-light text-sm">
                  Berliner Beauftragte für Datenschutz und Informationsfreiheit
                  <br />
                  Alt-Moabit 59-61
                  <br />
                  10555 Berlin
                  <br />
                  <a
                    href="https://www.datenschutz-berlin.de"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent-cyan hover:underline"
                  >
                    www.datenschutz-berlin.de
                    <ExternalLink size={12} className="inline ml-1" />
                  </a>
                </p>
              </div>
            </div>
          </section>

          {/* Powered By */}
          <section className="pt-8 border-t border-retro-gray">
            <div className="flex flex-wrap items-center justify-center gap-6">
              <a
                href="https://skillbox.software"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-retro-dark/50 rounded-lg border border-retro-gray hover:border-accent-red transition-colors"
              >
                <img
                  src="https://skillbox.software/assets/icons/logo.png"
                  alt="remAIke.IT"
                  className="w-6 h-6"
                />
                <span className="text-sm text-retro-muted">Powered by remAIke.IT</span>
                <ExternalLink size={14} className="text-retro-muted" />
              </a>
              <a
                href="https://www.youtube.com/@FRai_TV"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-retro-dark/50 rounded-lg border border-retro-gray hover:border-red-500 transition-colors"
              >
                <svg viewBox="0 0 24 24" className="w-6 h-6 fill-red-500">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
                </svg>
                <span className="text-sm text-retro-muted">Videos auf YouTube</span>
                <ExternalLink size={14} className="text-retro-muted" />
              </a>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
