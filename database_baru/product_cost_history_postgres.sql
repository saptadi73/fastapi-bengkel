-- Create product_cost_history table for tracking cost changes
CREATE TABLE IF NOT EXISTS product_cost_history (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES product(id) NOT NULL,
    old_cost NUMERIC(10,2),
    new_cost NUMERIC(10,2) NOT NULL,
    old_quantity NUMERIC(10,2),
    new_quantity NUMERIC(10,2) NOT NULL,
    purchase_quantity NUMERIC(10,2),
    purchase_price NUMERIC(10,2),
    calculation_method VARCHAR DEFAULT 'average',
    notes TEXT,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_product_cost_history_product_id ON product_cost_history(product_id);
CREATE INDEX IF NOT EXISTS idx_product_cost_history_created_at ON product_cost_history(created_at);

-- Add comment to table
COMMENT ON TABLE product_cost_history IS 'Tracks historical changes to product costs using average costing method';
COMMENT ON COLUMN product_cost_history.old_cost IS 'Previous cost before calculation';
COMMENT ON COLUMN product_cost_history.new_cost IS 'New calculated average cost';
COMMENT ON COLUMN product_cost_history.old_quantity IS 'Quantity before the transaction';
COMMENT ON COLUMN product_cost_history.new_quantity IS 'Quantity after the transaction';
COMMENT ON COLUMN product_cost_history.purchase_quantity IS 'Quantity purchased in this transaction';
COMMENT ON COLUMN product_cost_history.purchase_price IS 'Price per unit in this purchase';
COMMENT ON COLUMN product_cost_history.calculation_method IS 'Method used for cost calculation (average, manual, etc)';
