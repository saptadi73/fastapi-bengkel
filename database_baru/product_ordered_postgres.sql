CREATE TABLE IF NOT EXISTS product_ordered (
    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    product_id UUID REFERENCES product(id),
    workorder_id UUID REFERENCES workorder(id)
);
