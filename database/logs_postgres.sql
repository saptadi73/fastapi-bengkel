-- PostgreSQL version of logs table and data
DROP TABLE IF EXISTS logs;
CREATE TABLE logs (
    no INTEGER PRIMARY KEY,
    menu VARCHAR(50),
    rincian VARCHAR(255),
    aksi VARCHAR(50),
    officer VARCHAR(50)
);
TRUNCATE TABLE logs RESTART IDENTITY;
INSERT INTO logs (no, menu, rincian, aksi, officer) VALUES
(1,'USER','2025-08-01 03:32:54|sa1cs|666555|125.163.158.237','LOGIN','sa1cs'),
(2,'USER','2025-08-01 03:47:26|admin|iwan0707|182.253.126.6','LOGIN','admin'),
(3,'USER','2025-08-01 05:59:57|admin2|666555|125.163.158.237','LOGIN','admin2'),
(4,'USER','2025-08-01 06:45:15|admin|iwan0707|125.163.158.237','LOGIN','admin'),
(5,'USER','2025-08-01 07:07:56|admin|iwan0707|125.163.158.237','LOGIN','admin'),
(6,'USER','2025-08-01 17:00:05||125.163.158.237','LOGOUT',''),
(7,'USER','2025-08-01 10:00:10|admin2|666555|125.163.158.237','LOGIN','admin2'),
(8,'USER','2025-08-01 10:22:41|admin|iwan0707|182.253.126.6','LOGIN','admin'),
(9,'USER','2025-08-02 00:28:53|admin|iwan0707|182.253.126.6','LOGIN','admin'),
(10,'USER','2025-08-02 01:16:31|admin2|666555|125.163.158.237','LOGIN','admin2'),
(11,'USER','2025-08-02 01:22:13|sa1cs|666555|125.163.158.237','LOGIN','sa1cs');
-- Lanjutkan data sesuai file sumber
