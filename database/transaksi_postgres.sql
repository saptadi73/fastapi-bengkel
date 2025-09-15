DROP TABLE IF EXISTS transaksi;
CREATE TABLE transaksi (
    id SERIAL PRIMARY KEY,
    tanggal DATE NOT NULL,
    waktu TIME NOT NULL,
    jenis VARCHAR(50) NOT NULL, -- e.g. 'penjualan', 'pembelian', 'service', etc.
    keterangan TEXT,
    jumlah NUMERIC(18,2) NOT NULL,
    metode_pembayaran VARCHAR(50),
    customer_id INTEGER,
    user_id INTEGER
);

-- Sample data
INSERT INTO transaksi (tanggal, waktu, jenis, keterangan, jumlah, metode_pembayaran, customer_id, user_id) VALUES
('2025-09-12', '10:15:00', 'penjualan', 'Penjualan sparepart', 150000.00, 'CASH', 1, 2),
('2025-09-12', '11:30:00', 'pembelian', 'Pembelian oli', 120000.00, 'TRANSFER', 2, 3),
('2025-09-12', '13:00:00', 'service', 'Service AC mobil', 350000.00, 'QRIS', 3, 2);
