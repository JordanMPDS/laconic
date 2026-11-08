const express = require("express");
const db = require("../db");

const router = express.Router();

router.post("/", async (req, res) => {
  const [appt] = await db.query(
    "INSERT INTO appointments (patient_id, starts_at) VALUES ($1, $2) RETURNING id",
    [req.body.patientId, req.body.startsAt]
  );
  await db.query(
    "INSERT INTO jobs (kind, payload) VALUES ('booking-confirmation', $1)",
    [{ appointmentId: appt.id }]
  );
  res.status(201).json({ id: appt.id });
});

router.post("/:id/cancel", async (req, res) => {
  await db.query("UPDATE appointments SET status = 'cancelled' WHERE id = $1", [
    req.params.id,
  ]);
  res.status(204).end();
});

module.exports = router;
