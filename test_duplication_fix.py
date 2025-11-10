#!/usr/bin/env python3
"""
Test script to verify the duplication fix in create_sales_journal_entry and create_sales_payment_journal_entry.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from models.database import SessionLocal
from schemas.service_accounting import SalesJournalEntry, SalesPaymentJournalEntry
from services.services_accounting import create_sales_journal_entry, create_sales_payment_journal_entry
from uuid import uuid4
from datetime import date

def test_duplication_prevention():
    """Test that duplicate journal entries are prevented."""
    db: Session = SessionLocal()
    try:
        # Get existing customer and workorder IDs from database
        from models.customer import Customer
        from models.workorder import Workorder

        customer = db.query(Customer).first()
        if not customer:
            print("❌ No customer found in database")
            return False

        workorder = db.query(Workorder).first()
        if not workorder:
            print("❌ No workorder found in database")
            return False

        workorder_id = workorder.id

        # Test data for sales journal
        sales_data = SalesJournalEntry(
            date=date.today(),
            memo="Test Sales Journal",
            customer_id=customer.id,
            workorder_id=workorder_id,
            harga_product=100000,
            harga_service=50000,
            hpp_product=80000,
            hpp_service=40000,
            pajak=15000
        )

        # Test data for payment journal
        payment_data = SalesPaymentJournalEntry(
            date=date.today(),
            memo="Test Payment Journal",
            customer_id=customer.id,
            workorder_id=workorder_id,
            amount=165000,  # 100k + 50k + 15k
            kas_bank_code="1001",
            piutang_code="2001"
        )

        print("Testing sales journal creation...")
        # First sales journal should succeed
        try:
            result1 = create_sales_journal_entry(db, sales_data)
            print("✅ First sales journal created successfully")
        except Exception as e:
            print(f"❌ Unexpected error on first sales journal: {e}")
            return False

        # Second sales journal should fail
        try:
            result2 = create_sales_journal_entry(db, sales_data)
            print("❌ Second sales journal was created - duplication not prevented!")
            return False
        except ValueError as e:
            if "already exists" in str(e):
                print("✅ Second sales journal correctly prevented")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")
            return False

        print("Testing payment journal creation...")
        # First payment journal should succeed
        try:
            result3 = create_sales_payment_journal_entry(db, payment_data)
            print("✅ First payment journal created successfully")
        except Exception as e:
            print(f"❌ Unexpected error on first payment journal: {e}")
            return False

        # Second payment journal should fail
        try:
            result4 = create_sales_payment_journal_entry(db, payment_data)
            print("❌ Second payment journal was created - duplication not prevented!")
            return False
        except ValueError as e:
            if "already exists" in str(e):
                print("✅ Second payment journal correctly prevented")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error type: {e}")
            return False

        print("Testing different workorders...")
        # Test with different workorder - should succeed
        different_workorder = db.query(Workorder).filter(Workorder.id != workorder_id).first()
        if not different_workorder:
            print("⚠️  Only one workorder in database, skipping different workorder test")
        else:
            different_workorder_id = different_workorder.id
            sales_data2 = SalesJournalEntry(
                date=date.today(),
                memo="Test Sales Journal 2",
                customer_id=customer.id,
                workorder_id=different_workorder_id,
                harga_product=50000,
                harga_service=25000,
                hpp_product=40000,
                hpp_service=20000,
                pajak=7500
            )

            try:
                result5 = create_sales_journal_entry(db, sales_data2)
                print("✅ Sales journal for different workorder created successfully")
            except Exception as e:
                print(f"❌ Unexpected error for different workorder: {e}")
                return False

        print("All tests passed! ✅")
        return True

    except Exception as e:
        print(f"❌ Test setup error: {e}")
        return False
    finally:
        db.rollback()  # Rollback any changes
        db.close()

if __name__ == "__main__":
    success = test_duplication_prevention()
    sys.exit(0 if success else 1)
