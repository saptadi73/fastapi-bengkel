# TODO: Make Service 'description' field optional

## Pending Tasks
- [x] Update Service model in models/workorder.py: Change description column nullable=False to nullable=True
- [x] Update schemas in schemas/service_product.py: Change description field to Optional[str] = None in CreateService and ServiceResponse
- [x] Update service in services/services_product.py: Allow description to be None in createServicenya function
- [x] Update DB schema in database_baru/service_postgres.sql: Remove NOT NULL from description column
- [x] Create migration file database_baru/service_alter_description_optional.sql: ALTER TABLE service ALTER COLUMN description DROP NOT NULL;
- [x] Test the changes: Run migration and verify API works with optional description
