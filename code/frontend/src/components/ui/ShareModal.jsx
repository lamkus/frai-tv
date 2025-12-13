import { useState, useEffect, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import { X, Copy, Check, Share2, Mail, MessageCircle, Send, Link2 } from 'lucide-react';
import { cn, getYouTubeThumbnail } from '../../lib/utils';

// Social platform icons (using Lucide + custom SVGs)
const TwitterIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
  </svg>
);

const FacebookIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
  </svg>
);

const WhatsAppIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
  </svg>
);

const TelegramIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
  </svg>
);

const RedditIcon = () => (
  <svg viewBox="0 0 24 24" className="w-5 h-5" fill="currentColor">
    <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z" />
  </svg>
);

/**
 * ShareModal - Social sharing dialog with platform buttons
 *
 * Features:
 * - Video preview thumbnail
 * - Direct share buttons for major platforms
 * - Copy link functionality
 * - Native share API fallback on mobile
 */
export default function ShareModal({ isOpen, onClose, video }) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState('');

  // Generate share URL
  useEffect(() => {
    if (video) {
      const url = `${window.location.origin}/video/${video.ytId || video.id}`;
      setShareUrl(url);
    }
  }, [video]);

  // Copy to clipboard
  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [shareUrl]);

  // Native share (mobile)
  const handleNativeShare = useCallback(async () => {
    if (!navigator.share) return;
    try {
      await navigator.share({
        title: video?.title || t('shareVideo'),
        text: `${t('checkOutVideo')}: ${video?.title}`,
        url: shareUrl,
      });
      onClose();
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Share failed:', err);
      }
    }
  }, [video, shareUrl, onClose]);

  // Social share handlers
  const shareHandlers = {
    twitter: () => {
      const text = encodeURIComponent(`${video?.title} - ${t('checkOutOnRemAIke')}`);
      window.open(
        `https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(shareUrl)}`,
        '_blank'
      );
    },
    facebook: () => {
      window.open(
        `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
        '_blank'
      );
    },
    whatsapp: () => {
      const text = encodeURIComponent(`${video?.title} - ${shareUrl}`);
      window.open(`https://wa.me/?text=${text}`, '_blank');
    },
    telegram: () => {
      const text = encodeURIComponent(video?.title || '');
      window.open(
        `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${text}`,
        '_blank'
      );
    },
    reddit: () => {
      const title = encodeURIComponent(video?.title || '');
      window.open(
        `https://reddit.com/submit?url=${encodeURIComponent(shareUrl)}&title=${title}`,
        '_blank'
      );
    },
    email: () => {
      const subject = encodeURIComponent(`${t('videoRecommendation')}: ${video?.title}`);
      const body = encodeURIComponent(
        `${t('foundVideo')}:\n\n${video?.title}\n\n${shareUrl}\n\n${t('enjoyWatching')}`
      );
      window.location.href = `mailto:?subject=${subject}&body=${body}`;
    },
  };

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleEscape);
      return () => window.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  if (!isOpen || !video) return null;

  const thumbnail = video.thumbnailUrl || getYouTubeThumbnail(video.ytId, 'hq');

  return (
    <div
      className="fixed inset-0 z-[70] flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fade-in"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="w-full max-w-md mx-4 bg-retro-darker border border-retro-gray/30 rounded-2xl shadow-2xl overflow-hidden animate-scale-in">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-retro-gray/20">
          <div className="flex items-center gap-2">
            <Share2 className="text-accent-gold" size={20} />
            <h2 className="font-semibold text-lg">{t('shareVideo')}</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-retro-gray/20 rounded-full transition-colors"
            aria-label={t('close')}
          >
            <X size={20} />
          </button>
        </div>

        {/* Video Preview */}
        <div className="p-4 border-b border-retro-gray/20">
          <div className="flex gap-3">
            <img src={thumbnail} alt={video.title} className="w-24 h-14 object-cover rounded-lg" />
            <div className="flex-1 min-w-0">
              <h3 className="font-medium text-sm line-clamp-2">{video.title}</h3>
              <p className="text-xs text-retro-muted mt-1">{video.channelName || 'remAIke.TV'}</p>
            </div>
          </div>
        </div>

        {/* Share Buttons */}
        <div className="p-4">
          <div className="grid grid-cols-3 gap-3">
            {/* X/Twitter */}
            <button
              onClick={shareHandlers.twitter}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-[#1DA1F2]/20 hover:text-[#1DA1F2] transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-[#1DA1F2]/20">
                <TwitterIcon />
              </div>
              <span className="text-xs">X</span>
            </button>

            {/* Facebook */}
            <button
              onClick={shareHandlers.facebook}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-[#1877F2]/20 hover:text-[#1877F2] transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-[#1877F2]/20">
                <FacebookIcon />
              </div>
              <span className="text-xs">Facebook</span>
            </button>

            {/* WhatsApp */}
            <button
              onClick={shareHandlers.whatsapp}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-[#25D366]/20 hover:text-[#25D366] transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-[#25D366]/20">
                <WhatsAppIcon />
              </div>
              <span className="text-xs">WhatsApp</span>
            </button>

            {/* Telegram */}
            <button
              onClick={shareHandlers.telegram}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-[#0088cc]/20 hover:text-[#0088cc] transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-[#0088cc]/20">
                <TelegramIcon />
              </div>
              <span className="text-xs">Telegram</span>
            </button>

            {/* Reddit */}
            <button
              onClick={shareHandlers.reddit}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-[#FF4500]/20 hover:text-[#FF4500] transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-[#FF4500]/20">
                <RedditIcon />
              </div>
              <span className="text-xs">Reddit</span>
            </button>

            {/* Email */}
            <button
              onClick={shareHandlers.email}
              className="flex flex-col items-center gap-2 p-3 rounded-xl bg-retro-dark/50 
                       hover:bg-accent-gold/20 hover:text-accent-gold transition-colors group"
            >
              <div className="p-2 rounded-full bg-retro-gray/20 group-hover:bg-accent-gold/20">
                <Mail size={20} />
              </div>
              <span className="text-xs">{t('email')}</span>
            </button>
          </div>
        </div>

        {/* Copy Link */}
        <div className="p-4 pt-0">
          <div className="flex items-center gap-2 p-3 bg-retro-dark rounded-xl border border-retro-gray/20">
            <Link2 size={18} className="text-retro-muted shrink-0" />
            <input
              type="text"
              value={shareUrl}
              readOnly
              className="flex-1 bg-transparent text-sm truncate focus:outline-none"
            />
            <button
              onClick={handleCopy}
              className={cn(
                'px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                copied
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-accent-gold/20 text-accent-gold hover:bg-accent-gold/30'
              )}
            >
              {copied ? (
                <span className="flex items-center gap-1">
                  <Check size={14} />
                  {t('copied')}
                </span>
              ) : (
                <span className="flex items-center gap-1">
                  <Copy size={14} />
                  {t('copy')}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Native Share (Mobile) */}
        {typeof navigator !== 'undefined' && navigator.share && (
          <div className="p-4 pt-0">
            <button
              onClick={handleNativeShare}
              className="w-full btn btn-primary flex items-center justify-center gap-2"
            >
              <Send size={18} />
              {t('moreOptions')}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
