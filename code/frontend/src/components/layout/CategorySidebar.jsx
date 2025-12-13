import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ChevronRight, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';
import { CATEGORIES, DECADES, MILESTONE_TYPES } from '../../data/remaikeData';

/**
 * CategorySidebar - Right-side category filter (frai.tv style)
 *
 * Features:
 * - Expandable category groups
 * - Active state highlighting
 * - Quick filters (Trending, New, etc.)
 */
export default function CategorySidebar({ className }) {
  const [searchParams] = useSearchParams();
  const [expandedGroups, setExpandedGroups] = useState(['quick']);

  const activeCategory = searchParams.get('category');
  const activeFilter = searchParams.get('filter');
  const activeDecade = searchParams.get('decade');

  const toggleGroup = (groupId) => {
    setExpandedGroups((prev) =>
      prev.includes(groupId) ? prev.filter((g) => g !== groupId) : [...prev, groupId]
    );
  };

  // Quick filters
  const quickFilters = [
    { id: 'trending', label: 'Trending Now', color: 'text-accent-red' },
    { id: 'new', label: 'New Releases', color: 'text-accent-green' },
    { id: 'action', label: 'Action', color: 'text-accent-amber' },
    { id: 'drama', label: 'Drama', color: 'text-white' },
    { id: 'comedy', label: 'Comedy', color: 'text-white' },
    { id: 'horror', label: 'Horror', color: 'text-white' },
  ];

  // Genre/Category items derived from CATEGORIES
  const genreItems = CATEGORIES.map((cat) => ({
    id: cat.id,
    label: cat.label,
    icon: cat.icon,
  }));

  // Decade items
  const decadeItems = DECADES.map((dec) => ({
    id: dec.id,
    label: dec.label,
    icon: dec.icon,
  }));

  return (
    <aside
      className={cn(
        'w-48 lg:w-56 flex-shrink-0 hidden xl:block',
        'bg-retro-darker/50 border-l border-retro-gray/30',
        'h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto',
        className
      )}
    >
      <div className="p-4 space-y-6">
        {/* Quick Filters */}
        <div>
          <button
            onClick={() => toggleGroup('quick')}
            className="flex items-center justify-between w-full mb-3"
          >
            <h3 className="text-xs font-semibold text-retro-muted uppercase tracking-wider">
              Quick Filters
            </h3>
            {expandedGroups.includes('quick') ? (
              <ChevronDown size={14} className="text-retro-muted" />
            ) : (
              <ChevronRight size={14} className="text-retro-muted" />
            )}
          </button>

          {expandedGroups.includes('quick') && (
            <ul className="space-y-1">
              {quickFilters.map((filter) => (
                <li key={filter.id}>
                  <Link
                    to={`/browse?filter=${filter.id}`}
                    className={cn(
                      'block px-3 py-2 rounded-lg text-sm transition-colors',
                      activeFilter === filter.id
                        ? 'bg-accent-amber text-black font-medium'
                        : `${filter.color} hover:bg-white/5`
                    )}
                  >
                    {filter.label}
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Categories */}
        <div>
          <button
            onClick={() => toggleGroup('categories')}
            className="flex items-center justify-between w-full mb-3"
          >
            <h3 className="text-xs font-semibold text-retro-muted uppercase tracking-wider">
              Categories
            </h3>
            {expandedGroups.includes('categories') ? (
              <ChevronDown size={14} className="text-retro-muted" />
            ) : (
              <ChevronRight size={14} className="text-retro-muted" />
            )}
          </button>

          {expandedGroups.includes('categories') && (
            <ul className="space-y-1">
              {genreItems.map((genre) => (
                <li key={genre.id}>
                  <Link
                    to={`/browse?category=${genre.id}`}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                      activeCategory === genre.id
                        ? 'bg-accent-amber text-black font-medium'
                        : 'text-white hover:bg-white/5'
                    )}
                  >
                    <span>{genre.icon}</span>
                    <span>{genre.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Decades */}
        <div>
          <button
            onClick={() => toggleGroup('decades')}
            className="flex items-center justify-between w-full mb-3"
          >
            <h3 className="text-xs font-semibold text-retro-muted uppercase tracking-wider">
              By Decade
            </h3>
            {expandedGroups.includes('decades') ? (
              <ChevronDown size={14} className="text-retro-muted" />
            ) : (
              <ChevronRight size={14} className="text-retro-muted" />
            )}
          </button>

          {expandedGroups.includes('decades') && (
            <ul className="space-y-1">
              {decadeItems.map((decade) => (
                <li key={decade.id}>
                  <Link
                    to={`/browse?decade=${decade.id}`}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                      activeDecade === decade.id
                        ? 'bg-accent-amber text-black font-medium'
                        : 'text-white hover:bg-white/5'
                    )}
                  >
                    <span>{decade.icon}</span>
                    <span>{decade.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Milestones */}
        <div>
          <button
            onClick={() => toggleGroup('milestones')}
            className="flex items-center justify-between w-full mb-3"
          >
            <h3 className="text-xs font-semibold text-retro-muted uppercase tracking-wider">
              Milestones
            </h3>
            {expandedGroups.includes('milestones') ? (
              <ChevronDown size={14} className="text-retro-muted" />
            ) : (
              <ChevronRight size={14} className="text-retro-muted" />
            )}
          </button>

          {expandedGroups.includes('milestones') && (
            <ul className="space-y-1">
              {MILESTONE_TYPES.slice(0, 6).map((ms) => (
                <li key={ms.id}>
                  <Link
                    to={`/browse?milestone=${ms.id}`}
                    className={cn(
                      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors',
                      'text-white hover:bg-white/5'
                    )}
                  >
                    <span>{ms.icon}</span>
                    <span>{ms.label}</span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </aside>
  );
}
