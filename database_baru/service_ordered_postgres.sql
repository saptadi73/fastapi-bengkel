CREATE TABLE IF NOT EXISTS service_ordered (
    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    price NUMERIC(10,2) NOT NULL,
    discount NUMERIC(10,2) DEFAULT 0,
    service_id UUID REFERENCES service(id),
    workorder_id UUID REFERENCES workorder(id)
);
