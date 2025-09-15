-- Migration for table category
CREATE TABLE IF NOT EXISTS category (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR
);
