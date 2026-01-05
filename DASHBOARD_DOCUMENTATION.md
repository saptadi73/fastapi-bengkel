# Dashboard Documentation - FastAPI Bengkel

## Overview

Dashboard API menyediakan endpoint untuk mengakses ringkasan data operasional bengkel dalam bentuk kartu metrik, pie chart, dan laporan bulanan (sales, purchase, expenses) untuk frontend.

**Features:**

- ✅ Ringkasan harian: work orders hari ini, selesai, pending, karyawan hadir
- ✅ Pie chart: perbandingan work order selesai vs pending
- ✅ Laporan penjualan bulanan (6 bulan terakhir, customizable 1-24 bulan)
- ✅ Laporan pembelian bulanan
- ✅ Laporan pengeluaran bulanan
- ✅ Laporan gabungan sales/purchase/expenses bulanan
- ✅ JWT authentication untuk semua endpoint
- ✅ Flexible month range (1-24 bulan)

---

## API Endpoints

### Base URL

```
http://localhost:8000/dashboard
```

### Authentication

Semua endpoint memerlukan **JWT Token** di header:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 1. Dashboard Summary (Kartu Ringkasan)

### Endpoint

```
GET /dashboard/summary
```

### Response Success

```json
{
  "success": true,
  "data": {
    "workorders_today": 120,
    "workorders_finished": 80,
    "workorders_pending": 40,
    "employees_present": 15
  },
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `workorders_today` | integer | Jumlah work order yang masuk hari ini |
| `workorders_finished` | integer | Total work order yang sudah selesai (semua waktu) |
| `workorders_pending` | integer | Total work order yang belum selesai |
| `employees_present` | integer | Jumlah karyawan yang hadir hari ini |

### Example cURL

```bash
curl -X GET "http://localhost:8000/dashboard/summary" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example JavaScript

```javascript
const response = await fetch('http://localhost:8000/dashboard/summary', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
const data = await response.json();
console.log(data.data);
// {
//   workorders_today: 120,
//   workorders_finished: 80,
//   workorders_pending: 40,
//   employees_present: 15
// }
```

---

## 2. Work Orders Pie Chart

### Endpoint

```
GET /dashboard/workorders-pie
```

### Response Success

```json
{
  "success": true,
  "data": {
    "completed": 80,
    "pending": 40
  },
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `completed` | integer | Jumlah work order yang selesai |
| `pending` | integer | Jumlah work order yang belum selesai |

### Use Cases

Digunakan untuk menampilkan pie chart perbandingan WO selesai vs pending.

### Example cURL

```bash
curl -X GET "http://localhost:8000/dashboard/workorders-pie" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example Chart.js

```javascript
const response = await fetch('http://localhost:8000/dashboard/workorders-pie', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

const pieChart = new Chart(document.getElementById('workorderChart'), {
  type: 'pie',
  data: {
    labels: ['Completed', 'Pending'],
    datasets: [{
      data: [data.completed, data.pending],
      backgroundColor: ['#3b82f6', '#ef4444']
    }]
  }
});
```

---

## 3. Sales Monthly (Laporan Penjualan Bulanan)

### Endpoint

```
GET /dashboard/sales-monthly?months=6
```

### Query Parameters

| Parameter | Type | Default | Range | Description |
| --- | --- | --- | --- | --- |
| `months` | integer | 6 | 1-24 | Jumlah bulan yang ditampilkan |

### Response Success

```json
{
  "success": true,
  "data": [
    {
      "month": "2025-08",
      "total": 15000000.00
    },
    {
      "month": "2025-09",
      "total": 18500000.00
    },
    {
      "month": "2025-10",
      "total": 22300000.00
    },
    {
      "month": "2025-11",
      "total": 25100000.00
    },
    {
      "month": "2025-12",
      "total": 28700000.00
    },
    {
      "month": "2026-01",
      "total": 31400000.00
    }
  ],
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `month` | string | Format: YYYY-MM (tahun-bulan) |
| `total` | float | Total penjualan bulan tersebut (dari work order yang selesai) |

### Notes

- Data diambil dari `total_biaya` work order yang statusnya "selesai"
- Status selesai: `selesai`, `finished`, `done`, `complete`, `completed` (case-insensitive)
- Bulan yang tidak ada data akan menunjukkan 0

### Example cURL

```bash
# 6 bulan terakhir (default)
curl -X GET "http://localhost:8000/dashboard/sales-monthly" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 12 bulan terakhir
curl -X GET "http://localhost:8000/dashboard/sales-monthly?months=12" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# 3 bulan terakhir
curl -X GET "http://localhost:8000/dashboard/sales-monthly?months=3" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example Chart.js (Line Chart)

```javascript
const response = await fetch('http://localhost:8000/dashboard/sales-monthly?months=6', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

const labels = data.map(item => item.month);
const values = data.map(item => item.total);

const lineChart = new Chart(document.getElementById('salesChart'), {
  type: 'line',
  data: {
    labels: labels,
    datasets: [{
      label: 'Sales',
      data: values,
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { display: true }
    },
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

---

## 4. Purchase Monthly (Laporan Pembelian Bulanan)

### Endpoint

```
GET /dashboard/purchase-monthly?months=6
```

### Query Parameters

| Parameter | Type | Default | Range | Description |
| --- | --- | --- | --- | --- |
| `months` | integer | 6 | 1-24 | Jumlah bulan yang ditampilkan |

### Response Success

```json
{
  "success": true,
  "data": [
    {
      "month": "2025-08",
      "total": 5000000.00
    },
    {
      "month": "2025-09",
      "total": 6200000.00
    },
    {
      "month": "2025-10",
      "total": 7100000.00
    },
    {
      "month": "2025-11",
      "total": 8300000.00
    },
    {
      "month": "2025-12",
      "total": 9500000.00
    },
    {
      "month": "2026-01",
      "total": 10200000.00
    }
  ],
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `month` | string | Format: YYYY-MM |
| `total` | float | Total pembelian bulan tersebut (dari purchase order) |

### Notes

- Data diambil dari `total` purchase order dengan status: `dijalankan`, `diterima`, `dibayarkan`
- Bulan yang tidak ada data akan menunjukkan 0
- Tidak termasuk PO dengan status `draft`

### Example cURL

```bash
curl -X GET "http://localhost:8000/dashboard/purchase-monthly?months=6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 5. Expenses Monthly (Laporan Pengeluaran Bulanan)

### Endpoint

```
GET /dashboard/expenses-monthly?months=6
```

### Query Parameters

| Parameter | Type | Default | Range | Description |
| --- | --- | --- | --- | --- |
| `months` | integer | 6 | 1-24 | Jumlah bulan yang ditampilkan |

### Response Success

```json
{
  "success": true,
  "data": [
    {
      "month": "2025-08",
      "total": 2000000.00
    },
    {
      "month": "2025-09",
      "total": 2300000.00
    },
    {
      "month": "2025-10",
      "total": 2150000.00
    },
    {
      "month": "2025-11",
      "total": 2500000.00
    },
    {
      "month": "2025-12",
      "total": 2700000.00
    },
    {
      "month": "2026-01",
      "total": 2900000.00
    }
  ],
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `month` | string | Format: YYYY-MM |
| `total` | float | Total pengeluaran bulan tersebut (gaji, listrik, air, dll) |

### Expense Types (Informasi)

Expenses dapat terdiri dari:

- `listrik` - Biaya listrik
- `gaji` - Gaji karyawan
- `air` - Biaya air
- `internet` - Biaya internet
- `transportasi` - Biaya transportasi
- `komunikasi` - Biaya komunikasi
- `konsumsi` - Biaya konsumsi
- `entertaint` - Biaya hiburan
- `umum` - Pengeluaran umum
- `lain-lain` - Pengeluaran lainnya

### Example cURL

```bash
curl -X GET "http://localhost:8000/dashboard/expenses-monthly?months=6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 6. Combined Monthly (Laporan Gabungan Sales/Purchase/Expenses)

### Endpoint

```
GET /dashboard/combined-monthly?months=6
```

### Query Parameters

| Parameter | Type | Default | Range | Description |
| --- | --- | --- | --- | --- |
| `months` | integer | 6 | 1-24 | Jumlah bulan yang ditampilkan |

### Response Success

```json
{
  "success": true,
  "data": [
    {
      "month": "2025-08",
      "sales": 15000000.00,
      "purchase": 5000000.00,
      "expenses": 2000000.00
    },
    {
      "month": "2025-09",
      "sales": 18500000.00,
      "purchase": 6200000.00,
      "expenses": 2300000.00
    },
    {
      "month": "2025-10",
      "sales": 22300000.00,
      "purchase": 7100000.00,
      "expenses": 2150000.00
    },
    {
      "month": "2025-11",
      "sales": 25100000.00,
      "purchase": 8300000.00,
      "expenses": 2500000.00
    },
    {
      "month": "2025-12",
      "sales": 28700000.00,
      "purchase": 9500000.00,
      "expenses": 2700000.00
    },
    {
      "month": "2026-01",
      "sales": 31400000.00,
      "purchase": 10200000.00,
      "expenses": 2900000.00
    }
  ],
  "message": "Success"
}
```

### Field Descriptions

| Field | Type | Description |
| --- | --- | --- |
| `month` | string | Format: YYYY-MM |
| `sales` | float | Total penjualan bulan tersebut |
| `purchase` | float | Total pembelian bulan tersebut |
| `expenses` | float | Total pengeluaran bulan tersebut |

### Use Cases

Digunakan untuk membandingkan 3 metrik sekaligus (sales vs purchase vs expenses) dalam satu chart.

### Example cURL

```bash
curl -X GET "http://localhost:8000/dashboard/combined-monthly?months=6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Example Chart.js (Mixed Chart)

```javascript
const response = await fetch('http://localhost:8000/dashboard/combined-monthly?months=6', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const { data } = await response.json();

const labels = data.map(item => item.month);
const sales = data.map(item => item.sales);
const purchase = data.map(item => item.purchase);
const expenses = data.map(item => item.expenses);

const mixedChart = new Chart(document.getElementById('combinedChart'), {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [
      {
        label: 'Sales',
        type: 'bar',
        data: sales,
        backgroundColor: 'rgba(16, 185, 129, 0.7)'
      },
      {
        label: 'Purchase',
        type: 'bar',
        data: purchase,
        backgroundColor: 'rgba(245, 158, 11, 0.7)'
      },
      {
        label: 'Expenses',
        type: 'bar',
        data: expenses,
        backgroundColor: 'rgba(239, 68, 68, 0.7)'
      }
    ]
  },
  options: {
    responsive: true,
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

---

## Error Handling

### Invalid Month Range

```json
{
  "success": false,
  "data": {},
  "message": "months must be between 1 and 24"
}
```

### Authentication Error

```json
{
  "success": false,
  "data": {},
  "message": "Not authenticated"
}
```

### Database Error

```json
{
  "success": false,
  "data": {},
  "message": "Database connection error"
}
```

---

## Frontend Integration Examples

### Complete Dashboard Page (React)

```javascript
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement } from 'chart.js';
import { Pie, Line, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement);

export default function Dashboard() {
  const token = localStorage.getItem('token');
  const [summary, setSummary] = useState(null);
  const [pieData, setPieData] = useState(null);
  const [salesData, setSalesData] = useState(null);
  const [purchaseData, setPurchaseData] = useState(null);
  const [combinedData, setCombinedData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        // Fetch all data in parallel
        const [summaryRes, pieRes, salesRes, purchaseRes, combinedRes] = await Promise.all([
          fetch('http://localhost:8000/dashboard/summary', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/dashboard/workorders-pie', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/dashboard/sales-monthly?months=6', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/dashboard/purchase-monthly?months=6', {
            headers: { 'Authorization': `Bearer ${token}` }
          }),
          fetch('http://localhost:8000/dashboard/combined-monthly?months=6', {
            headers: { 'Authorization': `Bearer ${token}` }
          })
        ]);

        const summaryRes_data = await summaryRes.json();
        const pieRes_data = await pieRes.json();
        const salesRes_data = await salesRes.json();
        const purchaseRes_data = await purchaseRes.json();
        const combinedRes_data = await combinedRes.json();

        setSummary(summaryRes_data.data);
        setPieData(pieRes_data.data);
        setSalesData(salesRes_data.data);
        setPurchaseData(purchaseRes_data.data);
        setCombinedData(combinedRes_data.data);
      } catch (error) {
        console.error('Error fetching dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [token]);

  if (loading) return <div>Loading...</div>;

  const pieChartData = {
    labels: ['Completed', 'Pending'],
    datasets: [{
      data: [pieData?.completed || 0, pieData?.pending || 0],
      backgroundColor: ['#3b82f6', '#ef4444']
    }]
  };

  const salesChartData = {
    labels: salesData?.map(item => item.month) || [],
    datasets: [{
      label: 'Sales',
      data: salesData?.map(item => item.total) || [],
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  const combinedChartData = {
    labels: combinedData?.map(item => item.month) || [],
    datasets: [
      {
        label: 'Sales',
        type: 'bar',
        data: combinedData?.map(item => item.sales) || [],
        backgroundColor: 'rgba(16, 185, 129, 0.7)'
      },
      {
        label: 'Purchase',
        type: 'bar',
        data: combinedData?.map(item => item.purchase) || [],
        backgroundColor: 'rgba(245, 158, 11, 0.7)'
      },
      {
        label: 'Expenses',
        type: 'bar',
        data: combinedData?.map(item => item.expenses) || [],
        backgroundColor: 'rgba(239, 68, 68, 0.7)'
      }
    ]
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-8">Dashboard Bengkel</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-blue-500 text-white p-6 rounded-lg">
          <p className="text-sm">Work Orders Today</p>
          <p className="text-3xl font-bold">{summary?.workorders_today || 0}</p>
        </div>
        <div className="bg-green-500 text-white p-6 rounded-lg">
          <p className="text-sm">Work Orders Finished</p>
          <p className="text-3xl font-bold">{summary?.workorders_finished || 0}</p>
        </div>
        <div className="bg-red-500 text-white p-6 rounded-lg">
          <p className="text-sm">Work Orders Pending</p>
          <p className="text-3xl font-bold">{summary?.workorders_pending || 0}</p>
        </div>
        <div className="bg-purple-500 text-white p-6 rounded-lg">
          <p className="text-sm">Employees Present</p>
          <p className="text-3xl font-bold">{summary?.employees_present || 0}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Work Orders Status</h2>
          <Pie data={pieChartData} />
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-4">Sales (6 Months)</h2>
          <Line data={salesChartData} />
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Sales, Purchase & Expenses (6 Months)</h2>
        <Bar data={combinedChartData} options={{ responsive: true }} />
      </div>
    </div>
  );
}
```

---

## Best Practices

### 1. Caching Data

```javascript
const fetchDashboard = async () => {
  const cacheKey = 'dashboard_cache';
  const cached = sessionStorage.getItem(cacheKey);
  
  if (cached) {
    const { timestamp, data } = JSON.parse(cached);
    const age = Date.now() - timestamp;
    
    // Cache valid for 5 minutes
    if (age < 5 * 60 * 1000) {
      return data;
    }
  }
  
  const response = await fetch('/dashboard/summary', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  sessionStorage.setItem(cacheKey, JSON.stringify({
    timestamp: Date.now(),
    data: data.data
  }));
  
  return data.data;
};
```

### 2. Error Handling

```javascript
try {
  const response = await fetch('/dashboard/summary', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const json = await response.json();
  if (!json.success) {
    throw new Error(json.message || 'Unknown error');
  }
  
  return json.data;
} catch (error) {
  console.error('Dashboard error:', error);
  // Show user-friendly error message
  setError('Failed to load dashboard. Please try again.');
}
```

### 3. Refresh on Interval

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchDashboard(); // Refresh every 5 minutes
  }, 5 * 60 * 1000);
  
  return () => clearInterval(interval);
}, []);
```

### 4. Month Range Validation

```javascript
const getMonths = (months) => {
  const months_num = parseInt(months);
  if (isNaN(months_num) || months_num < 1 || months_num > 24) {
    return 6; // Default to 6
  }
  return months_num;
};

const handleMonthChange = (e) => {
  const months = getMonths(e.target.value);
  fetchSalesData(months);
};
```

---

## Database Queries (Reference)

Berikut query yang digunakan backend untuk mengambil data:

### Work Orders Today

```sql
SELECT COUNT(*) 
FROM workorder 
WHERE DATE(tanggal_masuk) = CURRENT_DATE
```

### Work Orders Finished

```sql
SELECT COUNT(*) 
FROM workorder 
WHERE LOWER(status) IN ('selesai', 'finished', 'done', 'complete', 'completed')
```

### Employees Present

```sql
SELECT COUNT(*) 
FROM attendance 
WHERE date = CURRENT_DATE AND LOWER(status) = 'present'
```

### Sales Monthly

```sql
SELECT 
  DATE_TRUNC('month', tanggal_masuk)::DATE as month,
  SUM(total_biaya) as total
FROM workorder
WHERE LOWER(status) IN ('selesai', 'finished', 'done', 'complete', 'completed')
  AND tanggal_masuk >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
GROUP BY DATE_TRUNC('month', tanggal_masuk)
ORDER BY month
```

### Purchase Monthly

```sql
SELECT 
  DATE_TRUNC('month', date)::DATE as month,
  SUM(total) as total
FROM purchase_order
WHERE status IN ('dijalankan', 'diterima', 'dibayarkan')
  AND date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
GROUP BY DATE_TRUNC('month', date)
ORDER BY month
```

### Expenses Monthly

```sql
SELECT 
  DATE_TRUNC('month', date)::DATE as month,
  SUM(amount) as total
FROM expenses
WHERE date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '6 months')
GROUP BY DATE_TRUNC('month', date)
ORDER BY month
```

---

## Troubleshooting

### Issue: Data tidak muncul

**Possible Causes:**

- JWT token expired atau invalid
- Database kosong
- Status work order tidak sesuai dengan filter

**Solution:**

1. Pastikan JWT token valid: refresh token jika diperlukan
2. Cek data di database:

   ```sql
   SELECT COUNT(*) FROM workorder;
   SELECT COUNT(*) FROM attendance WHERE date = CURRENT_DATE;
   ```

3. Cek status work order:

   ```sql
   SELECT DISTINCT status FROM workorder;
   ```

### Issue: months parameter error

**Possible Causes:**

- Parameter tidak dalam range 1-24
- Parameter bukan integer

**Solution:**

```javascript
// Frontend validation
const months = Math.max(1, Math.min(24, parseInt(months) || 6));
```

### Issue: Chart tidak responsive

**Solution:**

```javascript
const options = {
  responsive: true,
  maintainAspectRatio: true,
  scales: {
    y: {
      beginAtZero: true,
      responsive: true
    }
  }
};
```

---

## Performance Notes

- **Summary endpoint:** ~50-100ms (simple COUNT queries)
- **Monthly endpoints:** ~200-500ms (GROUP BY queries dengan 6+ bulan data)
- **Recommended refresh rate:** 5 menit untuk dashboard otomatis

Jika performa lambat:

1. Pastikan database memiliki index pada `tanggal_masuk`, `date`, `status`
2. Pertimbangkan materialized view untuk monthly reports
3. Implementasikan caching di frontend (5-10 menit)

---

## Integration Checklist

- [ ] JWT token tersedia dan valid
- [ ] Database sudah terisi dengan data (work orders, attendance, purchases, expenses)
- [ ] Routes sudah terdaftar di main.py (auto-load dari `routes/__init__.py`)
- [ ] Frontend library installed (Chart.js, React Chart.js 3, atau Chart library pilihan)
- [ ] Error handling implemented
- [ ] Responsive design (mobile-friendly)
- [ ] Loading state handled
- [ ] Token refresh mechanism implemented
- [ ] Data refresh interval set (optional)

---

**Last Updated:** January 5, 2026  
**Version:** 1.0.0  
**Status:** Production Ready
