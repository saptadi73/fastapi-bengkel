-- Migration to add 'consignment' value to journaltype enum
-- Run this in DBeaver or any PostgreSQL client after the initial enum creation

-- Add 'consignment' to the journaltype enum if it doesn't already exist
DO $$ BEGIN
    ALTER TYPE journaltype ADD VALUE 'consignment';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
