const express = require("express");
const db = require("../db");

const router = express.Router();

router.patch("/:id", async (req, res) => {
  const row = await db.write(
    "UPDATE accounts SET display_name = $1, billing_email = $2 WHERE id = $3 RETURNING *",
    [req.body.display_name, req.body.billing_email, req.params.id]
  );
  res.json(row);
});

router.delete("/:id", async (req, res) => {
  await db.write("UPDATE accounts SET deleted_at = now() WHERE id = $1 RETURNING id",
    [req.params.id]);
  res.status(204).end();
});

module.exports = router;
