const Redis = require("ioredis");

// The session store. One Redis, shared by every worker on every box - it is
// already the only piece of state the workers have in common.
const client = new Redis(process.env.REDIS_URL);

async function getSession(token) {
  const raw = await client.get(`sess:${token}`);
  return raw ? JSON.parse(raw) : null;
}

async function putSession(token, data, ttlSeconds) {
  await client.set(`sess:${token}`, JSON.stringify(data), "EX", ttlSeconds);
}

module.exports = { client, getSession, putSession };
