# TODO List

## Fix 422 Error for tanggal_lahir Field ✅

### Step 1: Update schemas/service_customer.py ✅
- Add field_validator for tanggal_lahir in CreateCustomerWithVehicles and CreateCustomer classes to convert empty string to None.

### Step 2: Update schemas/service_karyawan.py ✅
- Add field_validator for tanggal_lahir in relevant schema classes (e.g., CreateKaryawan) to convert empty string to None.

### Step 3: Test the Changes ✅
- Test endpoints by sending requests without tanggal_lahir or with empty string to ensure 422 error is resolved.

## Add Validation for Lost Goods Journal Entry ✅

### Step 1: Update services/services_accounting.py ✅
- Add validation to ensure quantity is positive in create_lost_goods_journal_entry function.

### Step 2: Update test_lost_goods_journal.py ✅
- Update the test case for zero quantity to expect ValueError instead of allowing zero quantity.

### Step 3: Run Tests ✅
- Execute the test to verify the validation works correctly.
