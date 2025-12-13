import React, { useState, useEffect } from 'react';
import { createBrowserRouter, RouterProvider, Navigate, Outlet } from 'react-router-dom';
import { AppProvider, useApp } from './context/AppContext';
import { MainLayout } from './components/layout';
import ErrorBoundary from './components/ui/ErrorBoundary';
import { CookieConsent } from './components/ui';
import { VideoPlayer, VideoInfoModal, MiniPlayer } from './components/video';
import { AnalyticsProvider, usePageTracking } from './lib/useAnalytics';
import { useTVNavigation } from './hooks/useTVNavigation';
import { InstallPrompt } from './components/ui/InstallPrompt';
import { InfoPopup, QuickNotice } from './components/ui/InfoPopup';
import { Lock } from 'lucide-react';
import {
  BrowsePage,
  SearchPage,
  WatchlistPage,
  HistoryPage,
  SettingsPage,
  VideoDetailPage,
  AdminPage,
  AdminLoginPage,
  TimelinePage,
  MediathekPage,
  ExplorePage,
  ImpressumPage,
  DatenschutzPage,
  NotFoundPage,
  LivestreamPage,
  SenderPage,
  ShortsPage,
  SeriesPage,
} from './pages';

/**
 * Global Overlays - VideoPlayer & VideoInfoModal
 */
function GlobalOverlays() {
  const { infoVideo, isInfoModalOpen, closeInfoModal, videos } = useApp();

  return (
    <>
      <VideoPlayer />
      <MiniPlayer />
      <VideoInfoModal video={infoVideo} isOpen={isInfoModalOpen} onClose={closeInfoModal} />
    </>
  );
}

/**
 * GlobalUI - Renders globally accessible popups and quick notices; listens to demo events
 */
function GlobalUI() {
  const { preferences } = useApp();
  const [showInfo, setShowInfo] = React.useState(false);
  const [showQuick, setShowQuick] = React.useState(false);
  const [showInstall, setShowInstall] = React.useState(false);

  React.useEffect(() => {
    const onShowInfo = () => setShowInfo(true);
    const onShowQuick = () => setShowQuick(true);
    const onShowInstall = () => setShowInstall(true);

    window.addEventListener('remake:showInfoPopup', onShowInfo);
    window.addEventListener('remake:showQuickNotice', onShowQuick);
    window.addEventListener('remake:showInstallPrompt', onShowInstall);

    return () => {
      window.removeEventListener('remake:showInfoPopup', onShowInfo);
      window.removeEventListener('remake:showQuickNotice', onShowQuick);
      window.removeEventListener('remake:showInstallPrompt', onShowInstall);
    };
  }, []);

  React.useEffect(() => {
    // If user toggles premium UI and is not in production, auto-trigger demo popups
    if (preferences?.premiumUI && import.meta.env.MODE !== 'production') {
      setShowInfo(true);
      setShowQuick(true);
      setShowInstall(true);
    }
  }, [preferences]);

  return (
    <>
      <InfoPopup
        isOpen={showInfo}
        onClose={() => setShowInfo(false)}
        title="Privacy Policy"
        icon={Lock}
        size="lg"
      >
        <div className="space-y-6">
          <p className="text-gray-400 text-sm">Data protection information pursuant to GDPR</p>

          {/* Data Controller Box */}
          <div className="bg-[#111] border border-[#c9a962]/30 rounded-lg p-5">
            <h4 className="text-[#c9a962] font-semibold mb-2">Data Controller</h4>
            <p className="text-white font-medium">skillbox.nrw GmbH</p>
            <p className="text-gray-400 text-sm">Im Springen 2, 58791 Werdohl, Germany</p>
            <p className="text-gray-400 text-sm mt-2">
              Email:{' '}
              <a href="mailto:contact@remaike.it" className="text-[#c9a962] hover:underline">
                contact@remaike.it
              </a>
            </p>
          </div>

          {/* Accordion Items (Mock) */}
          <div className="space-y-2">
            {[
              '1. Data Collection Overview',
              '2. Cookies & Analytics',
              '3. Your Rights (GDPR)',
              '4. Data Security',
              '5. Data Retention',
              '6. Third-Party Services',
            ].map((item) => (
              <div
                key={item}
                className="flex items-center justify-between p-3 hover:bg-white/5 rounded cursor-pointer group transition-colors"
              >
                <span className="text-white font-medium group-hover:text-[#c9a962] transition-colors">
                  ▶ {item}
                </span>
              </div>
            ))}
          </div>
        </div>
      </InfoPopup>

      <QuickNotice
        isOpen={showQuick}
        onClose={() => setShowQuick(false)}
        message="Premium UI demo is active"
        variant="info"
      />

      {showInstall && <InstallPrompt forceOpen={true} onClose={() => setShowInstall(false)} />}
    </>
  );
}

/**
 * Root Layout - enthält globale Provider und Overlays
 */
function RootLayout() {
  usePageTracking();
  useTVNavigation({ enabled: true });

  return (
    <>
      {/* Skip to main content - Accessibility */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] 
                   focus:px-4 focus:py-2 focus:bg-accent-gold focus:text-black focus:rounded-lg 
                   focus:font-semibold focus:outline-none focus:ring-2 focus:ring-white"
      >
        Zum Hauptinhalt springen
      </a>
      <CookieConsent />
      <InstallPrompt />
      <GlobalUI />
      <GlobalOverlays />
      <Outlet />
    </>
  );
}

/**
 * Router-Konfiguration mit Future Flags für React Router v7 Kompatibilität
 */
const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      {
        element: <MainLayout />,
        children: [
          { path: '/', element: <MediathekPage /> },
          { path: '/explore', element: <ExplorePage /> },
          { path: '/browse', element: <BrowsePage /> },
          { path: '/browse/:category', element: <BrowsePage /> },
          { path: '/video/:id', element: <VideoDetailPage /> },
          { path: '/watch/:id', element: <VideoDetailPage /> },
          { path: '/search', element: <SearchPage /> },
          { path: '/timeline', element: <TimelinePage /> },
          { path: '/watchlist', element: <WatchlistPage /> },
          { path: '/history', element: <HistoryPage /> },
          { path: '/settings', element: <SettingsPage /> },
          { path: '/admin', element: <AdminPage /> },
          { path: '/admin/login', element: <AdminLoginPage /> },
          { path: '/live', element: <LivestreamPage /> },
          { path: '/sender', element: <SenderPage /> },
          { path: '/shorts', element: <ShortsPage /> },
          { path: '/series', element: <SeriesPage /> },
          { path: '/series/:seriesId', element: <SeriesPage /> },
          { path: '/impressum', element: <ImpressumPage /> },
          { path: '/datenschutz', element: <DatenschutzPage /> },
          { path: '/category/:categoryName', element: <BrowsePage /> },
          { path: '/videos', element: <Navigate to="/browse" replace /> },
          { path: '/library', element: <Navigate to="/" replace /> },
          { path: '/mediathek', element: <Navigate to="/" replace /> },
          { path: '/home', element: <Navigate to="/" replace /> },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
]);

/**
 * frai.tv - FREE AI Enhanced TV
 *
 * Main application with routing and global providers.
 * Responsive design for mobile, 1080p desktops, 4K workstations, and Smart TVs.
 * Supports TV remote navigation via arrow keys and Enter/OK button.
 */
function App() {
  return (
    <div className="remaike-ui">
      <AppProvider>
        <ErrorBoundary>
          <AnalyticsProvider>
            <RouterProvider router={router} />
          </AnalyticsProvider>
        </ErrorBoundary>
      </AppProvider>
    </div>
  );
}

export default App;
