import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, ExternalLink } from 'lucide-react';

/**
 * Impressum / Legal Notice Page for FRai.TV
 *
 * Legal notice required by German law (TMG §5)
 */
export default function ImpressumPage() {
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
          <span>{t('impressumPage.backToHome')}</span>
        </Link>

        {/* Header */}
        <div className="mb-12">
          <h1 className="text-fluid-4xl font-display text-white mb-4">
            {t('impressumPage.title')}
          </h1>
          <p className="text-retro-muted">{t('impressumPage.subtitle')}</p>
        </div>

        {/* Content */}
        <div className="prose prose-invert max-w-none space-y-8">
          {/* Anbieter */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              {t('impressumPage.serviceProvider')}
            </h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-light mb-2">
                <strong>FRai.TV</strong> – FREE ai Enhanced TV
              </p>
              <p className="text-retro-muted text-sm">{t('impressumPage.projectBy')}</p>
              <div className="mt-4 pt-4 border-t border-retro-gray">
                <p className="text-retro-light">
                  Maxim Seer
                  <br />
                  Copernicusstraße 1<br />
                  10243 Berlin
                  <br />
                  Deutschland
                </p>
              </div>
            </div>
          </section>

          {/* Kontakt */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              {t('impressumPage.contact')}
            </h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-light">
                E-Mail:{' '}
                <a href="mailto:contact@frai.tv" className="text-accent-cyan hover:underline">
                  contact@frai.tv
                </a>
              </p>
              <p className="text-retro-muted text-sm mt-2">{t('impressumPage.contactNote')}</p>
            </div>
          </section>

          {/* Verantwortlich für Inhalt */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              {t('impressumPage.responsibleContent')}
            </h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-light">
                Maxim Seer
                <br />
                Copernicusstraße 1<br />
                10243 Berlin
              </p>
            </div>
          </section>

          {/* Haftungsausschluss */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">
              {t('impressumPage.disclaimer')}
            </h2>

            <div className="space-y-6">
              {/* Haftung für Inhalte */}
              <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
                <h3 className="text-lg font-semibold text-white mb-3">
                  {t('impressumPage.liabilityContent')}
                </h3>
                <p className="text-retro-muted text-sm leading-relaxed">
                  {t('impressumPage.liabilityContentText')}
                </p>
              </div>

              {/* Haftung für Links */}
              <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
                <h3 className="text-lg font-semibold text-white mb-3">Haftung für Links</h3>
                <p className="text-retro-muted text-sm leading-relaxed">
                  Unser Angebot enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir
                  keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine
                  Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige
                  Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden
                  zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige
                  Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.
                </p>
              </div>

              {/* YouTube-Inhalte */}
              <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
                <h3 className="text-lg font-semibold text-white mb-3">YouTube-Inhalte</h3>
                <p className="text-retro-muted text-sm leading-relaxed">
                  FRai.TV ist eine Mediathek-Oberfläche, die Videos vom YouTube-Kanal
                  <a
                    href="https://www.youtube.com/@FRai_TV"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent-cyan hover:underline mx-1"
                  >
                    @FRai_TV
                  </a>
                  kuratiert und präsentiert. Die Videos selbst werden direkt von YouTube eingebettet
                  und unterliegen den
                  <a
                    href="https://www.youtube.com/t/terms"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-accent-cyan hover:underline mx-1"
                  >
                    YouTube-Nutzungsbedingungen
                  </a>
                  . Wir hosten keine Videos selbst.
                </p>
              </div>
            </div>
          </section>

          {/* Urheberrecht */}
          <section>
            <h2 className="text-fluid-xl font-semibold text-white mb-4">Urheberrecht</h2>
            <div className="bg-retro-dark/50 rounded-lg p-6 border border-retro-gray">
              <p className="text-retro-muted text-sm leading-relaxed">
                Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten
                unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung,
                Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes
                bedürfen der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers.
                Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen
                Gebrauch gestattet.
              </p>
              <p className="text-retro-muted text-sm leading-relaxed mt-4">
                Die präsentierten Videos sind urheberrechtlich geschützt und werden mit Genehmigung
                oder unter fairen Nutzungsbedingungen verwendet. Bei Fragen zum Urheberrecht wenden
                Sie sich bitte an den jeweiligen Rechteinhaber oder an uns.
              </p>
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
