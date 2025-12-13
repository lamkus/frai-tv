import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite configuration for the frontend. This config enables the React plugin and
// proxies API requests to the backend server running on port 4000 during development.
// Adjust the proxy target if your backend runs on a different port or host.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:4000',
    },
  },
  build: {
    // Target for better browser compatibility (Safari 14+, Chrome 87+)
    target: ['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14'],
    // Ensure sourcemaps for debugging
    sourcemap: false,
    // CSS code splitting
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          ui: ['lucide-react', 'clsx'],
          data: ['./src/data/remaikeData.js'],
        },
      },
    },
  },
  // Ensure modern JavaScript features are transpiled for Safari
  esbuild: {
    target: 'es2020',
  },
});
