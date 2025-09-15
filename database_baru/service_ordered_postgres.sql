    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    service_id UUID REFERENCES service(id),
    workorder_id UUID REFERENCES workorder(id)
);

CREATE TABLE IF NOT EXISTS service_ordered (
    id UUID PRIMARY KEY,
    quantity NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    service_id UUID REFERENCES service(id),
    workorder_id UUID REFERENCES workorder(id)
);
