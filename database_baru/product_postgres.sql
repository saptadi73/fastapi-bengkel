CREATE TABLE IF NOT EXISTS product (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    description VARCHAR,
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    min_stock NUMERIC(10,2) NOT NULL,
    brand_id UUID REFERENCES brand(id),
    satuan_id UUID REFERENCES satuan(id),
    category_id UUID REFERENCES category(id)
);
