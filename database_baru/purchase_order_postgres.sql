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
