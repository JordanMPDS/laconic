const express = require("express");
const { sessionUser } = require("./auth");
const accounts = require("./routes/accounts");
const orders = require("./routes/orders");

const app = express();
app.use(express.json());

// Resolves the session cookie to a user row and sets req.user for every
// request; requests without a valid session are rejected here.
app.use(sessionUser);

app.use("/accounts", accounts);
app.use("/orders", orders);

app.listen(process.env.PORT || 3000);
