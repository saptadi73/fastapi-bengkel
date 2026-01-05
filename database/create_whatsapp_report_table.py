"""
Script untuk membuat table whatsapp_report di database.
Table ini digunakan untuk tracking pengiriman WhatsApp ke customer dan vehicle.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Base, engine
from models.whatsapp_report import WhatsappReport
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_whatsapp_report_table():
    """
    Create table whatsapp_report jika belum ada.
    """
    try:
        # Create table menggunakan Base metadata
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Table 'whatsapp_report' created successfully")
        
        print("\nColumns:")
        for column in WhatsappReport.__table__.columns:
            print(f"  - {column.name}: {column.type}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Error creating table: {str(e)}")
        return False


if __name__ == "__main__":
    create_whatsapp_report_table()
