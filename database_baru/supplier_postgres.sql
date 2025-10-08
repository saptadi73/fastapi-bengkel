-- Migration for table supplier
CREATE TABLE IF NOT EXISTS supplier (
    id UUID PRIMARY KEY,
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR,
    email VARCHAR UNIQUE,
    npwp VARCHAR,
    perusahaan VARCHAR,
    toko VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
