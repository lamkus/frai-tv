import fs from 'node:fs/promises';
import path from 'node:path';

const TOKEN_SETTINGS_KEY = 'youtube_oauth_tokens';
const TOKEN_FILE = path.resolve(process.cwd(), 'tmp', 'youtube_oauth_tokens.json');

function getRequiredEnv(name) {
  const v = process.env[name];
  if (!v) throw new Error(`${name} is required`);
  return v;
}

export function requireAdminSecret(req) {
  const expected = process.env.ADMIN_SECRET;
  if (!expected) return { ok: false, status: 503, error: 'ADMIN_SECRET not set' };

  const provided = req.get('x-admin-secret') || '';
  if (!provided || provided !== expected) return { ok: false, status: 401, error: 'Unauthorized' };

  return { ok: true };
}

export async function createOAuthClient() {
  // Lazy import to avoid boot crashes if dependency missing in certain envs
  const { google } = await import('googleapis');
  const clientId = getRequiredEnv('YOUTUBE_OAUTH_CLIENT_ID');
  const clientSecret = getRequiredEnv('YOUTUBE_OAUTH_CLIENT_SECRET');
  const redirectUri = getRequiredEnv('YOUTUBE_OAUTH_REDIRECT_URI');

  return new google.auth.OAuth2(clientId, clientSecret, redirectUri);
}

export async function getAuthUrl({ state }) {
  const oauth2Client = await createOAuthClient();

  // Full access needed for updating titles/descriptions/playlists
  const scopes = ['https://www.googleapis.com/auth/youtube'];

  return oauth2Client.generateAuthUrl({
    access_type: 'offline',
    prompt: 'consent',
    scope: scopes,
    state,
    include_granted_scopes: true,
  });
}

export async function exchangeCodeForTokens(code) {
  const oauth2Client = await createOAuthClient();
  const { tokens } = await oauth2Client.getToken(code);
  return tokens;
}

export async function saveTokens({ prisma, tokens }) {
  const serialized = JSON.stringify(tokens);

  if (prisma) {
    await prisma.settings.upsert({
      where: { key: TOKEN_SETTINGS_KEY },
      create: { key: TOKEN_SETTINGS_KEY, value: serialized },
      update: { value: serialized },
    });
    return;
  }

  await fs.mkdir(path.dirname(TOKEN_FILE), { recursive: true });
  await fs.writeFile(TOKEN_FILE, serialized, 'utf8');
}

export async function loadTokens({ prisma }) {
  if (prisma) {
    const row = await prisma.settings.findUnique({ where: { key: TOKEN_SETTINGS_KEY } });
    if (!row?.value) return null;
    try {
      return JSON.parse(row.value);
    } catch {
      return null;
    }
  }

  try {
    const txt = await fs.readFile(TOKEN_FILE, 'utf8');
    return JSON.parse(txt);
  } catch {
    return null;
  }
}

export async function clearTokens({ prisma }) {
  if (prisma) {
    try {
      await prisma.settings.delete({ where: { key: TOKEN_SETTINGS_KEY } });
    } catch {
      // ignore
    }
    return;
  }

  try {
    await fs.rm(TOKEN_FILE, { force: true });
  } catch {
    // ignore
  }
}

export async function getYoutubeClient({ prisma }) {
  const { google } = await import('googleapis');
  const oauth2Client = await createOAuthClient();

  const tokens = await loadTokens({ prisma });
  if (!tokens) return null;

  oauth2Client.setCredentials(tokens);
  return google.youtube({ version: 'v3', auth: oauth2Client });
}
