const express = require('express');
const db = require('../db');

const router = express.Router();

// Everything here is per-user and must never be stored by anything in front of
// the app. This is what the audit finding was about.
router.get('/orders', async (req, res) => {
  const orders = await db.ordersForUser(req.session.userId);
  res.render('orders', { orders });
});

module.exports = router;
