import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import useMeta from '../lib/useMeta';
import { useApp } from '../context/AppContext';
import { DashboardGrid } from '../components/dashboard';
import {
  getSessionStats,
  getHybridRecommendations,
  explainRecommendation,
  RECOMMENDATION_CONFIG,
} from '../lib/recommendationEngine';

/**
 * HomePage - Main landing page for remAIke.TV
 *
 * Sections:
 * 1. Hero (Featured video)
 * 2. Continue Watching (if applicable)
 * 3. New Additions
 * 4. Categories
 * 5. Popular
 */
export default function HomePage() {
  const { t } = useTranslation();
  useMeta({
    title: t('homePage.title'),
    description: t('homePage.description'),
  });
  const { videos, categories, continueWatching, loading, error } = useApp();

  // --- Smart Hybrid Recommendations (Research-Based) ---
  const smartRecommendations = useMemo(() => {
    if (!videos || videos.length === 0) return [];
    return getHybridRecommendations(videos, {
      count: 30,
      exploreMode: false, // 20% exploration, 80% exploitation
      excludeWatched: true,
    });
  }, [videos]);

  // --- Deduplication Logic ---
  const usedVideoIds = new Set();

  // 1. Featured Videos (Top 5)
  const featuredVideos = videos.slice(0, 5);
  featuredVideos.forEach((v) => usedVideoIds.add(v.id || v.ytId));

  // 2. Continue Watching (User specific)
  const continueWatchingVideos = continueWatching
    .map((cw) => {
      const video = videos.find((v) => v.id === cw.videoId || v.ytId === cw.videoId);
      return video ? { ...video, progress: cw.percentage } : null;
    })
    .filter(Boolean);
  continueWatchingVideos.forEach((v) => usedVideoIds.add(v.id || v.ytId));

  // 3. New Videos (Most recent, excluding above)
  const newVideos = [...videos]
    .sort((a, b) => new Date(b.publishDate) - new Date(a.publishDate))
    .filter((v) => !usedVideoIds.has(v.id || v.ytId))
    .slice(0, 15);
  newVideos.forEach((v) => usedVideoIds.add(v.id || v.ytId));

  // If we don't have enough videos for personalized, we might skip it or relax the constraint.
  // For now, strict deduplication as requested.

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-retro-black">
        <div className="text-center">
          <div className="relative w-20 h-20 mx-auto mb-6">
            <div className="absolute inset-0 border-4 border-retro-gray/30 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-accent-red border-t-transparent rounded-full animate-spin"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-2xl">R</span>
            </div>
          </div>
          <p className="text-fluid-lg font-display tracking-wider text-white animate-pulse">
            {t('homePage.loading')}
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 safe-bottom">
        <div className="text-center max-w-md bg-retro-darker/50 p-8 rounded-2xl border border-retro-gray/30 backdrop-blur-md shadow-2xl">
          <div className="text-6xl mb-6 animate-pulse-slow">📡</div>
          <h2 className="text-fluid-2xl font-display mb-3 text-white">
            {t('homePage.noConnection')}
          </h2>
          <p className="text-fluid-base text-retro-muted mb-8 leading-relaxed">
            {error || t('homePage.loadError')}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary w-full justify-center py-4 text-lg shadow-neon-red hover:scale-105 transition-transform"
          >
            {t('homePage.retryConnection')}
          </button>
        </div>
      </div>
    );
  }

  // Get session stats for engagement display
  const sessionStats = getSessionStats();

  // --- Dashboard Data Preparation ---
  // 1. Main Featured Video (Latest Upload)
  const dashboardMain = newVideos[0];

  // 2. Side List (Next 5 Uploads)
  const dashboardSide = newVideos.slice(1, 6);

  // 3. Personalized Recommendations (Hybrid Algorithm)
  const personalizedVideos = smartRecommendations.slice(0, 15);

  return (
    <div className="min-h-screen pt-16">
      {/* Algorithm Info Banner */}
      <div className="bg-gradient-to-r from-accent-gold/10 via-accent-amber/5 to-transparent border-b border-accent-gold/20 px-4 py-2">
        <div className="container mx-auto flex items-center gap-3 text-xs">
          <span className="text-accent-gold font-semibold">🧠 HYBRID AI</span>
          <span className="text-retro-muted">
            {RECOMMENDATION_CONFIG.EPSILON * 100}% Exploration •
            {(1 - RECOMMENDATION_CONFIG.EPSILON) * 100}% Personalization • Cold-Start Boost •
            Long-Tail Discovery
          </span>
        </div>
      </div>

      {/* Dashboard View (frai.tv Style) - Only View */}
      <DashboardGrid
        featuredVideo={dashboardMain}
        recentVideos={dashboardSide}
        continueWatching={continueWatchingVideos}
        categories={categories}
        personalizedVideos={personalizedVideos}
        recommendationExplainer={explainRecommendation}
      />

      {/* Empty State */}
      {videos.length === 0 && !loading && (
        <div className="text-center py-20 px-4">
          <div className="text-8xl mb-6">🎬</div>
          <h2 className="text-fluid-3xl font-display mb-4">Noch keine Videos</h2>
          <p className="text-fluid-lg text-retro-muted max-w-md mx-auto">
            Die Mediathek ist noch leer. Videos werden automatisch importiert, sobald sie auf dem
            YouTube-Kanal verfügbar sind.
          </p>
        </div>
      )}
    </div>
  );
}
