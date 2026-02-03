# Margin Analysis Quick Reference

## TL;DR - What Changed

Added margin profit calculation to all sales reports:
- **total_margin** (Rp) = total_sales - total_hpp
- **margin_percentage** (%) = (total_margin / total_sales) × 100%

## Affected Endpoints

1. **POST /accounting/product-sales-report** ✨
2. **POST /accounting/service-sales-report** ✨
3. **POST /accounting/daily-report** ✨ (product_sales & service_sales sections)

## New Response Fields

All three endpoints now return:
```json
{
  "total_sales": 5000000,
  "total_hpp": 3333333.33,
  "total_margin": 1666666.67,          // ✨ NEW
  "margin_percentage": 33.33,           // ✨ NEW
  "items": [...]
}
```

## Formulas

| Metric | Formula | Example |
|--------|---------|---------|
| **HPP** | Σ(cost × qty) | 5 units × Rp100K = Rp500K |
| **Margin** | sales - hpp | Rp750K - Rp500K = Rp250K |
| **Margin %** | (margin / sales) × 100% | (Rp250K / Rp750K) × 100% = 33.33% |

## Schema Changes

### ProductSalesReport (Added)
```python
total_margin: Decimal       # Absolute profit in Rp
margin_percentage: Decimal  # Profit % (0-100)
```

### ServiceSalesReport (Added)
```python
total_margin: Decimal       # Absolute profit in Rp
margin_percentage: Decimal  # Profit % (0-100)
```

## Code Location

| Component | File | What Changed |
|-----------|------|-------------|
| **Schemas** | [schemas/service_accounting.py](schemas/service_accounting.py) | Added 2 fields to each schema |
| **Business Logic** | [services/services_accounting.py](services/services_accounting.py) | Added margin calculation in 2 functions |
| **Documentation** | [routes/docs/API_DOCUMENTATION_COMPLETE.md](routes/docs/API_DOCUMENTATION_COMPLETE.md) | Updated 3 sections with examples |

## Calculation Logic (Simplified)

```python
# For each report:
total_hpp = sum(item.hpp * item.qty for item in items)
total_margin = total_sales - total_hpp
margin_percentage = (total_margin / total_sales * 100) if total_sales > 0 else 0
```

## Key Points

✅ **Type Safe** - Uses Decimal for financial precision  
✅ **Edge Case Handled** - Returns 0% if no sales (no division by zero)  
✅ **Backward Compatible** - No breaking changes  
✅ **Well Documented** - Examples in API docs  
✅ **Production Ready** - Fully tested and validated  

## Testing

### Test Case 1: Normal Calculation
- Sales: Rp 1,000,000
- Cost: Rp 700,000
- Expected: Margin = Rp 300,000, % = 30.00% ✓

### Test Case 2: Zero Sales
- Sales: Rp 0
- Cost: Rp 0
- Expected: Margin = Rp 0, % = 0.00% ✓

### Test Case 3: Negative Margin
- Sales: Rp 500,000
- Cost: Rp 600,000
- Expected: Margin = Rp -100,000, % = -20.00% ✓

## Frontend Integration

```javascript
// Example: Display margin percentage
const response = await fetch('/accounting/product-sales-report', {
  method: 'POST',
  body: JSON.stringify({ start_date, end_date })
});

const data = await response.json();
console.log(`Margin: ${data.total_margin} (${data.margin_percentage}%)`);
```

## Related Docs

📖 [Full Implementation Guide](MARGIN_ANALYSIS_IMPLEMENTATION.md)  
📖 [Complete Implementation Summary](DAILY_REPORT_MARGIN_ANALYSIS_COMPLETE.md)  
📖 [API Documentation](routes/docs/API_DOCUMENTATION_COMPLETE.md)  

---

**Last Updated:** 2025-01-18  
**Status:** ✅ Production Ready
