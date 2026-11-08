CREATE TABLE patients (
    id     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email  text NOT NULL
);

CREATE TABLE appointments (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id  bigint NOT NULL REFERENCES patients (id),
    starts_at   timestamptz NOT NULL,
    status      text NOT NULL DEFAULT 'booked'  -- 'booked' or 'cancelled'
);

-- Deferred work. worker.js runs a row once its run_at has passed.
CREATE TABLE jobs (
    id       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kind     text NOT NULL,
    payload  jsonb NOT NULL,
    run_at   timestamptz NOT NULL DEFAULT now(),
    done_at  timestamptz
);
