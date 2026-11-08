const db = require("./db");
const handlers = require("./jobs");

// One worker process, deployed beside the API. Every thirty seconds it claims
// the jobs that are due and runs them; a row whose run_at is still in the
// future waits for a later tick.
async function tick() {
  const due = await db.query(
    `UPDATE jobs SET done_at = now()
      WHERE id IN (SELECT id FROM jobs
                    WHERE done_at IS NULL AND run_at <= now()
                    ORDER BY run_at
                    LIMIT 20
                    FOR UPDATE SKIP LOCKED)
      RETURNING kind, payload`
  );
  for (const job of due) {
    await handlers[job.kind](job.payload);
  }
}

setInterval(tick, 30000);
