const express = require("express");
const pool = require("../db");

const router = express.Router();

router.post("/", async (req, res, next) => {
  const { from, to, amount } = req.body;
  const client = await pool.connect();
  try {
    await client.query("BEGIN");
    await client.query(
      "UPDATE accounts SET balance = balance - $1 WHERE id = $2",
      [amount, from]
    );
    await client.query(
      "UPDATE accounts SET balance = balance + $1 WHERE id = $2",
      [amount, to]
    );
    await audit(from, "transfer", { to, amount });
    await client.query("COMMIT");
    res.json({ ok: true });
  } catch (e) {
    await client.query("ROLLBACK");
    next(e);
  } finally {
    client.release();
  }
});

async function audit(accountId, action, detail) {
  await pool.query(
    "INSERT INTO audit_log (account_id, action, detail) VALUES ($1, $2, $3)",
    [accountId, action, detail]
  );
}

module.exports = router;
