# How Consignment Product Detection Works

## Question: How does the system know if a product in product_ordered is a consignment product?

**Answer:** Yes, the system checks the `is_consignment` field on the Product model. Here's exactly how it works:

## The Detection Flow

### 1. **Data Structure**

```
Workorder
  └── product_ordered (list of ProductOrdered items)
       └── ProductOrdered
            ├── product_id (UUID - reference to Product)
            ├── quantity (Decimal)
            ├── price (Decimal)
            └── product (relationship to Product model)
                 ├── is_consignment (Boolean) ← THIS IS CHECKED
                 ├── consignment_commission (Decimal)
                 └── supplier_id (UUID)
```

### 2. **The Code Implementation**

Located in `services/services_accounting.py`, function `create_sales_journal_entry()`:

```python
# Calculate and record consignment commission if workorder has consignment products
if data_entry.workorder_id:
    # Step 1: Get the workorder from database
    workorder = db.query(Workorder).filter(Workorder.id == data_entry.workorder_id).first()
    
    if workorder:
        total_commission = Decimal("0.00")
        
        # Step 2: Loop through all products in the workorder
        for po in workorder.product_ordered:
            
            # Step 3: Get the product details via relationship
            product = po.product
            
            # Step 4: CHECK IF CONSIGNMENT
            # This is where we check: is_consignment == True
            if product and product.is_consignment and product.consignment_commission:
                
                # Step 5: Calculate commission for this product
                commission = po.quantity * product.consignment_commission
                total_commission += commission
        
        # Step 6: Record commission if any consignment products found
        if total_commission > 0:
            # Record expense and payable journal entries
            lines.append(JournalLineCreate(
                account_code="6003",  # Beban Komisi Konsinyasi
                description="Komisi Konsinyasi",
                debit=total_commission,
                credit=Decimal("0.00")
            ))
            lines.append(JournalLineCreate(
                account_code="3002",  # Hutang Komisi Konsinyasi
                description="Hutang Komisi Konsinyasi",
                debit=Decimal("0.00"),
                credit=total_commission
            ))
```

## Step-by-Step Explanation

### Step 1: Access Workorder
```python
workorder = db.query(Workorder).filter(Workorder.id == data_entry.workorder_id).first()
```
- Retrieves the workorder from database using the workorder_id

### Step 2: Loop Through Products
```python
for po in workorder.product_ordered:
```
- Iterates through all ProductOrdered items in the workorder
- `po` = ProductOrdered instance

### Step 3: Get Product Details
```python
product = po.product
```
- Uses SQLAlchemy relationship to get the full Product object
- This gives access to ALL product fields including `is_consignment`

### Step 4: Check Consignment Status
```python
if product and product.is_consignment and product.consignment_commission:
```
This condition checks THREE things:
1. **`product`** - Product exists (not None)
2. **`product.is_consignment`** - ✅ **THIS IS THE KEY CHECK** - Is it a consignment product?
3. **`product.consignment_commission`** - Does it have a commission rate defined?

### Step 5: Calculate Commission
```python
commission = po.quantity * product.consignment_commission
```
- Multiplies quantity sold by the commission rate
- Example: 5 units × Rp 10,000 = Rp 50,000 commission

### Step 6: Record Journal Entry
Only if `total_commission > 0`, the system records:
```
Dr 6003 (Beban Komisi Konsinyasi)      Rp 50,000
   Cr 3002 (Hutang Komisi Konsinyasi)  Rp 50,000
```

## Example Scenario

### Workorder with Mixed Products:

```json
{
  "workorder_id": "wo-123",
  "product_ordered": [
    {
      "product_id": "prod-1",
      "quantity": 5,
      "product": {
        "name": "Oil Filter",
        "is_consignment": true,        ← CONSIGNMENT
        "consignment_commission": 10000
      }
    },
    {
      "product_id": "prod-2",
      "quantity": 2,
      "product": {
        "name": "Brake Pad",
        "is_consignment": false,       ← NOT CONSIGNMENT
        "consignment_commission": null
      }
    },
    {
      "product_id": "prod-3",
      "quantity": 3,
      "product": {
        "name": "Air Filter",
        "is_consignment": true,        ← CONSIGNMENT
        "consignment_commission": 5000
      }
    }
  ]
}
```

### Commission Calculation:

```
Product 1 (Oil Filter):
  - is_consignment = true ✓
  - commission = 5 × 10,000 = Rp 50,000

Product 2 (Brake Pad):
  - is_consignment = false ✗
  - commission = 0 (skipped)

Product 3 (Air Filter):
  - is_consignment = true ✓
  - commission = 3 × 5,000 = Rp 15,000

Total Commission = Rp 65,000
```

### Journal Entry Created:
```
Dr 6003 (Beban Komisi Konsinyasi)      Rp 65,000
   Cr 3002 (Hutang Komisi Konsinyasi)  Rp 65,000
```

## Key Points

1. **Automatic Detection**: The system automatically detects consignment products by checking `product.is_consignment`

2. **No Manual Flagging Needed**: You don't need to manually specify which products are consignment in the workorder - it's determined from the Product master data

3. **Relationship-Based**: Uses SQLAlchemy relationships:
   ```
   ProductOrdered.product → Product.is_consignment
   ```

4. **Safe Checking**: The code checks for None values to prevent errors:
   ```python
   if product and product.is_consignment and product.consignment_commission:
   ```

5. **Commission Only When Sold**: Commission is calculated and recorded only when:
   - Workorder status changes to 'selesai' (completed)
   - Sales journal entry is created
   - Product has `is_consignment = true`
   - Product has a commission rate defined

## Database Relationships

```sql
-- ProductOrdered table
product_ordered
  ├── id (UUID)
  ├── product_id (UUID) → references product.id
  ├── quantity (NUMERIC)
  └── workorder_id (UUID)

-- Product table
product
  ├── id (UUID)
  ├── name (VARCHAR)
  ├── is_consignment (BOOLEAN) ← Checked here
  ├── consignment_commission (NUMERIC)
  └── supplier_id (UUID)
```

## When Commission is NOT Recorded

Commission will NOT be recorded if:

1. **Product is not consignment**
   ```python
   product.is_consignment = False
   ```

2. **No commission rate defined**
   ```python
   product.consignment_commission = None
   ```

3. **Product doesn't exist**
   ```python
   product = None
   ```

4. **Workorder not completed**
   - Commission only recorded when workorder status = 'selesai'

## Summary

**Yes, the system checks `product.is_consignment = true` to determine if a product in product_ordered is a consignment product.**

The check happens automatically through SQLAlchemy relationships:
```
ProductOrdered → Product → is_consignment field
```

No additional configuration or manual flagging is needed in the workorder creation process. The consignment status is determined entirely from the Product master data.
