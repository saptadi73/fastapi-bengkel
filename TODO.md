# TODO: Add dp and status_pembayaran fields to Purchase Order

## Steps to Complete
- [ ] Edit models/purchase_order.py: Add 'dp' as Numeric(10,2), nullable=True, and 'status_pembayaran' as String, nullable=False, default='belum_ada_pembayaran'
- [ ] Edit schemas/service_purchase_order.py: Add 'dp' and 'status_pembayaran' to CreatePurchaseOrder, UpdatePurchaseOrder, and PurchaseOrderResponse
- [ ] Edit services/services_purchase_order.py: Update create_purchase_order and edit_purchase_order to handle the new fields
- [ ] Create database_baru/purchase_order_add_dp_status_pembayaran.sql with ALTER TABLE statements to add the columns
- [ ] Run the migration script to apply database changes
- [ ] Test the API endpoints to ensure the new fields are handled correctly
- [ ] Update any related tests if necessary
