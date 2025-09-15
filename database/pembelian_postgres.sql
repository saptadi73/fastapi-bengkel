-- PostgreSQL version of pembelian table and data
DROP TABLE IF EXISTS pembelian;
CREATE TABLE pembelian (
    no INTEGER PRIMARY KEY,
    invoice VARCHAR(50),
    no_faktur VARCHAR(50),
    tgl_faktur DATE,
    sis_byr VARCHAR(50),
    tgl_jth_tmp VARCHAR(50),
    salesman VARCHAR(50),
    barcode VARCHAR(50),
    kode_brg VARCHAR(50),
    id_part VARCHAR(50),
    waktu TIMESTAMP,
    waktu_update VARCHAR(50),
    nama_barang VARCHAR(255),
    satuan_brg VARCHAR(20),
    jenis VARCHAR(20),
    suplier VARCHAR(100),
    kode_suplier VARCHAR(50),
    alamat_suplier VARCHAR(255),
    harga_beli NUMERIC,
    qty_awal NUMERIC,
    qty_add NUMERIC,
    subtotal NUMERIC,
    ttl_diskon NUMERIC,
    ttl_dpp NUMERIC,
    ttl_ppn NUMERIC,
    ttl_nett NUMERIC,
    "user" VARCHAR(50)
);
TRUNCATE TABLE pembelian RESTART IDENTITY;
INSERT INTO pembelian (no, invoice, no_faktur, tgl_faktur, sis_byr, tgl_jth_tmp, salesman, barcode, kode_brg, id_part, waktu, waktu_update, nama_barang, satuan_brg, jenis, suplier, kode_suplier, alamat_suplier, harga_beli, qty_awal, qty_add, subtotal, ttl_diskon, ttl_dpp, ttl_ppn, ttl_nett, "user") VALUES
(1,'IS-00001','-','0000-00-00','','0000-00-00','','04478-BZ060','S00001','CYLINDER K','2024-12-11 07:29:16','0000-00-00','CYLINDER KIT FR BRAKE 04478-BZ060 TOYOTA','Pcs','PART','CARFIX','','','188397',0,1,'188397',0,0,0,0,'KOSWARA'),
(2,'IS-00001','-','0000-00-00','','0000-00-00','','04478-BZ170','S00002','CYLINDER K','2024-12-11 07:29:16','0000-00-00','CYLINDER KIT FR BRAKE 04478-BZ170 TOYOTA','Pcs','PART','CARFIX','','','224504',0,1,'224504',0,0,0,0,'KOSWARA'),
(3,'IS-00001','-','0000-00-00','','0000-00-00','','04495-BZ100-008','S00003','','2024-12-11 07:29:16','0000-00-00','BRAKE SHOE 04495-BZ100-008 DAIHATSU','Pcs','PART','CARFIX','','','151591',0,1,'151591',0,0,0,0,'KOSWARA'),
(4,'IS-00001','-','0000-00-00','','0000-00-00','','04495-BZ111','S00004','BRAKE SHOE','2024-12-11 07:29:16','0000-00-00','BRAKE SHOE 04495-BZ111 TOYOTA','Pcs','PART','CARFIX','','','168378',0,1,'168378',0,0,0,0,'KOSWARA'),
(5,'IS-00001','-','0000-00-00','','0000-00-00','','04495-BZ121','S00005','BRAKE SHOE','2024-12-11 07:29:16','0000-00-00','BRAKE SHOE 04495-BZ121 TOYOTA','Pcs','PART','CARFIX','','','344774',0,1,'344774',0,0,0,0,'KOSWARA'),
(6,'IS-00001','-','0000-00-00','','0000-00-00','','04495-YZZD1','S00006','BRAKE SHOE','2024-12-11 07:29:16','0000-00-00','BRAKE SHOE RR 04495-YZZD1 TOYOTA','Pcs','PART','CARFIX','','','220496',0,1,'220496',0,0,0,0,'KOSWARA'),
(7,'IS-00001','-','0000-00-00','','0000-00-00','','04495-YZZQ1','S00007','BRAKE SHOE','2024-12-11 07:29:16','0000-00-00','BRAKE SHOE 04495-YZZQ1 TOYOTA','Pcs','PART','CARFIX','','','180406',0,1,'180406',0,0,0,0,'KOSWARA'),
(8,'IS-00001','-','0000-00-00','','0000-00-00','','08267-P99-01ZS1','S00008','HONDA','2024-12-11 07:29:16','0000-00-00','OIL TRANS M/T FLUID 1LT HONDA','Pcs','OIL','CARFIX','','','67110',0,2,'134220',0,0,0,0,'KOSWARA'),
(9,'IS-00001','-','0000-00-00','','0000-00-00','','08268-P991BS1','S00009','HONDA','2024-12-11 07:29:16','0000-00-00','OIL TRANS A/T DW-1 1LT HONDA','Pcs','OIL','CARFIX','','','87236',0,4,'348944',0,0,0,0,'KOSWARA'),
(10,'IS-00001','-','0000-00-00','','0000-00-00','','08269-P9908ZB3','S00010','HONDA','2024-12-11 07:29:16','0000-00-00','OIL TRANS A/T CVT-F 3.5LT HONDA','Pcs','OIL','CARFIX','','','349025',0,1,'349025',0,0,0,0,'KOSWARA');
-- Lanjutkan data sesuai file sumber
