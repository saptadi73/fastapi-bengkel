-- Create enum type for expense type
CREATE TYPE expense_type AS ENUM ('listrik', 'gaji', 'air', 'internet', 'transportasi', 'komunikasi', 'konsumsi', 'entertaint', 'umum', 'lain-lain');

-- Migration for table expenses
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    expense_type expense_type NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    date DATE NOT NULL,
    bukti_transfer VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
