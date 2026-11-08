const express = require("express");
const transfers = require("./routes/transfers");

const app = express();
app.use(express.json());
app.use("/transfers", transfers);

app.listen(process.env.PORT || 3000);
