import { Youtube } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// FRAI.TV primary channel + socials (remAIke nur als Backend/Powered-by, nicht im UI)
const YOUTUBE_CHANNEL = 'https://www.youtube.com/@FRai_TV';
const FACEBOOK_PAGE = 'https://www.facebook.com/frai.tv';
const TWITTER_PAGE = 'https://x.com/FRai_TV';
const INSTAGRAM_PAGE = 'https://www.instagram.com/frai.tv';
const SUBSCRIBER_LABEL = '12.8K';

/**
 * YouTube Header Button mit Subscriber-Zahl + Round Social Icons
 * remAIke.IT Style: Round icons with neon glow hover effects
 */
export function SocialIconsDesktop() {
  const { t } = useTranslation();
  return (
    <div className="hidden md:flex items-center gap-2">
      {/* Round Social Icons - remAIke.IT Style */}

      {/* Instagram */}
      <a
        href={INSTAGRAM_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="Instagram"
        className="w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.35)',
          color: 'rgba(255, 255, 255, 0.85)',
          boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#E4405F';
          e.currentTarget.style.color = '#E4405F';
          e.currentTarget.style.boxShadow =
            '0 0 20px rgba(228,64,95,0.5), 0 0 40px rgba(228,64,95,0.25)';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.35)';
          e.currentTarget.style.color = 'rgba(255, 255, 255, 0.85)';
          e.currentTarget.style.boxShadow = '0 4px 14px rgba(0,0,0,0.4)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={16} height={16}>
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
        </svg>
      </a>

      {/* X (Twitter) */}
      <a
        href={TWITTER_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="X (Twitter)"
        className="w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.35)',
          color: 'rgba(255, 255, 255, 0.85)',
          boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#fff';
          e.currentTarget.style.color = '#fff';
          e.currentTarget.style.boxShadow =
            '0 0 20px rgba(255,255,255,0.4), 0 0 40px rgba(255,255,255,0.2)';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.35)';
          e.currentTarget.style.color = 'rgba(255, 255, 255, 0.85)';
          e.currentTarget.style.boxShadow = '0 4px 14px rgba(0,0,0,0.4)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={14} height={14}>
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
      </a>

      {/* Facebook */}
      <a
        href={FACEBOOK_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="Facebook"
        className="w-9 h-9 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.35)',
          color: 'rgba(255, 255, 255, 0.85)',
          boxShadow: '0 4px 14px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#1877F2';
          e.currentTarget.style.color = '#1877F2';
          e.currentTarget.style.boxShadow =
            '0 0 20px rgba(24,119,242,0.5), 0 0 40px rgba(24,119,242,0.25)';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.35)';
          e.currentTarget.style.color = 'rgba(255, 255, 255, 0.85)';
          e.currentTarget.style.boxShadow = '0 4px 14px rgba(0,0,0,0.4)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={16} height={16}>
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      </a>

      {/* Separator */}
      <div className="w-px h-6 bg-white/10 mx-1" />

      {/* YouTube Subscribe Button - Gold Pill */}
      <a
        href={YOUTUBE_CHANNEL}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 px-3 py-1.5 rounded-full transition-all duration-300"
        style={{
          background: 'linear-gradient(135deg, #c9a962 0%, #b08a3c 50%, #8c6a27 100%)',
          color: '#0b0b0c',
          fontSize: '12px',
          fontWeight: '700',
          letterSpacing: '0.35px',
          border: '1px solid rgba(201, 169, 98, 0.55)',
          boxShadow: '0 8px 24px rgba(201,169,98,0.3), 0 0 0 1px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow =
            '0 12px 32px rgba(201, 169, 98, 0.45), 0 0 0 1px rgba(0,0,0,0.5)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow =
            '0 8px 24px rgba(201,169,98,0.3), 0 0 0 1px rgba(0,0,0,0.4)';
        }}
      >
        <Youtube size={14} />
        <span>{t('subscribe')}</span>
        <span
          style={{
            background: 'rgba(0,0,0,0.25)',
            padding: '1px 6px',
            borderRadius: '999px',
            fontSize: '10px',
            fontWeight: 700,
          }}
        >
          {SUBSCRIBER_LABEL}
        </span>
      </a>
    </div>
  );
}

/**
 * Social Media Buttons für Mobile Header - remAIke.IT Style
 */
export function SocialIconsMobile() {
  const { t } = useTranslation();
  return (
    <div className="flex md:hidden items-center gap-2">
      {/* YouTube Subscribe Button - Gold Gradient wie auf remaike.it */}
      <a
        href={YOUTUBE_CHANNEL}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 px-4 py-2.5 rounded-full text-sm font-semibold transition-all duration-300"
        style={{
          background: 'linear-gradient(135deg, #c9a962 0%, #b08a3c 50%, #8c6a27 100%)',
          color: '#0b0b0c',
          letterSpacing: '0.35px',
          border: '1px solid rgba(201, 169, 98, 0.55)',
          boxShadow: '0 10px 28px rgba(201,169,98,0.35), 0 0 0 1px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow =
            '0 12px 32px rgba(201, 169, 98, 0.45), 0 0 0 1px rgba(0,0,0,0.5)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow =
            '0 10px 28px rgba(201,169,98,0.35), 0 0 0 1px rgba(0,0,0,0.4)';
        }}
      >
        <Youtube size={16} />
        <span>{t('subscribe')}</span>
      </a>
    </div>
  );
}

/**
 * Social Media Links für Footer - Premium Style mit Icons
 * Runde Buttons wie auf remaike.it, aber nur im Footer
 */
export function SocialLinksFooter() {
  return (
    <div className="flex items-center justify-center gap-3">
      {/* YouTube */}
      <a
        href={YOUTUBE_CHANNEL}
        target="_blank"
        rel="noopener noreferrer"
        title="YouTube"
        className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.4)',
          color: 'rgba(255, 255, 255, 0.9)',
          boxShadow: '0 6px 18px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#c9a962';
          e.currentTarget.style.color = '#c9a962';
          e.currentTarget.style.boxShadow = '0 8px 26px rgba(201,169,98,0.35)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.4)';
          e.currentTarget.style.color = 'rgba(255, 255, 255, 0.9)';
          e.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.4)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={18} height={18}>
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
        </svg>
      </a>

      {/* Facebook */}
      <a
        href={FACEBOOK_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="Facebook"
        className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.25)',
          color: 'rgba(255,255,255,0.85)',
          boxShadow: '0 6px 18px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#c9a962';
          e.currentTarget.style.color = '#c9a962';
          e.currentTarget.style.boxShadow = '0 8px 26px rgba(201,169,98,0.35)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.25)';
          e.currentTarget.style.color = 'rgba(255,255,255,0.85)';
          e.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.4)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={18} height={18}>
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      </a>

      {/* X (Twitter) */}
      <a
        href={TWITTER_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="X (Twitter)"
        className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.25)',
          color: 'rgba(255,255,255,0.85)',
          boxShadow: '0 6px 18px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#c9a962';
          e.currentTarget.style.color = '#c9a962';
          e.currentTarget.style.boxShadow = '0 8px 26px rgba(201,169,98,0.35)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.25)';
          e.currentTarget.style.color = 'rgba(255,255,255,0.85)';
          e.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.4)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={16} height={16}>
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
        </svg>
      </a>

      {/* Instagram */}
      <a
        href={INSTAGRAM_PAGE}
        target="_blank"
        rel="noopener noreferrer"
        title="Instagram"
        className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300"
        style={{
          background: '#0c0c0e',
          border: '1px solid rgba(201,169,98,0.25)',
          color: 'rgba(255,255,255,0.85)',
          boxShadow: '0 6px 18px rgba(0,0,0,0.4)',
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.borderColor = '#c9a962';
          e.currentTarget.style.color = '#c9a962';
          e.currentTarget.style.boxShadow = '0 8px 26px rgba(201,169,98,0.35)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.borderColor = 'rgba(201,169,98,0.25)';
          e.currentTarget.style.color = 'rgba(255,255,255,0.85)';
          e.currentTarget.style.boxShadow = '0 6px 18px rgba(0,0,0,0.4)';
        }}
      >
        <svg viewBox="0 0 24 24" fill="currentColor" width={18} height={18}>
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
        </svg>
      </a>
    </div>
  );
}

export default { SocialIconsDesktop, SocialIconsMobile, SocialLinksFooter };
