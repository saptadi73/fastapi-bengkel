    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    description VARCHAR,
    price NUMERIC(10,2) NOT NULL,
    cost NUMERIC(10,2) NOT NULL,
    brand_id UUID REFERENCES brand(id),
    satuan_id UUID REFERENCES satuan(id),
    categor_id UUID REFERENCES category(id)
);

CREATE TABLE IF NOT EXISTS product (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    description VARCHAR,
    price NUMERIC(10,2) NOT NULL,
    min_stock NUMERIC(10,2) NOT NULL,
    brand_id UUID REFERENCES brand(id),
    satuan_id UUID REFERENCES satuan(id),
    categor_id UUID REFERENCES category(id)
);
