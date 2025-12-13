import { Play, Info, Clock, TrendingUp } from 'lucide-react';
import { getYouTubeThumbnail } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import VideoListItem from '../ui/VideoListItem';
import useVideoI18n from '../../lib/useVideoI18n';

export default function DashboardHero({ featuredVideo, sideVideos = [] }) {
  const { openPlayer } = useApp();
  const { getVideoText } = useVideoI18n();

  if (!featuredVideo) return null;

  const { ytId, category, thumbnailUrl, publishDate } = featuredVideo;
  const { title, description } = getVideoText(featuredVideo);
  const backgroundImage = thumbnailUrl || getYouTubeThumbnail(ytId, 'maxres');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-4 sm:p-6 lg:p-8 lg:h-[85vh] max-h-[1000px] min-h-[600px]">
      {/* Main Hero (2/3 width) */}
      <div className="lg:col-span-2 relative rounded-2xl overflow-hidden group shadow-2xl border border-retro-gray/20 bg-retro-dark">
        {/* Background */}
        <div className="absolute inset-0">
          <img
            src={backgroundImage}
            alt={title}
            className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-60 group-hover:opacity-40"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-retro-black via-retro-black/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-retro-black/80 via-transparent to-transparent" />
        </div>

        {/* Content */}
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8 lg:p-12 flex flex-col justify-end h-full">
          <div className="transform transition-transform duration-500 translate-y-4 group-hover:translate-y-0">
            <div className="flex items-center gap-3 mb-4">
              <span className="badge badge-year bg-accent-red text-white border-none px-3 py-1 text-sm">
                NEU
              </span>
              <span className="badge badge-year">{category}</span>
              {publishDate && (
                <span className="text-retro-muted text-sm flex items-center gap-1">
                  <Clock size={14} />
                  {new Date(publishDate).toLocaleDateString('de-DE')}
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-5xl xl:text-6xl font-display text-white mb-4 drop-shadow-lg leading-tight max-w-4xl">
              {title}
            </h1>

            <p className="text-base sm:text-lg text-retro-white/90 line-clamp-2 sm:line-clamp-3 max-w-2xl mb-8 drop-shadow-md">
              {description}
            </p>

            <div className="flex flex-wrap gap-4 opacity-0 group-hover:opacity-100 transition-opacity duration-500 delay-100">
              <button
                onClick={() => openPlayer(featuredVideo)}
                className="btn btn-primary px-6 py-3 sm:px-8 sm:py-4 text-base sm:text-lg shadow-neon-red hover:scale-105 transition-transform"
              >
                <Play className="mr-2 w-5 h-5 sm:w-6 sm:h-6" fill="currentColor" />
                Jetzt ansehen
              </button>
              <button className="btn btn-secondary px-6 py-3 sm:px-8 sm:py-4 text-base sm:text-lg hover:bg-white/10">
                <Info className="mr-2 w-5 h-5 sm:w-6 sm:h-6" />
                Details
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Side List (1/3 width) */}
      <div className="lg:col-span-1 bg-retro-darker/80 backdrop-blur-sm rounded-2xl border border-retro-gray/20 p-6 flex flex-col h-full overflow-hidden shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-display flex items-center gap-2 text-white">
            <TrendingUp className="text-accent-cyan" size={24} />
            Aktuelle Uploads
          </h3>
          <span className="text-xs font-mono text-retro-muted bg-retro-gray/20 px-2 py-1 rounded">
            LAST 5
          </span>
        </div>

        <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
          {sideVideos.map((video, index) => (
            <div key={video.id || index} className="relative group/item">
              <div className="absolute -left-2 top-1/2 -translate-y-1/2 w-1 h-0 bg-accent-cyan transition-all duration-300 group-hover/item:h-12 rounded-r-full" />
              <VideoListItem
                video={video}
                className="bg-retro-dark/40 hover:bg-retro-gray/20 p-3 border border-transparent hover:border-retro-gray/30 transition-all"
              />
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-retro-gray/20 text-center">
          <button className="text-sm text-retro-muted hover:text-white transition-colors uppercase tracking-widest font-bold">
            Alle neuen Videos anzeigen
          </button>
        </div>
      </div>
    </div>
  );
}
