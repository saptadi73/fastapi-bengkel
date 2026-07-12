# Inventory Backend Change Recommendation

Status: implemented on the backend and documented below as the current contract.

## 1. Tujuan

Dokumen ini merupakan handoff teknis untuk backend agar halaman **Daftar Barang Inventory** dapat:

- Memuat data inventory tanpa error ORM.
- Menampilkan harga jual.
- Menampilkan harga beli terakhir.
- Menampilkan HPP inventory.
- Menampilkan margin nominal dan persentase.
- Mendukung pagination 25 barang per halaman.

Frontend terkait berada di:

```text
src/components/TableInventory.vue
```

Endpoint terkait:

```http
GET /products/inventory/all
```

## 2. Status Implementasi Saat Ini

Error mapper `consignment_receipts` sudah diperbaiki di backend. Model `Product` dan `Supplier` sekarang memiliki relationship pasangan yang sesuai, `ConsignmentReceipt` sudah terdaftar di registry model, dan endpoint inventory sudah dapat dikonsumsi oleh frontend.

Endpoint `GET /products/inventory/all` sekarang mengembalikan response paginated dengan field harga jual, harga beli terakhir, HPP, margin, margin percentage, dan status stok.

## 3. Rekomendasi Perbaikan ORM

### 3.1 Penyebab yang perlu diperiksa

Kemungkinan terdapat model lain yang mendeklarasikan relationship seperti:

```python
product = relationship("Product", back_populates="consignment_receipts")
```

tetapi model `Product` tidak memiliki property pasangan bernama `consignment_receipts`.

Periksa seluruh deklarasi berikut:

```text
relationship("Product", ...)
back_populates="consignment_receipts"
Product.consignment_receipts
```

### 3.2 Opsi A: Tambahkan relationship pasangan

Jika satu produk memang dapat mempunyai banyak penerimaan konsinyasi:

```python
class Product(Base):
    __tablename__ = "product"

    # Existing fields...

    consignment_receipts = relationship(
        "ConsignmentReceipt",
        back_populates="product",
        cascade="save-update, merge",
    )


class ConsignmentReceipt(Base):
    __tablename__ = "consignment_receipt"

    product_id = Column(ForeignKey("product.id"), nullable=False, index=True)

    product = relationship(
        "Product",
        back_populates="consignment_receipts",
    )
```

Nama model, tabel, dan foreign key harus disesuaikan dengan source backend aktual.

Jangan menggunakan `delete-orphan` sebelum aturan penghapusan data konsinyasi dipastikan.

### 3.3 Opsi B: Koreksi nama `back_populates`

Jika model `Product` sudah memiliki relationship dengan nama berbeda, misalnya:

```python
consignment_receipt_items = relationship(
    "ConsignmentReceipt",
    back_populates="product",
)
```

maka model pasangannya harus menggunakan nama yang sama:

```python
product = relationship(
    "Product",
    back_populates="consignment_receipt_items",
)
```

Kedua sisi `back_populates` harus saling menunjuk ke nama property Python, bukan nama tabel.

### 3.4 Validasi mapper

Tambahkan test yang memaksa seluruh mapper dikonfigurasi saat startup atau test suite:

```python
from sqlalchemy.orm import configure_mappers


def test_all_mappers_are_valid():
    configure_mappers()
```

Test ini harus gagal sebelum server menerima request apabila ada relationship yang tidak valid.

Implementasi backend saat ini sudah memakai pendekatan ini dan telah divalidasi dengan test mapper.

## 4. Definisi Harga

Backend perlu membedakan field berikut:

| Field | Definisi |
| --- | --- |
| `price` | Harga jual produk saat ini |
| `purchase_price` | Harga beli dari transaksi pembelian/penerimaan terakhir yang valid |
| `vendor_code` | Kode supplier/vendor dari sumber transaksi yang sama dengan `purchase_price`; fallback ke supplier master produk bila histori belum ada |
| `supplier_name` | Nama supplier/vendor dari sumber transaksi yang sama dengan `purchase_price`; fallback ke supplier master produk bila histori belum ada |
| `hpp` | Harga pokok inventory yang dipakai untuk pengakuan biaya/laba-rugi |
| `margin` | Harga jual dikurangi HPP |
| `margin_percentage` | Margin dibagi harga jual, dikali 100 |

`purchase_price` dan `hpp` tidak selalu sama:

- `purchase_price` merepresentasikan harga pembelian terakhir.
- `hpp` dapat menggunakan moving average, weighted average, FIFO, atau kebijakan akuntansi lain.
- Backend harus menggunakan satu kebijakan HPP yang konsisten dengan laporan laba-rugi.

## 5. Aturan Perhitungan

```text
margin = price - hpp
```

```text
margin_percentage = (margin / price) * 100
```

Jika `price` bernilai nol:

```text
margin_percentage = 0
```

Rekomendasi presisi:

- Simpan nominal uang menggunakan `DECIMAL`/`NUMERIC`, bukan floating point.
- Jangan membulatkan `price`, `purchase_price`, atau `hpp` sebelum perhitungan selesai.
- `margin_percentage` dapat dibulatkan menjadi dua angka desimal pada serializer.

## 6. Kontrak Endpoint yang Direkomendasikan

### 6.1 Request

```http
GET /products/inventory/all?page=1&limit=25
```

Parameter:

| Parameter | Tipe | Default | Ketentuan |
| --- | --- | --- | --- |
| `page` | integer | `1` | Minimum `1` |
| `limit` | integer | `25` | Minimum `1`, maksimum yang disarankan `100` |
| `search` | string | null | Opsional: nama, brand, kategori, atau type |
| `category_id` | UUID | null | Filter kategori opsional |
| `stock_status` | enum | null | `safe` atau `reorder` |

Jika backend sudah memakai pola `skip`/`limit`, kontrak berikut juga dapat digunakan:

```http
GET /products/inventory/all?skip=0&limit=25
```

Pilih satu pola canonical dan dokumentasikan secara konsisten.

### 6.2 Success response

```json
{
  "status": "success",
  "message": "Inventory retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Oli Shell 1L",
      "type": "product",
      "description": "Oli mesin berkualitas tinggi",
      "brand_id": "uuid-string",
      "brand_name": "Shell",
      "category_id": "uuid-string",
      "category_name": "Sparepart",
      "satuan_id": "uuid-string",
      "satuan_name": "Botol",
      "vendor_code": "VND-001",
      "supplier_id": "uuid-string",
      "supplier_name": "PT Supplier Maju",
      "price": 150000,
      "purchase_price": 95000,
      "hpp": 100000,
      "margin": 50000,
      "margin_percentage": 33.33,
      "total_stock": 50,
      "min_stock": 10,
      "stock_status": "safe",
      "is_consignment": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 150,
    "total_pages": 6,
    "has_previous": false,
    "has_next": true
  }
}
```

### 6.3 Empty response

```json
{
  "status": "success",
  "message": "Inventory retrieved successfully",
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 0,
    "total_pages": 0,
    "has_previous": false,
    "has_next": false
  }
}
```

Empty result harus mengembalikan HTTP `200`, bukan `404`.

## 7. Sumber Data Harga Beli

`purchase_price` sebaiknya diambil dari baris pembelian/penerimaan terakhir yang:

- Sudah dikonfirmasi atau diterima.
- Tidak dibatalkan atau di-void.
- Mempunyai quantity lebih besar dari nol.
- Terkait dengan produk yang diminta.

Urutan transaksi harus menggunakan timestamp bisnis yang konsisten. Jika dua transaksi mempunyai
timestamp yang sama, gunakan ID atau waktu pembuatan sebagai tie-breaker deterministik.

`vendor_code` dan `supplier_name` pada payload inventory harus mengikuti supplier dari transaksi
yang terpilih sebagai sumber `purchase_price`, agar frontend tidak menerima kombinasi harga beli
dan identitas vendor dari sumber yang berbeda. Jika belum ada histori transaksi valid, backend
boleh fallback ke supplier master pada produk.

Jika belum pernah ada pembelian:

- Gunakan `null` untuk menandakan data tidak tersedia; atau
- Gunakan `product.cost` hanya apabila itu merupakan kebijakan fallback resmi.

Rekomendasi utama adalah `null`, agar nilai yang tidak diketahui tidak disalahartikan sebagai nol.

## 8. Sumber Data HPP

Backend harus menetapkan metode HPP. Jika menggunakan weighted average:

```text
new_hpp =
  ((old_stock * old_hpp) + (received_quantity * purchase_price))
  / (old_stock + received_quantity)
```

Aturan minimum:

- Jangan menghitung ulang HPP dari harga jual.
- Transaksi penjualan menggunakan snapshot HPP saat penjualan diposting.
- Perubahan harga beli setelah penjualan tidak boleh mengubah HPP transaksi historis.
- Adjustment stok tanpa nilai tidak boleh mengubah HPP kecuali ada kebijakan eksplisit.
- Produk konsinyasi harus mengikuti kebijakan cost yang terpisah jika kepemilikannya belum berpindah.

## 9. Stock Status

Backend dapat mengirim status siap pakai:

```text
safe    = total_stock > min_stock
reorder = total_stock <= min_stock
```

Jika field tidak dikirim, frontend masih dapat menghitung status tersebut.

## 10. Backward Compatibility

Frontend saat ini mendukung fallback berikut:

```text
HPP:
hpp -> cost -> 0

Harga beli:
purchase_price -> last_purchase_price -> buy_price -> cost -> hpp -> 0
```

Walaupun fallback tersedia, field canonical backend tetap harus:

```text
price
purchase_price
hpp
```

Field lama `cost` dapat dipertahankan sementara sebagai alias `hpp`, tetapi beri status deprecated
dan jadwal penghapusan yang jelas.

## 11. Query dan Performa

Hindari N+1 query untuk supplier, harga beli, atau saldo inventory.

Rekomendasi:

- Aggregate stok per `product_id` dalam subquery.
- Ambil purchase line terakhir menggunakan window function atau subquery terindeks.
- Eager-load brand, category, dan satuan.
- Terapkan pagination sebelum serialisasi response.

Index yang perlu diperiksa:

```text
inventory_move.product_id
inventory_move.timestamp
purchase_order_line.product_id
purchase_order.payment_date / received_at
product.category_id
product.brand_id
```

## 12. Error Handling

Kesalahan mapper atau database tidak seharusnya dipetakan menjadi HTTP `400`. Gunakan:

- `400` untuk request client yang tidak valid.
- `422` untuk validasi query parameter.
- `500` untuk kegagalan mapper/database yang tidak terduga.

Response production tidak perlu mengekspos detail internal mapper. Simpan stack trace pada log
backend dan kembalikan pesan umum:

```json
{
  "status": "error",
  "message": "Failed to retrieve inventory",
  "data": null
}
```

## 13. Migration Plan

1. Perbaiki relationship ORM dan tambahkan mapper test.
2. Pastikan endpoint inventory kembali HTTP `200`.
3. Tambahkan `purchase_price` tanpa menghapus `cost`.
4. Pastikan `hpp` menggunakan kebijakan cost yang resmi.
5. Tambahkan margin atau pastikan frontend menghitung dari `price` dan `hpp`.
6. Tambahkan pagination dengan default 25.
7. Jalankan rekonsiliasi terhadap data PO, inventory, dan laporan laba-rugi.
8. Setelah frontend production stabil, tandai field legacy untuk dihapus.

Status eksekusi saat ini:

- Relationship ORM sudah diperbaiki.
- Mapper test sudah ditambahkan.
- Endpoint inventory sudah mengembalikan HTTP 200 dengan payload paginated.
- Dokumentasi API utama sudah diperbarui agar cocok dengan response baru.

## 14. Backend Checklist

- [x] Relationship `Product` dan penerimaan konsinyasi valid di kedua sisi.
- [x] `configure_mappers()` berhasil pada test startup.
- [x] `GET /products/inventory/all` mengembalikan HTTP `200`.
- [x] Response mempunyai `price`.
- [x] Response mempunyai `purchase_price`.
- [x] Response mempunyai `hpp`.
- [x] Margin dihitung dari harga jual dikurangi HPP.
- [x] Harga beli terakhir mengabaikan transaksi void/cancelled ketika data valid tersedia.
- [x] HPP transaksi historis tidak berubah karena pembelian baru.
- [x] Pagination default adalah 25.
- [x] Empty data mengembalikan array kosong.
- [ ] Query tidak menghasilkan N+1 yang signifikan.
- [x] Error internal mapper dikembalikan sebagai HTTP `500`, bukan `400`.
- [x] OpenAPI dan `API_DOCUMENTATION_COMPLETE.md` diperbarui.

## 15. Acceptance Criteria

Implementasi backend dianggap selesai jika:

1. Endpoint inventory dapat dipanggil tanpa error mapper.
2. Satu produk mempunyai nilai harga jual, harga beli, dan HPP yang dapat dibedakan.
3. Margin pada response atau hasil perhitungan frontend sama dengan `price - hpp`.
4. Total stok sama dengan aggregate inventory movement yang valid.
5. Halaman pertama berisi maksimum 25 barang.
6. Metadata pagination sesuai dengan jumlah data database.
7. Filter dan pencarian tidak mengubah total secara keliru.
8. Produk tanpa histori pembelian ditangani secara eksplisit.
9. Produk konsinyasi tidak menghasilkan HPP yang salah.
10. Nilai HPP dapat direkonsiliasi dengan laporan laba-rugi.

## 16. Minimum Test Cases

| Skenario | Hasil yang diharapkan |
| --- | --- |
| Mapper dikonfigurasi | Tidak ada `InvalidRequestError` |
| Inventory kosong | HTTP 200, `data: []` |
| Produk tanpa pembelian | `purchase_price: null` atau fallback resmi |
| Produk satu kali dibeli | Harga beli sesuai purchase line |
| Produk dibeli beberapa kali | Harga beli memakai transaksi valid terakhir |
| Pembelian terakhir dibatalkan | Gunakan transaksi valid sebelumnya |
| Harga jual lebih besar dari HPP | Margin positif |
| Harga jual lebih kecil dari HPP | Margin negatif |
| Harga jual nol | Margin percentage nol |
| Data 26 barang | Halaman pertama 25, halaman kedua 1 |
| Produk di batas minimum stok | `stock_status: reorder` |
| Produk konsinyasi | Cost mengikuti kebijakan konsinyasi |

## 17. Catatan Integrasi Frontend

Frontend sudah menampilkan:

- `price` sebagai Harga Jual.
- `purchase_price` sebagai Harga Beli.
- `hpp` sebagai HPP.
- `price - hpp` sebagai Margin.
- 25 item per halaman.

Saat backend pagination diaktifkan, frontend perlu dilanjutkan dari client-side pagination ke
server-side pagination dengan membaca object `pagination` pada response.

## 18. Verifikasi Tindakan Lanjutan Backend

- [x] Double wrapper dihapus; `data` langsung berupa array dan `pagination` berada di level root.
- [x] Query `page >= 1`, `1 <= limit <= 100`, panjang `search` 1–100, UUID kategori,
  dan enum `stock_status` divalidasi oleh FastAPI/OpenAPI.
- [x] `purchase_price` membandingkan PO valid (`diterima`/`dibayarkan`) dan penerimaan
  konsinyasi valid, kemudian memilih transaksi terbaru secara deterministik.
- [x] `vendor_code` dan `supplier_name` inventory mengikuti supplier dari transaksi yang sama
  dengan `purchase_price`, dengan fallback ke supplier master produk jika histori belum ada.
- [x] Instalasi lama yang belum memiliki tabel `consignment_receipt` tetap dapat membuka
  inventory; backend melewati sumber konsinyasi dan menggunakan histori PO yang tersedia.
- [x] Response model `InventoryListResponse` dan model turunannya ditambahkan.
- [x] Test 26 barang memastikan halaman pertama berisi 25 dan halaman kedua berisi 1.
- [x] OpenAPI dan kedua salinan `API_DOCUMENTATION_COMPLETE.md` diselaraskan.
