const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// The dashboard does not read raw events. It reads `rollup`, which is
// truncated and rewritten by the ingest job on a fixed schedule - see
// jobs/rollup.md. Between two rewrites every row in here is byte-identical.
exports.currentRollup = async () =>
  (await pool.query('select * from rollup order by queue_name')).rows;

module.exports.pool = pool;
