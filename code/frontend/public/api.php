<?php
/**
 * frai.tv API entrypoint for Checkdomain "SPA rewrite catches /api/*" setups.
 *
 * This file is deployed with the frontend build (Vite public/) and provides
 * JSON responses under /api.php so the SPA fallback doesn't swallow API calls.
 *
 * Call format:
 *   /api.php?path=health
 *   /api.php?path=videos
 *   /api.php?path=analytics/summary&days=7
 *   POST /api.php?path=analytics/event
 */

error_reporting(E_ALL);
ini_set('display_errors', '0');
ini_set('log_errors', '1');

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: https://frai.tv');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

function jsonOut($data, $status = 200) {
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_SLASHES);
    exit;
}

function readJsonBody() {
    $raw = file_get_contents('php://input');
    if (!$raw) return null;
    $json = json_decode($raw, true);
    return is_array($json) ? $json : null;
}

function logDebug($msg) {
    $log = __DIR__ . '/data/api-debug.log';
    @file_put_contents($log, date('c') . ' ' . $msg . "\n", FILE_APPEND | LOCK_EX);
}

function ensureDataDir() {
    $dir = __DIR__ . '/data';
    if (!is_dir($dir)) {
        @mkdir($dir, 0755, true);
    }
    return $dir;
}

$path = isset($_GET['path']) ? trim((string)$_GET['path']) : '';
$path = ltrim($path, '/');

if ($path === '') {
    jsonOut(['error' => 'Missing path'], 400);
}

// -----------------------------------------------------------------------------
// health
// -----------------------------------------------------------------------------
if ($path === 'health') {
    jsonOut([
        'status' => 'ok',
        'service' => 'frai.tv api.php',
        'timestamp' => date('c'),
    ]);
}

// -----------------------------------------------------------------------------
// videos
// Supports data/videos.json in docroot.
// Accepts either an array, {videos:[...]}, or Node-style {data:[...]}.
// Returns Node-style shape used by the frontend.
// -----------------------------------------------------------------------------
if ($path === 'videos') {
    $videosFile = __DIR__ . '/data/videos.json';
    if (!file_exists($videosFile)) {
        jsonOut([
            'data' => [],
            'pageInfo' => ['hasMore' => false, 'nextCursor' => null],
            'source' => 'missing-file',
        ]);
    }

    $raw = @file_get_contents($videosFile);
    if ($raw === false) {
        jsonOut([
            'error' => 'Cannot read videos file',
            'data' => [],
            'pageInfo' => ['hasMore' => false, 'nextCursor' => null],
            'source' => 'read-failed',
        ], 500);
    }

    // Strip UTF-8 BOM if present
    if (substr($raw, 0, 3) === "\xEF\xBB\xBF") {
        $raw = substr($raw, 3);
    }

    // If videos.json is a raw JSON array, wrap it without decoding.
    // This is more robust on shared hosting (memory limits / encoding issues).
    $trimmed = ltrim($raw);
    if ($trimmed !== '' && $trimmed[0] === '[') {
        // If file looks like an empty array, try to use a backup copy before returning.
        $t = trim($trimmed);
        if ($t === '[]') {
            $bak = __DIR__ . '/data/videos.json.bak';
            if (file_exists($bak)) {
                $bakraw = @file_get_contents($bak);
                if ($bakraw !== false) {
                    $bktrim = ltrim($bakraw);
                    if ($bktrim !== '' && $bktrim[0] === '[' && trim($bktrim) !== '[]') {
                        http_response_code(200);
                        echo '{"data":' . $bktrim . ',"pageInfo":{"hasMore":false,"nextCursor":null},"source":"data/videos.json.bak"}';
                        exit;
                    }
                }
            }
            // Log the empty-array condition for later debugging
            $size = strlen($raw);
            $mtime = @filemtime($videosFile) ?: 0;
            logDebug("videos.json appears empty (size={$size} mtime=" . ($mtime ? date('c', $mtime) : 'unknown') . ")");
        }

        http_response_code(200);
        echo '{"data":' . $trimmed . ',"pageInfo":{"hasMore":false,"nextCursor":null},"source":"data/videos.json"}';
        exit;
    }

    $json = json_decode($raw, true);

    $items = [];
    if (is_array($json)) {
        // raw array OR associative array
        if (array_keys($json) === range(0, count($json) - 1)) {
            $items = $json;
        } else if (isset($json['data']) && is_array($json['data'])) {
            $items = $json['data'];
        } else if (isset($json['videos']) && is_array($json['videos'])) {
            $items = $json['videos'];
        }
    }

    // If decode failed, return a helpful error payload (frontend will fallback)
    if (!is_array($json) && json_last_error() !== JSON_ERROR_NONE) {
        jsonOut([
            'error' => 'Invalid videos.json',
            'details' => json_last_error_msg(),
            'data' => [],
            'pageInfo' => ['hasMore' => false, 'nextCursor' => null],
            'source' => 'decode-failed',
        ], 500);
    }

    // If we decoded JSON successfully but ended up with no items, try a backup as a fallback
    if (empty($items)) {
        $bak = __DIR__ . '/data/videos.json.bak';
        if (file_exists($bak)) {
            $bakraw = @file_get_contents($bak);
            if ($bakraw !== false) {
                $bkjson = json_decode($bakraw, true);
                if (is_array($bkjson)) {
                    // prefer raw array in bak or {data:[]}
                    if (array_keys($bkjson) === range(0, count($bkjson) - 1)) {
                        $items = $bkjson;
                    } else if (isset($bkjson['data']) && is_array($bkjson['data'])) {
                        $items = $bkjson['data'];
                    }
                    if (!empty($items)) {
                        logDebug('Using videos.json.bak fallback with ' . count($items) . ' items');
                        jsonOut([
                            'data' => $items,
                            'pageInfo' => ['hasMore' => false, 'nextCursor' => null],
                            'source' => 'data/videos.json.bak',
                        ]);
                    }
                }
            }
        }
    }

    jsonOut([
        'data' => $items,
        'pageInfo' => ['hasMore' => false, 'nextCursor' => null],
        'source' => 'data/videos.json',
    ]);
}

// -----------------------------------------------------------------------------
// analytics/event
// Minimal event sink that writes NDJSON to data/analytics_events.ndjson
// -----------------------------------------------------------------------------
if ($path === 'analytics/event') {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        jsonOut(['error' => 'Method not allowed'], 405);
    }

    $evt = readJsonBody();
    if (!$evt) {
        jsonOut(['error' => 'Invalid JSON'], 400);
    }

    $dir = ensureDataDir();
    $file = $dir . '/analytics_events.ndjson';

    $row = [
        'id' => bin2hex(random_bytes(8)),
        'occurredAt' => date('c'),
        'type' => $evt['type'] ?? null,
        'path' => $evt['path'] ?? null,
        'title' => $evt['title'] ?? null,
        'ytId' => $evt['ytId'] ?? null,
        'sessionId' => $evt['sessionId'] ?? null,
        'meta' => $evt['meta'] ?? null,
    ];

    @file_put_contents($file, json_encode($row, JSON_UNESCAPED_SLASHES) . "\n", FILE_APPEND | LOCK_EX);

    jsonOut(['ok' => true]);
}

// -----------------------------------------------------------------------------
// analytics/summary
// Aggregates last N days from NDJSON event log.
// -----------------------------------------------------------------------------
if ($path === 'analytics/summary') {
    $days = isset($_GET['days']) ? intval($_GET['days']) : 7;
    if ($days <= 0) $days = 7;
    if ($days > 31) $days = 31;

    $file = __DIR__ . '/data/analytics_events.ndjson';
    if (!file_exists($file)) {
        jsonOut([
            'range' => ['days' => $days],
            'totals' => ['totalEvents' => 0, 'uniqueSessions' => 0],
            'topPages' => [],
            'recentEvents' => [],
            'source' => 'missing-log',
        ]);
    }

    $cutoff = time() - ($days * 86400);

    $total = 0;
    $sessions = [];
    $pageCounts = [];
    $recent = [];

    $fh = fopen($file, 'r');
    if (!$fh) {
        jsonOut(['error' => 'Cannot read log'], 500);
    }

    while (!feof($fh)) {
        $line = trim(fgets($fh));
        if ($line === '') continue;
        $row = json_decode($line, true);
        if (!is_array($row)) continue;

        $ts = isset($row['occurredAt']) ? strtotime($row['occurredAt']) : 0;
        if ($ts && $ts < $cutoff) {
            continue;
        }

        $total += 1;
        if (!empty($row['sessionId'])) {
            $sessions[$row['sessionId']] = true;
        }

        // Count page views if path present
        if (!empty($row['path'])) {
            $p = $row['path'];
            if (!isset($pageCounts[$p])) $pageCounts[$p] = 0;
            $pageCounts[$p] += 1;
        }

        // Keep up to 50 most recent (we'll sort after)
        $recent[] = $row;
        if (count($recent) > 200) {
            array_shift($recent);
        }
    }
    fclose($fh);

    usort($recent, function($a, $b) {
        return strtotime($b['occurredAt'] ?? '') <=> strtotime($a['occurredAt'] ?? '');
    });
    $recent = array_slice($recent, 0, 20);

    arsort($pageCounts);
    $topPages = [];
    foreach ($pageCounts as $p => $c) {
        $topPages[] = ['path' => $p, 'count' => $c];
        if (count($topPages) >= 10) break;
    }

    jsonOut([
        'range' => ['days' => $days],
        'totals' => ['totalEvents' => $total, 'uniqueSessions' => count($sessions)],
        'topPages' => $topPages,
        'recentEvents' => $recent,
        'source' => 'data/analytics_events.ndjson',
    ]);
}

// -----------------------------------------------------------------------------
// analytics/backup
// Move current analytics log to backups with timestamp. Protect with simple key file.
// Usage: /api.php?path=analytics/backup&key=SECRET
// Place secret token in `public/data/ANALYTICS_ADMIN_KEY` (simple protected method)
// -----------------------------------------------------------------------------
if ($path === 'analytics/backup') {
    $key = $_GET['key'] ?? '';
    $keyFile = __DIR__ . '/data/ANALYTICS_ADMIN_KEY';
    if (!file_exists($keyFile) || trim(file_get_contents($keyFile)) !== trim($key)) {
        jsonOut(['error' => 'Forbidden'], 403);
    }

    $dir = __DIR__ . '/data';
    $file = $dir . '/analytics_events.ndjson';
    if (!file_exists($file)) {
        jsonOut(['ok' => true, 'message' => 'No log to backup']);
    }

    if (!is_dir($dir . '/backups')) mkdir($dir . '/backups', 0755, true);
    $dst = sprintf('%s/backups/analytics_events_%s.ndjson', $dir, date('Ymd-His'));
    if (!@rename($file, $dst)) {
        jsonOut(['error' => 'Backup failed'], 500);
    }

    jsonOut(['ok' => true, 'path' => basename($dst)]);
}

// -----------------------------------------------------------------------------
// admin/youtube (Proxy/Stub for local admin server)
// -----------------------------------------------------------------------------
if (strpos($path, 'admin/youtube') === 0) {
    jsonOut([
        'error' => 'Admin Server Required',
        'message' => 'This feature requires the remAIke Admin Server running on localhost:3333.',
        'hint' => 'Run "npm run admin" locally to use the YouTube Manager.',
        'connected' => false
    ], 503);
}

// -----------------------------------------------------------------------------
// youtube/webhook - PubSubHubbub receiver for YouTube channel updates
// - GET: verification (hub.challenge)
// - POST: receives push notifications and triggers a GitHub Actions dispatch
// -----------------------------------------------------------------------------
if (strpos($path, 'youtube/webhook') === 0) {
    // Verification challenge
    if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['hub_challenge'])) {
        echo $_GET['hub_challenge'];
        exit;
    }

    // Only accept POST for notifications
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        jsonOut(['ok' => true]);
    }

    $raw = file_get_contents('php://input');

    // Optional secret verification
    $secretFile = __DIR__ . '/data/YOUTUBE_WEBHOOK_SECRET';
    if (file_exists($secretFile)) {
        $secret = trim(file_get_contents($secretFile));
        $signature = $_SERVER['HTTP_X_HUB_SIGNATURE'] ?? '';
        $expected = 'sha1=' . hash_hmac('sha1', $raw, $secret);
        if (!hash_equals($expected, $signature)) {
            jsonOut(['error' => 'Invalid signature'], 403);
        }
    }

    // Trigger GitHub Actions workflow via repository dispatch
    $tokenFile = __DIR__ . '/data/YOUTUBE_GITHUB_TOKEN';
    $repoFile = __DIR__ . '/data/YOUTUBE_GITHUB_REPO';
    if (!file_exists($tokenFile) || !file_exists($repoFile)) {
        // No token/repo configured - accept but don't dispatch
        jsonOut(['ok' => true, 'dispatched' => false, 'message' => 'No dispatch token configured']);
    }

    $token = trim(file_get_contents($tokenFile));
    $repo = trim(file_get_contents($repoFile)); // expected format owner/repo

    $url = "https://api.github.com/repos/{$repo}/actions/workflows/youtube-sync.yml/dispatches";
    $body = json_encode([ 'ref' => 'main', 'inputs' => ['trigger' => 'webhook'] ]);

    $opts = [
        'http' => [
            'method' => 'POST',
            'header' => "Content-Type: application/json\r\n" .
                        "Authorization: token {$token}\r\n" .
                        "User-Agent: frai-webhook\r\n" .
                        "Accept: application/vnd.github.v3+json\r\n",
            'content' => $body,
            'timeout' => 10,
        ],
    ];

    $ctx = stream_context_create($opts);
    $result = @file_get_contents($url, false, $ctx);
    if ($result === false) {
        jsonOut(['ok' => false, 'dispatched' => false, 'message' => 'Failed to call GitHub API'], 502);
    }

    jsonOut(['ok' => true, 'dispatched' => true]);
}


jsonOut(['error' => 'Not found', 'path' => $path], 404);
