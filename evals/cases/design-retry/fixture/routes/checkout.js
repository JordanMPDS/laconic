const express = require("express");
const db = require("../db");
const payments = require("../payments");

const router = express.Router();

router.post("/:orderId/pay", async (req, res) => {
  const rows = await db.query(
    "SELECT id, total_cents, currency, customer_id, status FROM orders WHERE id = $1",
    [req.params.orderId]
  );
  if (!rows.length) return res.status(404).end();
  const order = rows[0];
  if (order.status !== "pending") return res.status(409).json({ status: order.status });

  try {
    const charge = await payments.charge({
      amountCents: order.total_cents,
      currency: order.currency,
      customerId: order.customer_id,
      source: req.body.source,
    });
    await db.query(
      "UPDATE orders SET status = 'paid', charge_id = $2 WHERE id = $1",
      [order.id, charge.id]
    );
    res.json({ status: "paid", charge: charge.id });
  } catch (err) {
    // Anything that throws lands here, including a timeout, and the customer
    // is shown a failure.
    res.status(502).json({ error: "payment failed" });
  }
});

module.exports = router;
