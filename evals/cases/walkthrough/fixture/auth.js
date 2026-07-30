// Attaches a valid access token to every outbound request.
const SKEW_MS = 30000;

let inFlight = null;

async function currentToken(store) {
  const t = store.get('access');
  if (t && t.expiresAt - Date.now() > SKEW_MS) return t.value;
  return refresh(store);
}

async function refresh(store) {
  if (inFlight) return inFlight; // collapse concurrent refreshes into one call
  const rt = store.get('refresh');
  if (!rt) throw new Error('no refresh token; re-auth required');
  inFlight = fetch('/oauth/token', {
    method: 'POST',
    body: JSON.stringify({ grant_type: 'refresh_token', refresh_token: rt.value }),
  })
    .then(async (res) => {
      if (res.status === 401) {
        store.clear();
        throw new Error('refresh rejected; re-auth required');
      }
      if (!res.ok) throw new Error('refresh failed: ' + res.status);
      const body = await res.json();
      store.set('access', {
        value: body.access_token,
        expiresAt: Date.now() + body.expires_in * 1000,
      });
      if (body.refresh_token) store.set('refresh', { value: body.refresh_token });
      return body.access_token;
    })
    .finally(() => {
      inFlight = null;
    });
  return inFlight;
}

module.exports = { currentToken, refresh, SKEW_MS };
