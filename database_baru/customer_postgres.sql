-- Migration for table customer
CREATE TABLE IF NOT EXISTS customer (
    id UUID PRIMARY KEY,
    nama VARCHAR NOT NULL,
    hp VARCHAR NOT NULL,
    alamat VARCHAR NOT NULL,
    email VARCHAR NOT NULL UNIQUE
);

