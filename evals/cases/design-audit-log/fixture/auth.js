const db = require("./db");

// Resolves the session cookie to its user and account. Every request that
// reaches a route handler has passed through here.
async function sessionUser(req, res, next) {
  const rows = await db.query(
    "SELECT u.id, u.email, u.account_id FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token = $1 AND s.expires_at > now()",
    [req.cookies && req.cookies.session]
  );
  if (!rows.length) return res.status(401).end();
  req.user = { id: rows[0].id, email: rows[0].email, accountId: rows[0].account_id };
  next();
}

module.exports = { sessionUser };
