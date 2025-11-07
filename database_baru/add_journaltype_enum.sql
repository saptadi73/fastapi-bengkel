-- Migration to add JournalType enum to PostgreSQL
-- Run this in DBeaver or any PostgreSQL client

-- First, create the enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE journaltype AS ENUM (
        'purchase',
        'sale',
        'ar_receipt',
        'ap_payment',
        'consignment',
        'expense',
        'general'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Add the journal_type column to journal_entries table if it doesn't exist
DO $$ BEGIN
    ALTER TABLE journal_entries ADD COLUMN journal_type journaltype DEFAULT 'general';
EXCEPTION
    WHEN duplicate_column THEN null;
END $$;

-- Update existing records to have a default journal_type if they are NULL
UPDATE journal_entries SET journal_type = 'general' WHERE journal_type IS NULL;

-- Make the column NOT NULL
ALTER TABLE journal_entries ALTER COLUMN journal_type SET NOT NULL;

-- Create index for better performance
CREATE INDEX IF NOT EXISTS ix_journal_entries_date_type ON journal_entries (date, journal_type);
