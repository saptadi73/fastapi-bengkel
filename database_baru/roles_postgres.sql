-- Migration: CREATE TABLE roles and role_user sesuai model role.py dan role_user.py

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS role_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE
);

-- Insert initial roles
INSERT INTO roles (name) VALUES ('admin'), ('pegawai'), ('user') ON CONFLICT (name) DO NOTHING;
