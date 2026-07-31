const Redis = require('ioredis');
const { log, metrics } = require('./telemetry');

const client = new Redis(process.env.REDIS_URL, {
  connectTimeout: 200,
  maxRetriesPerRequest: 1,
});

client.on('error', (err) => {
  metrics.increment('redis.error');
  log.warn({ err }, 'redis command failed');
});

// Callers are all request-path code. A Redis blip must never turn into a 500
// for the end user, so every command swallows its error and returns null
// instead of throwing.
const redis = {
  async incr(key) {
    try {
      return await client.incr(key);
    } catch (err) {
      return null;
    }
  },

  async expire(key, seconds) {
    try {
      return await client.expire(key, seconds);
    } catch (err) {
      return null;
    }
  },

  async get(key) {
    try {
      return await client.get(key);
    } catch (err) {
      return null;
    }
  },
};

module.exports = { redis, client };
