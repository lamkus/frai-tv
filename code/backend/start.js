/**
 * Plesk-Compatible Start Script for remAIke.TV Backend
 * 
 * This CommonJS wrapper allows Plesk's Node.js extension to start the
 * ES module-based backend (index.js uses "type": "module").
 * 
 * Plesk requires a .js file as the "Application Startup File" and may
 * not properly handle ES modules directly. This script uses dynamic
 * import() to load the ES module entry point.
 * 
 * Usage in Plesk:
 *   - Set "Application Startup File" to: start.js
 *   - Set "Application Root" to: /httpdocs/backend (or your path)
 *   - Click "NPM Install" then "Restart App"
 * 
 * @see https://docs.plesk.com/en-US/obsidian/administrator-guide/website-management/nodejs-support.html
 */

'use strict';

// Set production environment if not already set
process.env.NODE_ENV = process.env.NODE_ENV || 'production';

// Log startup for debugging
console.log(`[start.js] Starting remAIke.TV Backend...`);
console.log(`[start.js] NODE_ENV: ${process.env.NODE_ENV}`);
console.log(`[start.js] PORT: ${process.env.PORT || 4000}`);

// Dynamically import the ES module entry point
import('./src/index.js')
  .then(() => {
    console.log('[start.js] Backend module loaded successfully');
  })
  .catch((error) => {
    console.error('[start.js] Failed to load backend module:', error);
    process.exit(1);
  });
