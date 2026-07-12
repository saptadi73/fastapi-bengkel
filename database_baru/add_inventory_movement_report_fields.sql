ALTER TABLE supplier
    ADD COLUMN IF NOT EXISTS supplier_code VARCHAR(50) NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_supplier_supplier_code
    ON supplier (supplier_code)
    WHERE supplier_code IS NOT NULL;

ALTER TABLE product_moved_history
    ADD COLUMN IF NOT EXISTS reference_type VARCHAR(32) NULL,
    ADD COLUMN IF NOT EXISTS reference_id UUID NULL,
    ADD COLUMN IF NOT EXISTS purchase_order_id UUID NULL REFERENCES purchase_order(id),
    ADD COLUMN IF NOT EXISTS workorder_id UUID NULL REFERENCES workorder(id),
    ADD COLUMN IF NOT EXISTS supplier_id UUID NULL REFERENCES supplier(id),
    ADD COLUMN IF NOT EXISTS customer_id UUID NULL REFERENCES customer(id),
    ADD COLUMN IF NOT EXISTS vehicle_id UUID NULL REFERENCES vehicle(id),
    ADD COLUMN IF NOT EXISTS purchase_price NUMERIC(14,2) NULL,
    ADD COLUMN IF NOT EXISTS selling_price NUMERIC(14,2) NULL,
    ADD COLUMN IF NOT EXISTS hpp_snapshot NUMERIC(14,2) NULL;

CREATE INDEX IF NOT EXISTS ix_product_move_product_timestamp
    ON product_moved_history (product_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_product_move_reference
    ON product_moved_history (reference_type, reference_id);
CREATE INDEX IF NOT EXISTS ix_product_move_purchase_order
    ON product_moved_history (purchase_order_id);
CREATE INDEX IF NOT EXISTS ix_product_move_workorder
    ON product_moved_history (workorder_id);
CREATE INDEX IF NOT EXISTS ix_product_move_supplier_timestamp
    ON product_moved_history (supplier_id, timestamp);
CREATE INDEX IF NOT EXISTS ix_product_move_customer_timestamp
    ON product_moved_history (customer_id, timestamp);
