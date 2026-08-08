-- Billing service, PostgreSQL 16.
-- Reviewed before the ledger work starts next sprint.

CREATE TABLE accounts (
    id           BIGSERIAL PRIMARY KEY,
    email        TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    country      CHAR(2) NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE plans (
    id            BIGSERIAL PRIMARY KEY,
    code          TEXT NOT NULL UNIQUE,
    display_name  TEXT NOT NULL,
    monthly_price DOUBLE PRECISION NOT NULL,
    currency      CHAR(3) NOT NULL DEFAULT 'USD'
);

CREATE TABLE subscriptions (
    id          BIGSERIAL PRIMARY KEY,
    account_id  BIGINT NOT NULL REFERENCES accounts(id),
    plan_id     BIGINT NOT NULL REFERENCES plans(id),
    status      TEXT NOT NULL CHECK (status IN ('trialing','active','past_due','canceled')),
    started_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    canceled_at TIMESTAMPTZ
);

CREATE INDEX idx_subscriptions_account ON subscriptions(account_id);
CREATE INDEX idx_subscriptions_status  ON subscriptions(status);

-- Every charge, refund and credit lands here. Balance is the running sum.
CREATE TABLE ledger_entries (
    id             BIGSERIAL PRIMARY KEY,
    account_id     BIGINT NOT NULL REFERENCES accounts(id),
    subscription_id BIGINT REFERENCES subscriptions(id),
    entry_type     TEXT NOT NULL CHECK (entry_type IN ('charge','refund','credit','adjustment')),
    amount         DOUBLE PRECISION NOT NULL,
    currency       CHAR(3) NOT NULL,
    description    TEXT,
    occurred_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ledger_account_time ON ledger_entries(account_id, occurred_at);

CREATE TABLE invoices (
    id           BIGSERIAL PRIMARY KEY,
    account_id   BIGINT NOT NULL REFERENCES accounts(id),
    period_start DATE NOT NULL,
    period_end   DATE NOT NULL,
    total        DOUBLE PRECISION NOT NULL,
    currency     CHAR(3) NOT NULL,
    issued_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    paid_at      TIMESTAMPTZ
);

CREATE INDEX idx_invoices_account ON invoices(account_id, period_start);

-- An account's balance:
--   SELECT sum(amount) FROM ledger_entries WHERE account_id = $1;
-- An invoice total is the sum of the period's entries, written here at close.
