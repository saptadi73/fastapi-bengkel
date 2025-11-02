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
