-- Migration to set default value of dp column to 0 in purchase_order and workorder tables
-- Update existing NULL values to 0
UPDATE purchase_order SET dp = 0 WHERE dp IS NULL;
UPDATE workorder SET dp = 0 WHERE dp IS NULL;

-- Alter columns to set default to 0
ALTER TABLE purchase_order ALTER COLUMN dp SET DEFAULT 0;
ALTER TABLE workorder ALTER COLUMN dp SET DEFAULT 0;
