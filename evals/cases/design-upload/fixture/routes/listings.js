const express = require('express');
const db = require('../db');
const storage = require('../storage');

const router = express.Router();

router.get('/:id', async (req, res) => {
  const listing = await db.listing(req.params.id);
  res.json(listing);
});

// The existing read path: the row stores a key, and the client is handed a
// signed URL for it rather than the bytes.
router.get('/:id/invoice', async (req, res) => {
  const listing = await db.listing(req.params.id);
  res.json({ url: await storage.signedUrl(listing.invoice_key) });
});

module.exports = router;
