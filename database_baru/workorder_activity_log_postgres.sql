-- Migration: CREATE TABLE workorder_activity_log sesuai model di workorder.py

CREATE TABLE IF NOT EXISTS workorder_activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workorder_id UUID REFERENCES workorder(id),
    action VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    performed_by VARCHAR NOT NULL
);
