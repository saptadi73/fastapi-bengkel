-- Accounting tables migration
-- Based on models/accounting.py

-- Create enums
CREATE TYPE normal_balance AS ENUM ('debit', 'credit');
CREATE TYPE journal_type AS ENUM ('purchase', 'sale', 'ar_receipt', 'ap_payment', 'expense', 'general');
CREATE TYPE account_type AS ENUM ('asset', 'liability', 'equity', 'revenue', 'expense', 'other');

-- Create accounts table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(32) NOT NULL UNIQUE,
    name VARCHAR(128) NOT NULL,
    normal_balance normal_balance NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    account_type account_type NOT NULL DEFAULT 'other'
);

-- Create index on accounts.code
CREATE INDEX ix_accounts_code ON accounts (code);

-- Create journal_entries table
CREATE TABLE journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_no VARCHAR(40) NOT NULL,
    date DATE NOT NULL,
    memo VARCHAR(255),
    journal_type journal_type NOT NULL DEFAULT 'general',
    customer_id UUID REFERENCES customer(id),
    supplier_id UUID REFERENCES supplier(id),
    workorder_id UUID REFERENCES workorder(id),
    purchase_id UUID REFERENCES purchase_order(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(64)
);

-- Create index on journal_entries.entry_no
CREATE INDEX ix_journal_entries_entry_no ON journal_entries (entry_no);

-- Create index on journal_entries.date and journal_type
CREATE INDEX ix_journal_entries_date_type ON journal_entries (date, journal_type);

-- Create journal_lines table
CREATE TABLE journal_lines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id UUID NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id),
    description VARCHAR(255),
    debit NUMERIC(18, 2) DEFAULT 0.00 NOT NULL,
    credit NUMERIC(18, 2) DEFAULT 0.00 NOT NULL
);

-- Add check constraints to journal_lines
ALTER TABLE journal_lines ADD CONSTRAINT chk_journal_lines_debit_nonneg CHECK (debit >= 0);
ALTER TABLE journal_lines ADD CONSTRAINT chk_journal_lines_credit_nonneg CHECK (credit >= 0);
ALTER TABLE journal_lines ADD CONSTRAINT chk_one_side_positive CHECK ((debit = 0 AND credit > 0) OR (credit = 0 AND debit > 0));
