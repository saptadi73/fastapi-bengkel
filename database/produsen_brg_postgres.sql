-- PostgreSQL version of produsen_brg table and data
DROP TABLE IF EXISTS produsen_brg;
CREATE TABLE produsen_brg (
    no INTEGER PRIMARY KEY,
    produsen VARCHAR(100)
);
TRUNCATE TABLE produsen_brg RESTART IDENTITY;
INSERT INTO produsen_brg (no, produsen) VALUES
(1,'TOYOTA'),
(2,'DAIHATSU GENUINE PARTS'),
(3,'HONDA GENUINE OIL'),
(4,'FORTAG'),
(5,'SHELL'),
(6,'PRESTONE'),
(7,'AKEBONO'),
(8,'AISIN'),
(9,'JIMCO'),
(10,'MESRAN'),
(11,'DENSO PART'),
(12,'NGK'),
(13,'OTHER PARTS'),
(14,'OSRAM LAMP'),
(15,'STP CHEMICAL'),
(16,'ASPIRA'),
(17,'EXXON MOBIL'),
(18,'MASUMA'),
(19,'OTHER');
