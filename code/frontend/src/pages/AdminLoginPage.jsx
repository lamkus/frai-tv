import { useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';

function useQuery() {
  const location = useLocation();
  return useMemo(() => new URLSearchParams(location.search), [location.search]);
}

async function fetchJson(url, { method = 'GET', headers = {}, body } = {}) {
  const res = await fetch(url, {
    method,
    headers: {
      'content-type': 'application/json',
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  const json = text ? JSON.parse(text) : null;

  if (!res.ok) {
    const message = json?.error || `Request failed (${res.status})`;
    throw new Error(message);
  }

  return json;
}

export default function AdminLoginPage() {
  const query = useQuery();
  const [adminSecret, setAdminSecret] = useState(() => sessionStorage.getItem('adminSecret') || '');
  const [status, setStatus] = useState(null);
  const [statusError, setStatusError] = useState('');
  const [busy, setBusy] = useState(false);

  const [ytId, setYtId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [updateResult, setUpdateResult] = useState('');

  const connectedHint = query.get('connected');

  useEffect(() => {
    sessionStorage.setItem('adminSecret', adminSecret);
  }, [adminSecret]);

  async function refreshStatus() {
    setStatusError('');
    setStatus(null);

    if (!adminSecret) {
      setStatusError('ADMIN secret required');
      return;
    }

    try {
      const json = await fetchJson('/api/admin/youtube/oauth/status', {
        headers: { 'x-admin-secret': adminSecret },
      });
      setStatus(json);
    } catch (e) {
      setStatusError(e?.message || 'Failed to load status');
    }
  }

  useEffect(() => {
    // If we just got redirected back from OAuth, try refreshing immediately.
    if (connectedHint === '1' && adminSecret) {
      refreshStatus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [connectedHint]);

  async function startOAuth() {
    setBusy(true);
    setStatusError('');
    setUpdateResult('');
    try {
      if (!adminSecret) throw new Error('ADMIN secret required');
      const json = await fetchJson('/api/admin/youtube/oauth/url', {
        headers: { 'x-admin-secret': adminSecret },
      });
      window.location.href = json.url;
    } catch (e) {
      setStatusError(e?.message || 'Failed to start OAuth');
    } finally {
      setBusy(false);
    }
  }

  async function disconnect() {
    setBusy(true);
    setStatusError('');
    try {
      if (!adminSecret) throw new Error('ADMIN secret required');
      await fetchJson('/api/admin/youtube/oauth/disconnect', {
        method: 'POST',
        headers: { 'x-admin-secret': adminSecret },
      });
      setStatus({ connected: false });
    } catch (e) {
      setStatusError(e?.message || 'Failed to disconnect');
    } finally {
      setBusy(false);
    }
  }

  async function pushUpdate() {
    setBusy(true);
    setUpdateResult('');
    setStatusError('');

    try {
      if (!adminSecret) throw new Error('ADMIN secret required');
      if (!ytId) throw new Error('YouTube video ID required');
      if (!title && !description) throw new Error('Title or description required');

      await fetchJson(`/api/admin/youtube/videos/${encodeURIComponent(ytId)}`, {
        method: 'POST',
        headers: { 'x-admin-secret': adminSecret },
        body: {
          title: title || undefined,
          description: description || undefined,
        },
      });
      setUpdateResult('Updated successfully.');
      await refreshStatus();
    } catch (e) {
      setUpdateResult('');
      setStatusError(e?.message || 'Failed to update video');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-2xl font-semibold">Admin Login</h1>
      <p className="mt-2 text-sm opacity-80">
        Connect YouTube OAuth once, then push metadata updates.
      </p>

      <div className="mt-6 rounded-xl border border-white/10 bg-white/5 p-4">
        <label className="block text-sm font-medium">Admin Secret</label>
        <input
          className="mt-2 w-full rounded-md border border-white/10 bg-black/20 px-3 py-2"
          type="password"
          value={adminSecret}
          onChange={(e) => setAdminSecret(e.target.value)}
          placeholder="Set ADMIN_SECRET on backend and paste it here"
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            className="rounded-md bg-white/10 px-3 py-2 text-sm hover:bg-white/15 disabled:opacity-50"
            onClick={refreshStatus}
            disabled={busy}
          >
            Check status
          </button>
          <button
            className="rounded-md bg-white px-3 py-2 text-sm text-black hover:bg-white/90 disabled:opacity-50"
            onClick={startOAuth}
            disabled={busy}
          >
            Connect YouTube OAuth
          </button>
          <button
            className="rounded-md bg-white/10 px-3 py-2 text-sm hover:bg-white/15 disabled:opacity-50"
            onClick={disconnect}
            disabled={busy}
          >
            Disconnect
          </button>
        </div>

        {status && (
          <div className="mt-4 text-sm">
            <div>
              Status:{' '}
              <span className="font-medium">
                {status.connected ? 'CONNECTED' : 'NOT CONNECTED'}
              </span>
            </div>
            {status.connected && (
              <div className="mt-1 opacity-80">
                <div>Has refresh token: {String(status.has_refresh_token)}</div>
                <div>
                  Expiry: {status.expiry_date ? new Date(status.expiry_date).toISOString() : 'n/a'}
                </div>
              </div>
            )}
          </div>
        )}

        {statusError && <div className="mt-4 text-sm text-red-200">{statusError}</div>}
      </div>

      <div className="mt-6 rounded-xl border border-white/10 bg-white/5 p-4">
        <h2 className="text-lg font-semibold">Push metadata</h2>
        <div className="mt-4 grid gap-3">
          <div>
            <label className="block text-sm font-medium">YouTube Video ID</label>
            <input
              className="mt-2 w-full rounded-md border border-white/10 bg-black/20 px-3 py-2"
              value={ytId}
              onChange={(e) => setYtId(e.target.value)}
              placeholder="e.g. 3gzbxznJ_PM"
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Title</label>
            <input
              className="mt-2 w-full rounded-md border border-white/10 bg-black/20 px-3 py-2"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="New YouTube title (optional)"
            />
          </div>
          <div>
            <label className="block text-sm font-medium">Description</label>
            <textarea
              className="mt-2 w-full rounded-md border border-white/10 bg-black/20 px-3 py-2"
              rows={8}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="New YouTube description (optional)"
            />
          </div>

          <div className="flex gap-2">
            <button
              className="rounded-md bg-white px-3 py-2 text-sm text-black hover:bg-white/90 disabled:opacity-50"
              onClick={pushUpdate}
              disabled={busy}
            >
              Push to YouTube
            </button>
          </div>

          {updateResult && <div className="text-sm text-green-200">{updateResult}</div>}
        </div>
      </div>
    </div>
  );
}
