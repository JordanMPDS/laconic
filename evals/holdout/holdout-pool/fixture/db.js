const { Pool } = require("pg");

// Ten connections is the per-service quota the database team gave us.
const pool = new Pool({ max: 10, connectionTimeoutMillis: 30000 });

module.exports = pool;
