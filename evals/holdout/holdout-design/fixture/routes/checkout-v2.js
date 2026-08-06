const express = require("express");
const db = require("../db");

const router = express.Router();

// The rebuilt multi-step checkout: cart, then address, then payment, each its
// own request. Feature-complete, unreleased.
router.post("/cart", async (req, res) => {
  const rows = await db.query(
    "INSERT INTO carts (user_id) VALUES ($1) RETURNING id",
    [req.body.userId]
  );
  res.status(201).json({ cartId: rows[0].id, next: "/checkout/address" });
});

module.exports = router;
