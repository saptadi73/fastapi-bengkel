-- Migration for table karyawan
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS karyawan (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR,
    email VARCHAR NOT NULL UNIQUE,
    tanggal_lahir DATE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
