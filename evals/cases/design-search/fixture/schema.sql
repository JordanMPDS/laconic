-- Production sits on PostgreSQL 16 (RDS). The products table holds about
-- 38,000 rows and grows by a few hundred a month.

CREATE TABLE products (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku         text NOT NULL UNIQUE,
    name        text NOT NULL,
    description text NOT NULL DEFAULT '',
    price_cents integer NOT NULL,
    active      boolean NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX products_active_idx ON products (active);
