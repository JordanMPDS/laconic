const FLAG_HOST = process.env.FLAG_HOST;
const CACHE_TTL_MS = 60 * 1000;

// One in-process cache per service instance. Refetch once the TTL is up.
let cache = null;
let fetchedAt = 0;

async function getFlags() {
  if (cache && Date.now() - fetchedAt < CACHE_TTL_MS) {
    return cache;
  }

  const res = await fetch(`${FLAG_HOST}/v1/flags`, {
    headers: {
      Accept: 'application/json',
      'Cache-Control': 'max-age=3600',
    },
  });

  cache = await res.json();
  fetchedAt = Date.now();
  return cache;
}

async function isEnabled(name, userId) {
  const flags = await getFlags();
  const flag = flags[name];
  if (!flag || !flag.enabled) {
    return false;
  }
  return bucket(userId) < flag.rollout;
}

module.exports = { getFlags, isEnabled, CACHE_TTL_MS };
