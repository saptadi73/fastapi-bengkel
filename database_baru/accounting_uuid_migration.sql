-- Migration script to alter journal_entries table for UUID foreign keys
-- Run this after creating the tables with accounting_postgres.sql

-- Alter customer_id to UUID with foreign key
ALTER TABLE journal_entries ALTER COLUMN customer_id TYPE UUID USING customer_id::UUID;
ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_customer_id FOREIGN KEY (customer_id) REFERENCES customer(id);

-- Alter supplier_id to UUID with foreign key
ALTER TABLE journal_entries ALTER COLUMN supplier_id TYPE UUID USING supplier_id::UUID;
ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_supplier_id FOREIGN KEY (supplier_id) REFERENCES supplier(id);

-- Alter workorder_id to UUID with foreign key
ALTER TABLE journal_entries ALTER COLUMN workorder_id TYPE UUID USING workorder_id::UUID;
ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_workorder_id FOREIGN KEY (workorder_id) REFERENCES workorder(id);

-- Add purchase_id column as UUID with foreign key
ALTER TABLE journal_entries ADD COLUMN purchase_id UUID;
ALTER TABLE journal_entries ADD CONSTRAINT fk_journal_entries_purchase_id FOREIGN KEY (purchase_id) REFERENCES purchase_order(id);
