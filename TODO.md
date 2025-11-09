# TODO: Implement Roles with Many-to-Many Relationship to Users

## Steps to Complete

- [x] Create models/role.py: Role model with id, name
- [x] Create models/role_user.py: Pivot model for many-to-many relationship
- [x] Update models/user.py: Add roles relationship
- [x] Create database_baru/roles_postgres.sql: Migration for roles table with initial inserts (admin, pegawai, user)
- [x] Create schemas/service_role.py: Pydantic schemas for Role
- [x] Create services/services_role.py: CRUD operations for roles
- [x] Create routes/routes_role.py: API endpoints for roles
- [x] Create schemas/service_role_user.py: Schemas for assigning roles to users
- [x] Create services/services_role_user.py: Operations for role-user associations
- [x] Create routes/routes_role_user.py: Endpoints for managing user roles

## Followup Steps
- [ ] Run the roles migration
- [ ] Test the new endpoints
