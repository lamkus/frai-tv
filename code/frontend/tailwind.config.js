/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      // ═══════════════════════════════════════════════════════════════
      // remAIke.TV RetroTVManager - Custom Design System
      // Responsive: Mobile → 1080p Desktop → 4K Workstation
      // ═══════════════════════════════════════════════════════════════

      screens: {
        // Mobile First Breakpoints
        xs: '375px', // iPhone SE, small phones
        sm: '640px', // Large phones, small tablets
        md: '768px', // Tablets
        lg: '1024px', // Small desktops, laptops
        xl: '1280px', // Standard desktop
        '2xl': '1536px', // Large desktop
        '3xl': '1920px', // Full HD 1080p
        '4k': '2560px', // QHD / 1440p
        '5k': '3840px', // 4K UHD
      },

      colors: {
        // RetroTV Theme - Adapted from remaike.IT Premium Dark Theme
        retro: {
          black: '#0a0a0b', // --bg
          darker: '#111113', // --bg-secondary
          dark: '#161618', // --bg-card
          gray: '#2c2c2e', // --border
          light: '#3a3a4a',
          muted: '#8e8e93', // --text-muted
          white: '#f5f5f7', // --text
        },
        // Accent Colors - Gold/Amber Theme (remAIke.IT)
        accent: {
          gold: '#c9a962', // --accent (remaike.IT Gold)
          amber: '#c9a962', // Unified to remaike.IT Gold
          honey: '#a88b4a', // Darker Gold gradient end
          red: '#e50914',
          orange: '#ff6b35',
          cyan: '#00d4ff',
          purple: '#8b5cf6',
          green: '#00e676',
        },
        // Glass/Overlay - Enhanced blur effects
        glass: {
          light: 'rgba(255, 255, 255, 0.05)',
          medium: 'rgba(255, 255, 255, 0.08)',
          card: 'rgba(26, 26, 36, 0.6)',
          dark: 'rgba(0, 0, 0, 0.6)',
          heavy: 'rgba(10, 10, 12, 0.9)',
        },
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        display: ['Bebas Neue', 'Impact', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },

      fontSize: {
        // Fluid Typography - scales with viewport
        'fluid-xs': 'clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)',
        'fluid-sm': 'clamp(0.875rem, 0.8rem + 0.375vw, 1rem)',
        'fluid-base': 'clamp(1rem, 0.9rem + 0.5vw, 1.125rem)',
        'fluid-lg': 'clamp(1.125rem, 1rem + 0.625vw, 1.25rem)',
        'fluid-xl': 'clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem)',
        'fluid-2xl': 'clamp(1.5rem, 1.25rem + 1.25vw, 2rem)',
        'fluid-3xl': 'clamp(1.875rem, 1.5rem + 1.875vw, 2.5rem)',
        'fluid-4xl': 'clamp(2.25rem, 1.75rem + 2.5vw, 3rem)',
        'fluid-5xl': 'clamp(3rem, 2rem + 5vw, 4.5rem)',
        'fluid-hero': 'clamp(2.5rem, 2rem + 4vw, 6rem)',
      },

      spacing: {
        // Custom spacing for media grids
        18: '4.5rem',
        22: '5.5rem',
        30: '7.5rem',
        34: '8.5rem',
        68: '17rem',
        76: '19rem',
        84: '21rem',
        88: '22rem',
        92: '23rem',
        100: '25rem',
        112: '28rem',
        128: '32rem',
      },

      aspectRatio: {
        video: '16 / 9',
        poster: '2 / 3',
        wide: '21 / 9',
        ultrawide: '32 / 9',
        square: '1 / 1',
      },

      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'fade-up': 'fadeUp 0.4s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        shimmer: 'shimmer 2s infinite linear',
        'pulse-slow': 'pulse 3s infinite',
        glow: 'glow 2s ease-in-out infinite alternate',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(229, 9, 20, 0.5)' },
          '100%': { boxShadow: '0 0 20px rgba(229, 9, 20, 0.8)' },
        },
      },

      backdropBlur: {
        xs: '2px',
      },

      boxShadow: {
        card: '0 4px 20px rgba(0, 0, 0, 0.5)',
        'card-hover': '0 8px 40px rgba(0, 0, 0, 0.7)',
        'neon-red': '0 0 30px rgba(229, 9, 20, 0.5)',
        'neon-cyan': '0 0 30px rgba(0, 212, 255, 0.5)',
        'inner-dark': 'inset 0 2px 4px rgba(0, 0, 0, 0.3)',
      },

      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(var(--tw-gradient-stops))',
        'hero-gradient':
          'linear-gradient(to right, rgba(10,10,10,1) 0%, rgba(10,10,10,0.8) 30%, rgba(10,10,10,0) 60%)',
        'card-gradient': 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 60%)',
        shimmer: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
      },

      transitionDuration: {
        250: '250ms',
        350: '350ms',
        400: '400ms',
      },

      scale: {
        98: '0.98',
        102: '1.02',
      },

      zIndex: {
        60: '60',
        70: '70',
        80: '80',
        90: '90',
        100: '100',
      },

      gridTemplateColumns: {
        // Video grid columns for different screen sizes
        'video-mobile': 'repeat(2, minmax(140px, 1fr))',
        'video-tablet': 'repeat(3, minmax(180px, 1fr))',
        'video-desktop': 'repeat(4, minmax(200px, 1fr))',
        'video-hd': 'repeat(5, minmax(220px, 1fr))',
        'video-fhd': 'repeat(6, minmax(240px, 1fr))',
        'video-4k': 'repeat(8, minmax(280px, 1fr))',
      },
    },
  },
  plugins: [require('@tailwindcss/aspect-ratio')],
};
