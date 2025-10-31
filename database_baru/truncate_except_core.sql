-- Truncate all tables in public schema except specific core tables
-- Excluded tables: users, accounts, supplier, customer
-- Database: PostgreSQL

DO $$
DECLARE
    r RECORD;
    excluded_tables TEXT[] := ARRAY['users', 'accounts', 'supplier', 'customer'];
    stmts TEXT := '';
BEGIN
    -- Build TRUNCATE statements for all non-excluded tables in schema public
    FOR r IN
        SELECT c.relname AS table_name
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind = 'r' -- ordinary tables
          AND n.nspname = 'public'
          AND c.relname <> ALL (excluded_tables)
    LOOP
        stmts := stmts || format('TRUNCATE TABLE %I.%I CASCADE;', 'public', r.table_name) || chr(10);
    END LOOP;

    IF stmts <> '' THEN
        RAISE NOTICE 'Executing:%', chr(10) || stmts;
        EXECUTE stmts;
    ELSE
        RAISE NOTICE 'No tables to truncate (all tables are excluded).';
    END IF;
END $$;