import { Outlet } from 'react-router-dom';
import TopNavigation, { MobileBottomNav } from './TopNavigation';
import Footer from './Footer';
import Sidebar from './Sidebar';

/**
 * MainLayout - Root layout wrapper for remAIke.TV
 *
 * Design Research Implementation:
 * - Desktop: TopNavigation + Sidebar (Left) + Content + Footer
 * - Mobile: TopNavigation + Content + MobileBottomNav
 */
export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-retro-black text-retro-white">
      {/* Top Navigation */}
      <TopNavigation />

      <div className="flex flex-1">
        {/* Desktop Sidebar - Sticky on left */}
        <Sidebar variant="desktop" />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          <main id="main-content" className="flex-1 pb-20 lg:pb-0" role="main" tabIndex={-1}>
            <Outlet />
          </main>

          {/* Footer - Desktop only (at bottom of content) */}
          <div className="hidden lg:block">
            <Footer />
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Drawer (Overlay) */}
      <Sidebar variant="mobile" />

      {/* Mobile Bottom Navigation */}
      <MobileBottomNav />
    </div>
  );
}
