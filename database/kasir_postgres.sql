-- PostgreSQL version of kasir table and data
DROP TABLE IF EXISTS kasir;
CREATE TABLE kasir (
    no INTEGER PRIMARY KEY,
    "user" VARCHAR(50),
    tgl DATE,
    jam TIME,
    saldo_awal VARCHAR(30),
    omzet VARCHAR(30),
    saldo_akhir VARCHAR(30),
    jam_str TIME
);
TRUNCATE TABLE kasir RESTART IDENTITY;
INSERT INTO kasir (no, "user", tgl, jam, saldo_awal, omzet, saldo_akhir, jam_str) VALUES
(1,'kasircs','2024-12-11','14:28:54','100000','0','100000','16:30:21'),
(2,'kasircs','2024-12-12','11:36:23','1000','0','1000','11:37:29'),
(3,'kasircs','2024-12-13','07:43:04','2121000','0','2121000','07:43:21'),
(4,'kasircs','2024-12-14','10:14:42','2258000','0','0','00:00:00'),
(5,'kasircs','2025-07-08','13:54:12','1','0','1','13:54:25');
