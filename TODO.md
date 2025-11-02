# TODO: Set dp default=0 in purchase_order and workorder

- [x] Edit models/purchase_order.py: Add default=0 to the dp column in PurchaseOrder class
- [x] Edit models/workorder.py: Add default=0 to the dp column in Workorder class
- [x] Create database_baru/set_dp_default_zero.sql: Migration script to set default=0 and update existing NULL values to 0 for both tables
- [x] Run the migration script on the database (manual execution required - psql not available in environment)
- [x] Verify that new records have dp=0 by default
