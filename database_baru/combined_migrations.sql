-- accounting_postgres.sql
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


-- accounting_uuid_migration.sql
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


-- add_consignment_to_journaltype.sql
-- Migration to add 'consignment' value to journaltype enum
-- Run this in DBeaver or any PostgreSQL client after the initial enum creation

-- Add 'consignment' to the journaltype enum if it doesn't already exist
DO $$ BEGIN
    ALTER TYPE journaltype ADD VALUE 'consignment';
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;


-- add_journaltype_enum.sql
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


-- attendance_postgres.sql
-- Migration for table attendance
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    karyawan_id UUID NOT NULL REFERENCES karyawan(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    status VARCHAR NOT NULL DEFAULT 'absent',
    notes VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_attendance_karyawan_id ON attendance(karyawan_id);
CREATE INDEX idx_attendance_date ON attendance(date);


-- booking_postgres.sql
-- Migration: CREATE TABLE booking sesuai model booking.py

CREATE TABLE IF NOT EXISTS booking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    model VARCHAR,
    type VARCHAR,
    no_pol VARCHAR,
    warna VARCHAR,
    tanggal_booking TIMESTAMP,
    vehicle_id UUID,
    customer_id UUID,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);


-- brand_postgres.sql
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS brand (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    UNIQUE(name)
);


-- category_postgres.sql
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR
);

CREATE TABLE IF NOT EXISTS category (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    UNIQUE(name)
);


-- customer_postgres.sql
-- Migration for table customer
CREATE TABLE IF NOT EXISTS customer (
    id UUID PRIMARY KEY,
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE
    tanggal_lahir DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);



-- drop_consignment.sql
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


-- expenses_postgres.sql
-- Create enum type for expense type
CREATE TYPE expense_type AS ENUM ('listrik', 'gaji', 'air', 'internet', 'transportasi', 'komunikasi', 'konsumsi', 'entertaint', 'umum', 'lain-lain');

-- Migration for table expenses
CREATE TABLE IF NOT EXISTS expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    expense_type expense_type NOT NULL,
    amount NUMERIC(10,2) NOT NULL,
    date DATE NOT NULL,
    bukti_transfer VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- expenses_status_alter.sql
-- Add status column to expenses table with default 'open'
ALTER TABLE expenses
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'open';

-- Optional: Add a check constraint to ensure status is either 'open' or 'dibayarkan'
ALTER TABLE expenses
ADD CONSTRAINT status_check CHECK (status IN ('open', 'dibayarkan'));


-- inventory_cost_drop.sql
ALTER TABLE inventory DROP COLUMN IF EXISTS cost;


-- inventory_postgres.sql
CREATE TABLE IF NOT EXISTS product_moved_history (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES product(id),
    type VARCHAR NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    performed_by VARCHAR NOT NULL,
    notes VARCHAR
);

CREATE TABLE IF NOT EXISTS inventory (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES product(id),
    quantity NUMERIC(10,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_moved_history (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES product(id),
    type VARCHAR NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    performed_by VARCHAR NOT NULL,
    notes VARCHAR
);


-- karyawan_postgres.sql
-- Migration for table karyawan
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS karyawan (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    tanggal_lahir DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- packet_order.sql
CREATE TABLE packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL
);

CREATE TABLE product_line_packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_order_id UUID,
    quantity NUMERIC(10,2),
    price NUMERIC(10,2),
    discount NUMERIC(10,2),
    subtotal NUMERIC(10,2),
    satuan_id UUID,
    product_id UUID,
    FOREIGN KEY (packet_order_id) REFERENCES packet_order(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    FOREIGN KEY (satuan_id) REFERENCES satuan(id) ON DELETE CASCADE
);

CREATE TABLE service_line_packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_order_id UUID,
    quantity NUMERIC(10,2),
    price NUMERIC(10,2),
    discount NUMERIC(10,2),
    subtotal NUMERIC(10,2),
    service_id UUID,
    FOREIGN KEY (packet_order_id) REFERENCES packet_order(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(id) ON DELETE CASCADE
);


-- product_alter_type_optional.sql
ALTER TABLE product ALTER COLUMN type DROP NOT NULL;


-- product_consignment_add.sql
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


-- product_cost_add.sql
ALTER TABLE product ADD COLUMN IF NOT EXISTS cost NUMERIC(10,2);


-- product_cost_history_postgres.sql
-- Create product_cost_history table for tracking cost changes
CREATE TABLE IF NOT EXISTS product_cost_history (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES product(id) NOT NULL,
    old_cost NUMERIC(10,2),
    new_cost NUMERIC(10,2) NOT NULL,
    old_quantity NUMERIC(10,2),
    new_quantity NUMERIC(10,2) NOT NULL,
    purchase_quantity NUMERIC(10,2),
    purchase_price NUMERIC(10,2),
    calculation_method VARCHAR DEFAULT 'average',
    notes TEXT,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_product_cost_history_product_id ON product_cost_history(product_id);
CREATE INDEX IF NOT EXISTS idx_product_cost_history_created_at ON product_cost_history(created_at);

-- Add comment to table
COMMENT ON TABLE product_cost_history IS 'Tracks historical changes to product costs using average costing method';
COMMENT ON COLUMN product_cost_history.old_cost IS 'Previous cost before calculation';
COMMENT ON COLUMN product_cost_history.new_cost IS 'New calculated average cost';
COMMENT ON COLUMN product_cost_history.old_quantity IS 'Quantity before the transaction';
COMMENT ON COLUMN product_cost_history.new_quantity IS 'Quantity after the transaction';
COMMENT ON COLUMN product_cost_history.purchase_quantity IS 'Quantity purchased in this transaction';
COMMENT ON COLUMN product_cost_history.purchase_price IS 'Price per unit in this purchase';
COMMENT ON COLUMN product_cost_history.calculation_method IS 'Method used for cost calculation (average, manual, etc)';


-- product_ordered_postgres.sql
CREATE TABLE IF NOT EXISTS product_ordered (
    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    product_id UUID REFERENCES product(id),
    workorder_id UUID REFERENCES workorder(id)
);


-- product_postgres.sql
CREATE TABLE IF NOT EXISTS product (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR,
    description VARCHAR,
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    min_stock NUMERIC(10,2) NOT NULL,
    brand_id UUID REFERENCES brand(id),
    satuan_id UUID REFERENCES satuan(id),
    category_id UUID REFERENCES category(id),
    supplier_id UUID REFERENCES supplier(id),
    is_consignment BOOLEAN NOT NULL DEFAULT FALSE,
    consignment_commission NUMERIC(10,2)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_product_supplier_id ON product(supplier_id);
CREATE INDEX IF NOT EXISTS idx_product_is_consignment ON product(is_consignment);


-- purchase_order_add_dp_status_pembayaran.sql
-- Migration to add dp and status_pembayaran fields to purchase_order table

ALTER TABLE purchase_order
ADD COLUMN dp NUMERIC(10,2) NULL,
ADD COLUMN status_pembayaran VARCHAR(255) NOT NULL DEFAULT 'belum_ada_pembayaran';


-- purchase_order_postgres.sql
-- Create enum type for purchase order status
CREATE TYPE purchase_order_status AS ENUM ('draft', 'dijalankan', 'diterima', 'dibayarkan');

-- Create sequence for PO number
CREATE SEQUENCE IF NOT EXISTS purchase_order_seq START 1;

-- Migration for table purchase_order
CREATE TABLE IF NOT EXISTS purchase_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    po_no VARCHAR NOT NULL UNIQUE,
    supplier_id UUID NOT NULL,
    date DATE NOT NULL,
    total NUMERIC(10,2) NOT NULL,
    pajak NUMERIC(10,2),
    pembayaran NUMERIC(10,2),
    status purchase_order_status NOT NULL DEFAULT 'draft',
    bukti_transfer VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (supplier_id) REFERENCES supplier(id) ON DELETE CASCADE
);

-- Migration for table purchase_order_line
CREATE TABLE IF NOT EXISTS purchase_order_line (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purchase_order_id UUID NOT NULL,
    product_id UUID NOT NULL,
    quantity NUMERIC(10,2) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    subtotal NUMERIC(10,2) NOT NULL,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_order(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
);


-- roles_postgres.sql
-- Migration: CREATE TABLE roles and role_user sesuai model role.py dan role_user.py

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS role_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE
);

-- Insert initial roles
INSERT INTO roles (name) VALUES ('admin'), ('pegawai'), ('user') ON CONFLICT (name) DO NOTHING;


-- satuan_postgres.sql
CREATE TABLE IF NOT EXISTS satuan (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    UNIQUE(name)
);


-- service_ordered_postgres.sql
CREATE TABLE IF NOT EXISTS service_ordered (
    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    service_id UUID REFERENCES service(id),
    workorder_id UUID REFERENCES workorder(id)
);


-- service_postgres.sql
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    price VARCHAR NOT NULL,
    cost NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS service (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    price VARCHAR NOT NULL,
    cost NUMERIC(10,2) NOT NULL
);


-- set_dp_default_zero.sql
-- Migration to set default value of dp column to 0 in purchase_order and workorder tables
-- Update existing NULL values to 0
UPDATE purchase_order SET dp = 0 WHERE dp IS NULL;
UPDATE workorder SET dp = 0 WHERE dp IS NULL;

-- Alter columns to set default to 0
ALTER TABLE purchase_order ALTER COLUMN dp SET DEFAULT 0;
ALTER TABLE workorder ALTER COLUMN dp SET DEFAULT 0;


-- supplier_postgres.sql
-- Migration for table supplier
CREATE TABLE IF NOT EXISTS supplier (
    id UUID PRIMARY KEY,
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR,
    email VARCHAR UNIQUE,
    npwp VARCHAR,
    perusahaan VARCHAR,
    toko VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- truncate_except_core.sql
-- Truncate all tables in public schema except specific core tables
-- Excluded tables: users, accounts, supplier, customer
-- Database: PostgreSQL

DO $$
DECLARE
    r RECORD;
    excluded_tables TEXT[] := ARRAY['users', 'accounts', 'supplier', 'customer'];
    stmts TEXT := '';
BEGIN
    -- Build TRUNCATE statements for all non-excluded tables in schema public
    FOR r IN
        SELECT c.relname AS table_name
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r' -- ordinary tables
          AND n.nspname = 'public'
          AND c.relname <> ALL (excluded_tables)
    LOOP
        stmts := stmts || format('TRUNCATE TABLE %I.%I CASCADE;', 'public', r.table_name) || chr(10);
    END LOOP;

    IF stmts <> '' THEN
        RAISE NOTICE 'Executing:%', chr(10) || stmts;
        EXECUTE stmts;
    ELSE
        RAISE NOTICE 'No tables to truncate (all tables are excluded).';
    END IF;
END $$;

-- vehicle_postgres.sql

CREATE TABLE IF NOT EXISTS vehicle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model VARCHAR NOT NULL,
    brand_id UUID REFERENCES brand(id),
    type VARCHAR NOT NULL,
    kapasitas VARCHAR NOT NULL,
    no_pol VARCHAR NOT NULL,
    tahun NUMERIC NOT NULL,
    warna VARCHAR NOT NULL,
    no_mesin VARCHAR,
    no_rangka VARCHAR,
    customer_id UUID REFERENCES customer(id)
);

-- Data awal brand
INSERT INTO brand (id, name, description) VALUES
    ('11111111-1111-1111-1111-111111111111', 'TOYOTA', NULL),
    ('22222222-2222-2222-2222-222222222222', 'HONDA', NULL),
    ('33333333-3333-3333-3333-333333333333', 'SUZUKI', NULL),
    ('44444444-4444-4444-4444-444444444444', 'DAIHATSU', NULL)
    ON CONFLICT (id) DO NOTHING;

-- workorder_activity_log_postgres.sql
-- Migration: CREATE TABLE workorder_activity_log sesuai model di workorder.py

CREATE TABLE IF NOT EXISTS workorder_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorder(id),
    action VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    performed_by VARCHAR NOT NULL
);


-- workorder_alter_dp_next_service.sql
ÿþ- -   A l t e r   w o r k o r d e r   t a b l e   t o   r e n a m e   u p d a t e _ p e m b a y a r a n   t o   d p   a n d   a d d   n e x t _ s e r v i c e _ d a t e   a n d   n e x t _ s e r v i c e _ k m 
 A L T E R   T A B L E   w o r k o r d e r   R E N A M E   C O L U M N   u p d a t e _ p e m b a y a r a n   T O   d p ; 
 A L T E R   T A B L E   w o r k o r d e r   A D D   C O L U M N   n e x t _ s e r v i c e _ d a t e   D A T E ; 
 A L T E R   T A B L E   w o r k o r d e r   A D D   C O L U M N   n e x t _ s e r v i c e _ k m   N U M E R I C ( 1 0 , 2 ) ; 
 

-- workorder_alter_keluhan_keterangan.sql
-- Migrasi untuk workorder: tambah kolom keterangan dan ubah keluhan menjadi NOT NULL

ALTER TABLE workorder ADD COLUMN keterangan VARCHAR;
ALTER TABLE workorder ALTER COLUMN keluhan SET NOT NULL;


-- workorder_alter_kilometer.sql
-- Migration to add kilometer column to workorder table
ALTER TABLE workorder ADD COLUMN kilometer NUMERIC(10,2);


-- workorder_postgres.sql

-- CREATE TABLE migration for workorder and related tables (PostgreSQL)

CREATE TABLE IF NOT EXISTS workorder (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    no_wo VARCHAR NOT NULL,
    tanggal_masuk TIMESTAMP NOT NULL,
    tanggal_keluar TIMESTAMP,
    keluhan VARCHAR,
    saran VARCHAR,
    status VARCHAR NOT NULL,
    total_discount NUMERIC(10,2) DEFAULT 0,
    total_biaya NUMERIC(10,2) DEFAULT 0,
    pajak NUMERIC(10,2) DEFAULT 0,
    customer_id UUID REFERENCES customer(id),
    vehicle_id UUID REFERENCES vehicle(id)
);

CREATE TABLE IF NOT EXISTS product_ordered (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    product_id UUID REFERENCES product(id),
    workorder_id UUID REFERENCES workorder(id)
);

CREATE TABLE IF NOT EXISTS service_ordered (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    service_id UUID REFERENCES service(id),
    workorder_id UUID REFERENCES workorder(id)
);

CREATE TABLE IF NOT EXISTS workorder_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorder(id),
    action VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    performed_by VARCHAR NOT NULL
);


