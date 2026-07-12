# Rekomendasi Perubahan Backend untuk Laporan Pembelian dan Pergerakan Barang

## 1. Tujuan

Dokumen ini menjadi spesifikasi implementasi backend untuk melengkapi kebutuhan laporan berikut:

1. Laporan pembelian yang menyertakan identitas/kode vendor.
2. Laporan pergerakan barang yang menyertakan harga jual/beli, nomor WO, nomor PO, pelanggan, dan vendor.
3. Riwayat per item barang dari penerimaan/pembelian sampai pengeluaran/penjualan dalam bentuk kartu stok.

Perubahan harus mempertahankan kompatibilitas response yang saat ini digunakan frontend.

## 2. Kondisi API Saat Ini

### 2.1 Laporan pembelian

`PurchaseOrderReportItem` saat ini menyediakan:

- `po_no`
- `po_date`
- `supplier_name`
- `product_name`
- `quantity`
- `price`
- `subtotal`
- `discount`

Response belum menyediakan ID dan kode/nomor vendor.

### 2.2 Laporan pergerakan barang

Endpoint saat ini:

```http
POST /inventory/product-move-history-report
```

Informasi WO atau PO masih terkandung dalam `notes`. Field referensi transaksi belum tersedia secara terstruktur. Request juga belum mendukung filter `product_id` dan pagination.

## 3. Prioritas Implementasi

| Prioritas | Perubahan | Keterangan |
|---|---|---|
| P0 | Tambahkan referensi transaksi terstruktur pada laporan pergerakan | Dibutuhkan frontend untuk menampilkan nomor WO/PO tanpa parsing `notes` |
| P0 | Tambahkan filter `product_id` dan saldo berjalan | Dibutuhkan untuk kartu stok per barang |
| P1 | Tambahkan ID dan kode vendor pada laporan pembelian | Dibutuhkan untuk identifikasi vendor yang tidak ambigu |
| P1 | Tambahkan pagination dan filter lanjutan | Mencegah response terlalu besar |
| P2 | Tambahkan ringkasan per tipe pergerakan | Memudahkan rekonsiliasi dan ekspor |

## 4. Perubahan Laporan Pembelian

### 4.1 Endpoint

Gunakan endpoint laporan pembelian yang sudah menjadi bagian dari Daily Report atau endpoint laporan pembelian yang sudah tersedia. Tidak perlu membuat endpoint baru jika query yang sama dapat diperluas.

Setiap `PurchaseOrderReportItem` wajib ditambah:

```json
{
  "purchase_order_id": "550e8400-e29b-41d4-a716-446655440000",
  "po_no": "PO-20260712-001",
  "po_date": "2026-07-12",
  "supplier_id": "550e8400-e29b-41d4-a716-446655440001",
  "vendor_code": "VND-001",
  "supplier_name": "PT Supplier Jaya",
  "product_id": "550e8400-e29b-41d4-a716-446655440002",
  "product_name": "Oli Mesin 1L",
  "quantity": 10,
  "price": 100000,
  "discount": 0,
  "subtotal": 1000000
}
```

### 4.2 Definisi field

| Field | Type | Nullable | Keterangan |
|---|---|---:|---|
| `purchase_order_id` | UUID | Tidak | Primary key PO |
| `po_no` | string | Tidak | Nomor PO yang dapat dibaca pengguna |
| `supplier_id` | UUID | Tidak | ID supplier/vendor |
| `vendor_code` | string | Ya | Nomor atau kode vendor, misalnya `VND-001` |
| `supplier_name` | string | Tidak | Nama supplier/vendor |
| `product_id` | UUID | Tidak | ID produk pada baris PO |

Jika master supplier belum memiliki `vendor_code`, tambahkan kolom nullable dan unique:

```sql
ALTER TABLE suppliers ADD COLUMN vendor_code VARCHAR(50) NULL;
CREATE UNIQUE INDEX uq_suppliers_vendor_code
  ON suppliers (vendor_code)
  WHERE vendor_code IS NOT NULL;
```

Nama tabel dan sintaks migration harus disesuaikan dengan ORM/database aktual.

### 4.3 Aturan kompatibilitas

- Field lama tidak boleh dihapus atau diganti nama.
- `supplier_code` boleh `null` untuk data lama.
- `supplier_name` tetap dikirim agar frontend lama tetap bekerja.
- Jangan menggunakan UUID supplier sebagai kode vendor yang ditampilkan kepada pengguna.

## 5. Perubahan Laporan Pergerakan Barang

### 5.1 Endpoint

Pertahankan endpoint:

```http
POST /inventory/product-move-history-report
Authorization: Bearer <token>
Content-Type: application/json
```

Endpoint lama diperluas agar tidak menimbulkan breaking change.

### 5.2 Request baru

```json
{
  "start_date": "2026-07-01",
  "end_date": "2026-07-31",
  "product_id": "550e8400-e29b-41d4-a716-446655440002",
  "movement_type": null,
  "reference_type": null,
  "supplier_id": null,
  "customer_id": null,
  "search": null,
  "page": 1,
  "limit": 25,
  "sort_order": "asc"
}
```

Semua field baru bersifat opsional kecuali `start_date` dan `end_date`.

### 5.3 Validasi request

| Field | Aturan |
|---|---|
| `start_date` | Wajib, format `YYYY-MM-DD` |
| `end_date` | Wajib, format `YYYY-MM-DD`, tidak boleh sebelum `start_date` |
| `product_id` | UUID valid atau `null` |
| `movement_type` | `income`, `outcome`, `adjustment`, `loss`, `internal_consumption`, atau `null` |
| `reference_type` | `purchase_order`, `workorder`, `consignment_receipt`, `adjustment`, `loss`, `internal_consumption`, atau `null` |
| `page` | Integer, minimal `1`, default `1` |
| `limit` | Integer `1-100`, default `25` |
| `sort_order` | `asc` atau `desc`; default `asc` untuk kartu stok |

### 5.4 Response baru

```json
{
  "status": "success",
  "message": "Laporan pergerakan barang berhasil dihasilkan",
  "data": {
    "summary": {
      "opening_balance": 5,
      "total_in": 10,
      "total_out": 4,
      "total_adjustment": 0,
      "closing_balance": 11
    },
    "total_entries": 2,
    "items": [
      {
        "movement_id": "550e8400-e29b-41d4-a716-446655440010",
        "product_id": "550e8400-e29b-41d4-a716-446655440002",
        "product_name": "Oli Mesin 1L",
        "type": "income",
        "quantity": 10,
        "quantity_in": 10,
        "quantity_out": 0,
        "balance_before": 5,
        "balance_after": 15,
        "purchase_price": 100000,
        "selling_price": null,
        "price": 100000,
        "hpp": 100000,
        "reference_type": "purchase_order",
        "reference_id": "550e8400-e29b-41d4-a716-446655440020",
        "reference_no": "PO-20260712-001",
        "purchase_order_id": "550e8400-e29b-41d4-a716-446655440020",
        "purchase_order_no": "PO-20260712-001",
        "workorder_id": null,
        "workorder_no": null,
        "supplier_id": "550e8400-e29b-41d4-a716-446655440001",
        "vendor_code": "VND-001",
        "supplier_name": "PT Supplier Jaya",
        "customer_id": null,
        "customer_name": null,
        "vehicle_id": null,
        "nopol": null,
        "timestamp": "2026-07-12T10:00:00+07:00",
        "performed_by": "admin",
        "notes": "Purchase order received"
      },
      {
        "movement_id": "550e8400-e29b-41d4-a716-446655440011",
        "product_id": "550e8400-e29b-41d4-a716-446655440002",
        "product_name": "Oli Mesin 1L",
        "type": "outcome",
        "quantity": -4,
        "quantity_in": 0,
        "quantity_out": 4,
        "balance_before": 15,
        "balance_after": 11,
        "purchase_price": null,
        "selling_price": 150000,
        "price": 150000,
        "hpp": 100000,
        "reference_type": "workorder",
        "reference_id": "550e8400-e29b-41d4-a716-446655440030",
        "reference_no": "WO-20260712-001",
        "purchase_order_id": null,
        "purchase_order_no": null,
        "workorder_id": "550e8400-e29b-41d4-a716-446655440030",
        "workorder_no": "WO-20260712-001",
        "supplier_id": null,
        "vendor_code": null,
        "supplier_name": null,
        "customer_id": "550e8400-e29b-41d4-a716-446655440040",
        "customer_name": "Budi",
        "vehicle_id": "550e8400-e29b-41d4-a716-446655440050",
        "nopol": "B 1234 ABC",
        "timestamp": "2026-07-12T14:00:00+07:00",
        "performed_by": "kasir",
        "notes": "Product used in work order"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 25,
      "total": 2,
      "total_pages": 1,
      "has_previous": false,
      "has_next": false
    }
  }
}
```

### 5.5 Arti harga

| Field | Aturan |
|---|---|
| `purchase_price` | Harga beli aktual per unit dari baris PO atau penerimaan konsinyasi |
| `selling_price` | Harga jual aktual per unit yang tersimpan pada baris WO |
| `price` | Alias kompatibilitas: harga beli untuk `income`, harga jual untuk `outcome` |
| `hpp` | HPP snapshot pada saat transaksi, bukan cost master produk saat laporan dibuka |

Harga transaksi harus berasal dari snapshot baris transaksi. Jangan menghitung ulang histori menggunakan harga produk saat ini.

### 5.6 Referensi transaksi

Backend harus mengisi referensi berdasarkan sumber pergerakan:

| Sumber | `reference_type` | Nomor utama | Pihak terkait |
|---|---|---|---|
| Penerimaan PO | `purchase_order` | `purchase_order_no` | Vendor |
| Penjualan/pemakaian WO | `workorder` | `workorder_no` | Pelanggan dan kendaraan |
| Penerimaan konsinyasi | `consignment_receipt` | Nomor penerimaan | Vendor |
| Penyesuaian stok | `adjustment` | Nomor adjustment | Tidak wajib |
| Kehilangan | `loss` | Nomor kehilangan | Tidak wajib |
| Pemakaian internal | `internal_consumption` | Nomor dokumen | Unit/pemohon bila tersedia |

`reference_no` harus berisi nomor dokumen sumber yang sama dengan field khususnya. Field `notes` tetap disediakan sebagai keterangan, tetapi tidak boleh menjadi satu-satunya sumber nomor dokumen.

## 6. Aturan Perhitungan Kartu Stok

### 6.1 Normalisasi quantity

```text
quantity_in  = quantity,      jika quantity > 0
quantity_out = ABS(quantity), jika quantity < 0
```

Untuk data yang menyimpan tipe dan quantity tanpa tanda, backend harus menormalisasi tanda sebelum menghitung saldo.

### 6.2 Saldo awal dan akhir

```text
opening_balance = SUM(quantity seluruh transaksi sebelum start_date)
balance_after   = balance_before + quantity
closing_balance = opening_balance + total_in - total_out + net_adjustment
```

Urutan saldo berjalan wajib deterministik:

```sql
ORDER BY timestamp ASC, created_at ASC, movement_id ASC
```

Jika response diminta dengan `sort_order = desc`, saldo tetap dihitung dalam urutan kronologis lalu daftar boleh dibalik untuk tampilan.

### 6.3 Batas waktu

- `start_date` dimulai pada `00:00:00` timezone bisnis.
- `end_date` menggunakan batas eksklusif sebelum `00:00:00` hari berikutnya.
- Gunakan timezone bisnis yang sama dengan Daily Report, yaitu `Asia/Bangkok`, kecuali konfigurasi aplikasi menentukan nilai lain.

## 7. Model Data yang Direkomendasikan

Jika tabel pergerakan belum memiliki referensi terstruktur, tambahkan kolom berikut:

```text
reference_type       VARCHAR/ENUM nullable
reference_id         UUID nullable
purchase_order_id    UUID nullable
workorder_id         UUID nullable
supplier_id          UUID nullable
customer_id          UUID nullable
vehicle_id           UUID nullable
purchase_price       DECIMAL nullable
selling_price        DECIMAL nullable
hpp_snapshot         DECIMAL nullable
```

Pilihan minimal adalah `reference_type` dan `reference_id`, kemudian join dilakukan berdasarkan tipe. Namun foreign key khusus tetap direkomendasikan jika skema saat ini sudah memiliki relasi tersebut.

Data baru harus menyimpan snapshot harga/HPP saat pergerakan dibuat. Untuk data lama, backend boleh menggunakan fallback hasil join selama diberi nilai `null` jika sumber tidak dapat ditemukan.

## 8. Indeks Database

Indeks berikut direkomendasikan:

```text
(product_id, timestamp)
(reference_type, reference_id)
(purchase_order_id)
(workorder_id)
(supplier_id, timestamp)
(customer_id, timestamp)
```

Tujuannya agar filter per produk dan rentang tanggal tetap cepat ketika histori bertambah besar.

## 9. Response Error

Gunakan format error konsisten:

```json
{
  "status": "error",
  "message": "Product tidak ditemukan",
  "detail": "Tidak ada product dengan ID yang diberikan"
}
```

| HTTP | Kondisi |
|---:|---|
| `200` | Laporan berhasil, termasuk ketika `items` kosong |
| `401` | Token tidak ada atau tidak valid |
| `403` | Pengguna tidak memiliki akses laporan |
| `404` | `product_id`, supplier, atau customer filter tidak ditemukan |
| `422` | Tanggal, UUID, enum, page, atau limit tidak valid |
| `500` | Query atau kegagalan database yang tidak terduga |

## 10. Keamanan dan Hak Akses

- Endpoint laporan pergerakan harus menggunakan Bearer Token.
- Terapkan permission laporan inventory sesuai role aplikasi.
- Jangan menerima nama tabel, nama kolom, atau ekspresi sort mentah dari request.
- Nilai `sort_order` harus dipetakan dari enum yang telah divalidasi.

## 11. Strategi Migrasi

1. Tambahkan kolom baru dalam keadaan nullable.
2. Isi referensi transaksi untuk pergerakan baru.
3. Lakukan backfill data lama secara bertahap dari relasi dan pola `notes` yang dapat dipercaya.
4. Jangan menggagalkan laporan jika data lama tidak dapat direkonstruksi; kembalikan `null` pada field yang tidak ditemukan.
5. Tambahkan indeks setelah atau bersamaan dengan migration sesuai ukuran tabel.
6. Perluas schema OpenAPI dan dokumentasi API.
7. Pertahankan seluruh field response lama.

Parsing `notes` hanya boleh digunakan untuk proses backfill terkontrol, bukan pada request laporan normal.

## 12. Acceptance Criteria

Implementasi dianggap selesai jika seluruh kondisi berikut terpenuhi:

- [x] Laporan pembelian mengembalikan `purchase_order_id`, `supplier_id`, `supplier_code`, dan `product_id`.
- [x] Laporan pergerakan dapat difilter dengan satu `product_id`.
- [x] Pergerakan baru dari PO mengembalikan nomor PO dan identitas vendor secara terstruktur.
- [x] Pergerakan baru dari WO mengembalikan nomor WO, pelanggan, dan nopol secara terstruktur.
- [x] Harga beli movement baru berasal dari snapshot baris pembelian.
- [x] Harga jual movement baru berasal dari snapshot baris WO.
- [x] HPP movement baru berasal dari snapshot saat transaksi.
- [x] `opening_balance`, `balance_before`, `balance_after`, dan `closing_balance` terhitung konsisten.
- [x] Pagination mengembalikan tepat maksimal `limit` item.
- [x] Field response lama tetap dipertahankan; data lama yang tidak dapat direkonstruksi bernilai `null`.
- [x] Response OpenAPI mencantumkan `200`, `401`, `403`, `404`, `422`, dan `500`.
- [ ] Pengujian mencakup pembelian, penjualan, adjustment, loss, konsinyasi, dan internal consumption.

## 13. Test Case Minimum

### 13.1 Alur pembelian sampai penjualan

1. Saldo awal produk adalah `5`.
2. Terima PO sebanyak `10` dengan harga beli `100.000`.
3. Jual melalui WO sebanyak `4` dengan harga jual `150.000` dan HPP `100.000`.
4. Laporan harus menghasilkan:

```text
opening_balance = 5
total_in        = 10
total_out       = 4
closing_balance = 11
```

Baris PO harus menampilkan `PO`, vendor, dan harga beli. Baris WO harus menampilkan `WO`, pelanggan, nopol, harga jual, dan HPP.

### 13.2 Data lama tanpa referensi

- Laporan tidak boleh gagal.
- Field referensi boleh `null`.
- `notes` lama tetap dikirim.
- Saldo tetap dihitung dari quantity.

### 13.3 Validasi

- UUID salah menghasilkan `422`.
- `end_date < start_date` menghasilkan `422`.
- `limit > 100` menghasilkan `422`.
- Product valid tanpa histori menghasilkan `200`, summary nol, dan `items: []`.

## 14. Dampak ke Frontend Setelah Backend Selesai

Setelah kontrak ini tersedia, frontend dapat:

1. Mengganti laporan pembelian statis dengan data API nyata.
2. Menampilkan kolom Kode Vendor pada laporan pembelian.
3. Menampilkan kolom No. WO dan No. PO pada laporan pergerakan.
4. Membuat halaman kartu stok per barang dengan saldo berjalan.
5. Menyediakan tautan dari nomor WO/PO ke halaman detail transaksi.
