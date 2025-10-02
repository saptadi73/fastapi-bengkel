CREATE TABLE packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL
);

CREATE TABLE product_line_packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_order_id UUID,
    quantity NUMERIC(10,2),
    price NUMERIC(10,2),
    discount NUMERIC(10,2),
    subtotal NUMERIC(10,2),
    satuan_id UUID,
    product_id UUID,
    FOREIGN KEY (packet_order_id) REFERENCES packet_order(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
    FOREIGN KEY (satuan_id) REFERENCES satuan(id) ON DELETE CASCADE
);

CREATE TABLE service_line_packet_order (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    packet_order_id UUID,
    quantity NUMERIC(10,2),
    price NUMERIC(10,2),
    discount NUMERIC(10,2),
    subtotal NUMERIC(10,2),
    service_id UUID,
    FOREIGN KEY (packet_order_id) REFERENCES packet_order(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES service(id) ON DELETE CASCADE
);
