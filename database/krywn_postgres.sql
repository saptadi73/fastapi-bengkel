-- PostgreSQL version of krywn table and data
DROP TABLE IF EXISTS krywn;
CREATE TABLE krywn (
    no INTEGER PRIMARY KEY,
    id VARCHAR(30),
    tgl_input TIMESTAMP,
    tgl_update TIMESTAMP,
    tgl_masuk DATE,
    nama_lengkap VARCHAR(100),
    alamat VARCHAR(255),
    no_hp VARCHAR(30),
    jabatan VARCHAR(50),
    persen_jasa VARCHAR(10),
    persen_spr VARCHAR(10),
    tgt_unit VARCHAR(10),
    tgt_js VARCHAR(10),
    tgt_spr VARCHAR(10),
    cost_per_jam VARCHAR(20),
    officer VARCHAR(50)
);
TRUNCATE TABLE krywn RESTART IDENTITY;
-- INSERTs will be added next
