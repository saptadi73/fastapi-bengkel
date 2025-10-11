# TODO: Remove 'cost' field from Inventory components

## Tasks
- [x] Update schemas/service_inventory.py: Remove UpdateInventoryCost class
- [x] Update services/services_inventory.py: Remove update_inventory_cost function and cost references
- [x] Update routes/routes_inventory.py: Remove /cost endpoint
- [x] Update database_baru/inventory_postgres.sql: Remove cost column from CREATE TABLE
- [x] Create database_baru/inventory_cost_drop.sql: ALTER TABLE DROP COLUMN cost
- [x] Update services/services_product.py: Remove cost=0 from createProductMoveHistoryNew
- [x] Ensure cost remains in Product table
- [x] Create database_baru/product_cost_add.sql: ALTER TABLE ADD COLUMN cost
- [x] Create function update_product_cost in services/services_product.py
- [x] Create schema UpdateProductCost in schemas/service_product.py
- [x] Create route PUT /products/cost in routes/routes_product.py

## Followup Steps
- [ ] Test inventory API to ensure no cost-related errors
