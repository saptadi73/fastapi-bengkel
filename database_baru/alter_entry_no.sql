-- Alter the entry_no column to VARCHAR(100) to accommodate longer payment_no values
ALTER TABLE journal_entries ALTER COLUMN entry_no TYPE VARCHAR(100);
