# TODO for PurchaseOrder Edit Function Enhancement

- [x] Add UpdatePurchaseOrderLine schema with optional id field in schemas/service_purchase_order.py
- [x] Modify UpdatePurchaseOrder schema to use UpdatePurchaseOrderLine for lines
- [x] Implement edit_purchase_order function in services/services_purchase_order.py
  - Update existing lines if id provided
  - Add new lines if no id
  - Delete lines not present in update
  - Update purchase order fields and recalculate total
  - Handle status change to 'diterima' with product move history
- [x] Integrate edit_purchase_order in routes/routes_purchase_order.py
  - Modified PUT /{purchase_order_id} to use edit_purchase_order
  - Added file upload handling with old file deletion
  - Updated upload-bukti route to delete old file before saving new
- [ ] Write unit tests for edit_purchase_order function
- [ ] Test the full update flow including line additions, updates, and deletions
