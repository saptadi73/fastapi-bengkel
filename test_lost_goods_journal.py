import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.accounting import Base, Account
from models.workorder import Product
from services.services_accounting import create_lost_goods_journal_entry
from schemas.service_accounting import LostGoodsJournalEntry

# Create in-memory SQLite database for testing
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_test_accounts_and_product(db):
    # Create test accounts
    # Loss account (Kerugian Barang)
    acc1 = Account(id=uuid.uuid4(), code="6003", name="Kerugian Barang", normal_balance="debit", account_type="expense", is_active=True)
    db.add(acc1)
    # Inventory account (Persediaan Barang)
    acc2 = Account(id=uuid.uuid4(), code="2002", name="Persediaan Barang", normal_balance="debit", account_type="asset", is_active=True)
    db.add(acc2)

    # Create a test product with cost
    product_id = uuid.uuid4()
    product = Product(
        id=product_id,
        name="Test Product",
        type="sparepart",
        description="Test product for lost goods",
        price=Decimal("10000.00"),
        cost=Decimal("8000.00"),
        min_stock=Decimal("10.00"),
        brand_id=None,
        satuan_id=None,
        category_id=None
    )
    db.add(product)
    db.commit()
    return product_id

def test_create_lost_goods_journal_entry():
    # Test data - main functionality
    engine1 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine1)
    SessionLocal1 = sessionmaker(autocommit=False, autoflush=False, bind=engine1)
    db = SessionLocal1()
    product_id = create_test_accounts_and_product(db)

    data = LostGoodsJournalEntry(
        date=date.today(),
        memo="Test lost goods",
        product_id=product_id,
        quantity=Decimal("5.00"),
        loss_account_code="6003",
        inventory_account_code="2002"
    )

    try:
        entry = create_lost_goods_journal_entry(db, data)
        print("Test passed: Lost goods journal entry created successfully")
        print(f"Entry No: {entry['entry_no']}")
        print(f"Total Lines: {len(entry['lines'])}")
        total_debit = sum(line['debit'] for line in entry['lines'])
        total_credit = sum(line['credit'] for line in entry['lines'])
        print(f"Total Debit: {total_debit}, Total Credit: {total_credit}")
        assert total_debit == total_credit, "Journal not balanced"
        # Check amount calculation: cost * quantity = 8000 * 5 = 40000
        expected_amount = Decimal("40000.00")
        assert total_debit == expected_amount, f"Expected debit {expected_amount}, got {total_debit}"
        print("Amount calculation and balance check passed")
    except Exception as e:
        print(f"Test failed: {e}")
        db.close()
        return False

    db.close()

    # Test edge case: invalid product_id
    engine2 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine2)
    SessionLocal2 = sessionmaker(autocommit=False, autoflush=False, bind=engine2)
    db2 = SessionLocal2()
    create_test_accounts_and_product(db2)
    invalid_data = LostGoodsJournalEntry(
        date=date.today(),
        memo="Test invalid product",
        product_id=uuid.uuid4(),  # Invalid ID
        quantity=Decimal("1.00"),
        loss_account_code="6003",
        inventory_account_code="2002"
    )

    try:
        create_lost_goods_journal_entry(db2, invalid_data)
        print("Test failed: Should have raised ValueError for invalid product_id")
        db2.close()
        return False
    except ValueError as e:
        if "not found" in str(e):
            print("Test passed: Correctly raised ValueError for invalid product_id")
        else:
            print(f"Test failed: Unexpected error: {e}")
            db2.close()
            return False
    except Exception as e:
        print(f"Test failed: Unexpected exception: {e}")
        db2.close()
        return False

    db2.close()

    # Test edge case: product without cost
    engine3 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine3)
    SessionLocal3 = sessionmaker(autocommit=False, autoflush=False, bind=engine3)
    db3 = SessionLocal3()
    # Create accounts
    acc1 = Account(id=uuid.uuid4(), code="6003", name="Kerugian Barang", normal_balance="debit", account_type="expense", is_active=True)
    db3.add(acc1)
    acc2 = Account(id=uuid.uuid4(), code="2002", name="Persediaan Barang", normal_balance="debit", account_type="asset", is_active=True)
    db3.add(acc2)
    # Create product without cost
    product_id_no_cost = uuid.uuid4()
    product_no_cost = Product(
        id=product_id_no_cost,
        name="Test Product No Cost",
        type="sparepart",
        description="Test product without cost",
        price=Decimal("10000.00"),
        cost=None,
        min_stock=Decimal("10.00"),
        brand_id=None,
        satuan_id=None,
        category_id=None
    )
    db3.add(product_no_cost)
    db3.commit()

    no_cost_data = LostGoodsJournalEntry(
        date=date.today(),
        memo="Test no cost",
        product_id=product_id_no_cost,
        quantity=Decimal("1.00"),
        loss_account_code="6003",
        inventory_account_code="2002"
    )

    try:
        create_lost_goods_journal_entry(db3, no_cost_data)
        print("Test failed: Should have raised ValueError for missing cost")
        db3.close()
        return False
    except ValueError as e:
        if "does not have a cost defined" in str(e):
            print("Test passed: Correctly raised ValueError for missing cost")
        else:
            print(f"Test failed: Unexpected error: {e}")
            db3.close()
            return False
    except Exception as e:
        print(f"Test failed: Unexpected exception: {e}")
        db3.close()
        return False

    db3.close()

    # Test edge case: zero quantity
    engine4 = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine4)
    SessionLocal4 = sessionmaker(autocommit=False, autoflush=False, bind=engine4)
    db4 = SessionLocal4()
    product_id_zero = create_test_accounts_and_product(db4)

    zero_quantity_data = LostGoodsJournalEntry(
        date=date.today(),
        memo="Test zero quantity",
        product_id=product_id_zero,
        quantity=Decimal("0.00"),
        loss_account_code="6003",
        inventory_account_code="2002"
    )

    try:
        create_lost_goods_journal_entry(db4, zero_quantity_data)
        print("Test failed: Should have raised ValueError for zero quantity")
        db4.close()
        return False
    except ValueError as e:
        if "must be positive" in str(e):
            print("Test passed: Correctly raised ValueError for zero quantity")
        else:
            print(f"Test failed: Unexpected error: {e}")
            db4.close()
            return False
    except Exception as e:
        print(f"Test failed: Unexpected exception: {e}")
        db4.close()
        return False

    db4.close()

    return True

if __name__ == "__main__":
    success = test_create_lost_goods_journal_entry()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
