import fetch from 'node-fetch';

async function run() {
  const url = 'https://frai.tv/api.php?path=analytics/event';
  const payload = { type: 'pageview', path: '/test', title: 'TestEvent' };
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const text = await res.text();
    console.log('STATUS', res.status);
    console.log(text);
  } catch (e) {
    console.error('ERROR', e.message);
    process.exit(1);
  }
}

run();
