const express = require("express");
const db = require("../db");

const router = express.Router();

// Every request to /v1 carries an API key. Keys belong to a client account;
// one client may call from many addresses, and several clients share an
// address when they sit behind the same corporate NAT.
router.use(async (req, res, next) => {
  const key = req.get("X-Api-Key");
  if (!key) return res.status(401).end();
  const rows = await db.query(
    "SELECT client_id, plan FROM api_keys WHERE key = $1 AND revoked_at IS NULL",
    [key]
  );
  if (!rows.length) return res.status(401).end();
  req.client = rows[0];
  next();
});

router.get("/reports", async (req, res) => {
  const rows = await db.query(
    "SELECT id, name, generated_at FROM reports WHERE client_id = $1 ORDER BY generated_at DESC LIMIT 100",
    [req.client.client_id]
  );
  res.json(rows);
});

router.post("/reports", async (req, res) => {
  const rows = await db.query(
    "INSERT INTO reports (client_id, name) VALUES ($1, $2) RETURNING id",
    [req.client.client_id, req.body.name]
  );
  res.status(201).json(rows[0]);
});

module.exports = router;
