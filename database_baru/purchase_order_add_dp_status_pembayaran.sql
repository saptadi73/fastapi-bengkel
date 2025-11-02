-- Add dp and status_pembayaran columns to purchase_order table
ALTER TABLE purchase_order ADD COLUMN dp NUMERIC(10,2);
ALTER TABLE purchase_order ADD COLUMN status_pembayaran VARCHAR(255) DEFAULT 'belum_ada_pembayaran';
