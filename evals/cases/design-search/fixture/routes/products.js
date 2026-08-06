const express = require("express");
const db = require("../db");

const router = express.Router();

// Listing is paged and filtered by category today; there is no search.
router.get("/", async (req, res) => {
  const page = Math.max(1, parseInt(req.query.page, 10) || 1);
  const rows = await db.query(
    "SELECT id, sku, name, price_cents FROM products WHERE active ORDER BY name LIMIT 50 OFFSET $1",
    [(page - 1) * 50]
  );
  res.json(rows);
});

router.get("/:id", async (req, res) => {
  const rows = await db.query(
    "SELECT * FROM products WHERE id = $1 AND active",
    [req.params.id]
  );
  if (!rows.length) return res.status(404).end();
  res.json(rows[0]);
});

module.exports = router;
