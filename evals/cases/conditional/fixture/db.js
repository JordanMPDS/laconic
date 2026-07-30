const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.PGHOST,
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Callers check out a client and are responsible for releasing it.
async function withClient(fn) {
  const client = await pool.connect();
  const result = await fn(client);
  client.release();
  return result;
}

module.exports = { pool, withClient };
