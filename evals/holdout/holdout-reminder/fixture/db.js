const { Pool } = require("pg");

const pool = new Pool();

async function query(text, params) {
  const res = await pool.query(text, params);
  return res.rows;
}

module.exports = { query };
