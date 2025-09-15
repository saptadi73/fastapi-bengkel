-- PostgreSQL version of akun_kas table and data
DROP TABLE IF EXISTS akun_kas;
CREATE TABLE akun_kas (
    no INTEGER PRIMARY KEY,
    kode VARCHAR(20),
    jenis VARCHAR(20),
    kelompok VARCHAR(50),
    nama VARCHAR(100)
);
TRUNCATE TABLE akun_kas RESTART IDENTITY;
INSERT INTO akun_kas (no, kode, jenis, kelompok, nama) VALUES
(6, '', 'KREDIT', 'BEBAN', 'BENSIN'),
(7, '', 'KREDIT', 'BEBAN', 'BAUT'),
(9, '', 'KREDIT', 'BEBAN', 'BAYAR HUTANG'),
(14, '', 'KREDIT', 'BEBAN', 'CUCI'),
(15, '', 'KREDIT', 'BEBAN', 'AQUA'),
(16, '', 'KREDIT', 'BEBAN', 'ALAT'),
(17, '', 'KREDIT', 'BEBAN', 'PART'),
(32, '', 'KREDIT', 'BEBAN', 'CUSTOMER PINJAM'),
(55, '', 'KREDIT', 'BEBAN', 'BUBUT'),
(61, '', 'KREDIT', 'BEBAN', 'ROKOK'),
(62, '', 'KREDIT', 'BEBAN', 'TAMBAL BAN'),
(63, '', 'KREDIT', 'BEBAN', 'LAS'),
(66, '', 'KREDIT', 'BEBAN', 'IT SOFWARE'),
(71, '', 'KREDIT', 'BEBAN', 'SABUN COLEK'),
(80, '', 'KREDIT', 'BEBAN', 'APK ONLINE'),
(81, '', 'KREDIT', 'BEBAN', 'HANDLE  FREED'),
(82, '', 'KREDIT', 'BEBAN', 'PARKIR'),
(93, '', 'KREDIT', 'BEBAN', 'TOKEN LISTRIK'),
(94, '', 'KREDIT', 'BEBAN', 'UANG MAKAN');
