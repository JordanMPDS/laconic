const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

// listings.photo_keys is a text[] that is always empty today. It was added
// with the table and never populated, because there has never been an upload
// path. Nothing stores bytes in Postgres; the column holds bucket keys.
exports.listing = async (id) =>
  (await pool.query('select * from listings where id = $1', [id])).rows[0];

exports.addPhotoKey = async (id, key) =>
  pool.query('update listings set photo_keys = photo_keys || $2 where id = $1',
             [id, [key]]);
