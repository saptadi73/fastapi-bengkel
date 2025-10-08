-- Migration for table expenses
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    description VARCHAR NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    date DATE NOT NULL,
    bukti_transfer VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
