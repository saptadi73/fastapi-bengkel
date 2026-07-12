# Daily Report Technical Recommendation

## 1. Tujuan

Dokumen ini menjadi acuan teknis untuk menyederhanakan halaman **Laporan Harian** dan
menyamakan kontrak data antara frontend Vue dan backend.

Target laporan:

1. Menampilkan total Work Order hari ini di bagian paling atas.
2. Menampilkan cash-out aktual dari biaya dan pembayaran Purchase Order.
3. Menampilkan penjualan produk dan jasa beserta HPP dan margin.
4. Menampilkan posisi Cash, Bank, QRIS, Debit, dan Kas Kecil secara ringkas.
5. Menampilkan sisa uang tunai di kasir.
6. Menampilkan net profit harian.

## 2. Kondisi Saat Ini

Frontend menggunakan endpoint:

```http
POST /accounting/daily-report
Authorization: Bearer <token>
Content-Type: application/json
```

Implementasi halaman berada di:

- `src/pages/DailyReport.vue`

Bagian yang sudah tersedia di frontend:

- Ringkasan dan daftar Work Order.
- Daftar biaya dan Purchase Order.
- Penjualan produk dan jasa.
- Cashbook per akun.
- Margin produk dan jasa.
- Laporan laba rugi dan net profit.

Kesenjangan saat ini:

- Kontrak response pada dokumentasi API belum sama dengan struktur yang dibaca frontend.
- Biaya masih berasal dari `profit_loss.expenses`, bukan cash-out aktual.
- Nilai PO masih menggunakan nilai pembelian, bukan pembayaran PO aktual.
- Cashbook belum mempunyai klasifikasi channel yang stabil.
- Saldo kas kasir belum tersedia sebagai field khusus.
- Edit nama akun dapat merusak filter apabila frontend bergantung pada `account_name`.
- Definisi `total_biaya` pada Work Order belum cukup jelas untuk menghitung profit WO.

## 3. Keputusan Arsitektur

Gunakan dan perluas endpoint yang sudah ada:

```http
POST /accounting/daily-report
```

Tidak direkomendasikan memecah halaman menjadi banyak request karena:

- Semua nilai laporan harus memakai snapshot tanggal yang sama.
- Mengurangi risiko total antarbagian berbeda akibat data berubah di antara request.
- Mengurangi jumlah request frontend.
- Memusatkan aturan perhitungan akuntansi di backend.

Endpoint tambahan hanya diperlukan jika perhitungan posisi kas mempunyai otorisasi,
sumber data, atau beban komputasi yang benar-benar berbeda. Kandidat opsional:

```http
POST /accounting/daily-cash-position
```

## 4. Request Contract

### Endpoint

```http
POST /accounting/daily-report
```

### Authentication

Wajib menggunakan JWT bearer token.

### Request body

```json
{
  "date": "2026-07-12"
}
```

### Validasi

- `date` wajib diisi.
- Format `date` adalah `YYYY-MM-DD`.
- Perhitungan tanggal menggunakan timezone aplikasi, yaitu `Asia/Bangkok` atau timezone
  bisnis yang dikonfigurasi backend.
- Backend harus menentukan batas hari secara eksplisit, misalnya
  `2026-07-12T00:00:00+07:00` sampai sebelum `2026-07-13T00:00:00+07:00`.

## 5. Recommended Response Contract

```json
{
  "status": "success",
  "message": "Daily report retrieved successfully",
  "data": {
    "date": "2026-07-12",
    "timezone": "Asia/Bangkok",
    "generated_at": "2026-07-12T17:30:00+07:00",
    "work_orders": {
      "total_workorders": 10,
      "total_revenue": 7500000,
      "total_hpp": 4200000,
      "gross_profit": 3300000,
      "items": [
        {
          "workorder_id": "uuid-string",
          "workorder_no": "WO-20260712-001",
          "customer_name": "Budi",
          "total_revenue": 750000,
          "total_hpp": 420000,
          "gross_profit": 330000,
          "payment_status": "paid"
        }
      ]
    },
    "outflows": {
      "total_cash_out": 2500000,
      "expenses": {
        "total": 500000,
        "items": [
          {
            "expense_id": "uuid-string",
            "payment_id": "uuid-string",
            "payment_date": "2026-07-12",
            "category": "listrik",
            "description": "Pembayaran listrik",
            "amount": 500000,
            "payment_channel": "bank",
            "channel_code": "BANK_110201",
            "account_code": "110201",
            "account_name": "Bank BCA"
          }
        ]
      },
      "purchase_order_payments": {
        "total": 2000000,
        "items": [
          {
            "purchase_order_id": "uuid-string",
            "purchase_order_no": "PO-20260710-001",
            "payment_id": "uuid-string",
            "payment_date": "2026-07-12",
            "supplier_name": "PT Supplier Jaya",
            "amount_paid": 2000000,
            "payment_channel": "bank",
            "channel_code": "BANK_110201",
            "account_code": "110201",
            "account_name": "Bank BCA"
          }
        ]
      }
    },
    "product_sales": {
      "total_quantity": 15,
      "total_sales": 3750000,
      "total_hpp": 2250000,
      "total_margin": 1500000,
      "margin_percentage": 40,
      "items": [
        {
          "workorder_id": "uuid-string",
          "workorder_no": "WO-20260712-001",
          "product_id": "uuid-string",
          "product_name": "Oli Mesin",
          "quantity": 1,
          "price": 150000,
          "hpp": 100000,
          "discount": 0,
          "subtotal": 150000,
          "margin": 50000
        }
      ]
    },
    "service_sales": {
      "total_quantity": 8,
      "total_sales": 3750000,
      "total_hpp": 1950000,
      "total_margin": 1800000,
      "margin_percentage": 48,
      "items": [
        {
          "workorder_id": "uuid-string",
          "workorder_no": "WO-20260712-001",
          "service_id": "uuid-string",
          "service_name": "Tune Up",
          "quantity": 1,
          "price": 300000,
          "hpp": 150000,
          "discount": 0,
          "subtotal": 300000,
          "margin": 150000
        }
      ]
    },
    "payment_channels": [
      {
        "code": "CASHIER_CASH",
        "name": "Kas Kasir",
        "type": "cashier_cash",
        "account_code": "110101",
        "opening_balance": 1000000,
        "cash_in": 3500000,
        "cash_out": 500000,
        "closing_balance": 4000000
      },
      {
        "code": "BANK_BCA",
        "name": "Bank BCA",
        "type": "bank",
        "account_code": "110201",
        "opening_balance": 10000000,
        "cash_in": 1500000,
        "cash_out": 2000000,
        "closing_balance": 9500000
      },
      {
        "code": "QRIS",
        "name": "QRIS",
        "type": "qris",
        "account_code": "110202",
        "opening_balance": 0,
        "cash_in": 1250000,
        "cash_out": 0,
        "closing_balance": 1250000
      },
      {
        "code": "DEBIT",
        "name": "Debit",
        "type": "debit",
        "account_code": "110203",
        "opening_balance": 0,
        "cash_in": 750000,
        "cash_out": 0,
        "closing_balance": 750000
      },
      {
        "code": "PETTY_CASH",
        "name": "Kas Kecil",
        "type": "petty_cash",
        "account_code": "110102",
        "opening_balance": 500000,
        "cash_in": 0,
        "cash_out": 100000,
        "closing_balance": 400000
      }
    ],
    "cashier_cash": {
      "code": "CASHIER_CASH",
      "account_code": "110101",
      "account_name": "Kas Kasir",
      "opening_balance": 1000000,
      "cash_in": 3500000,
      "cash_out": 500000,
      "closing_balance": 4000000
    },
    "profit_loss": {
      "total_revenue": 7500000,
      "product_hpp": 2250000,
      "service_hpp": 1950000,
      "total_hpp": 4200000,
      "gross_profit": 3300000,
      "operating_expenses": 500000,
      "net_profit": 2800000,
      "revenues": [],
      "expenses": []
    }
  }
}
```

## 6. Definisi dan Rumus

### 6.1 Work Order

```text
work_orders.total_workorders = jumlah WO sesuai kebijakan status pada tanggal laporan
work_orders.total_revenue    = total penjualan produk + jasa setelah diskon
work_orders.total_hpp        = HPP produk + HPP jasa
work_orders.gross_profit     = total_revenue - total_hpp
```

Backend harus menetapkan WO mana yang masuk laporan. Rekomendasi: gunakan WO dengan transaksi
penjualan yang diakui pada tanggal laporan, bukan sekadar WO yang dibuat pada tanggal tersebut.

### 6.2 Cash-out

```text
outflows.total_cash_out = expenses.total + purchase_order_payments.total
```

Aturan penting:

- Gunakan tanggal pembayaran aktual.
- PO yang belum dibayar tidak masuk cash-out.
- Pembayaran sebagian hanya memasukkan nominal yang dibayar pada tanggal laporan.
- Pembuatan PO tidak otomatis menjadi expense.
- Pembayaran PO mengurangi kas tetapi tidak otomatis mengurangi net profit karena barang dapat
  masih tercatat sebagai persediaan.

### 6.3 Margin Penjualan

```text
line_subtotal     = (quantity * price) - discount
line_margin       = line_subtotal - (quantity * hpp)
total_margin      = total_sales - total_hpp
margin_percentage = total_margin / total_sales * 100
```

Jika `total_sales` nol, `margin_percentage` harus bernilai nol.

### 6.4 Posisi Kas

```text
closing_balance = opening_balance + cash_in - cash_out
```

`closing_balance` harus dihitung backend dari jurnal yang sudah diposting. Frontend hanya
menampilkan hasil dan tidak menjadi sumber perhitungan resmi.

### 6.5 Net Profit

```text
total_hpp         = product_hpp + service_hpp
gross_profit      = total_revenue - total_hpp
net_profit        = gross_profit - operating_expenses
```

Jangan mengurangkan `purchase_order_payments` langsung dari net profit.

## 7. Klasifikasi Payment Channel

Backend harus mengirim kode dan tipe yang stabil. Frontend tidak boleh menentukan tipe akun
dengan mencocokkan teks `account_name`.

Nilai `type` yang direkomendasikan:

| Type | Kegunaan |
| --- | --- |
| `cashier_cash` | Uang tunai fisik di kasir |
| `bank` | Rekening bank |
| `qris` | Penerimaan QRIS |
| `debit` | Penerimaan kartu debit/EDC |
| `petty_cash` | Kas kecil operasional |

Apabila QRIS atau debit masuk langsung ke rekening bank, backend tetap boleh menampilkan channel
transaksi secara terpisah sambil mengaitkannya ke akun buku besar yang sama.

## 8. Rekomendasi Layout Frontend

Urutan tampilan:

1. **Ringkasan utama**: total WO, revenue, cash-out, sisa kas kasir, dan net profit.
2. **Work Order hari ini**: tabel ringkas dan dapat diperluas.
3. **Outflow**: biaya dan pembayaran PO dalam dua panel.
4. **Sales**: product sales dan service sales.
5. **Payment channels**: kartu ringkas Cash, Bank, QRIS, Debit, dan Kas Kecil.
6. **Profit & Loss**: revenue, HPP, expense, gross profit, dan net profit.

Detail cashbook tidak perlu terbuka secara default. Gunakan tombol **Lihat Detail** atau accordion
agar halaman tidak terlalu panjang.

## 9. Backward Compatibility

Selama masa transisi, backend dapat mempertahankan field lama dan menambahkan field baru.

Frontend saat ini telah melakukan normalisasi sebagian untuk:

- `cash_book` menjadi `cash_books`.
- Nilai kosong pada `product_sales`, `service_sales`, `profit_loss`, `work_orders`, dan
  `purchase_orders`.

Rencana migrasi:

1. Tambahkan struktur response baru tanpa menghapus field lama.
2. Perbarui frontend agar memakai `outflows`, `payment_channels`, dan `cashier_cash`.
3. Verifikasi angka lama dan baru pada tanggal yang sama.
4. Hapus fallback lama setelah frontend production sudah menggunakan kontrak baru.
5. Jika perubahan dianggap breaking, gunakan versi endpoint seperti
   `POST /accounting/v2/daily-report`.

## 10. Error Response

### Invalid date

```json
{
  "status": "error",
  "message": "Invalid date format. Expected YYYY-MM-DD"
}
```

Status HTTP: `422 Unprocessable Entity`.

### Unauthorized

```json
{
  "status": "error",
  "message": "Authentication required"
}
```

Status HTTP: `401 Unauthorized`.

## 11. Backend Implementation Checklist

- [ ] Tetapkan timezone bisnis dan batas awal/akhir hari.
- [ ] Tetapkan status WO yang diakui sebagai revenue harian.
- [ ] Pisahkan nilai penjualan, HPP, pembayaran, dan arus kas.
- [ ] Ambil expense berdasarkan payment journal aktual.
- [ ] Ambil pembayaran PO berdasarkan payment journal aktual.
- [ ] Jangan memasukkan PO belum dibayar ke cash-out.
- [ ] Tambahkan klasifikasi payment channel yang stabil.
- [ ] Tambahkan posisi kas kasir dan closing balance.
- [ ] Hitung seluruh aggregate menggunakan decimal/numeric, bukan floating point.
- [ ] Pastikan transaksi void/cancelled tidak masuk aggregate.
- [ ] Pastikan transaksi yang dibalik/refund memengaruhi laporan dengan arah yang benar.
- [ ] Tambahkan index database pada tanggal transaksi dan foreign key pembayaran.
- [ ] Tambahkan automated test untuk semua rumus laporan.

## 12. Frontend Implementation Checklist

- [ ] Tempatkan kartu total WO di paling atas.
- [ ] Ganti sumber biaya dari `profit_loss.expenses` ke `outflows.expenses`.
- [ ] Ganti total PO dengan `outflows.purchase_order_payments`.
- [ ] Tampilkan hanya payment channel yang diperlukan.
- [ ] Jadikan detail cashbook collapsible atau pindahkan ke halaman detail.
- [ ] Tampilkan `cashier_cash.closing_balance` sebagai **Sisa Cash di Kasir**.
- [ ] Tampilkan `profit_loss.net_profit` di ringkasan paling atas dan bagian laba rugi.
- [ ] Jangan menghitung angka akuntansi utama ulang di frontend.
- [ ] Perbarui export Excel agar memakai struktur response baru.
- [ ] Sediakan empty state ketika suatu bagian tidak memiliki transaksi.

## 13. Acceptance Criteria

Implementasi dianggap selesai jika:

1. Total WO sama dengan data transaksi pada tanggal dan timezone yang dipilih.
2. Cash-out biaya hanya berisi biaya yang benar-benar dibayar pada tanggal laporan.
3. Cash-out PO hanya berisi pembayaran PO pada tanggal laporan.
4. Total product dan service sales dapat direkonsiliasi ke Work Order.
5. Closing balance setiap channel sama dengan saldo jurnal.
6. Sisa cash kasir dapat diidentifikasi tanpa membaca nama akun.
7. Net profit mengikuti rumus revenue dikurangi HPP dan operating expense.
8. Total PO tidak langsung mengurangi net profit.
9. Angka pada tampilan dan export Excel konsisten.
10. Response kosong tetap menghasilkan nilai nol dan array kosong, bukan error frontend.

## 14. Test Scenarios Minimum

| Skenario | Hasil yang diharapkan |
| --- | --- |
| Tidak ada transaksi | Semua total nol dan array kosong |
| WO tunai lunas | Revenue, cash-in, kas kasir, dan profit bertambah |
| WO dibayar QRIS | Revenue dan QRIS bertambah; kas kasir tidak bertambah |
| Biaya dibayar kas kecil | Expense dan cash-out kas kecil bertambah |
| PO dibuat tetapi belum dibayar | Nilai pembelian ada, cash-out tetap nol |
| PO dibayar sebagian | Cash-out hanya sebesar nominal pembayaran |
| Refund/void | Aggregate dikurangi atau transaksi dikecualikan sesuai aturan |
| HPP kosong | Backend memakai nilai nol atau menolak data sesuai kebijakan yang ditetapkan |
| Laporan tanggal lampau | Menggunakan data dan saldo pada tanggal tersebut, bukan saldo hari ini |

## 15. Dokumentasi yang Perlu Diselaraskan

Setelah backend menerapkan kontrak ini, perbarui bagian **16.32 Daily Report** pada
`src/docs/API_DOCUMENTATION_COMPLETE.md`. Response lama yang hanya berisi `sales_count`,
`sales_total`, `cash_in`, `cash_out`, `expenses`, dan `net_cash` tidak lagi cukup untuk kebutuhan
halaman `DailyReport.vue`.

## 16. Koreksi Pasca-Implementasi Backend

Bagian ini mencatat hasil review terhadap kontrak terbaru pada bagian **16.32 Daily Report** di
`API_DOCUMENTATION_COMPLETE.md`. Struktur utama backend sudah mengikuti rekomendasi, tetapi
koreksi berikut harus diselesaikan agar kontrak konsisten dan dapat direkonsiliasi.

### 16.1 Koreksi wajib profit-loss

`total_expenses` tidak boleh ambigu antara HPP dan operating expense. Gunakan field terpisah:

```json
{
  "profit_loss": {
    "total_revenue": 7500000,
    "product_hpp": 2250000,
    "service_hpp": 1950000,
    "total_hpp": 4200000,
    "gross_profit": 3300000,
    "operating_expenses": 500000,
    "net_profit": 2800000,
    "revenues": [],
    "expenses": []
  }
}
```

Rumus resmi:

```text
total_hpp    = product_hpp + service_hpp
gross_profit = total_revenue - total_hpp
net_profit   = gross_profit - operating_expenses
```

Rumus `net_profit = total_revenue - total_expenses` hanya valid jika `total_expenses` sudah
mencakup HPP dan operating expense. Pemakaian tersebut tidak direkomendasikan karena mudah
disalahartikan.

### 16.2 Pemisahan kode channel dan kode akun

Gunakan definisi berikut secara konsisten:

| Field | Arti | Contoh |
| --- | --- | --- |
| `code` | Identifier stabil untuk channel frontend | `CASHIER_CASH` |
| `channel_code` | Referensi channel pada item transaksi | `BANK_110201` |
| `account_code` | Kode Chart of Account | `110201` |
| `account_name` | Nama akun yang dapat ditampilkan | `Bank BCA` |

`cashier_cash.account_code` harus sama dengan `account_code` milik elemen
`payment_channels` bertipe `cashier_cash`. Jangan mengisi `account_code` dengan nilai
`CASHIER_CASH`; nilai tersebut adalah identifier channel.

Contoh:

```json
{
  "code": "CASHIER_CASH",
  "account_code": "110101",
  "account_name": "Kas Kasir"
}
```

### 16.3 Rekonsiliasi payment channel dan legacy fields

Jika field legacy masih dikirim, nilainya harus dapat direkonsiliasi dengan struktur baru:

```text
cash_in  = sum(payment_channels[].cash_in)
cash_out = sum(payment_channels[].cash_out)
net_cash = cash_in - cash_out
expenses = outflows.expenses.total
```

Semua channel yang membentuk total legacy harus disertakan di `payment_channels`. Jangan
menampilkan hanya Cash dan Bank apabila total legacy juga mengandung QRIS atau Debit.

### 16.4 Rekonsiliasi alias Work Order

Selama backward compatibility masih berlaku:

```text
workorders = work_orders.items
```

Jika `work_orders.items` berisi data, alias `workorders` tidak boleh berupa array kosong. Alias
legacy dapat dihapus setelah seluruh frontend production selesai dimigrasikan.

### 16.5 Enum status Work Order

Pisahkan status proses WO dari status pembayarannya:

```text
status:
draft | process | completed | cancelled

payment_status:
unpaid | partial | paid | refunded
```

Nilai enum sebaiknya berupa kode stabil berbahasa Inggris, sedangkan label Indonesia ditentukan
frontend. Jangan mencampur `dibayar`, `dibayarkan`, dan `paid` untuk kondisi yang sama.

Contoh item:

```json
{
  "workorder_id": "uuid-string",
  "workorder_no": "WO-20260712-001",
  "status": "completed",
  "payment_status": "paid",
  "total_revenue": 750000,
  "total_hpp": 420000,
  "gross_profit": 330000
}
```

### 16.6 Definisi detail outflow

Field minimum expense payment:

| Field | Tipe | Ketentuan |
| --- | --- | --- |
| `expense_id` | UUID/null | Nullable hanya untuk jurnal biaya yang tidak berasal dari master expense |
| `payment_id` | UUID | ID payment journal |
| `payment_date` | date | Tanggal pembayaran aktual |
| `category` | string | Kategori biaya |
| `description` | string/null | Deskripsi pembayaran |
| `amount` | decimal | Nominal yang benar-benar dibayar |
| `payment_channel` | enum | Tipe channel pembayaran |
| `channel_code` | string | Identifier channel pembayaran |
| `account_code` | string | Kode akun sumber dana |
| `account_name` | string | Nama akun sumber dana |

Field minimum PO payment:

| Field | Tipe | Ketentuan |
| --- | --- | --- |
| `purchase_order_id` | UUID | ID Purchase Order |
| `purchase_order_no` | string | Nomor Purchase Order |
| `payment_id` | UUID | ID payment journal |
| `payment_date` | date | Tanggal pembayaran aktual |
| `supplier_name` | string | Nama supplier |
| `amount_paid` | decimal | Nominal pembayaran pada tanggal laporan |
| `payment_channel` | enum | Tipe channel pembayaran |
| `channel_code` | string | Identifier channel pembayaran |
| `account_code` | string | Kode akun sumber dana |
| `account_name` | string | Nama akun sumber dana |

### 16.7 Checklist koreksi kontrak terbaru

- [ ] Tambahkan `total_hpp`, `gross_profit`, dan `operating_expenses` ke `profit_loss`.
- [ ] Perbaiki rumus dan contoh angka `net_profit`.
- [ ] Samakan `cashier_cash.account_code` dengan akun pada `payment_channels`.
- [ ] Pastikan total `cash_in` dan `cash_out` legacy sama dengan jumlah seluruh channel.
- [ ] Isi `workorders` dengan alias aktual `work_orders.items` selama masa transisi.
- [ ] Normalisasi enum `status` dan `payment_status`.
- [ ] Dokumentasikan nullable field dan semua kode pada detail outflow.
- [ ] Tambahkan automated reconciliation test untuk field baru dan legacy.

### 16.8 Acceptance criteria tambahan

Kontrak hasil revisi dianggap konsisten apabila:

1. Contoh `net_profit` dapat dihitung tepat dari field yang tersedia di response.
2. Setiap `account_code` dapat ditemukan pada Chart of Account.
3. Setiap `channel_code` item outflow dapat dipetakan ke `payment_channels[].code` atau aturan
   mapping backend yang terdokumentasi.
4. Jumlah arus kas seluruh channel sama dengan aggregate legacy.
5. `workorders` dan `work_orders.items` mempunyai isi ekuivalen selama kompatibilitas aktif.
6. Status WO dan status pembayaran tidak memakai beberapa kode untuk arti yang sama.
