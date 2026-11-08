const express = require("express");
const db = require("../db");

const router = express.Router();

// The current single-page checkout. The rebuilt multi-step flow lands behind
// routes/checkout-v2.js and is feature-complete but unreleased.
router.post("/", async (req, res) => {
  const rows = await db.query(
    "INSERT INTO carts (user_id) VALUES ($1) RETURNING id",
    [req.body.userId]
  );
  res.status(201).json({ cartId: rows[0].id });
});

module.exports = router;
