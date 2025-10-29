"""
Migration script to add consignment fields to product table.
Run this script to update your existing database with consignment functionality.

Usage:
    python run_consignment_migration.py
"""

from models.database import engine
from sqlalchemy import text
import sys

def run_migration():
    """Execute the consignment migration SQL script."""
    
    migration_sql = """
    -- Migration to add consignment fields to product table
    
    -- Add supplier_id column if it doesn't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'product' AND column_name = 'supplier_id'
        ) THEN
            ALTER TABLE product ADD COLUMN supplier_id UUID REFERENCES supplier(id);
            RAISE NOTICE 'Column supplier_id added to product table';
        ELSE
            RAISE NOTICE 'Column supplier_id already exists in product table';
        END IF;
    END $$;
    
    -- Add is_consignment column if it doesn't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'product' AND column_name = 'is_consignment'
        ) THEN
            ALTER TABLE product ADD COLUMN is_consignment BOOLEAN NOT NULL DEFAULT FALSE;
            RAISE NOTICE 'Column is_consignment added to product table';
        ELSE
            RAISE NOTICE 'Column is_consignment already exists in product table';
        END IF;
    END $$;
    
    -- Add consignment_commission column if it doesn't exist
    DO $$ 
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'product' AND column_name = 'consignment_commission'
        ) THEN
            ALTER TABLE product ADD COLUMN consignment_commission NUMERIC(10,2);
            RAISE NOTICE 'Column consignment_commission added to product table';
        ELSE
            RAISE NOTICE 'Column consignment_commission already exists in product table';
        END IF;
    END $$;
    
    -- Create index on supplier_id for better query performance
    CREATE INDEX IF NOT EXISTS idx_product_supplier_id ON product(supplier_id);
    
    -- Create index on is_consignment for filtering consignment products
    CREATE INDEX IF NOT EXISTS idx_product_is_consignment ON product(is_consignment);
    """
    
    try:
        print("=" * 60)
        print("CONSIGNMENT MIGRATION SCRIPT")
        print("=" * 60)
        print("\nStarting migration to add consignment fields to product table...")
        print("\nThis will add the following columns:")
        print("  - supplier_id (UUID, nullable)")
        print("  - is_consignment (BOOLEAN, default FALSE)")
        print("  - consignment_commission (NUMERIC(10,2), nullable)")
        print("\nAnd create indexes for better performance.")
        print("\n" + "=" * 60)
        
        # Confirm before proceeding
        response = input("\nDo you want to proceed with the migration? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("\nMigration cancelled by user.")
            sys.exit(0)
        
        print("\nExecuting migration...")
        
        with engine.connect() as conn:
            # Execute the migration SQL
            conn.execute(text(migration_sql))
            conn.commit()
            
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nThe following changes have been applied:")
        print("  ✓ supplier_id column added/verified")
        print("  ✓ is_consignment column added/verified")
        print("  ✓ consignment_commission column added/verified")
        print("  ✓ Indexes created for performance")
        print("\nYou can now use consignment product features!")
        print("\nNext steps:")
        print("  1. Verify the changes in your database")
        print("  2. Test creating a consignment product")
        print("  3. Review CONSIGNMENT_IMPLEMENTATION_SUMMARY.md for usage")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ MIGRATION FAILED!")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nPlease check:")
        print("  1. Database connection is working")
        print("  2. You have necessary permissions")
        print("  3. The supplier table exists")
        print("  4. Review the error message above")
        print("\n" + "=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
