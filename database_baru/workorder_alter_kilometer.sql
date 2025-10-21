-- Migration to add kilometer column to workorder table
ALTER TABLE workorder ADD COLUMN kilometer NUMERIC(10,2);
