const https = require("https");

const PROVIDER = "api.cardstream.example";

// One call, one charge. There is no retry anywhere in this file today: a
// timeout propagates straight out to the route handler.
function charge({ amountCents, currency, customerId, source }) {
  const body = JSON.stringify({
    amount: amountCents,
    currency,
    customer: customerId,
    source,
  });
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        host: PROVIDER,
        path: "/v2/charges",
        method: "POST",
        timeout: 10000,
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(body),
          Authorization: `Bearer ${process.env.CARDSTREAM_KEY}`,
        },
      },
      (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => {
          if (res.statusCode >= 400) return reject(new Error(data));
          resolve(JSON.parse(data));
        });
      }
    );
    req.on("timeout", () => req.destroy(new Error("provider timeout")));
    req.on("error", reject);
    req.end(body);
  });
}

module.exports = { charge };
