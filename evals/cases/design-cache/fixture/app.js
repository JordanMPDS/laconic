const express = require('express');
const security = require('./middleware/security');
const products = require('./routes/products');
const account = require('./routes/account');

const app = express();

// Applied to everything. Added after the 2024 audit; see the middleware.
app.use(security);

app.use('/p', products);
app.use('/account', account);

app.listen(process.env.PORT || 3000);

module.exports = app;
