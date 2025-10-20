-- Migration for table attendance
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    karyawan_id UUID NOT NULL REFERENCES karyawan(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    check_in_time TIME,
    check_out_time TIME,
    status VARCHAR NOT NULL DEFAULT 'absent',
    notes VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index for performance
CREATE INDEX idx_attendance_karyawan_id ON attendance(karyawan_id);
CREATE INDEX idx_attendance_date ON attendance(date);
