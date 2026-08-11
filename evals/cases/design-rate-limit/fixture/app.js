const cluster = require("cluster");
const os = require("os");
const express = require("express");

// Four workers per box, behind the load balancer. Each is its own process
// with its own heap; nothing in module scope is shared between them.
const WORKERS = 4;

if (cluster.isPrimary) {
  for (let i = 0; i < WORKERS; i++) cluster.fork();
  cluster.on("exit", () => cluster.fork());
} else {
  const app = express();
  app.use(express.json());
  app.use("/v1", require("./routes/api"));
  app.listen(process.env.PORT || 3000);
}

module.exports = { WORKERS };
