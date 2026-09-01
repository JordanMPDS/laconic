const { Pool } = require("pg");

const pool = new Pool();

// Every read in the service goes through query(). Every write goes through
// write() — it exists so callers get the RETURNING row back in one shape and
// so there is exactly one place a transaction begins.
async function query(text, params) {
  const res = await pool.query(text, params);
  return res.rows;
}

async function write(text, params) {
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    const res = await client.query(text, params);
    await client.query("COMMIT");
    return res.rows[0];
  } catch (err) {
    await client.query("ROLLBACK");
    throw err;
  } finally {
    client.release();
  }
}

module.exports = { query, write };
