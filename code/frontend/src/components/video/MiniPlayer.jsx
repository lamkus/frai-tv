import { useState, useEffect, useRef } from 'react';
import { X, Maximize2, Play, Pause } from 'lucide-react';
import { cn, getYouTubeEmbedUrl } from '../../lib/utils';
import { useApp } from '../../context/AppContext';

/**
 * MiniPlayer - Picture-in-Picture style player
 * Keeps video playing while browsing other pages.
 * Generates valid watch time.
 */
export default function MiniPlayer() {
  const { currentVideo, isMiniPlayerOpen, restorePlayer, closePlayer } = useApp();

  const [isPlaying, setIsPlaying] = useState(true);

  if (!isMiniPlayerOpen || !currentVideo) return null;

  const { title, ytId } = currentVideo;

  // Embed URL - Autoplay enabled, Mute disabled (0)
  const embedUrl = getYouTubeEmbedUrl(ytId, {
    autoplay: true,
    params: {
      mute: '0', // Force sound
      controls: '1',
      modestbranding: '1',
      rel: '0',
      fs: '0', // No fullscreen button in mini player
    },
  });

  return (
    <div className="fixed bottom-4 right-4 z-[100] w-80 sm:w-96 aspect-video bg-black rounded-xl shadow-2xl border border-white/10 overflow-hidden animate-in slide-in-from-bottom-10 fade-in duration-300 group">
      {/* Header / Controls Overlay */}
      <div className="absolute top-0 left-0 right-0 p-2 bg-gradient-to-b from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity z-10 flex justify-between items-start pointer-events-none">
        <div className="pointer-events-auto flex gap-2 ml-auto">
          <button
            onClick={restorePlayer}
            className="p-1.5 rounded-full bg-black/60 text-white hover:bg-accent-gold hover:text-black transition-colors"
            title="Vergrößern"
          >
            <Maximize2 size={14} />
          </button>
          <button
            onClick={closePlayer}
            className="p-1.5 rounded-full bg-black/60 text-white hover:bg-red-500 transition-colors"
            title="Schließen"
          >
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Video Frame */}
      <iframe
        src={embedUrl}
        title={title}
        className="w-full h-full"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        frameBorder="0"
      />

      {/* Title Overlay (Bottom) */}
      <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/90 to-transparent pointer-events-none">
        <p className="text-xs font-medium text-white line-clamp-1">{title}</p>
      </div>
    </div>
  );
}
