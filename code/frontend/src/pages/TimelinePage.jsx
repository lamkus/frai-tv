import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Calendar, Filter } from 'lucide-react';
import { cn } from '../lib/utils';
import { useApp } from '../context/AppContext';
import { DECADES, CATEGORIES, MILESTONE_TYPES, sortVideos } from '../data/remaikeData';
import VideoCard from '../components/video/VideoCard';

/**
 * TimelinePage - Visuelle Timeline durch die Tech-Geschichte
 *
 * Features:
 * - Horizontale Timeline mit Jahrzehnten
 * - Filter nach Kategorie und Milestone-Typ
 * - Responsive Grid für Videos
 */
export default function TimelinePage() {
  const { t } = useTranslation();
  const { videos } = useApp();
  const [selectedDecade, setSelectedDecade] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [selectedMilestone, setSelectedMilestone] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  // Filter videos based on selection
  const filteredVideos = useMemo(() => {
    let filtered = [...videos];

    // Apply decade filter
    if (selectedDecade) {
      const decade = DECADES.find((d) => d.id === selectedDecade);
      if (decade) {
        filtered = filtered.filter((v) => {
          // Only use historical year, do NOT fallback to upload date for timeline
          const year = v.year;
          return year && year >= decade.range[0] && year <= decade.range[1];
        });
      }
    }

    // Apply category filter
    if (selectedCategory) {
      filtered = filtered.filter((v) => v.category === selectedCategory);
    }

    // Apply milestone filter
    if (selectedMilestone) {
      filtered = filtered.filter((v) => v.milestones && v.milestones.includes(selectedMilestone));
    }

    // Sort by year (oldest first for timeline view)
    // Filter out videos without year for the timeline view to avoid confusion
    return sortVideos(
      filtered.filter((v) => v.year),
      'year',
      'asc'
    );
  }, [videos, selectedDecade, selectedCategory, selectedMilestone]);

  // Group videos by decade for display
  const videosByDecade = useMemo(() => {
    const groups = {};

    filteredVideos.forEach((video) => {
      // Only use historical year
      const year = video.year;
      if (!year) return;

      const decade = DECADES.find((d) => year >= d.range[0] && year <= d.range[1]);
      const decadeId = decade?.id || 'unknown';

      if (!groups[decadeId]) {
        groups[decadeId] = [];
      }
      groups[decadeId].push(video);
    });

    return groups;
  }, [filteredVideos]);

  const clearFilters = () => {
    setSelectedDecade(null);
    setSelectedCategory(null);
    setSelectedMilestone(null);
  };

  const hasActiveFilters = selectedDecade || selectedCategory || selectedMilestone;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-retro-darker/95 backdrop-blur-sm border-b border-retro-gray">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-fluid-2xl font-display">
              <Calendar className="inline-block mr-2 text-accent-cyan" size={28} />
              {t('timelinePage.title')}
            </h1>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className={cn('btn btn-secondary text-sm', showFilters && 'bg-accent-cyan/20')}
            >
              <Filter size={18} />
              {t('timelinePage.filter')}
              {hasActiveFilters && <span className="ml-2 w-2 h-2 bg-accent-red rounded-full" />}
            </button>
          </div>

          {/* Decade Navigation */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-thin">
            <button
              onClick={() => setSelectedDecade(null)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                !selectedDecade
                  ? 'bg-accent-red text-white'
                  : 'bg-retro-gray/50 text-retro-muted hover:text-white'
              )}
            >
              {t('timelinePage.allTimes')}
            </button>

            {DECADES.map((decade) => (
              <button
                key={decade.id}
                onClick={() => setSelectedDecade(decade.id)}
                className={cn(
                  'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-2',
                  selectedDecade === decade.id
                    ? 'bg-accent-red text-white'
                    : 'bg-retro-gray/50 text-retro-muted hover:text-white'
                )}
              >
                <span>{decade.icon}</span>
                <span>{decade.label}</span>
              </button>
            ))}
          </div>

          {/* Filter Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-retro-dark rounded-lg animate-in slide-in-from-top-2 duration-200">
              <div className="flex flex-wrap gap-6">
                {/* Category Filter */}
                <div>
                  <h3 className="text-xs font-semibold text-retro-muted uppercase mb-2">
                    {t('timelinePage.category')}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {CATEGORIES.map((cat) => (
                      <button
                        key={cat.id}
                        onClick={() =>
                          setSelectedCategory(selectedCategory === cat.id ? null : cat.id)
                        }
                        className={cn(
                          'px-3 py-1.5 rounded text-xs font-medium transition-colors',
                          selectedCategory === cat.id
                            ? 'bg-accent-cyan text-white'
                            : 'bg-retro-gray/50 text-retro-muted hover:text-white'
                        )}
                      >
                        {cat.icon} {t(`categories.${cat.id}`)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Milestone Filter */}
                <div>
                  <h3 className="text-xs font-semibold text-retro-muted uppercase mb-2">
                    {t('timelinePage.milestoneType')}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {MILESTONE_TYPES.slice(0, 6).map((ms) => (
                      <button
                        key={ms.id}
                        onClick={() =>
                          setSelectedMilestone(selectedMilestone === ms.id ? null : ms.id)
                        }
                        className={cn(
                          'px-3 py-1.5 rounded text-xs font-medium transition-colors',
                          selectedMilestone === ms.id
                            ? 'bg-accent-purple text-white'
                            : 'bg-retro-gray/50 text-retro-muted hover:text-white'
                        )}
                      >
                        {ms.icon} {t(`milestoneTypes.${ms.id}`)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {hasActiveFilters && (
                <button
                  onClick={clearFilters}
                  className="mt-4 text-xs text-accent-red hover:underline"
                >
                  {t('timelinePage.resetAllFilters')}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Timeline Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {filteredVideos.length === 0 ? (
          <div className="text-center py-16">
            <Calendar className="mx-auto mb-4 text-retro-muted" size={48} />
            <h2 className="text-fluid-xl font-display mb-2">{t('timelinePage.noVideosFound')}</h2>
            <p className="text-retro-muted mb-4">{t('timelinePage.tryOtherFilters')}</p>
            {hasActiveFilters && (
              <button onClick={clearFilters} className="btn btn-secondary">
                {t('timelinePage.resetFilters')}
              </button>
            )}
          </div>
        ) : selectedDecade ? (
          // Single decade view - grid of videos
          <div>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {filteredVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          </div>
        ) : (
          // All decades view - grouped timeline
          <div className="space-y-12">
            {DECADES.map((decade) => {
              const decadeVideos = videosByDecade[decade.id] || [];
              if (decadeVideos.length === 0) return null;

              return (
                <section key={decade.id} className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-0 top-0 bottom-0 w-px bg-gradient-to-b from-accent-cyan via-accent-purple to-accent-red opacity-30" />

                  {/* Decade header */}
                  <div className="flex items-center gap-4 mb-6 pl-6">
                    <div className="absolute left-0 w-3 h-3 rounded-full bg-accent-cyan shadow-glow-cyan" />
                    <span className="text-3xl">{decade.icon}</span>
                    <div>
                      <h2 className="text-fluid-xl font-display">
                        {t(`decades.${decade.id}.label`)}
                      </h2>
                      <p className="text-sm text-retro-muted">
                        {t(`decades.${decade.id}.description`)}
                      </p>
                    </div>
                    <Link
                      to={`/browse?decade=${decade.id}`}
                      className="ml-auto text-sm text-accent-cyan hover:underline"
                    >
                      {t('timelinePage.showAll')} →
                    </Link>
                  </div>

                  {/* Videos grid */}
                  <div className="pl-6 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                    {decadeVideos.slice(0, 5).map((video) => (
                      <VideoCard key={video.id} video={video} size="sm" />
                    ))}

                    {decadeVideos.length > 5 && (
                      <Link
                        to={`/browse?decade=${decade.id}`}
                        className="aspect-video bg-retro-gray/30 rounded-lg flex items-center justify-center hover:bg-retro-gray/50 transition-colors group"
                      >
                        <span className="text-center">
                          <span className="block text-2xl font-bold text-accent-cyan group-hover:scale-110 transition-transform">
                            +{decadeVideos.length - 5}
                          </span>
                          <span className="text-xs text-retro-muted">{t('timelinePage.more')}</span>
                        </span>
                      </Link>
                    )}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Extrahiert Jahr aus ISO-Datum
 */
function extractYearFromDate(dateString) {
  if (!dateString) return null;
  const date = new Date(dateString);
  return date.getFullYear();
}
