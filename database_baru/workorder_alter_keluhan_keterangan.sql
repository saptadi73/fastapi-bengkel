-- Migrasi untuk workorder: tambah kolom keterangan dan ubah keluhan menjadi NOT NULL

ALTER TABLE workorder ADD COLUMN keterangan VARCHAR;
ALTER TABLE workorder ALTER COLUMN keluhan SET NOT NULL;
