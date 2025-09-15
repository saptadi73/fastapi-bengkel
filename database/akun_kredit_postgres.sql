-- PostgreSQL version of akun_kredit table and data
DROP TABLE IF EXISTS akun_kredit;
CREATE TABLE akun_kredit (
    no INTEGER PRIMARY KEY,
    nama VARCHAR(100),
    ket VARCHAR(255)
);
TRUNCATE TABLE akun_kredit RESTART IDENTITY;
INSERT INTO akun_kredit (no, nama, ket) VALUES
(1, 'BELANJA', 'PEMBELIAN BARANG, DLL'),
(2, 'ATK', 'ATK'),
(3, 'KONSUMSI', 'KONSUMSI'),
(4, 'TRANSPORT', 'TRANSPORT'),
(5, 'KASBON', 'KASBON STAF/KARYAWAN');
