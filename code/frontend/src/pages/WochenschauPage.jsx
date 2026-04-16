import { useState, useMemo, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Film, Calendar, ChevronRight, Play, AlertTriangle, Clock, ExternalLink, Youtube } from 'lucide-react';
import { cn, formatDuration, getYouTubeThumbnail } from '../lib/utils';
import { useApp } from '../context/AppContext';
// VideoCard available for future use

/**
 * WochenschauPage - Deutsche Wochenschau Archiv
 *
 * The world's largest 8K-restored Wochenschau archive.
 * Filters all Wochenschau episodes from remaikeData, sorts chronologically,
 * and displays them in a timeline grouped by year (1939-1945).
 */

// Extract episode number from title like "Wochenschau 474: Fall of Warsaw..."
function extractEpisodeNumber(title) {
  const match = title.match(/Wochenschau\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
}

// Extract date from title like "... (04.10.1939) ..."
function extractDateFromTitle(title) {
  const match = title.match(/\((\d{2})\.(\d{2})\.(\d{4})\)/);
  if (match) {
    return `${match[1]}.${match[2]}.${match[3]}`;
  }
  return null;
}

// Extract event name from title like "Wochenschau 474: Fall of Warsaw (04.10.1939) | 8K..."
function extractEventName(title) {
  const match = title.match(/Wochenschau\s+\d+:\s*(.+?)(?:\s*\(|\s*\|)/);
  return match ? match[1].trim() : title;
}

// Year range for the Wochenschau archive
const WOCHENSCHAU_YEARS = [1939, 1940, 1941, 1942, 1943, 1944, 1945];

export default function WochenschauPage() {
  const { t } = useTranslation();
  const { videos, openPlayer } = useApp();
  const [selectedYear, setSelectedYear] = useState(null);

  // Set page title and meta tags
  useEffect(() => {
    document.title = t('wochenschauPage.metaTitle', { defaultValue: 'Deutsche Wochenschau Archiv | FRai.TV' });

    // Set meta description
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.setAttribute('name', 'description');
      document.head.appendChild(metaDesc);
    }
    metaDesc.setAttribute('content', t('wochenschauPage.metaDescription', {
      defaultValue: 'Das groesste 8K-restaurierte Deutsche Wochenschau-Archiv der Welt. Alle Episoden 1939-1945, AI-remastered in 4K/8K UHD. Historische Dokumentation.'
    }));

    // Set Open Graph tags
    const ogTags = {
      'og:title': t('wochenschauPage.metaTitle', { defaultValue: 'Deutsche Wochenschau Archiv | FRai.TV' }),
      'og:description': t('wochenschauPage.metaDescription', { defaultValue: 'Das groesste 8K-restaurierte Deutsche Wochenschau-Archiv der Welt.' }),
      'og:type': 'website',
    };

    Object.entries(ogTags).forEach(([property, content]) => {
      let tag = document.querySelector(`meta[property="${property}"]`);
      if (!tag) {
        tag = document.createElement('meta');
        tag.setAttribute('property', property);
        document.head.appendChild(tag);
      }
      tag.setAttribute('content', content);
    });

    return () => {
      document.title = 'FRai.TV';
    };
  }, [t]);

  // Filter Wochenschau videos: title starts with "Wochenschau" + has episode number
  const wochenschauVideos = useMemo(() => {
    return videos.filter((v) => {
      const hasWochenschauTitle = /^(?:\u{1F195}\s*)?(?:4K\s+24\/7\s+)?Wochenschau(?:TV)?\s+\d+/iu.test(v.title);
      const isDocCategory = v.category === 'documentaries';
      const titleContainsWochenschau = v.title.toLowerCase().includes('wochenschau');
      // Include if title starts with "Wochenschau NNN" pattern, or is a documentary with Wochenschau in title
      return hasWochenschauTitle || (isDocCategory && titleContainsWochenschau);
    });
  }, [videos]);

  // Parse and sort by episode number
  const sortedVideos = useMemo(() => {
    return wochenschauVideos
      .map((v) => ({
        ...v,
        episodeNumber: extractEpisodeNumber(v.title),
        eventDate: extractDateFromTitle(v.title),
        eventName: extractEventName(v.title),
      }))
      .filter((v) => v.episodeNumber !== null) // Only include videos with valid episode numbers
      .sort((a, b) => a.episodeNumber - b.episodeNumber);
  }, [wochenschauVideos]);

  // Group by year
  const videosByYear = useMemo(() => {
    const groups = {};
    WOCHENSCHAU_YEARS.forEach((year) => {
      groups[year] = [];
    });

    sortedVideos.forEach((video) => {
      const year = video.year;
      if (year && groups[year] !== undefined) {
        groups[year].push(video);
      }
    });

    return groups;
  }, [sortedVideos]);

  // Stats
  const totalEpisodes = sortedVideos.length;
  const totalDuration = sortedVideos.reduce((sum, v) => sum + (v.duration || 0), 0);
  const totalHours = Math.floor(totalDuration / 3600);

  // Filtered videos for display
  const displayVideos = selectedYear
    ? videosByYear[selectedYear] || []
    : sortedVideos;

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#1a1205] via-[#0d0d0d] to-retro-darker" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0ibm9uZSIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNTAiIHI9IjEiIGZpbGw9IiNjOWE5NjIiIGZpbGwtb3BhY2l0eT0iMC4wNSIvPjwvc3ZnPg==')] opacity-40" />

        <div className="relative max-w-7xl mx-auto px-4 py-12 sm:py-16 lg:py-20">
          <div className="flex flex-col items-center text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-accent-gold/10 border border-accent-gold/30 mb-6">
              <Film size={16} className="text-accent-gold" />
              <span className="text-xs font-semibold text-accent-gold uppercase tracking-wider">
                {t('wochenschauPage.badge', { defaultValue: '8K AI-Remastered Archive' })}
              </span>
            </div>

            {/* Title */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-bold mb-4">
              <span className="text-white">{t('wochenschauPage.titlePart1', { defaultValue: 'Deutsche' })}</span>
              {' '}
              <span className="text-accent-gold">{t('wochenschauPage.titlePart2', { defaultValue: 'Wochenschau' })}</span>
              {' '}
              <span className="text-white">{t('wochenschauPage.titlePart3', { defaultValue: 'Archiv' })}</span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-retro-muted max-w-2xl mb-8">
              {t('wochenschauPage.subtitle', {
                defaultValue: 'Das groesste 8K-restaurierte Wochenschau-Archiv der Welt',
              })}
            </p>

            {/* Stats */}
            <div className="flex flex-wrap items-center justify-center gap-6 sm:gap-10 mb-8">
              <div className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-accent-gold">{totalEpisodes}</div>
                <div className="text-xs sm:text-sm text-retro-muted uppercase tracking-wider">
                  {t('wochenschauPage.episodes', { defaultValue: 'Episoden' })}
                </div>
              </div>
              <div className="w-px h-12 bg-retro-gray/30 hidden sm:block" />
              <div className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-accent-gold">{totalHours}h+</div>
                <div className="text-xs sm:text-sm text-retro-muted uppercase tracking-wider">
                  {t('wochenschauPage.totalDuration', { defaultValue: 'Filmmaterial' })}
                </div>
              </div>
              <div className="w-px h-12 bg-retro-gray/30 hidden sm:block" />
              <div className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-accent-gold">8K</div>
                <div className="text-xs sm:text-sm text-retro-muted uppercase tracking-wider">
                  {t('wochenschauPage.quality', { defaultValue: 'AI-Remastered' })}
                </div>
              </div>
              <div className="w-px h-12 bg-retro-gray/30 hidden sm:block" />
              <div className="text-center">
                <div className="text-3xl sm:text-4xl font-bold text-accent-gold">1939-45</div>
                <div className="text-xs sm:text-sm text-retro-muted uppercase tracking-wider">
                  {t('wochenschauPage.period', { defaultValue: 'Zeitraum' })}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-center gap-4">
              {sortedVideos.length > 0 && (
                <button
                  onClick={() => openPlayer && openPlayer(sortedVideos[0])}
                  className="inline-flex items-center gap-3 px-8 py-3.5 bg-white text-black font-bold rounded-lg hover:bg-white/90 transition-all transform hover:scale-105 shadow-xl"
                >
                  <Play size={20} fill="currentColor" />
                  {t('wochenschauPage.watchNow', { defaultValue: 'Jetzt ansehen' })}
                </button>
              )}
              <a
                href="https://www.youtube.com/@remAIke_IT/playlists"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-6 py-3.5 bg-red-600/90 hover:bg-red-600 text-white font-semibold rounded-lg transition-all border border-red-500/50"
              >
                <Youtube size={20} />
                {t('wochenschauPage.youtubePlaylist', { defaultValue: 'Zur YouTube Playlist' })}
                <ExternalLink size={14} className="opacity-60" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Disclaimer */}
      <div className="max-w-7xl mx-auto px-4 mb-8">
        <div className="flex items-start gap-3 p-4 rounded-lg bg-amber-900/20 border border-amber-700/40">
          <AlertTriangle size={20} className="text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-sm font-semibold text-amber-400 mb-1">
              {t('wochenschauPage.disclaimerTitle', { defaultValue: 'Historisches Dokument' })}
            </h3>
            <p className="text-xs text-amber-200/70 leading-relaxed">
              {t('wochenschauPage.disclaimerText', {
                defaultValue:
                  'Diese Videos zeigen Original-Material der NS-Propaganda-Wochenschau und dienen ausschliesslich der historischen Dokumentation und Bildung. Die dargestellten Inhalte spiegeln NICHT die Meinung des Kanalbetreibers wider. Alle Inhalte sind Public Domain und werden zu Bildungszwecken bereitgestellt.',
              })}
            </p>
          </div>
        </div>
      </div>

      {/* Year Navigation */}
      <div className="sticky top-0 z-10 bg-retro-darker/95 backdrop-blur-sm border-b border-retro-gray/30">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
            <button
              onClick={() => setSelectedYear(null)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors',
                !selectedYear
                  ? 'bg-accent-gold text-black'
                  : 'bg-retro-gray/50 text-retro-muted hover:text-white'
              )}
            >
              {t('wochenschauPage.allYears', { defaultValue: 'Alle Jahre' })}
              <span className="ml-2 text-xs opacity-70">({totalEpisodes})</span>
            </button>

            {WOCHENSCHAU_YEARS.map((year) => {
              const count = (videosByYear[year] || []).length;
              return (
                <button
                  key={year}
                  onClick={() => setSelectedYear(year)}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors flex items-center gap-2',
                    selectedYear === year
                      ? 'bg-accent-gold text-black'
                      : 'bg-retro-gray/50 text-retro-muted hover:text-white',
                    count === 0 && 'opacity-40 cursor-not-allowed'
                  )}
                  disabled={count === 0}
                >
                  <Calendar size={14} />
                  <span>{year}</span>
                  <span className="text-xs opacity-70">({count})</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {displayVideos.length === 0 ? (
          <div className="text-center py-16">
            <Film className="mx-auto mb-4 text-retro-muted" size={48} />
            <h2 className="text-fluid-xl font-display mb-2">
              {t('wochenschauPage.noEpisodes', { defaultValue: 'Keine Episoden gefunden' })}
            </h2>
            <p className="text-retro-muted">
              {t('wochenschauPage.selectYear', { defaultValue: 'Waehle ein anderes Jahr.' })}
            </p>
          </div>
        ) : selectedYear ? (
          /* Single year view - grid of video cards */
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-display text-white">
                <span className="text-accent-gold">{selectedYear}</span>
                <span className="text-retro-muted text-lg ml-3">
                  ({displayVideos.length} {t('wochenschauPage.episodes', { defaultValue: 'Episoden' })})
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {displayVideos.map((video) => (
                <WochenschauCard key={video.id} video={video} />
              ))}
            </div>
          </div>
        ) : (
          /* All years view - grouped timeline */
          <div className="space-y-12">
            {WOCHENSCHAU_YEARS.map((year) => {
              const yearVideos = videosByYear[year] || [];
              if (yearVideos.length === 0) return null;

              return (
                <section key={year} className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-0 top-0 bottom-0 w-px bg-gradient-to-b from-accent-gold via-amber-600 to-amber-800 opacity-30" />

                  {/* Year header */}
                  <div className="flex items-center gap-4 mb-6 pl-6">
                    <div className="absolute left-0 w-3 h-3 rounded-full bg-accent-gold shadow-lg shadow-accent-gold/30" />
                    <div>
                      <h2 className="text-3xl font-display font-bold text-accent-gold">{year}</h2>
                      <p className="text-sm text-retro-muted">
                        {yearVideos.length} {t('wochenschauPage.episodes', { defaultValue: 'Episoden' })}
                        {' | '}
                        {t('wochenschauPage.episodeRange', { defaultValue: 'Nr.' })}{' '}
                        {yearVideos[0]?.episodeNumber}
                        {yearVideos.length > 1 && ` - ${yearVideos[yearVideos.length - 1]?.episodeNumber}`}
                      </p>
                    </div>
                    <button
                      onClick={() => setSelectedYear(year)}
                      className="ml-auto text-sm text-accent-gold hover:underline flex items-center gap-1"
                    >
                      {t('wochenschauPage.showAll', { defaultValue: 'Alle anzeigen' })}
                      <ChevronRight size={14} />
                    </button>
                  </div>

                  {/* Videos grid - show first 4 */}
                  <div className="pl-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {yearVideos.slice(0, 4).map((video) => (
                      <WochenschauCard key={video.id} video={video} />
                    ))}

                    {yearVideos.length > 4 && (
                      <button
                        onClick={() => setSelectedYear(year)}
                        className="aspect-video bg-retro-gray/20 rounded-lg flex items-center justify-center hover:bg-retro-gray/30 transition-colors group border border-retro-gray/20"
                      >
                        <span className="text-center">
                          <span className="block text-2xl font-bold text-accent-gold group-hover:scale-110 transition-transform">
                            +{yearVideos.length - 4}
                          </span>
                          <span className="text-xs text-retro-muted">
                            {t('wochenschauPage.moreEpisodes', { defaultValue: 'weitere Episoden' })}
                          </span>
                        </span>
                      </button>
                    )}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom SEO section */}
      <div className="max-w-7xl mx-auto px-4 pb-12">
        <div className="border-t border-retro-gray/20 pt-8">
          <h2 className="text-lg font-display text-retro-muted mb-3">
            {t('wochenschauPage.aboutTitle', { defaultValue: 'Ueber das Deutsche Wochenschau Archiv' })}
          </h2>
          <p className="text-sm text-retro-muted/70 leading-relaxed max-w-3xl">
            {t('wochenschauPage.aboutText', {
              defaultValue:
                'Die Deutsche Wochenschau war eine Nachrichtenfilmreihe, die von 1939 bis 1945 woechentlich in deutschen Kinos gezeigt wurde. remAIke.IT hat diese historischen Dokumente in 8K-Qualitaet restauriert und stellt sie zu Bildungszwecken bereit. Jede Episode wurde mit modernster AI-Technologie remastered, um die bestmoegliche Bildqualitaet zu erzielen.',
            })}
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * WochenschauCard - Specialized card for Wochenschau episodes
 * Shows episode number, date, event name prominently
 */
function WochenschauCard({ video }) {
  // eslint-disable-next-line no-unused-vars
  const { playVideo, openInfoModal } = useApp();
  const thumbnail = video.thumbnail || getYouTubeThumbnail(video.ytId);

  return (
    <div className="group relative bg-retro-dark rounded-lg overflow-hidden border border-retro-gray/20 hover:border-accent-gold/40 transition-all duration-300 hover:shadow-lg hover:shadow-accent-gold/10">
      {/* Thumbnail */}
      <Link to={`/video/${video.ytId || video.id}`} className="block relative aspect-video overflow-hidden">
        <img
          src={thumbnail}
          alt={video.eventName || video.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        {/* Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

        {/* Play button on hover */}
        <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
          <div className="w-12 h-12 rounded-full bg-accent-gold/90 flex items-center justify-center">
            <Play size={20} className="text-black ml-0.5" fill="black" />
          </div>
        </div>

        {/* Episode badge */}
        <div className="absolute top-2 left-2 px-2 py-0.5 rounded bg-black/70 text-accent-gold text-xs font-bold">
          Nr. {video.episodeNumber}
        </div>

        {/* Duration */}
        {video.duration && (
          <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 text-white text-xs flex items-center gap-1">
            <Clock size={10} />
            {formatDuration(video.duration)}
          </div>
        )}
      </Link>

      {/* Info */}
      <div className="p-3">
        <div className="flex items-start justify-between gap-2 mb-1">
          <h3 className="text-sm font-semibold text-white line-clamp-2 leading-snug group-hover:text-accent-gold transition-colors">
            {video.eventName || video.title}
          </h3>
        </div>

        <div className="flex items-center gap-2 text-xs text-retro-muted">
          {video.eventDate && (
            <>
              <Calendar size={11} />
              <span>{video.eventDate}</span>
            </>
          )}
          {video.year && (
            <span className="ml-auto text-accent-gold/60">{video.year}</span>
          )}
        </div>
      </div>
    </div>
  );
}
