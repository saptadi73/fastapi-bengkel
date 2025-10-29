"""
Script to run product_cost_history table migration
"""
import psycopg2
from models.database import URL_DATABASE
import sys

def run_migration():
    """Run the product_cost_history table migration"""
    
    # Read SQL file
    try:
        with open('database_baru/product_cost_history_postgres.sql', 'r') as f:
            sql_script = f.read()
    except FileNotFoundError:
        print("❌ Error: SQL file not found at database_baru/product_cost_history_postgres.sql")
        return False
    
    # Parse database URL
    # Format: postgresql://user:password@host:port/database
    try:
        # Extract connection details from SQLAlchemy URL
        db_url = URL_DATABASE.replace('postgresql+psycopg2://', '').replace('postgresql://', '')
        
        # Split user:password@host:port/database
        if '@' in db_url:
            user_pass, host_port_db = db_url.split('@')
            user, password = user_pass.split(':')
            host_port, database = host_port_db.split('/')
            host, port = host_port.split(':') if ':' in host_port else (host_port, '5432')
        else:
            print("❌ Error: Invalid database URL format")
            return False
        
        print(f"🔌 Connecting to database: {database} at {host}:{port}")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        print("📝 Running migration script...")
        
        # Execute SQL script
        cursor.execute(sql_script)
        
        print("✅ Migration completed successfully!")
        print("\n📊 Verifying table creation...")
        
        # Verify table was created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'product_cost_history'
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Table 'product_cost_history' created successfully")
            
            # Show table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'product_cost_history'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print("\n📋 Table structure:")
            print("-" * 60)
            for col in columns:
                print(f"  {col[0]:<25} {col[1]:<20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
            print("-" * 60)
        else:
            print("⚠️  Warning: Table not found after migration")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Product Cost History Table Migration")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    if success:
        print("✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("  1. Test the average costing functionality")
        print("  2. Create a Purchase Order and change status to 'diterima'")
        print("  3. Check cost history via API endpoints")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        print("\n💡 Troubleshooting:")
        print("  1. Check database connection in models/database.py")
        print("  2. Ensure PostgreSQL is running")
        print("  3. Verify database credentials")
        sys.exit(1)
