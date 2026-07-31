const { redis } = require('./redis-client');

const WINDOW_MS = 60000;
const MAX_REQUESTS = 100;

// Fixed-window counter. One key per client per minute; the key expires with
// the window, so old counters clean themselves up.
async function limit(req, res, next) {
  const window = Math.floor(Date.now() / WINDOW_MS);
  const key = `rl:${req.ip}:${window}`;

  const count = await redis.incr(key);
  if (count === 1) {
    await redis.expire(key, 60);
  }

  if (count > MAX_REQUESTS) {
    res.set('Retry-After', '60');
    return res.status(429).json({ error: 'rate limit exceeded' });
  }

  return next();
}

module.exports = { limit, MAX_REQUESTS, WINDOW_MS };
