# TODO: Fix Inventory Handling in edit_purchase_order

## Completed Tasks
- [x] Search for edit_purchase_order function in Python files
- [x] Read routes/routes_purchase_order.py to understand the API endpoint
- [x] Read services/services_purchase_order.py to analyze current implementation
- [x] Brainstorm plan: Modify edit_purchase_order to handle inventory moves when lines are changed for 'diterima' status
- [x] Implement changes: Add logic to store old_lines, reverse old moves, and add new moves when lines changed and status is 'diterima'
- [x] Edit the edit_purchase_order function in services/services_purchase_order.py

## Summary
The edit_purchase_order function has been updated to properly handle inventory movements when editing purchase order lines for orders that are already in 'diterima' status. It now reverses the old inventory moves and applies new ones to maintain accurate stock levels.
