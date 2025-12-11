-- Adds is_internal_consumption flag to product table if not exists
-- Default set to false for existing rows
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'product'
          AND column_name = 'is_internal_consumption'
    ) THEN
        ALTER TABLE product
        ADD COLUMN is_internal_consumption boolean DEFAULT false;
    END IF;
END $$;
