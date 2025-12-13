import { useState, useMemo, useEffect } from 'react';
import useMeta from '../lib/useMeta';
import { useSearchParams } from 'react-router-dom';
import { Search, X, Clock, TrendingUp, Mic, History, Filter, Calendar, Tag } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { VideoCard } from '../components/video';
import { CATEGORIES, DECADES } from '../data/remaikeData';
import { storage } from '../lib/utils';
import { useTranslation } from 'react-i18next';

/**
 * SearchPage - Dedicated search results page
 *
 * Features:
 * - Live search suggestions
 * - Search history (persisted)
 * - Trending searches
 * - Categorized results
 * - Advanced Filters (Category, Decade)
 */
export default function SearchPage() {
  const { t } = useTranslation();
  useMeta({
    title: t('searchTitle'),
    description: t('searchDescription'),
  });
  const { videos, searchQuery, setSearchQuery, loading } = useApp();
  const [searchParams, setSearchParams] = useSearchParams();

  // Search State
  const [localSearch, setLocalSearch] = useState(searchParams.get('q') || searchQuery);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Filter State
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || 'all');
  const [selectedDecade, setSelectedDecade] = useState(searchParams.get('decade') || 'all');
  const [showFilters, setShowFilters] = useState(false);

  // History State
  const [searchHistory, setSearchHistory] = useState(() =>
    storage.get('remaike_search_history', [])
  );
  const trendingSearches = [
    'Film Noir',
    'Popeye',
    'Metropolis',
    'Superman',
    'Charlie Chaplin',
    'Technicolor',
  ];

  // Update URL params when filters change
  useEffect(() => {
    const params = {};
    if (localSearch) params.q = localSearch;
    if (selectedCategory !== 'all') params.category = selectedCategory;
    if (selectedDecade !== 'all') params.decade = selectedDecade;
    setSearchParams(params);
  }, [localSearch, selectedCategory, selectedDecade, setSearchParams]);

  // Search results with filtering
  const searchResults = useMemo(() => {
    // If no search term and no filters, return empty (show initial state)
    if (!localSearch.trim() && selectedCategory === 'all' && selectedDecade === 'all') return [];

    const query = localSearch.toLowerCase();

    return videos
      .filter((v) => {
        // Text Match
        const matchesText =
          !query ||
          v.title?.toLowerCase().includes(query) ||
          v.description?.toLowerCase().includes(query) ||
          v.category?.toLowerCase().includes(query) ||
          v.channelName?.toLowerCase().includes(query);

        // Category Match
        const matchesCategory = selectedCategory === 'all' || v.category === selectedCategory;

        // Decade Match
        let matchesDecade = true;
        if (selectedDecade !== 'all') {
          const decadeData = DECADES.find((d) => d.id === selectedDecade);
          if (decadeData && v.year) {
            const year = parseInt(v.year);
            matchesDecade = year >= decadeData.range[0] && year <= decadeData.range[1];
          }
        }

        return matchesText && matchesCategory && matchesDecade;
      })
      .slice(0, 50); // Limit results
  }, [videos, localSearch, selectedCategory, selectedDecade]);

  // Search suggestions
  const suggestions = useMemo(() => {
    if (!localSearch.trim() || localSearch.length < 2) return [];

    const query = localSearch.toLowerCase();
    const titleMatches = videos
      .filter((v) => v.title?.toLowerCase().includes(query))
      .map((v) => v.title)
      .slice(0, 5);

    const categoryMatches = [
      ...new Set(
        videos.filter((v) => v.category?.toLowerCase().includes(query)).map((v) => v.category)
      ),
    ].slice(0, 3);

    return [...new Set([...titleMatches, ...categoryMatches])].slice(0, 6);
  }, [videos, localSearch]);

  // Add to history
  const addToHistory = (term) => {
    if (!term) return;
    const newHistory = [term, ...searchHistory.filter((t) => t !== term)].slice(0, 10);
    setSearchHistory(newHistory);
    storage.set('remaike_search_history', newHistory);
  };

  // Handle search submit
  const handleSearch = (e) => {
    e?.preventDefault();
    setSearchQuery(localSearch);
    addToHistory(localSearch);
    setShowSuggestions(false);
  };

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    setLocalSearch(suggestion);
    setSearchQuery(suggestion);
    addToHistory(suggestion);
    setShowSuggestions(false);
  };

  // Clear search
  const clearSearch = () => {
    setLocalSearch('');
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedDecade('all');
  };

  const hasResults = searchResults.length > 0;
  const showEmptyState =
    (localSearch.trim() || selectedCategory !== 'all' || selectedDecade !== 'all') &&
    searchResults.length === 0;
  const showInitialState =
    !localSearch.trim() && selectedCategory === 'all' && selectedDecade === 'all';

  return (
    <div className="min-h-screen pt-8 pb-12">
      {/* Search Header */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24 mb-8">
        <div className="max-w-3xl mx-auto">
          {/* Big Search Input */}
          <form onSubmit={handleSearch} className="relative">
            <div className="relative">
              <Search
                className="absolute left-4 sm:left-6 top-1/2 -translate-y-1/2 text-retro-muted"
                size={24}
              />
              <input
                type="search"
                value={localSearch}
                onChange={(e) => {
                  setLocalSearch(e.target.value);
                  setShowSuggestions(true);
                }}
                onFocus={() => setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                placeholder={t('searchPlaceholder')}
                className="w-full bg-retro-dark border-2 border-retro-gray rounded-xl
                         pl-14 sm:pl-16 pr-12 py-4 sm:py-5 text-fluid-lg
                         focus:outline-none focus:border-accent-cyan focus:shadow-glow-cyan
                         transition-all"
                autoFocus
              />
              {localSearch && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-4 top-1/2 -translate-y-1/2 
                           text-retro-muted hover:text-white transition-colors"
                >
                  <X size={20} />
                </button>
              )}
            </div>

            {/* Suggestions Dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div
                className="absolute top-full left-0 right-0 mt-2
                            bg-retro-dark border border-retro-gray rounded-xl
                            shadow-xl overflow-hidden z-50 animate-fade-in"
              >
                {suggestions.map((suggestion, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full flex items-center gap-3 px-4 py-3
                             hover:bg-retro-gray/50 text-left transition-colors"
                  >
                    <Search size={16} className="text-retro-muted shrink-0" />
                    <span className="truncate">{suggestion}</span>
                  </button>
                ))}
              </div>
            )}
          </form>

          {/* Filter Bar */}
          <div className="mt-6 flex flex-wrap items-center gap-3 justify-center">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`btn btn-sm gap-2 ${
                showFilters ? 'bg-accent-gold text-black' : 'btn-secondary'
              }`}
            >
              <Filter size={16} />
              {t('filters')}
            </button>

            {showFilters && (
              <div className="flex flex-wrap gap-3 animate-in fade-in slide-in-from-top-2">
                {/* Category Filter */}
                <div className="relative">
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="appearance-none bg-retro-dark border border-retro-gray rounded-lg pl-9 pr-8 py-2 text-sm focus:border-accent-gold focus:outline-none"
                  >
                    <option value="all">{t('allCategories')}</option>
                    {CATEGORIES.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {t(`categories.${cat.id}`)}
                      </option>
                    ))}
                  </select>
                  <Tag
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted"
                  />
                </div>

                {/* Decade Filter */}
                <div className="relative">
                  <select
                    value={selectedDecade}
                    onChange={(e) => setSelectedDecade(e.target.value)}
                    className="appearance-none bg-retro-dark border border-retro-gray rounded-lg pl-9 pr-8 py-2 text-sm focus:border-accent-gold focus:outline-none"
                  >
                    <option value="all">{t('allDecades')}</option>
                    {DECADES.map((dec) => (
                      <option key={dec.id} value={dec.id}>
                        {t(`decades.${dec.id}.label`)}
                      </option>
                    ))}
                  </select>
                  <Calendar
                    size={14}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-retro-muted"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Voice Search (placeholder) */}
          <button
            className="mt-4 flex items-center gap-2 mx-auto text-retro-muted hover:text-white transition-colors"
            onClick={() => alert(t('searchPage.voiceSearchComingSoon'))}
          >
            <Mic size={18} />
            <span className="text-fluid-sm">{t('searchPage.voiceSearch')}</span>
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="px-4 sm:px-6 md:px-8 lg:px-12 3xl:px-16 4k:px-24">
        {/* Initial State - Show Trending & History */}
        {showInitialState && (
          <div className="max-w-4xl mx-auto space-y-10">
            {/* Search History */}
            {searchHistory.length > 0 && (
              <section>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <History className="text-accent-cyan" size={20} />
                    <h2 className="text-fluid-lg font-semibold">{t('recentSearches')}</h2>
                  </div>
                  <button
                    onClick={() => {
                      setSearchHistory([]);
                      storage.set('remaike_search_history', []);
                    }}
                    className="text-xs text-retro-muted hover:text-white"
                  >
                    {t('clearHistory')}
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {searchHistory.map((term, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestionClick(term)}
                      className="flex items-center gap-2 px-4 py-2 
                               bg-retro-dark border border-retro-gray rounded-full
                               hover:border-accent-cyan hover:text-accent-cyan
                               transition-colors"
                    >
                      <Clock size={14} className="text-retro-muted" />
                      {term}
                    </button>
                  ))}
                </div>
              </section>
            )}

            {/* Trending Searches */}
            <section>
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="text-accent-red" size={20} />
                <h2 className="text-fluid-lg font-semibold">{t('trendingSearches')}</h2>
              </div>
              <div className="flex flex-wrap gap-2">
                {trendingSearches.map((term, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestionClick(term)}
                    className="flex items-center gap-2 px-4 py-2 
                             bg-gradient-to-r from-accent-red/20 to-accent-amber/20
                             border border-accent-red/30 rounded-full
                             hover:border-accent-red hover:shadow-glow-red
                             transition-all"
                  >
                    <span className="text-accent-red font-bold">#{i + 1}</span>
                    {term}
                  </button>
                ))}
              </div>
            </section>

            {/* Browse Categories CTA */}
            <section className="text-center py-8">
              <p className="text-retro-muted mb-4">{t('searchPage.browseCategories')}</p>
              <a href="/browse" className="btn btn-outline inline-flex">
                {t('viewAll')}
              </a>
            </section>
          </div>
        )}

        {/* Search Results */}
        {hasResults && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-fluid-xl font-semibold">
                {t('resultsFound', { count: searchResults.length })}
              </h2>
            </div>

            <div
              className="grid grid-cols-video-mobile sm:grid-cols-video-tablet md:grid-cols-video-desktop 
                           lg:grid-cols-video-hd 3xl:grid-cols-video-fhd 5k:grid-cols-video-4k gap-4"
            >
              {searchResults.map((video) => (
                <VideoCard key={video.id || video.ytId} video={video} />
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {showEmptyState && !loading && (
          <div className="text-center py-20 max-w-lg mx-auto">
            <div className="text-6xl mb-4">🔍</div>
            <h2 className="text-fluid-2xl font-semibold mb-2">{t('noResults')}</h2>
            <p className="text-fluid-base text-retro-muted mb-6">{t('tryDifferent')}</p>
            <div className="space-y-2">
              <p className="text-sm text-retro-muted">{t('searchPage.suggestions')}</p>
              <div className="flex flex-wrap justify-center gap-2">
                {trendingSearches.slice(0, 3).map((term, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestionClick(term)}
                    className="px-3 py-1.5 bg-retro-dark border border-retro-gray rounded-full
                             hover:border-accent-cyan text-sm transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div
            className="grid grid-cols-video-mobile sm:grid-cols-video-tablet md:grid-cols-video-desktop 
                         lg:grid-cols-video-hd 3xl:grid-cols-video-fhd 5k:grid-cols-video-4k gap-4"
          >
            {[...Array(8)].map((_, i) => (
              <div key={i} className="skeleton-shimmer aspect-video rounded-lg" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
