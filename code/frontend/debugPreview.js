import { spawn } from 'child_process';
import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const cwd = __dirname;

const server = spawn('npm', ['run', 'preview', '--', '--host', '127.0.0.1', '--port', '4173'], {
  cwd,
  env: process.env,
  stdio: ['ignore', 'pipe', 'pipe'],
  shell: process.platform === 'win32',
});

server.stdout.on('data', (data) => {
  const text = data.toString();
  process.stdout.write(text);
  if (text.includes('Local:')) {
    runBrowser().catch((err) => {
      console.error('Browser run failed:', err);
      shutdown();
    });
  }
});

server.stderr.on('data', (data) => process.stderr.write(data));
server.on('exit', (code) => {
  console.log(`Preview server exited with code ${code}`);
});

let ran = false;
async function runBrowser() {
  if (ran) return;
  ran = true;
  console.log('Launching headless Chromium...');
  const browser = await chromium.launch();
  const page = await browser.newPage();
  page.on('console', (msg) => {
    console.log(`[browser:${msg.type()}] ${msg.text()}`);
  });
  page.on('pageerror', (err) => {
    console.error('[pageerror]', err.message, err.stack);
  });
  try {
    await page.goto('http://127.0.0.1:4173', { waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
  } catch (err) {
    console.error('Navigation failed:', err.message);
  } finally {
    await browser.close();
    shutdown();
  }
}

function shutdown() {
  if (!server.killed) {
    server.kill();
  }
}
