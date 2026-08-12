const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// productBySlug is ~40ms. relatedProducts joins four tables and is ~600ms.
// stockFor is ~250ms. Nothing here is per-user.
exports.productBySlug = async (slug) =>
  (await pool.query('select * from products where slug = $1', [slug])).rows[0];

exports.relatedProducts = async (id) =>
  (await pool.query(
    `select p.* from products p
       join product_tags pt on pt.product_id = p.id
       join product_tags pt2 on pt2.tag_id = pt.tag_id
       join products p2 on p2.id = pt2.product_id
      where p2.id = $1 and p.id <> $1
      limit 8`, [id])).rows;

exports.stockFor = async (id) =>
  (await pool.query(
    'select sum(quantity) as n from inventory where product_id = $1', [id])).rows[0];

exports.ordersForUser = async (userId) =>
  (await pool.query('select * from orders where user_id = $1', [userId])).rows;
