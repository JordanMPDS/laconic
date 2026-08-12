const db = require('../db');

// GET /api/metrics - what the dashboard renders from today.
// Reads the rollup table. Typical response is 4KB and takes 30ms.
module.exports = async (req, res) => {
  const rows = await db.currentRollup();
  res.setHeader('Cache-Control', 'no-store');
  res.json({ rows, computed_at: rows[0] && rows[0].computed_at });
};
