import { useState, useMemo } from 'react';
import useMeta from '../lib/useMeta';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';
import { Search, Grid, List, X, SlidersHorizontal } from 'lucide-react';
import { cn } from '../lib/utils';
import { useApp } from '../context/AppContext';
import { VideoCard } from '../components/video';

/**
 * BrowsePage - Video browsing/search with filters
 *
 * Features:
 * - Grid/List view toggle
 * - Category filter
 * - Sort options
 * - Search integration
 * - Responsive grid (2-8 columns based on screen)
 */
export default function BrowsePage() {
  const { t } = useTranslation();
  useMeta({
    title: t('browsePage.title'),
    description: t('browsePage.description'),
  });
  const { videos, categories, searchQuery, setSearchQuery, loading } = useApp();
  const [searchParams, setSearchParams] = useSearchParams();

  // State
  const [viewMode, setViewMode] = useState('grid');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [localSearch, setLocalSearch] = useState(searchQuery);

  // Get filter params
  const selectedCategory = searchParams.get('category') || '';
  const sortBy = searchParams.get('sort') || 'newest';
  const filterNew = searchParams.get('filter') === 'new';

  // Update search params
  const updateParams = (key, value) => {
    const newParams = new URLSearchParams(searchParams);
    if (value) {
      newParams.set(key, value);
    } else {
      newParams.delete(key);
    }
    setSearchParams(newParams);
  };

  // Filter and sort videos
  const filteredVideos = useMemo(() => {
    let result = [...videos];

    // Search filter
    if (localSearch.trim()) {
      const query = localSearch.toLowerCase();
      result = result.filter(
        (v) =>
          v.title?.toLowerCase().includes(query) ||
          v.description?.toLowerCase().includes(query) ||
          v.category?.toLowerCase().includes(query)
      );
    }

    // Category filter
    if (selectedCategory) {
      result = result.filter((v) => v.category === selectedCategory);
    }

    // New filter (last 30 days)
    if (filterNew) {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      result = result.filter((v) => new Date(v.publishDate) > thirtyDaysAgo);
    }

    // Sort
    switch (sortBy) {
      case 'newest':
        result.sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate));
        break;
      case 'oldest':
        result.sort((a, b) => new Date(a.publishDate) - new Date(b.publishDate));
        break;
      case 'popular':
        result.sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0));
        break;
      case 'title':
        result.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
        break;
      case 'duration':
        result.sort((a, b) => (b.duration || 0) - (a.duration || 0));
        break;
      default:
        break;
    }

    return result;
  }, [videos, localSearch, selectedCategory, sortBy, filterNew]);

  // Handle search submit
  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(localSearch);
  };

  // Clear all filters
  const clearFilters = () => {
    setSearchParams({});
    setLocalSearch('');
    setSearchQuery('');
  };

  const hasActiveFilters = selectedCategory || sortBy !== 'newest' || filterNew || localSearch;

  return (
    <div className="min-h-screen pt-4 pb-12 safe-bottom">
      {/* Header */}
      <div className="px-3 xs:px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mb-4 xs:mb-6 md:mb-8">
        <h1 className="text-fluid-2xl xs:text-fluid-3xl font-display mb-1 xs:mb-2">
          {selectedCategory
            ? t(`categories.${selectedCategory}`) || selectedCategory
            : t('browsePage.allVideos')}
        </h1>
        <p className="text-fluid-sm xs:text-fluid-base text-retro-muted">
          {filteredVideos.length === 1
            ? t('browsePage.videoFound', { count: filteredVideos.length })
            : t('browsePage.videosFound', { count: filteredVideos.length })}
        </p>
      </div>

      {/* Toolbar */}
      <div
        className="sticky top-14 sm:top-16 md:top-18 lg:top-20 z-30 
                      bg-retro-black/95 backdrop-blur-md border-b border-retro-gray
                      px-3 xs:px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 py-2.5 xs:py-3"
      >
        <div className="flex flex-wrap items-center gap-2 xs:gap-3 md:gap-4">
          {/* Search */}
          <form
            onSubmit={handleSearch}
            className="flex-1 min-w-[140px] xs:min-w-[180px] sm:min-w-[200px] max-w-md"
          >
            <div className="relative">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted"
                size={18}
              />
              <input
                type="search"
                value={localSearch}
                onChange={(e) => setLocalSearch(e.target.value)}
                placeholder={t('browsePage.searchPlaceholder')}
                className="w-full bg-retro-dark border border-retro-gray rounded-lg
                         pl-10 pr-3 xs:pr-4 py-2.5 text-fluid-sm min-h-[44px]
                         focus:outline-none focus:border-accent-cyan
                         touch-manipulation"
              />
            </div>
          </form>

          {/* Filter Toggle (Mobile) */}
          <button
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className={cn(
              'btn btn-secondary md:hidden min-h-[44px] px-3 xs:px-4',
              isFilterOpen && 'bg-accent-red/20 text-accent-red'
            )}
          >
            <SlidersHorizontal size={18} />
            <span className="hidden xs:inline">{t('browsePage.filter')}</span>
          </button>

          {/* Desktop Filters */}
          <div className="hidden md:flex items-center gap-3">
            {/* Category Select */}
            <select
              value={selectedCategory}
              onChange={(e) => updateParams('category', e.target.value)}
              className="bg-retro-dark border border-retro-gray rounded-lg
                       px-3 py-2.5 text-fluid-sm min-h-[44px] focus:outline-none focus:border-accent-cyan"
            >
              <option value="">{t('browsePage.allCategories')}</option>
              {categories.map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {t(`categories.${cat.name}`) || cat.name} ({cat.videos?.length || 0})
                </option>
              ))}
            </select>

            {/* Sort Select */}
            <select
              value={sortBy}
              onChange={(e) => updateParams('sort', e.target.value)}
              className="bg-retro-dark border border-retro-gray rounded-lg
                       px-3 py-2.5 text-fluid-sm min-h-[44px] focus:outline-none focus:border-accent-cyan"
            >
              <option value="newest">{t('browsePage.sortNewest')}</option>
              <option value="oldest">{t('browsePage.sortOldest')}</option>
              <option value="popular">{t('browsePage.sortPopular')}</option>
              <option value="title">{t('browsePage.sortAZ')}</option>
              <option value="duration">{t('browsePage.sortDuration')}</option>
            </select>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <button onClick={clearFilters} className="btn btn-ghost text-accent-red">
              <X size={16} />
              <span className="hidden sm:inline">{t('browsePage.clearFilters')}</span>
            </button>
          )}

          {/* View Mode Toggle */}
          <div className="hidden sm:flex items-center border border-retro-gray rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('grid')}
              className={cn(
                'p-2.5 min-h-[44px] min-w-[44px] flex items-center justify-center transition-colors touch-manipulation',
                viewMode === 'grid'
                  ? 'bg-accent-red text-white'
                  : 'text-retro-muted hover:text-white'
              )}
              aria-label={t('browsePage.gridView')}
            >
              <Grid size={18} />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={cn(
                'p-2.5 min-h-[44px] min-w-[44px] flex items-center justify-center transition-colors touch-manipulation',
                viewMode === 'list'
                  ? 'bg-accent-red text-white'
                  : 'text-retro-muted hover:text-white'
              )}
              aria-label={t('browsePage.listView')}
            >
              <List size={18} />
            </button>
          </div>
        </div>

        {/* Mobile Filter Panel */}
        {isFilterOpen && (
          <div className="md:hidden pt-3 xs:pt-4 pb-2 space-y-2.5 xs:space-y-3 animate-fade-in">
            <select
              value={selectedCategory}
              onChange={(e) => updateParams('category', e.target.value)}
              className="w-full bg-retro-dark border border-retro-gray rounded-lg
                       px-3 py-3 text-fluid-sm min-h-[48px] touch-manipulation"
            >
              <option value="">{t('browsePage.allCategories')}</option>
              {categories.map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {t(`categories.${cat.name}`) || cat.name}
                </option>
              ))}
            </select>

            <select
              value={sortBy}
              onChange={(e) => updateParams('sort', e.target.value)}
              className="w-full bg-retro-dark border border-retro-gray rounded-lg
                       px-3 py-3 text-fluid-sm min-h-[48px] touch-manipulation"
            >
              <option value="newest">{t('browsePage.sortNewest')}</option>
              <option value="oldest">{t('browsePage.sortOldest')}</option>
              <option value="popular">{t('browsePage.sortPopular')}</option>
              <option value="title">{t('browsePage.sortAZ')}</option>
            </select>
          </div>
        )}
      </div>

      {/* Video Grid */}
      <div className="px-3 xs:px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mt-4 xs:mt-6">
        {loading ? (
          // Loading Skeleton
          <div
            className="grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4
                         lg:grid-cols-5 xl:grid-cols-5 3xl:grid-cols-6 5k:grid-cols-8 
                         gap-2 xs:gap-3 sm:gap-4"
          >
            {[...Array(12)].map((_, i) => (
              <div key={i} className="skeleton-shimmer aspect-video rounded-lg" />
            ))}
          </div>
        ) : filteredVideos.length > 0 ? (
          <div
            className={cn(
              viewMode === 'grid'
                ? 'grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 3xl:grid-cols-6 5k:grid-cols-8 gap-2 xs:gap-3 sm:gap-4'
                : 'flex flex-col gap-3 xs:gap-4'
            )}
          >
            {filteredVideos.map((video) => (
              <VideoCard
                key={video.id || video.ytId}
                video={video}
                variant={viewMode === 'list' ? 'compact' : 'responsive'}
                className={viewMode === 'list' ? 'w-full flex-row' : ''}
              />
            ))}
          </div>
        ) : (
          // Empty State
          <div className="text-center py-12 xs:py-16 sm:py-20">
            <div className="text-5xl xs:text-6xl mb-3 xs:mb-4">🔍</div>
            <h2 className="text-fluid-xl xs:text-fluid-2xl font-semibold mb-2">
              {t('browsePage.noVideosFound')}
            </h2>
            <p className="text-fluid-sm xs:text-fluid-base text-retro-muted mb-4 xs:mb-6 px-4">
              {t('browsePage.tryDifferent')}
            </p>
            {hasActiveFilters && (
              <button onClick={clearFilters} className="btn btn-primary">
                {t('browsePage.resetFilters')}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
