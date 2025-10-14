# TODO: Implement Full CRUD for ProductOrdered and ServiceOrdered by ID

## 1. Update Schemas (schemas/service_workorder.py)
- [x] Add AddProductOrderById schema for POST /add/productorder
- [x] Add UpdateProductOrderById schema for PUT /update/productorder/{id}
- [x] Add DeleteProductOrderById schema for DELETE /delete/productorder/{id}
- [x] Add AddServiceOrderById schema for POST /add/serviceorder
- [x] Add UpdateServiceOrderById schema for PUT /update/serviceorder/{id}
- [x] Add DeleteServiceOrderById schema for DELETE /delete/serviceorder/{id}

## 2. Update Services (services/services_workorder.py)
- [x] Add addProductOrder function to create new ProductOrdered
- [x] Add updateProductOrder function to update by product_ordered_id
- [x] Add deleteProductOrder function to delete by product_ordered_id
- [x] Add addServiceOrder function to create new ServiceOrdered
- [x] Add updateServiceOrder function to update by service_ordered_id
- [x] Add deleteServiceOrder function to delete by service_ordered_id

## 3. Update Routes (routes/routes_workorder.py)
- [x] Add POST /add/productorder route
- [x] Add PUT /update/productorder/{product_ordered_id} route
- [x] Add DELETE /delete/productorder/{product_ordered_id} route
- [x] Add POST /add/serviceorder route
- [x] Add PUT /update/serviceorder/{service_ordered_id} route
- [x] Add DELETE /delete/serviceorder/{service_ordered_id} route

## 4. Testing
- [x] Test the new endpoints to ensure CRUD operations work correctly
- [x] Verify database commits, refreshes, and proper error handling
