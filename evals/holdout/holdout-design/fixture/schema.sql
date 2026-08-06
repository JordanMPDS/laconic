CREATE TABLE settings (
    key        text PRIMARY KEY,
    value      jsonb NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now()
);

-- Currently holds one row: ('maintenance_mode', 'false').

CREATE TABLE carts (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id    bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
