/**
 * PM2 Ecosystem Configuration for remAIke.TV Backend
 * 
 * This file configures PM2 to manage the Node.js backend process on Strato VPS.
 * Use CommonJS format (.cjs) since PM2 requires it even for ES module projects.
 * 
 * Usage:
 *   pm2 start ecosystem.config.cjs --env production
 *   pm2 save
 *   pm2 startup
 * 
 * @see https://pm2.keymetrics.io/docs/usage/application-declaration/
 */

module.exports = {
  apps: [
    {
      name: 'remaike-backend',
      script: 'src/index.js',
      
      // Environment & Node.js settings
      node_args: '--experimental-specifier-resolution=node',
      interpreter: 'node',
      
      // Process management
      instances: 1,                    // Single instance (scale up on dedicated server)
      exec_mode: 'fork',               // Use fork mode for single instance
      autorestart: true,               // Auto-restart on crash
      watch: false,                    // Disable watch in production
      max_memory_restart: '500M',      // Restart if memory exceeds 500MB
      
      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      error_file: './logs/pm2-error.log',
      out_file: './logs/pm2-out.log',
      merge_logs: true,
      
      // Environment variables (development)
      env: {
        NODE_ENV: 'development',
        PORT: 4000
      },
      
      // Environment variables (production) - use with --env production
      env_production: {
        NODE_ENV: 'production',
        PORT: 4000,
        // These should be set via .env file or Plesk environment settings:
        // DATABASE_URL: 'postgres://...',
        // YOUTUBE_API_KEY: '...'
      }
    }
  ],

  // PM2 Deploy configuration for Git-based deployment
  deploy: {
    production: {
      // SSH user and host (adjust to your Strato VPS)
      user: 'root',
      host: 'your-strato-vps-ip',
      ref: 'origin/main',
      repo: 'git@github.com:your-username/remAIke.TV.git',
      path: '/var/www/remaike',
      
      // Post-deploy commands
      'pre-deploy-local': '',
      'post-deploy': 'cd code/backend && npm install && pm2 reload ecosystem.config.cjs --env production',
      'pre-setup': ''
    }
  }
};
