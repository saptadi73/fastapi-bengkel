# Work Order Status Flow Documentation

## Status Flow Update (Januari 2026)

### ⚠️ Perubahan Penting

Status work order telah diperbarui untuk menyederhanakan alur kerja. Status "dikerjakan" telah dihapus dari flow.

### Status Flow Baru

```
Draft → Selesai → Dibayar/Dibayarkan
```

**Status yang tersedia:**
1. **draft** - Work order baru dibuat, belum dikerjakan
2. **selesai** - Pekerjaan selesai, siap untuk pembayaran
3. **dibayar/dibayarkan** - Pembayaran telah diterima

### Status Flow Lama (Tidak Digunakan Lagi)

```
Draft → Dikerjakan → Selesai → Dibayar/Dibayarkan
```

Status "dikerjakan" tidak lagi digunakan dalam sistem.

## Proses Otomatis Saat Status Berubah ke "Selesai"

Ketika status work order berubah dari status lain menjadi **"selesai"**, sistem akan otomatis melakukan:

### 1. Product Moved History (Stock Movement)
- **Tujuan**: Mengurangi stok produk yang digunakan dalam work order
- **Proses**: 
  - Sistem membuat record di `product_moved_history` dengan type `outcome`
  - Quantity produk dikurangi sesuai dengan jumlah yang digunakan
  - Notes mencatat nomor work order untuk tracking
- **Proteksi**: Sistem mencek apakah stok sudah pernah dipindahkan untuk WO ini untuk menghindari duplikasi

### 2. Sales Journal Entry (Jurnal Penjualan)
- **Tujuan**: Mencatat transaksi penjualan untuk keperluan akuntansi
- **Proses**:
  - Membuat jurnal penjualan dengan detail:
    - Harga produk (setelah diskon)
    - Harga service (setelah diskon)
    - HPP (Harga Pokok Penjualan) produk
    - HPP service
    - Pajak
  - Journal entry untuk:
    - Piutang usaha (Accounts Receivable)
    - Pendapatan penjualan produk
    - Pendapatan penjualan jasa
    - HPP produk
    - HPP jasa
    - Inventory (pengurangan)
- **Note**: Sales journal hanya dibuat di fungsi `update_workorder_lengkap` karena membutuhkan data lengkap HPP dan detail harga

## Fungsi Update Work Order

### 1. `update_workorder_lengkap()`
**Endpoint**: `POST /workorders/update/workorderlengkap/{workorder_id}`

**Fitur**:
- Update semua field work order termasuk product_ordered dan service_ordered
- ✅ Membuat sales journal entry saat status → "selesai"
- ✅ Membuat product moved history saat status → "selesai"
- Memerlukan data lengkap: `totalProductHarga`, `totalProductCost`, `totalServiceHarga`, `totalServiceCost`, dll.

**Digunakan untuk**: Update work order dari aplikasi frontend dengan data lengkap

### 2. `update_only_workorder()`
**Endpoint**: `POST /workorders/update/onlyworkorder/{workorder_id}` (jika ada)

**Fitur**:
- Update hanya field-field utama work order (tanpa product_ordered/service_ordered)
- ❌ TIDAK membuat sales journal entry (data tidak lengkap)
- ✅ Membuat product moved history saat status → "selesai"
- Menggunakan schema `CreateWorkorderOnly` (tanpa field HPP dan detail harga)

**Digunakan untuk**: Update sederhana work order tanpa mengubah produk/service

### 3. `UpdateWorkorderOrdersnya()`
**Endpoint**: `POST /workorders/update/{workorder_id}`

**Fitur**:
- Update/sinkronisasi product_ordered dan service_ordered
- ❌ TIDAK membuat sales journal entry
- ❌ TIDAK membuat product moved history
- Hanya mengubah daftar produk dan service yang dipesan

**Digunakan untuk**: Mengubah produk dan service dalam work order tanpa mengubah status

## Konsekuensi untuk Developer

### ⚠️ Penting untuk Diperhatikan:

1. **Status "dikerjakan" tidak boleh digunakan lagi** dalam aplikasi frontend
2. **Product moved history dibuat saat status "selesai"**, bukan "dikerjakan"
3. **Sales journal dibuat saat status "selesai"**, bukan "dikerjakan"
4. Jika menggunakan `update_only_workorder()`, pastikan sales journal sudah dibuat secara manual atau gunakan `update_workorder_lengkap()` untuk otomatis
5. Tanggal keluar (`tanggal_keluar`) akan otomatis diisi dengan tanggal sekarang saat status diubah ke "selesai"

## Contoh Penggunaan

### Scenario 1: Create Work Order Baru
```python
# Status: draft
POST /workorders/create/new
{
    "status": "draft",
    "tanggal_masuk": "2026-01-10",
    ...
}
```

### Scenario 2: Selesai Mengerjakan (Update Lengkap)
```python
# Status: draft → selesai
POST /workorders/update/workorderlengkap/{workorder_id}
{
    "status": "selesai",
    "totalProductHarga": 500000,
    "totalProductDiscount": 50000,
    "totalProductCost": 300000,
    "totalServiceHarga": 200000,
    "totalServiceDiscount": 0,
    "totalServiceCost": 100000,
    ...
}
# Sistem akan otomatis:
# - Set tanggal_keluar = hari ini
# - Buat sales journal entry
# - Kurangi stok produk (product moved history)
```

### Scenario 3: Update Status Sederhana
```python
# Status: draft → selesai (tanpa sales journal)
POST /workorders/update/onlyworkorder/{workorder_id}
{
    "status": "selesai",
    ...
}
# Sistem akan otomatis:
# - Set tanggal_keluar = hari ini
# - Kurangi stok produk (product moved history)
# - TIDAK membuat sales journal (gunakan endpoint manual jika perlu)
```

### Scenario 4: Pembayaran
```python
# Status: selesai → dibayar
POST /workorders/update-only-status
{
    "workorder_id": "...",
    "status": "dibayar",
    ...
}
# Sistem akan:
# - Update status_pembayaran = "lunas"
# - Buat sales payment journal entry
```

## Migration dari Status Lama

Jika ada data work order dengan status "dikerjakan":

1. **Data lama tetap valid**, tidak perlu diubah
2. **Data baru** tidak boleh menggunakan status "dikerjakan"
3. Untuk work order yang masih "dikerjakan", ubah menjadi:
   - "draft" jika belum selesai dikerjakan
   - "selesai" jika sudah selesai dikerjakan

## Troubleshooting

### Stok tidak berkurang saat status berubah ke "selesai"
**Penyebab**: Product moved history sudah ada sebelumnya
**Solusi**: Cek tabel `product_moved_history` untuk WO tersebut, jika sudah ada maka sistem skip untuk menghindari duplikasi

### Sales journal tidak terbuat
**Penyebab**: Menggunakan `update_only_workorder()` atau endpoint lain yang tidak membuat sales journal
**Solusi**: 
- Gunakan `update_workorder_lengkap()` dengan data lengkap, atau
- Buat sales journal secara manual via `POST /accounting/sales-journal`

### Tanggal keluar tidak sesuai
**Penyebab**: Tanggal keluar otomatis diisi saat status berubah ke "selesai"
**Solusi**: 
- Jika ingin tanggal keluar custom, set dulu tanggal keluar sebelum mengubah status ke "selesai", atau
- Update tanggal keluar setelah status diubah via endpoint khusus

## Referensi Kode

### File Terkait:
- `services/services_workorder.py` - Logic update work order
  - `update_workorder_lengkap()` - Line 585
  - `update_only_workorder()` - Line 494
  - `_wo_stock_already_moved()` - Helper function Line 220
- `schemas/service_workorder.py` - Schema definition
  - `CreateWorkOrder` - Line 38
  - `CreateWorkorderOnly` - Line 71
- `services/services_accounting.py` - Logic jurnal akuntansi
  - `create_sales_journal_entry()` - Line 677
- `routes/routes_workorder.py` - API endpoints

## Changelog

**Januari 2026**: 
- ✅ Status "dikerjakan" dihapus dari flow
- ✅ Product moved history dipindah dari status "dikerjakan" ke "selesai"
- ✅ Sales journal entry dipindah dari status "dikerjakan" ke "selesai"
- ✅ Tambahan logika di `update_only_workorder()` untuk product moved history
- ✅ Auto-set tanggal keluar saat status = "selesai"
