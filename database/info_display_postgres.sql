-- PostgreSQL version of info_display table and data
DROP TABLE IF EXISTS info_display;
CREATE TABLE info_display (
    no INTEGER PRIMARY KEY,
    txt_info VARCHAR(255)
);
TRUNCATE TABLE info_display RESTART IDENTITY;
INSERT INTO info_display (no, txt_info) VALUES
(1, 'Selamat Datang di BENGKEL MOBIL CARSPEED'),
(2, 'Booking Service, Silahkan WA. 0818279233'),
(3, 'Service nyaman hati senang'),
(4, ''),
(5, '');
