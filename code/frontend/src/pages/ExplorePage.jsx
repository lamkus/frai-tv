import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Map, Newspaper, Grid3X3, ChevronRight, AlertTriangle, ArrowLeft } from 'lucide-react';
import { MindmapNavigator, TVGuide } from '../components/experimental';
import { cn } from '../lib/utils';

/**
 * ExplorePage - Experimental Navigation Hub
 *
 * ⚠️ EXPERIMENTAL: Diese Features sind noch in Entwicklung!
 * Nur sichtbar wenn VITE_EXPERIMENTAL_FEATURES=true
 *
 * Offers alternative ways to explore the video collection:
 * - Mindmap Navigator: Visual node-based exploration
 * - TV Guide: Category × Decade grid (like a program guide)
 * - More modes planned...
 */
export default function ExplorePage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [activeMode, setActiveMode] = useState('tvguide');

  // Check if experimental features are enabled
  const EXPERIMENTAL_ENABLED = import.meta.env.VITE_EXPERIMENTAL_FEATURES === 'true';

  // Redirect to browse if experimental features are disabled
  useEffect(() => {
    if (!EXPERIMENTAL_ENABLED) {
      navigate('/browse', { replace: true });
    }
  }, [EXPERIMENTAL_ENABLED, navigate]);

  // Don't render if not enabled (will redirect)
  if (!EXPERIMENTAL_ENABLED) {
    return (
      <div className="min-h-screen bg-retro-darker flex items-center justify-center">
        <div className="text-center p-8 max-w-md">
          <AlertTriangle className="w-16 h-16 text-accent-amber mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">
            {t('explorePage.experimentalFeatures')}
          </h1>
          <p className="text-retro-muted mb-4">{t('explorePage.featuresDisabled')}</p>
          <button
            onClick={() => navigate('/browse')}
            className="inline-flex items-center gap-2 px-4 py-2 bg-accent-amber text-black rounded-lg font-medium hover:bg-amber-400 transition-colors"
          >
            <ArrowLeft size={16} />
            {t('explorePage.toLibrary')}
          </button>
        </div>
      </div>
    );
  }

  const modes = [
    {
      id: 'tvguide',
      label: t('explorePage.tvGuide'),
      icon: Newspaper,
      description: t('explorePage.tvGuideDesc'),
    },
    {
      id: 'mindmap',
      label: t('explorePage.mindmap'),
      icon: Map,
      description: t('explorePage.mindmapDesc'),
    },
    {
      id: 'grid',
      label: t('explorePage.gridView'),
      icon: Grid3X3,
      description: t('explorePage.gridViewDesc'),
      comingSoon: true,
    },
  ];

  return (
    <div className="min-h-screen bg-retro-darker">
      {/* Header */}
      <div className="border-b border-retro-gray/30">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-white mb-2">
            {t('explorePage.title')} <span className="text-accent-amber">rem</span>
            <span className="text-accent-cyan">AI</span>
            <span className="text-accent-amber">ke.TV</span>
          </h1>
          <p className="text-retro-muted">{t('explorePage.subtitle')}</p>
        </div>

        {/* Mode Selector */}
        <div className="container mx-auto px-4 pb-4">
          <div className="flex gap-2 overflow-x-auto pb-2">
            {modes.map((mode) => (
              <button
                key={mode.id}
                onClick={() => !mode.comingSoon && setActiveMode(mode.id)}
                disabled={mode.comingSoon}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 rounded-xl transition-all min-w-[200px]',
                  activeMode === mode.id
                    ? 'bg-accent-amber text-black'
                    : mode.comingSoon
                    ? 'bg-retro-dark/50 text-retro-muted cursor-not-allowed'
                    : 'bg-retro-dark text-white hover:bg-retro-gray'
                )}
              >
                <mode.icon size={20} />
                <div className="text-left">
                  <div className="font-medium flex items-center gap-2">
                    {mode.label}
                    {mode.comingSoon && (
                      <span className="text-xs bg-accent-purple/20 text-accent-purple px-2 py-0.5 rounded">
                        Soon
                      </span>
                    )}
                  </div>
                  <div
                    className={cn(
                      'text-xs',
                      activeMode === mode.id ? 'text-black/70' : 'text-retro-muted'
                    )}
                  >
                    {mode.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Active Mode Content */}
      <div className="container mx-auto px-4 py-6">
        {activeMode === 'tvguide' && <TVGuide className="w-full" />}
        {activeMode === 'mindmap' && <MindmapNavigator className="w-full h-[600px]" />}
      </div>

      {/* Tips */}
      <div className="container mx-auto px-4 pb-8">
        <div className="bg-retro-dark rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <ChevronRight className="text-accent-amber" size={20} />
            Navigation Tips
          </h3>
          <div className="grid md:grid-cols-2 gap-4 text-sm text-retro-muted">
            {activeMode === 'tvguide' && (
              <>
                <div>• Kategorien sind wie TV-Kanäle (Zeilen)</div>
                <div>• Jahrzehnte sind wie Sendeplätze (Spalten)</div>
                <div>• Hover für Schnellvorschau</div>
                <div>• Klick auf Video zum Abspielen</div>
                <div>• Klick auf &quot;+N&quot; für alle Videos</div>
                <div>• Filter nach Jahrzehnt oben</div>
              </>
            )}
            {activeMode === 'mindmap' && (
              <>
                <div>• Ziehen zum Navigieren</div>
                <div>• Scrollen zum Zoomen</div>
                <div>• Klick auf Node zum Filtern</div>
                <div>• Zentrum = Archiv-Root</div>
                <div>• Äste = Jahrzehnte & Kategorien</div>
                <div>• Blätter = Einzelne Videos</div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
