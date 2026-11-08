const db = require("../db");
const mailer = require("../mailer");

module.exports = async function ({ appointmentId }) {
  const [appt] = await db.query(
    `SELECT a.starts_at, p.email
       FROM appointments a JOIN patients p ON p.id = a.patient_id
      WHERE a.id = $1`,
    [appointmentId]
  );
  await mailer.send(appt.email, "Your appointment is booked", {
    startsAt: appt.starts_at,
  });
};
