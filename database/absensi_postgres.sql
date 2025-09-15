-- PostgreSQL version of absensi table and data
-- Table definition
DROP TABLE IF EXISTS absensi;
CREATE TABLE absensi (
    no INTEGER PRIMARY KEY,
    id_krywn VARCHAR(20),
    nama_krywn VARCHAR(100),
    tgl_absen DATE,
    jam_update TIME
);

-- Truncate table (optional, for restore)
TRUNCATE TABLE absensi RESTART IDENTITY;

-- Data insert (example, first 10 rows)
INSERT INTO absensi (no, id_krywn, nama_krywn, tgl_absen, jam_update) VALUES
(1, '241128001', 'ANDI', '2024-12-12', '20:58:02'),
(2, '241128003', 'DAVA', '2024-12-12', '20:58:02'),
(3, '241211004', 'DICKY', '2024-12-12', '20:58:02'),
(4, '241128002', 'EGA', '2024-12-12', '20:58:02'),
(5, '241128001', 'ANDI', '2024-12-13', '12:52:48'),
(6, '241128003', 'DAVA', '2024-12-13', '12:52:48'),
(7, '241211004', 'DICKY', '2024-12-13', '12:52:48'),
(8, '241128002', 'EGA', '2024-12-13', '12:52:48'),
(9, '241128001', 'ANDI', '2024-12-17', '17:40:46'),
(10, '241128003', 'DAVA', '2024-12-17', '17:40:46');
-- Lanjutkan untuk seluruh data lain dengan format yang sama
