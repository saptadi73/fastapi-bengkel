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
