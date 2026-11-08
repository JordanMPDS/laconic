// Thin wrapper over the transactional email provider's HTTP API.
async function send(to, subject, data) {
  const res = await fetch(process.env.MAIL_API_URL, {
    method: "POST",
    headers: { authorization: `Bearer ${process.env.MAIL_API_KEY}` },
    body: JSON.stringify({ to, subject, data }),
  });
  if (!res.ok) throw new Error(`mail API returned ${res.status}`);
}

module.exports = { send };
