-- Migration: CREATE TABLE booking sesuai model booking.py

CREATE TABLE IF NOT EXISTS booking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    model VARCHAR,
    type VARCHAR,
    no_pol VARCHAR,
    warna VARCHAR,
    tanggal_booking DATE,
    jam_booking TIME,
    vehicle_id UUID,
    customer_id UUID,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at DATE NOT NULL DEFAULT CURRENT_DATE
);
