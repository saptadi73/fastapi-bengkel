"""
Script untuk create table manual_whatsapp
Jalankan: python database/create_manual_whatsapp_table.py
"""
from sqlalchemy import create_engine, inspect

from config import get_database_url
from models.database import Base
from models.manual_whatsapp import ManualWhatsApp


DATABASE_URL = get_database_url()


def create_table():
    """Create manual_whatsapp table"""
    engine = create_engine(DATABASE_URL)

    # Create table
    Base.metadata.create_all(bind=engine)

    print("Table 'manual_whatsapp' created successfully")

    inspector = inspect(engine)

    if "manual_whatsapp" in inspector.get_table_names():
        columns = inspector.get_columns("manual_whatsapp")
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")

    engine.dispose()


if __name__ == "__main__":
    create_table()
