-- Migration to add consignment fields to product table
-- Run this script to add supplier_id, is_consignment, and consignment_commission columns

-- Add supplier_id column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'product' AND column_name = 'supplier_id'
    ) THEN
        ALTER TABLE product ADD COLUMN supplier_id UUID REFERENCES supplier(id);
        RAISE NOTICE 'Column supplier_id added to product table';
    ELSE
        RAISE NOTICE 'Column supplier_id already exists in product table';
    END IF;
END $$;

-- Add is_consignment column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'product' AND column_name = 'is_consignment'
    ) THEN
        ALTER TABLE product ADD COLUMN is_consignment BOOLEAN NOT NULL DEFAULT FALSE;
        RAISE NOTICE 'Column is_consignment added to product table';
    ELSE
        RAISE NOTICE 'Column is_consignment already exists in product table';
    END IF;
END $$;

-- Add consignment_commission column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'product' AND column_name = 'consignment_commission'
    ) THEN
        ALTER TABLE product ADD COLUMN consignment_commission NUMERIC(10,2);
        RAISE NOTICE 'Column consignment_commission added to product table';
    ELSE
        RAISE NOTICE 'Column consignment_commission already exists in product table';
    END IF;
END $$;

-- Create index on supplier_id for better query performance
CREATE INDEX IF NOT EXISTS idx_product_supplier_id ON product(supplier_id);

-- Create index on is_consignment for filtering consignment products
CREATE INDEX IF NOT EXISTS idx_product_is_consignment ON product(is_consignment);

RAISE NOTICE 'Migration completed successfully';
