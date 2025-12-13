import { useState, useRef, useMemo, useCallback, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ZoomIn, ZoomOut, Maximize2, Home, AlertTriangle } from 'lucide-react';
import { cn, getYouTubeThumbnail } from '../../lib/utils';
import { useApp } from '../../context/AppContext';
import { DECADES, CATEGORIES } from '../../data/remaikeData';

/**
 * MindmapNavigator - Experimental visual navigation
 *
 * ⚠️ EXPERIMENTAL - Desktop only, not mobile optimized!
 *
 * A radial/force-directed visualization of video categories and relationships.
 * Users can explore the library by zooming and panning through connected nodes.
 *
 * Features:
 * - Central hub with category nodes
 * - Video nodes connected to categories
 * - Zoom and pan controls
 * - Click to navigate/play
 * - Centered preview at bottom (not corner)
 */
export default function MindmapNavigator({ className }) {
  const { videos, openPlayer } = useApp();
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);

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

  // Build node graph - MUST be before conditional returns
  const { nodes, connections } = useMemo(() => {
    const nodeList = [];
    const connList = [];

    // Center node
    nodeList.push({
      id: 'center',
      type: 'hub',
      label: 'FRai.TV',
      x: 0,
      y: 0,
      size: 80,
      color: '#f59e0b', // amber
    });

    // Category nodes in a circle around center
    const categoryRadius = 200;
    CATEGORIES.forEach((cat, i) => {
      const angle = (i / CATEGORIES.length) * Math.PI * 2 - Math.PI / 2;
      const x = Math.cos(angle) * categoryRadius;
      const y = Math.sin(angle) * categoryRadius;

      nodeList.push({
        id: `cat-${cat.id}`,
        type: 'category',
        label: cat.label,
        icon: cat.icon,
        x,
        y,
        size: 50,
        color: getCategoryColor(cat.id),
        categoryId: cat.id,
      });

      // Connect to center
      connList.push({
        from: 'center',
        to: `cat-${cat.id}`,
        strength: 1,
      });
    });

    // Decade nodes in outer ring
    const decadeRadius = 350;
    DECADES.forEach((dec, i) => {
      const angle = (i / DECADES.length) * Math.PI * 2 - Math.PI / 2;
      const x = Math.cos(angle) * decadeRadius;
      const y = Math.sin(angle) * decadeRadius;

      nodeList.push({
        id: `dec-${dec.id}`,
        type: 'decade',
        label: dec.label,
        icon: dec.icon,
        x,
        y,
        size: 40,
        color: '#64748b', // slate
        decadeId: dec.id,
      });
    });

    // Add video nodes (limited for performance)
    const videoRadius = 500;
    const maxVideos = 30;
    const videoSample = videos.slice(0, maxVideos);

    videoSample.forEach((video, i) => {
      const angle = (i / videoSample.length) * Math.PI * 2;
      const x = Math.cos(angle) * videoRadius + (Math.random() - 0.5) * 100;
      const y = Math.sin(angle) * videoRadius + (Math.random() - 0.5) * 100;

      nodeList.push({
        id: `video-${video.id}`,
        type: 'video',
        label: video.title,
        thumbnail: video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'default'),
        x,
        y,
        size: 30,
        video,
      });

      // Connect to category if exists
      if (video.category) {
        const catNode = nodeList.find((n) => n.categoryId === video.category);
        if (catNode) {
          connList.push({
            from: catNode.id,
            to: `video-${video.id}`,
            strength: 0.5,
          });
        }
      }
    });

    return { nodes: nodeList, connections: connList };
  }, [videos]);

  // Handle mouse events for panning - MUST be before conditional returns
  const handleMouseDown = useCallback(
    (e) => {
      if (e.target === containerRef.current || e.target.classList.contains('mindmap-bg')) {
        setIsDragging(true);
        setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
      }
    },
    [pan]
  );

  const handleMouseMove = useCallback(
    (e) => {
      if (isDragging) {
        setPan({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        });
      }
    },
    [isDragging, dragStart]
  );

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Handle zoom
  const handleWheel = useCallback((e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom((z) => Math.min(Math.max(z * delta, 0.3), 3));
  }, []);

  // Reset view
  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  // Handle node click
  const handleNodeClick = (node) => {
    if (node.type === 'video' && node.video) {
      openPlayer(node.video);
    } else if (node.type === 'category') {
      setSelectedNode(node);
    } else if (node.type === 'decade') {
      setSelectedNode(node);
    }
  };

  // Mobile fallback - AFTER all hooks
  if (isMobile) {
    return (
      <div
        className={cn(
          'relative w-full h-[400px] bg-retro-darker rounded-xl overflow-hidden flex items-center justify-center',
          className
        )}
      >
        <div className="text-center p-6">
          <AlertTriangle className="w-12 h-12 text-accent-amber mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">Desktop Feature</h3>
          <p className="text-retro-muted text-sm mb-4">
            Die Mindmap-Navigation ist für Desktop optimiert.
          </p>
          <button
            onClick={() => navigate('/browse')}
            className="px-4 py-2 bg-accent-amber text-black rounded-lg font-medium hover:bg-amber-400 transition-colors"
          >
            Zur Mediathek
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className={cn(
        'relative w-full h-[600px] lg:h-[800px] bg-retro-darker rounded-xl overflow-hidden',
        isDragging && 'cursor-grabbing',
        className
      )}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Background Grid */}
      <div className="mindmap-bg absolute inset-0 opacity-20">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#374151" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Main SVG Canvas */}
      <svg
        className="absolute inset-0 w-full h-full"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
          transformOrigin: 'center center',
        }}
      >
        <g transform="translate(50%, 50%)">
          {/* Connections */}
          {connections.map((conn, i) => {
            const fromNode = nodes.find((n) => n.id === conn.from);
            const toNode = nodes.find((n) => n.id === conn.to);
            if (!fromNode || !toNode) return null;

            return (
              <line
                key={i}
                x1={fromNode.x}
                y1={fromNode.y}
                x2={toNode.x}
                y2={toNode.y}
                stroke="#374151"
                strokeWidth={conn.strength * 2}
                strokeOpacity={0.3}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node) => (
            <g
              key={node.id}
              transform={`translate(${node.x}, ${node.y})`}
              className="cursor-pointer"
              onClick={() => handleNodeClick(node)}
              onMouseEnter={() => setHoveredNode(node)}
              onMouseLeave={() => setHoveredNode(null)}
            >
              {node.type === 'hub' && (
                <>
                  <circle r={node.size} fill={node.color} className="filter drop-shadow-lg" />
                  <text textAnchor="middle" dy=".3em" fill="black" fontSize="14" fontWeight="bold">
                    {node.label}
                  </text>
                </>
              )}

              {node.type === 'category' && (
                <>
                  <circle
                    r={node.size}
                    fill={node.color}
                    className={cn(
                      'transition-all duration-200',
                      hoveredNode?.id === node.id && 'filter drop-shadow-lg'
                    )}
                    style={{
                      transform: hoveredNode?.id === node.id ? 'scale(1.2)' : 'scale(1)',
                    }}
                  />
                  <text textAnchor="middle" dy="-0.5em" fill="white" fontSize="20">
                    {node.icon}
                  </text>
                  <text textAnchor="middle" dy="1.5em" fill="white" fontSize="10">
                    {node.label}
                  </text>
                </>
              )}

              {node.type === 'decade' && (
                <>
                  <circle r={node.size} fill={node.color} className="transition-all duration-200" />
                  <text textAnchor="middle" dy="-0.5em" fill="white" fontSize="16">
                    {node.icon}
                  </text>
                  <text textAnchor="middle" dy="1.2em" fill="white" fontSize="9">
                    {node.label}
                  </text>
                </>
              )}

              {node.type === 'video' && (
                <>
                  <clipPath id={`clip-${node.id}`}>
                    <circle r={node.size} />
                  </clipPath>
                  <circle
                    r={node.size}
                    fill="#1f2937"
                    stroke={hoveredNode?.id === node.id ? '#f59e0b' : '#374151'}
                    strokeWidth={hoveredNode?.id === node.id ? 3 : 1}
                  />
                  <image
                    href={node.thumbnail}
                    x={-node.size}
                    y={-node.size}
                    width={node.size * 2}
                    height={node.size * 2}
                    clipPath={`url(#clip-${node.id})`}
                  />
                  {hoveredNode?.id === node.id && <circle r={12} fill="white" fillOpacity={0.9} />}
                  {hoveredNode?.id === node.id && <polygon points="-4,-6 -4,6 6,0" fill="black" />}
                </>
              )}
            </g>
          ))}
        </g>
      </svg>

      {/* Controls */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button
          onClick={() => setZoom((z) => Math.min(z * 1.2, 3))}
          className="p-2 bg-retro-dark rounded-lg hover:bg-retro-gray transition-colors"
          title="Zoom In"
        >
          <ZoomIn size={20} />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z * 0.8, 0.3))}
          className="p-2 bg-retro-dark rounded-lg hover:bg-retro-gray transition-colors"
          title="Zoom Out"
        >
          <ZoomOut size={20} />
        </button>
        <button
          onClick={resetView}
          className="p-2 bg-retro-dark rounded-lg hover:bg-retro-gray transition-colors"
          title="Reset View"
        >
          <Maximize2 size={20} />
        </button>
        <Link
          to="/"
          className="p-2 bg-retro-dark rounded-lg hover:bg-retro-gray transition-colors"
          title="Home"
        >
          <Home size={20} />
        </Link>
      </div>

      {/* Hovered Node Info - CENTERED at bottom */}
      {hoveredNode && hoveredNode.type === 'video' && (
        <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-retro-dark/95 backdrop-blur-md rounded-xl p-4 max-w-sm w-full mx-4 border border-accent-amber/30 shadow-2xl">
          <div className="flex gap-3 items-start">
            <img src={hoveredNode.thumbnail} alt="" className="w-20 h-14 object-cover rounded" />
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-white truncate text-sm">{hoveredNode.label}</h3>
              <p className="text-xs text-accent-amber mt-1">Klicken zum Abspielen</p>
            </div>
          </div>
        </div>
      )}

      {/* Experimental Banner */}
      <div className="absolute top-0 left-0 right-0 bg-accent-amber/10 border-b border-accent-amber/30 px-4 py-2">
        <p className="text-xs text-center text-accent-amber">
          ⚡ Experimentelles Feature – Scrollen zum Zoomen, Ziehen zum Bewegen
        </p>
      </div>
    </div>
  );
}

/**
 * Get color for category
 */
function getCategoryColor(categoryId) {
  const colors = {
    'classic-films': '#d4af37', // gold
    cartoons: '#e50914', // red
    documentaries: '#2979ff', // blue
    propaganda: '#8b8b00', // olive
    comedy: '#ffd600', // yellow
    christmas: '#00c853', // green
    commercials: '#ff9100', // orange
  };
  return colors[categoryId] || '#6b7280';
}
