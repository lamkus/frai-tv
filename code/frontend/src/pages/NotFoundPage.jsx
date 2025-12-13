import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Home, Search, ArrowLeft, Film } from 'lucide-react';
import useMeta from '../lib/useMeta';

/**
 * NotFoundPage - 404 Error Page
 *
 * Premium design with animated elements and helpful navigation
 */
export default function NotFoundPage() {
  const { t } = useTranslation();
  useMeta({
    title: t('notFoundPage.metaTitle'),
    description: t('notFoundPage.metaDescription'),
  });

  return (
    <div className="min-h-screen bg-retro-black flex items-center justify-center px-4">
      {/* Background effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-accent-gold/5 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent-gold/5 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative text-center max-w-lg mx-auto">
        {/* 404 Number */}
        <div className="mb-8">
          <h1 className="text-[150px] md:text-[200px] font-display font-bold text-transparent bg-clip-text bg-gradient-to-b from-accent-gold via-accent-gold/50 to-transparent leading-none select-none">
            404
          </h1>
        </div>

        {/* Film strip decoration */}
        <div className="flex justify-center gap-2 mb-8">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-8 h-6 bg-white/10 rounded-sm border border-white/20"
              style={{ animationDelay: `${i * 0.1}s` }}
            />
          ))}
        </div>

        {/* Message */}
        <div className="mb-8">
          <h2 className="text-2xl md:text-3xl font-display font-bold text-white mb-4">
            {t('notFoundPage.title')}
          </h2>
          <p className="text-retro-muted text-lg">
            {t('notFoundPage.description')}
            <br />
            <span className="text-white/40 text-sm">{t('notFoundPage.subDescription')}</span>
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/"
            className="inline-flex items-center gap-3 px-8 py-4 bg-accent-gold text-black font-bold rounded-lg hover:bg-accent-amber transition-all transform hover:scale-105 shadow-xl shadow-accent-gold/20"
          >
            <Home size={20} />
            {t('notFoundPage.backToHome')}
          </Link>

          <Link
            to="/search"
            className="inline-flex items-center gap-3 px-8 py-4 bg-white/10 text-white font-semibold rounded-lg hover:bg-white/20 transition-all border border-white/20"
          >
            <Search size={20} />
            {t('notFoundPage.search')}
          </Link>
        </div>

        {/* Back link */}
        <button
          onClick={() => window.history.back()}
          className="mt-8 inline-flex items-center gap-2 text-retro-muted hover:text-accent-gold transition-colors"
        >
          <ArrowLeft size={16} />
          {t('notFoundPage.goBack')}
        </button>

        {/* Fun fact */}
        <div className="mt-12 p-4 bg-white/5 rounded-lg border border-white/10">
          <div className="flex items-center gap-2 text-accent-gold mb-2">
            <Film size={16} />
            <span className="text-xs font-semibold uppercase tracking-wider">
              {t('notFoundPage.funFact')}
            </span>
          </div>
          <p className="text-white/60 text-sm">{t('notFoundPage.funFactText')}</p>
        </div>
      </div>
    </div>
  );
}
