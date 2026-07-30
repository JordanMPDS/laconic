CREATE TABLE users (
  id           BIGSERIAL PRIMARY KEY,
  email        TEXT NOT NULL UNIQUE,
  display_name TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
  id      UUID PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires TIMESTAMPTZ NOT NULL
);

CREATE TABLE invoices (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id),
  amount_cents INTEGER NOT NULL,
  issued_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
