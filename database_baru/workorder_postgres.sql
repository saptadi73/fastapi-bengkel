CREATE TABLE IF NOT EXISTS workorder (
    id UUID PRIMARY KEY,
    no_wo VARCHAR NOT NULL,
    tanggal_masuk DATE NOT NULL,
    tanggal_keluar DATE,
    keluhan VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    total_biaya NUMERIC(10,2) NOT NULL,
    customer_id UUID REFERENCES customer(id),
    vehicle_id UUID REFERENCES vehicle(id)
);

CREATE TABLE IF NOT EXISTS workorder_activity_log (
    id UUID PRIMARY KEY,
    workorder_id UUID REFERENCES workorder(id),
    action VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL
);
