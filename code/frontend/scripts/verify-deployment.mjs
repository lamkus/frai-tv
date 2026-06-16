#!/usr/bin/env node

/**
 * Deployment Verification Script
 *
 * Validates production deployment by testing:
 * - API endpoints (health, videos, analytics)
 * - Static assets (index.html, CSS, JS bundles)
 * - Video data integrity
 * - Response times and error rates
 *
 * Usage:
 *   node scripts/verify-deployment.mjs https://frai.tv
 */

import https from 'https';
import { URL } from 'url';

const TIMEOUT = 10000; // 10s timeout
const baseUrl = process.argv[2] || 'https://frai.tv';

// Color output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

// Fetch with timeout
function fetch(url) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port || 443,
      path: urlObj.pathname + urlObj.search,
      method: 'GET',
      timeout: TIMEOUT,
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          headers: res.headers,
          body: data,
        });
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    req.end();
  });
}

// Test helpers
async function testEndpoint(name, url, validator) {
  process.stdout.write(`Testing ${name}... `);
  const startTime = Date.now();

  try {
    const response = await fetch(url);
    const duration = Date.now() - startTime;

    if (validator) {
      const valid = validator(response);
      if (!valid) {
        log(`✗ FAILED (${duration}ms)`, colors.red);
        return false;
      }
    }

    log(`✓ OK (${duration}ms)`, colors.green);
    return true;
  } catch (error) {
    const duration = Date.now() - startTime;
    log(`✗ ERROR (${duration}ms): ${error.message}`, colors.red);
    return false;
  }
}

// Validators
const validators = {
  isJSON: (res) => {
    if (res.status !== 200) return false;
    try {
      JSON.parse(res.body);
      return true;
    } catch {
      return false;
    }
  },

  isHTML: (res) => {
    return res.status === 200 && res.body.includes('<!DOCTYPE html>');
  },

  hasVideos: (res) => {
    if (res.status !== 200) return false;
    try {
      const data = JSON.parse(res.body);
      return Array.isArray(data.data) && data.data.length > 0;
    } catch {
      return false;
    }
  },

  isHealthy: (res) => {
    if (res.status !== 200) return false;
    try {
      const data = JSON.parse(res.body);
      return data.status === 'ok';
    } catch {
      return false;
    }
  },
};

// Main test suite
async function runTests() {
  log('\n═══════════════════════════════════════', colors.cyan);
  log('  Deployment Verification', colors.cyan);
  log(`  Target: ${baseUrl}`, colors.cyan);
  log('═══════════════════════════════════════\n', colors.cyan);

  const results = [];

  // 1. Static assets
  log('Static Assets:', colors.yellow);
  results.push(await testEndpoint('  index.html', `${baseUrl}/`, validators.isHTML));
  results.push(
    await testEndpoint('  favicon.ico', `${baseUrl}/favicon.ico`, (res) => res.status === 200)
  );

  log('');

  // 2. API endpoints
  log('API Endpoints:', colors.yellow);
  results.push(
    await testEndpoint(
      '  /api.php?path=health',
      `${baseUrl}/api.php?path=health`,
      validators.isHealthy
    )
  );
  results.push(
    await testEndpoint(
      '  /api.php?path=videos',
      `${baseUrl}/api.php?path=videos`,
      validators.hasVideos
    )
  );

  log('');

  // 3. Video data integrity
  log('Data Integrity:', colors.yellow);
  try {
    process.stdout.write('  Checking video count... ');
    const response = await fetch(`${baseUrl}/api.php?path=videos`);
    const data = JSON.parse(response.body);
    const count = data.data?.length || 0;

    if (count > 0) {
      log(`✓ ${count} videos found`, colors.green);
      results.push(true);

      // Check for required fields
      const sampleVideo = data.data[0];
      const requiredFields = ['ytId', 'title', 'thumbnail'];
      const hasAllFields = requiredFields.every((field) => sampleVideo[field]);

      if (hasAllFields) {
        log(`  ✓ Video schema valid`, colors.green);
        results.push(true);
      } else {
        log(`  ✗ Missing required fields`, colors.red);
        results.push(false);
      }
    } else {
      log('✗ No videos found', colors.red);
      results.push(false);
    }
  } catch (error) {
    log(`✗ Error: ${error.message}`, colors.red);
    results.push(false);
  }

  log('');

  // 4. Analytics
  log('Analytics:', colors.yellow);
  results.push(
    await testEndpoint(
      '  /api.php?path=analytics/summary',
      `${baseUrl}/api.php?path=analytics/summary&days=7`,
      validators.isJSON
    )
  );

  log('');

  // Summary
  const passed = results.filter(Boolean).length;
  const total = results.length;
  const allPassed = passed === total;

  log('═══════════════════════════════════════', colors.cyan);
  if (allPassed) {
    log(`  ✓ ALL TESTS PASSED (${passed}/${total})`, colors.green);
    log('  Deployment is healthy!', colors.green);
  } else {
    log(`  ✗ SOME TESTS FAILED (${passed}/${total})`, colors.red);
    log('  Please review the errors above.', colors.yellow);
  }
  log('═══════════════════════════════════════\n', colors.cyan);

  process.exit(allPassed ? 0 : 1);
}

// Run
runTests().catch((error) => {
  log(`\n✗ Fatal error: ${error.message}\n`, colors.red);
  process.exit(1);
});
