# TODO List for Accounting UUID Changes

## Models
- [x] Update models/accounting.py: Change customer_id, supplier_id, workorder_id, purchase_id to UUID with ForeignKey
- [x] Update related models: customer.py, supplier.py, workorder.py, purchase_order.py for back_populates

## Schemas
- [x] Update schemas/service_accounting.py: Change customer_id, supplier_id, workorder_id, purchase_id to Optional[UUID]

## Services
- [x] Check services/services_accounting.py: No changes needed, handles UUID conversion

## Routes
- [x] Check routes/routes_accounting.py: No changes needed

## Database Migration
- [x] Update database_baru/accounting_postgres.sql to reflect UUID types and foreign keys
- [x] Create database_baru/accounting_uuid_migration.sql for altering existing tables

## Expenses Module
- [x] Create expense journal entry function
- [x] Add ExpenseJournalEntry schema
- [x] Integrate with expense status update to 'dibayarkan'
- [x] Create test for expense journal

## Testing
- [ ] Test API endpoints after changes
- [ ] Verify database integrity
- [ ] Run migration script if needed
