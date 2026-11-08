const express = require("express");
const db = require("./db");
const checkout = require("./routes/checkout");

const app = express();
app.use(express.json());

// Maintenance mode is a settings row, checked per request and cached for
// fifteen seconds, so support can flip it from the admin panel with no deploy.
let cached = { value: false, at: 0 };
app.use(async (req, res, next) => {
  if (Date.now() - cached.at > 15000) {
    const rows = await db.query("SELECT value FROM settings WHERE key = 'maintenance_mode'");
    cached = { value: rows.length && rows[0].value === true, at: Date.now() };
  }
  if (cached.value) return res.status(503).json({ error: "down for maintenance" });
  next();
});

app.use("/checkout", checkout);

app.listen(process.env.PORT || 3000);
