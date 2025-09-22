
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
    total_biaya NUMERIC(10,2),
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
