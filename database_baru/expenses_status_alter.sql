-- Add status column to expenses table with default 'open'
ALTER TABLE expenses
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'open';

-- Optional: Add a check constraint to ensure status is either 'open' or 'dibayarkan'
ALTER TABLE expenses
ADD CONSTRAINT status_check CHECK (status IN ('open', 'dibayarkan'));
