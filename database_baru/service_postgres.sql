    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    price VARCHAR NOT NULL,
    cost NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS service (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    price VARCHAR NOT NULL,
    cost NUMERIC(10,2) NOT NULL
);
