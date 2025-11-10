-- Truncate tables as requested
-- Note: Truncate with CASCADE to handle foreign key constraints
-- Execute this after all tables are created
-- Order: Child tables first, then parent tables to avoid foreign key violations

TRUNCATE TABLE public.journal_lines CASCADE;
TRUNCATE TABLE public.product_ordered CASCADE;
TRUNCATE TABLE public.service_ordered CASCADE;
TRUNCATE TABLE public.purchase_order_line CASCADE;
TRUNCATE TABLE public.product_line_packet_order CASCADE;
TRUNCATE TABLE public.service_line_packet_order CASCADE;
TRUNCATE TABLE public.inventory CASCADE;
TRUNCATE TABLE public.product_moved_history CASCADE;
TRUNCATE TABLE public.journal_entries CASCADE;
TRUNCATE TABLE public.workorder CASCADE;
TRUNCATE TABLE public.purchase_order CASCADE;
TRUNCATE TABLE public.packet_order CASCADE;
TRUNCATE TABLE public.expenses CASCADE;
