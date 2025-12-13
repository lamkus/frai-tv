import { useState, useMemo, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Play, Clock, Calendar, Newspaper } from 'lucide-react';
import { cn, getYouTubeThumbnail, formatDuration } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { CATEGORIES, DECADES } from '../../data/remaikeData';

/**
 * TVGuide - TV-Programmzeitschrift-Style Navigator
 *
 * ⚠️ EXPERIMENTAL FEATURE - Desktop optimiert
 *
 * Instead of time slots, we use categories as "channels"
 * and decades/years as the time axis.
 *
 * Features:
 * - Grid layout like a TV guide
 * - Categories as rows (channels)
 * - Decades/Years as columns
 * - Hover for quick preview (cursor-following on desktop)
 * - Click to play
 * - Mobile: simplified list view
 */
export default function TVGuide({ className }) {
  const { videos, openPlayer } = useApp();
  const [selectedDecade, setSelectedDecade] = useState('all');
  const [hoveredVideo, setHoveredVideo] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  // Detect mobile/touch device
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768 || 'ontouchstart' in window);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Track mouse position for cursor-following preview
  const handleMouseMove = (e) => {
    if (isMobile) return;
    setMousePosition({
      x: e.clientX,
      y: e.clientY,
    });
  };

  // Group videos by category and decade
  const videoGrid = useMemo(() => {
    const grid = {};

    CATEGORIES.forEach((cat) => {
      grid[cat.id] = {};
      DECADES.forEach((dec) => {
        grid[cat.id][dec.id] = [];
      });
    });

    videos.forEach((video) => {
      // Strict categorization and dating
      const cat = video.category || 'media';

      // Only use historical year, ignore upload date for historical accuracy
      if (!video.year) return;

      const year = video.year;
      const decade = DECADES.find((d) => year >= d.range[0] && year <= d.range[1]);

      if (grid[cat] && decade) {
        grid[cat][decade.id].push(video);
      }
    });

    return grid;
  }, [videos]);

  // Get visible decades
  const visibleDecades =
    selectedDecade === 'all' ? DECADES : DECADES.filter((d) => d.id === selectedDecade);

  return (
    <div
      ref={containerRef}
      className={cn('bg-retro-darker rounded-xl overflow-hidden', className)}
      onMouseMove={handleMouseMove}
    >
      {/* Experimental Banner */}
      <div className="bg-accent-amber/10 border-b border-accent-amber/30 px-4 py-2">
        <p className="text-xs text-accent-amber text-center">
          ⚡ Experimentelles Feature – Desktop optimiert
        </p>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-retro-gray/30">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          <Newspaper className="text-accent-amber" size={24} />
          TV Guide
        </h2>

        {/* Decade Filter */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setSelectedDecade('all')}
            className={cn(
              'px-3 py-1.5 rounded-lg text-sm transition-colors',
              selectedDecade === 'all'
                ? 'bg-accent-amber text-black'
                : 'bg-retro-dark text-retro-muted hover:text-white'
            )}
          >
            All
          </button>
          {DECADES.slice(-4).map((dec) => (
            <button
              key={dec.id}
              onClick={() => setSelectedDecade(dec.id)}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm transition-colors',
                selectedDecade === dec.id
                  ? 'bg-accent-amber text-black'
                  : 'bg-retro-dark text-retro-muted hover:text-white'
              )}
            >
              {dec.icon} {dec.label}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          {/* Decade Headers */}
          <thead>
            <tr className="bg-retro-dark">
              <th className="sticky left-0 z-10 bg-retro-dark p-3 text-left text-sm font-medium text-retro-muted w-40">
                Category
              </th>
              {visibleDecades.map((dec) => (
                <th
                  key={dec.id}
                  className="p-3 text-center text-sm font-medium text-white min-w-[200px]"
                >
                  <span className="flex items-center justify-center gap-2">
                    <span>{dec.icon}</span>
                    <span>{dec.label}</span>
                  </span>
                  <span className="text-xs text-retro-muted">
                    {dec.range[0]}–{dec.range[1]}
                  </span>
                </th>
              ))}
            </tr>
          </thead>

          {/* Category Rows */}
          <tbody>
            {CATEGORIES.map((cat) => (
              <tr key={cat.id} className="border-t border-retro-gray/20">
                {/* Category Label */}
                <td className="sticky left-0 z-10 bg-retro-darker p-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{cat.icon}</span>
                    <div>
                      <p className="font-medium text-white text-sm">{cat.label}</p>
                      <p className="text-xs text-retro-muted">
                        {countCategoryVideos(videoGrid, cat.id)} videos
                      </p>
                    </div>
                  </div>
                </td>

                {/* Decade Cells */}
                {visibleDecades.map((dec) => {
                  const cellVideos = videoGrid[cat.id]?.[dec.id] || [];

                  return (
                    <td key={dec.id} className="p-2 align-top">
                      <div className="flex flex-wrap gap-2">
                        {cellVideos.slice(0, 3).map((video) => (
                          <div
                            key={video.id}
                            className="relative group cursor-pointer"
                            onMouseEnter={() => setHoveredVideo(video)}
                            onMouseLeave={() => setHoveredVideo(null)}
                            onClick={() => openPlayer(video)}
                          >
                            <div className="w-16 h-16 rounded overflow-hidden">
                              <img
                                src={
                                  video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'default')
                                }
                                alt=""
                                className="w-full h-full object-cover group-hover:scale-110 transition-transform"
                              />
                            </div>

                            {/* Play overlay */}
                            <div className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Play size={16} className="text-white" fill="white" />
                            </div>
                          </div>
                        ))}

                        {cellVideos.length > 3 && (
                          <Link
                            to={`/browse?category=${cat.id}&decade=${dec.id}`}
                            className="w-16 h-16 rounded bg-retro-dark flex items-center justify-center text-xs text-retro-muted hover:text-white hover:bg-retro-gray transition-colors"
                          >
                            +{cellVideos.length - 3}
                          </Link>
                        )}

                        {cellVideos.length === 0 && (
                          <div className="w-16 h-16 rounded bg-retro-dark/50 flex items-center justify-center">
                            <span className="text-retro-muted text-xs">—</span>
                          </div>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Hover Preview - Cursor following on Desktop, hidden on Mobile */}
      {hoveredVideo && !isMobile && (
        <div
          className="fixed z-50 w-72 bg-retro-dark/95 backdrop-blur rounded-xl shadow-2xl border border-accent-amber/30 overflow-hidden pointer-events-none"
          style={{
            left: Math.min(mousePosition.x + 20, window.innerWidth - 300),
            top: Math.min(mousePosition.y - 100, window.innerHeight - 250),
            transform: 'translateZ(0)', // GPU acceleration
          }}
        >
          <img
            src={hoveredVideo.thumbnailUrl || getYouTubeThumbnail(hoveredVideo.ytId, 'high')}
            alt=""
            className="w-full aspect-video object-cover"
          />
          <div className="p-3">
            <h3 className="font-semibold text-white truncate text-sm">{hoveredVideo.title}</h3>
            <div className="flex items-center gap-3 mt-1.5 text-xs text-retro-muted">
              {hoveredVideo.year && (
                <span className="flex items-center gap-1">
                  <Calendar size={12} />
                  {hoveredVideo.year}
                </span>
              )}
              {hoveredVideo.duration && (
                <span className="flex items-center gap-1">
                  <Clock size={12} />
                  {formatDuration(hoveredVideo.duration)}
                </span>
              )}
            </div>
            <p className="text-xs text-accent-amber mt-2">Klicken zum Abspielen</p>
          </div>
        </div>
      )}

      {/* Mobile Warning Banner */}
      {isMobile && (
        <div className="p-4 bg-accent-amber/10 border-t border-accent-amber/30">
          <p className="text-xs text-center text-accent-amber">
            📱 TV Guide ist für Desktop optimiert. Für Mobile nutze die Mediathek.
          </p>
        </div>
      )}
    </div>
  );
}

/**
 * Count videos in a category
 */
function countCategoryVideos(grid, categoryId) {
  if (!grid[categoryId]) return 0;
  return Object.values(grid[categoryId]).reduce((sum, arr) => sum + arr.length, 0);
}
