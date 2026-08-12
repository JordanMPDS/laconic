const express = require('express');
const db = require('../db');

const router = express.Router();

// Anonymous. No session is read here and nothing on the page varies by user -
// price, stock and copy are the same for everybody. Catalogue rows change when
// someone edits a product in the admin tool, which is a few times a day.
router.get('/:slug', async (req, res) => {
  const product = await db.productBySlug(req.params.slug);
  if (!product) return res.status(404).send('not found');
  const related = await db.relatedProducts(product.id);
  const stock = await db.stockFor(product.id);
  res.render('product', { product, related, stock });
});

module.exports = router;
