-- Migration to add dp and status_pembayaran fields to purchase_order table

ALTER TABLE purchase_order
ADD COLUMN dp NUMERIC(10,2) NULL,
ADD COLUMN status_pembayaran VARCHAR(255) NOT NULL DEFAULT 'belum_ada_pembayaran';
