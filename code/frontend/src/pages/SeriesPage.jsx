import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Play, ChevronLeft, Film, Grid3x3, List, Sparkles } from 'lucide-react';
import { cn, getYouTubeThumbnail } from '../lib/utils';
import useMeta from '../lib/useMeta';
import { useApp } from '../context/AppContext';

// Series metadata with icons and colors
const SERIES_META = {
  superman: {
    name: 'Superman',
    icon: '🦸',
    color: '#0066CC',
    studio: 'Fleischer Studios',
    years: '1941-1943',
    description: 'Die legendären Max Fleischer Superman Cartoons - Meilensteine der Animation.',
  },
  popeye: {
    name: 'Popeye',
    icon: '⚓',
    color: '#003366',
    studio: 'Fleischer Studios',
    years: '1930s-1950s',
    description: 'Der stärkste Seemann der Welt und sein Spinat-Power!',
  },
  'betty-boop': {
    name: 'Betty Boop',
    icon: '💋',
    color: '#CC0000',
    studio: 'Fleischer Studios',
    years: '1930s',
    description: 'Die Jazz-Age Cartoon-Queen - Boop-Oop-a-Doop!',
  },
  casper: {
    name: 'Casper',
    icon: '👻',
    color: '#6699CC',
    studio: 'Famous Studios',
    years: '1940s-1950s',
    description: 'Der freundliche Geist und seine Abenteuer.',
  },
  felix: {
    name: 'Felix the Cat',
    icon: '🐱',
    color: '#333333',
    studio: 'Pat Sullivan Studios',
    years: '1919-1930s',
    description: 'Der erste Cartoon-Superstar der Filmgeschichte.',
  },
  chaplin: {
    name: 'Charlie Chaplin',
    icon: '🎩',
    color: '#1A1A1A',
    studio: 'Various',
    years: '1910s-1920s',
    description: 'Der Tramp - Ikone der Stummfilm-Ära.',
  },
  keaton: {
    name: 'Buster Keaton',
    icon: '😐',
    color: '#4A4A4A',
    studio: 'Various',
    years: '1920s',
    description: 'Das große Steingesicht - Meister des Physical Comedy.',
  },
  'looney-tunes': {
    name: 'Looney Tunes',
    icon: '🐰',
    color: '#FF6600',
    studio: 'Warner Bros.',
    years: '1930s-1960s',
    description: 'Bugs Bunny, Daffy Duck und die ganze Bande.',
  },
  sherlock: {
    name: 'Sherlock Holmes',
    icon: '🔍',
    color: '#8B4513',
    studio: 'Various',
    years: '1930s-1940s',
    description: 'Der weltberühmte Detektiv aus der Baker Street.',
  },
  tarzan: {
    name: 'Tarzan',
    icon: '🌴',
    color: '#228B22',
    studio: 'Various',
    years: '1930s-1940s',
    description: 'Der Herr des Dschungels.',
  },
};

// Clean video title
const cleanTitle = (title) => {
  if (!title) return '';
  return title
    .replace(/\s*\|\s*(4K|8K|HD|4k|8k|hd)\s*/gi, '')
    .replace(/\s*\((4K|8K|HD|4k|8k|hd)\)\s*/gi, '')
    .replace(/\s*(4K|8K|HD|4k|8k|hd)$/gi, '')
    .replace(/\s+\|\s*$/g, '')
    .trim();
};

/**
 * SeriesPage - Displays all series or a specific series with its videos
 */
export default function SeriesPage() {
  const { seriesId } = useParams();
  const { openPlayer, videos: allVideos } = useApp();

  const [seriesData, setSeriesData] = useState(null);
  const [allSeries, setAllSeries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  useMeta({
    title: seriesId
      ? `${SERIES_META[seriesId]?.name || seriesId} | remAIke.TV`
      : 'Serien | remAIke.TV',
    description: seriesId
      ? SERIES_META[seriesId]?.description
      : 'Klassische Serien und Cartoon-Collections',
  });

  // Fallback: Client-side series grouping
  const fallbackGrouping = useCallback(() => {
    if (!allVideos || allVideos.length === 0) {
      return;
    }

    const seriesPatterns = [
      { id: 'superman', pattern: /\bsuperman\b/i },
      { id: 'popeye', pattern: /\bpopeye\b/i },
      { id: 'betty-boop', pattern: /\bbetty\s*boop\b/i },
      { id: 'casper', pattern: /\bcasper\b/i },
      { id: 'felix', pattern: /\bfelix\s*(the)?\s*cat\b/i },
      { id: 'chaplin', pattern: /\b(charlie\s*)?chaplin\b/i },
      { id: 'keaton', pattern: /\bbuster\s*keaton\b/i },
      { id: 'looney-tunes', pattern: /\b(looney\s*tunes|bugs\s*bunny|daffy)\b/i },
      { id: 'sherlock', pattern: /\bsherlock\s*holmes\b/i },
      { id: 'tarzan', pattern: /\btarzan\b/i },
    ];

    const grouped = {};
    allVideos.forEach((video) => {
      for (const series of seriesPatterns) {
        if (series.pattern.test(video.title || '')) {
          if (!grouped[series.id]) {
            grouped[series.id] = {
              id: series.id,
              name: SERIES_META[series.id]?.name || series.id,
              videos: [],
            };
          }
          grouped[series.id].videos.push(video);
          break;
        }
      }
    });

    if (seriesId) {
      setSeriesData(grouped[seriesId] || { id: seriesId, name: seriesId, videos: [] });
    } else {
      setAllSeries(Object.values(grouped).filter((s) => s.videos.length > 0));
    }
  }, [allVideos, seriesId]);

  // Fetch series data from API
  useEffect(() => {
    const fetchSeries = async () => {
      setLoading(true);

      try {
        if (seriesId) {
          // Fetch specific series
          const res = await fetch(`/api/series/${seriesId}`);
          if (!res.ok) throw new Error('Series not found');
          const json = await res.json();
          setSeriesData(json.data);
        } else {
          // Fetch all series
          const res = await fetch('/api/series');
          if (!res.ok) throw new Error('Failed to fetch series');
          const json = await res.json();
          setAllSeries(json.data?.series || []);
        }
      } catch (err) {
        console.error('Series fetch error:', err);
        // Fallback: Group videos from context by series patterns
        fallbackGrouping();
      } finally {
        setLoading(false);
      }
    };

    fetchSeries();
  }, [seriesId, fallbackGrouping]);

  // Series card for overview
  const SeriesCard = ({ series }) => {
    const meta = SERIES_META[series.id] || {};
    const videoCount = series.videos?.length || 0;
    const thumbnail =
      series.videos?.[0]?.thumbnail ||
      series.videos?.[0]?.thumbnailUrl ||
      (series.videos?.[0]?.ytId && getYouTubeThumbnail(series.videos[0].ytId, 'high'));

    return (
      <Link
        to={`/series/${series.id}`}
        className={cn(
          'group relative rounded-xl overflow-hidden',
          'bg-gradient-to-br from-retro-darker to-retro-black',
          'border border-white/10 hover:border-accent-gold/50',
          'transition-all duration-300',
          'hover:scale-[1.02] hover:shadow-xl hover:shadow-accent-gold/20'
        )}
      >
        {/* Thumbnail Background */}
        <div className="relative aspect-video">
          {thumbnail ? (
            <img
              src={thumbnail}
              alt={series.name}
              className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity"
            />
          ) : (
            <div
              className="w-full h-full flex items-center justify-center text-6xl"
              style={{ backgroundColor: meta.color || '#333' }}
            >
              {meta.icon || '🎬'}
            </div>
          )}

          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />

          {/* Series Info */}
          <div className="absolute bottom-0 left-0 right-0 p-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-2xl">{meta.icon || '🎬'}</span>
              <h3 className="text-xl font-bold text-white">{series.name || meta.name}</h3>
            </div>
            <p className="text-sm text-white/70">
              {meta.studio} • {meta.years}
            </p>
            <p className="text-sm text-accent-gold font-medium mt-1">
              {videoCount} {videoCount === 1 ? 'Video' : 'Videos'}
            </p>
          </div>

          {/* Play Icon on Hover */}
          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="w-16 h-16 rounded-full bg-accent-gold/90 flex items-center justify-center">
              <Play size={32} className="text-black ml-1" fill="currentColor" />
            </div>
          </div>
        </div>
      </Link>
    );
  };

  // Video card for series detail
  const VideoCard = ({ video, index }) => {
    const thumbnail =
      video.thumbnail || video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'high');

    return (
      <div
        className={cn(
          'group relative rounded-lg overflow-hidden cursor-pointer',
          'bg-retro-darker border border-white/10',
          'hover:border-accent-gold/50 hover:shadow-lg hover:shadow-accent-gold/10',
          'transition-all duration-200'
        )}
        onClick={() => openPlayer(video)}
      >
        {/* Thumbnail */}
        <div className="relative aspect-video">
          <img src={thumbnail} alt={video.title} className="w-full h-full object-cover" />

          {/* Episode Number Badge */}
          <div className="absolute top-2 left-2 px-2 py-1 bg-black/80 rounded text-xs font-bold text-accent-gold">
            #{index + 1}
          </div>

          {/* Year Badge */}
          {video.year && (
            <div className="absolute top-2 right-2 px-2 py-1 bg-black/80 rounded text-xs text-white/80">
              {video.year}
            </div>
          )}

          {/* Play Overlay */}
          <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/40 transition-colors">
            <div className="w-12 h-12 rounded-full bg-accent-gold/0 group-hover:bg-accent-gold/90 flex items-center justify-center transition-all scale-0 group-hover:scale-100">
              <Play size={24} className="text-black ml-0.5" fill="currentColor" />
            </div>
          </div>
        </div>

        {/* Info */}
        <div className="p-3">
          <h4 className="text-sm font-medium text-white line-clamp-2 group-hover:text-accent-gold transition-colors">
            {cleanTitle(video.title)}
          </h4>
          {video.description && (
            <p className="text-xs text-white/50 mt-1 line-clamp-2">{video.description}</p>
          )}
        </div>
      </div>
    );
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-retro-black px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-white/10 rounded w-48" />
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="aspect-video bg-white/10 rounded-lg" />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Series Detail View
  if (seriesId) {
    if (!seriesData) {
      return (
        <div className="min-h-screen bg-retro-black px-4 py-8 flex items-center justify-center">
          <div className="text-center">
            <Film size={48} className="mx-auto text-white/30 mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Serie nicht gefunden</h2>
            <p className="text-white/60 mb-4">
              Die gesuchte Serie &quot;{seriesId}&quot; existiert nicht.
            </p>
            <Link to="/series" className="text-accent-gold hover:underline">
              Zurück zur Übersicht
            </Link>
          </div>
        </div>
      );
    }

    const meta = SERIES_META[seriesId] || {};
    const videos = seriesData.videos || [];

    return (
      <div className="min-h-screen bg-retro-black">
        {/* Hero Header */}
        <div
          className="relative py-12 px-4"
          style={{
            background: `linear-gradient(to bottom, ${meta.color || '#333'}20, transparent)`,
          }}
        >
          <div className="max-w-7xl mx-auto">
            {/* Back Link */}
            <Link
              to="/series"
              className="inline-flex items-center gap-2 text-white/60 hover:text-white mb-6 transition-colors"
            >
              <ChevronLeft size={20} />
              <span>Alle Serien</span>
            </Link>

            {/* Series Info */}
            <div className="flex items-start gap-6">
              <div
                className="w-24 h-24 rounded-xl flex items-center justify-center text-5xl flex-shrink-0"
                style={{ backgroundColor: meta.color || '#333' }}
              >
                {meta.icon || '🎬'}
              </div>
              <div>
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                  {meta.name || seriesData.name}
                </h1>
                <p className="text-white/60 mb-2">
                  {meta.studio} • {meta.years}
                </p>
                <p className="text-white/80 max-w-2xl">{meta.description}</p>
                <p className="text-accent-gold font-medium mt-3">
                  {videos.length} {videos.length === 1 ? 'Video' : 'Videos'} verfügbar
                </p>
              </div>
            </div>

            {/* View Toggle */}
            <div className="flex items-center gap-2 mt-6">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  viewMode === 'grid'
                    ? 'bg-accent-gold text-black'
                    : 'bg-white/10 text-white/60 hover:bg-white/20'
                )}
              >
                <Grid3x3 size={20} />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  viewMode === 'list'
                    ? 'bg-accent-gold text-black'
                    : 'bg-white/10 text-white/60 hover:bg-white/20'
                )}
              >
                <List size={20} />
              </button>
            </div>
          </div>
        </div>

        {/* Videos Grid */}
        <div className="max-w-7xl mx-auto px-4 pb-12">
          {videos.length === 0 ? (
            <div className="text-center py-12">
              <Film size={48} className="mx-auto text-white/30 mb-4" />
              <p className="text-white/60">Keine Videos in dieser Serie gefunden.</p>
            </div>
          ) : (
            <div
              className={cn(
                viewMode === 'grid'
                  ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4'
                  : 'space-y-3'
              )}
            >
              {videos.map((video, index) =>
                viewMode === 'grid' ? (
                  <VideoCard key={video.id || video.ytId} video={video} index={index} />
                ) : (
                  <div
                    key={video.id || video.ytId}
                    className="flex gap-4 p-3 rounded-lg bg-retro-darker hover:bg-white/5 cursor-pointer transition-colors"
                    onClick={() => openPlayer(video)}
                  >
                    <img
                      src={
                        video.thumbnail ||
                        video.thumbnailUrl ||
                        getYouTubeThumbnail(video.ytId, 'medium')
                      }
                      alt=""
                      className="w-40 aspect-video object-cover rounded"
                    />
                    <div className="flex-1 min-w-0">
                      <span className="text-accent-gold text-sm font-bold">#{index + 1}</span>
                      <h4 className="text-white font-medium mt-1">{cleanTitle(video.title)}</h4>
                      <p className="text-white/50 text-sm mt-1">{video.year}</p>
                    </div>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Series Overview (all series)
  return (
    <div className="min-h-screen bg-retro-black px-4 py-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Sparkles className="text-accent-gold" size={28} />
            <h1 className="text-3xl font-bold text-white">Serien & Collections</h1>
          </div>
          <p className="text-white/60">
            Klassische Cartoon-Serien und Film-Collections - chronologisch sortiert
          </p>
        </div>

        {/* Series Grid */}
        {allSeries.length === 0 ? (
          <div className="text-center py-12">
            <Film size={48} className="mx-auto text-white/30 mb-4" />
            <p className="text-white/60">Keine Serien gefunden.</p>
            <Link to="/mediathek" className="text-accent-gold hover:underline mt-2 inline-block">
              Zur Mediathek →
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {allSeries
              .sort((a, b) => (b.videos?.length || 0) - (a.videos?.length || 0))
              .map((series) => (
                <SeriesCard key={series.id} series={series} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
