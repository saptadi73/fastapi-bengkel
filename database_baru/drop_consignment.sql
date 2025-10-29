-- Drop consignment-related tables and columns

-- Delete journal entries related to consignment first
DELETE FROM journal_entries WHERE consignment_id IS NOT NULL;
DELETE FROM journal_entries WHERE consignment_sale_id IS NOT NULL;

-- Drop foreign key constraints first
ALTER TABLE journal_entries DROP COLUMN IF EXISTS consignment_id;
ALTER TABLE journal_entries DROP COLUMN IF EXISTS consignment_sale_id;

-- Drop consignment tables
DROP TABLE IF EXISTS consignment_sale;
DROP TABLE IF EXISTS consignment_item;
DROP TABLE IF EXISTS consignment;

-- Drop consignment columns from product table
ALTER TABLE product DROP COLUMN IF EXISTS is_consignment;
ALTER TABLE product DROP COLUMN IF EXISTS consignment_cost;
ALTER TABLE product DROP COLUMN IF EXISTS consignment_supplier_id;
