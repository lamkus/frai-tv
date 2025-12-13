import { useState, useEffect, useRef } from 'react';
import { Play, Pause, Save, Image as ImageIcon } from 'lucide-react';
import { cn } from '../../lib/utils';
import { CATEGORIES } from '../../data/remaikeData';

export default function ThumbnailGenerator({ videos }) {
  const [selectedVideoId, setSelectedVideoId] = useState('');
  const [player, setPlayer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isApiReady, setIsApiReady] = useState(false);
  const playerContainerRef = useRef(null);

  // Load YouTube API
  useEffect(() => {
    if (!window.YT) {
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
      window.onYouTubeIframeAPIReady = () => setIsApiReady(true);
    } else {
      setIsApiReady(true);
    }
  }, []);

  // Initialize Player when video selected
  useEffect(() => {
    if (!isApiReady || !selectedVideoId) return;

    // If player exists, load new video
    if (player) {
      player.loadVideoById(selectedVideoId);
      return;
    }

    // Create new player
    // We need to wait for the ref to be available in the DOM
    if (playerContainerRef.current) {
      new window.YT.Player(playerContainerRef.current, {
        height: '100%',
        width: '100%',
        videoId: selectedVideoId,
        playerVars: {
          controls: 0, // Hide default controls
          modestbranding: 1,
          rel: 0,
          iv_load_policy: 3, // Hide annotations
        },
        events: {
          onReady: (event) => {
            setDuration(event.target.getDuration());
            setPlayer(event.target);
          },
          onStateChange: (event) => {
            setIsPlaying(event.data === window.YT.PlayerState.PLAYING);
          },
        },
      });
    }

    // Cleanup
    return () => {
      // Don't destroy on unmount immediately to avoid flickering if re-rendering
      // But here we might want to if the component is removed
    };
  }, [isApiReady, selectedVideoId, player]);

  // Update time slider
  useEffect(() => {
    if (!player || !isPlaying) return;

    const interval = setInterval(() => {
      if (player && typeof player.getCurrentTime === 'function') {
        setCurrentTime(player.getCurrentTime());
      }
    }, 500);

    return () => clearInterval(interval);
  }, [player, isPlaying]);

  const handleSeek = (e) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (player && typeof player.seekTo === 'function') {
      player.seekTo(time, true);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
      {/* Sidebar: Video List */}
      <div className="lg:col-span-1 bg-retro-dark rounded-xl border border-retro-gray/30 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-retro-gray/30">
          <h3 className="text-lg font-display">Video auswählen</h3>
        </div>
        <div className="overflow-y-auto p-2 space-y-2 flex-1">
          {videos.map((video) => (
            <button
              key={video.id}
              onClick={() => setSelectedVideoId(video.ytId || video.id)}
              className={cn(
                'w-full text-left p-3 rounded-lg transition-colors flex gap-3 items-start',
                selectedVideoId === (video.ytId || video.id)
                  ? 'bg-accent-red/20 border border-accent-red/50'
                  : 'bg-retro-darker hover:bg-retro-gray/20'
              )}
            >
              <div className="relative shrink-0">
                <img
                  src={video.thumbnailUrl}
                  alt=""
                  className="w-20 h-12 object-cover rounded bg-black"
                />
                <div
                  className="absolute top-0 right-0 w-0 h-0 border-t-[16px] border-l-[16px] border-l-transparent rounded-tr-sm z-10"
                  style={{
                    borderTopColor:
                      CATEGORIES.find((c) => c.label === video.category || c.id === video.category)
                        ?.hex || 'transparent',
                  }}
                />
              </div>
              <div>
                <p className="font-medium line-clamp-2 text-sm text-white">{video.title}</p>
                <p className="text-xs text-retro-muted mt-1">{video.category}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main: Preview & Controls */}
      <div className="lg:col-span-2 space-y-6 overflow-y-auto">
        {selectedVideoId ? (
          <>
            <div className="aspect-video bg-black rounded-xl overflow-hidden relative shadow-2xl border border-retro-gray/30">
              {/* The div that YouTube API replaces */}
              <div
                id="thumbnail-generator-player"
                ref={playerContainerRef}
                className="w-full h-full"
              />

              {/* Overlay for "Thumbnail Preview" look - optional */}
              {/* <div className="absolute inset-0 pointer-events-none border-4 border-transparent" /> */}
            </div>

            <div className="bg-retro-dark rounded-xl border border-retro-gray/30 p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-display">Thumbnail Generator</h3>
                <span className="font-mono text-accent-cyan text-xl">
                  {new Date(currentTime * 1000).toISOString().substr(11, 8)}
                </span>
              </div>

              {/* Slider */}
              <div className="space-y-2">
                <input
                  type="range"
                  min="0"
                  max={duration || 100}
                  step="0.1"
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-2 bg-retro-darker rounded-lg appearance-none cursor-pointer accent-accent-red"
                />
                <div className="flex justify-between text-xs text-retro-muted">
                  <span>00:00:00</span>
                  <span>{new Date((duration || 0) * 1000).toISOString().substr(11, 8)}</span>
                </div>
              </div>

              {/* Controls */}
              <div className="flex gap-4">
                <button
                  onClick={() => player?.playVideo()}
                  className="btn btn-secondary flex-1 justify-center"
                >
                  <Play size={18} className="mr-2" /> Play
                </button>
                <button
                  onClick={() => player?.pauseVideo()}
                  className="btn btn-secondary flex-1 justify-center"
                >
                  <Pause size={18} className="mr-2" /> Pause
                </button>
                <button
                  className="btn btn-primary flex-1 justify-center"
                  onClick={() => alert(`Thumbnail Timestamp: ${currentTime.toFixed(2)}s saved!`)}
                >
                  <Save size={18} className="mr-2" /> Save Frame
                </button>
              </div>

              <div className="p-4 bg-retro-darker rounded-lg border border-retro-gray/20 text-sm text-retro-muted">
                <p className="flex items-center gap-2">
                  <ImageIcon size={16} />
                  <span>
                    <strong>Hinweis:</strong> Wähle den perfekten Frame mit dem Slider. Der
                    Timestamp wird gespeichert, um das Thumbnail dynamisch zu generieren.
                  </span>
                </p>
              </div>
            </div>
          </>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-retro-muted bg-retro-dark rounded-xl border border-retro-gray/30 border-dashed p-12">
            <ImageIcon size={48} className="mb-4 opacity-50" />
            <p className="text-lg">Bitte wählen Sie ein Video aus der Liste</p>
            <p className="text-sm opacity-70">um ein Thumbnail zu generieren</p>
          </div>
        )}
      </div>
    </div>
  );
}
