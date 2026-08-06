const express = require("express");
const db = require("../db");

const router = express.Router();

router.post("/", async (req, res) => {
  const row = await db.write(
    "INSERT INTO orders (account_id, sku, quantity) VALUES ($1, $2, $3) RETURNING *",
    [req.user.accountId, req.body.sku, req.body.quantity]
  );
  res.status(201).json(row);
});

router.patch("/:id/cancel", async (req, res) => {
  const row = await db.write(
    "UPDATE orders SET status = 'cancelled' WHERE id = $1 RETURNING *",
    [req.params.id]
  );
  res.json(row);
});

module.exports = router;
