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

## New Task: Add Cash-In and Cash-Out Functions

## Pending Tasks
- [x] Add CashInCreate and CashOutCreate schemas to schemas/service_accounting.py
- [x] Update imports in services/services_accounting.py for new schemas
- [x] Add cash_in function to services/services_accounting.py
- [x] Add cash_out function to services/services_accounting.py
- [x] Test the new functions

## New Task: Add Cash Book Report Endpoint

## Completed Tasks
- [x] Add CashBookReportRequest and CashBookReport schemas to schemas/service_accounting.py
- [x] Add generate_cash_book_report function to services/services_accounting.py
- [x] Update imports in routes/routes_accounting.py for new schemas and function
- [x] Add /cash-book-report endpoint to routes/routes_accounting.py
- [x] Test the new endpoint with test_cash_book_report.py

## New Task: Add Expense Report Endpoint

## Completed Tasks
- [x] Add ExpenseReportRequest and ExpenseReport schemas to schemas/service_accounting.py
- [x] Add generate_expense_report function to services/services_accounting.py
- [x] Update imports in routes/routes_accounting.py for new schemas and function
- [x] Add /expense-report endpoint to routes/routes_accounting.py
