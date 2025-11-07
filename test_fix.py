#!/usr/bin/env python3
"""
Minimal test script to verify the create_sales_journal_entry fix.
This script mocks the database session to avoid needing a real DB connection.
"""

from decimal import Decimal
from datetime import date
from unittest.mock import MagicMock, patch
import uuid

# Import the function to test
from services.services_accounting import create_sales_journal_entry
from schemas.service_accounting import SalesJournalEntry


def test_create_sales_journal_entry_with_consignment():
    """
    Test that create_sales_journal_entry handles consignment products without nested transaction errors.
    """
    # Mock the database session
    db = MagicMock()

    # Mock Workorder query
    mock_workorder = MagicMock()
    mock_workorder.id = uuid.uuid4()

    # Mock ProductOrdered
    mock_po = MagicMock()
    mock_po.quantity = Decimal("2")
    mock_product = MagicMock()
    mock_product.is_consignment = True
    mock_product.consignment_commission = Decimal("50.00")
    mock_product.supplier_id = uuid.uuid4()
    mock_po.product = mock_product
    mock_workorder.product_ordered = [mock_po]

    # Mock Account queries
    mock_acc_piutang = MagicMock()
    mock_acc_piutang.id = uuid.uuid4()
    mock_acc_piutang.code = "2001"

    mock_acc_penjualan = MagicMock()
    mock_acc_penjualan.id = uuid.uuid4()
    mock_acc_penjualan.code = "4001"

    mock_acc_ppn = MagicMock()
    mock_acc_ppn.id = uuid.uuid4()
    mock_acc_ppn.code = "2410"

    mock_acc_commission = MagicMock()
    mock_acc_commission.id = uuid.uuid4()
    mock_acc_commission.code = "6003"

    mock_acc_payable = MagicMock()
    mock_acc_payable.id = uuid.uuid4()
    mock_acc_payable.code = "3002"

    # Mock select and scalar_one_or_none
    def mock_select_account(code):
        if code == "2001":
            return mock_acc_piutang
        elif code == "4001":
            return mock_acc_penjualan
        elif code == "2410":
            return mock_acc_ppn
        elif code == "6003":
            return mock_acc_commission
        elif code == "3002":
            return mock_acc_payable
        return None

    # Mock db.execute for select(Account)
    db.execute.return_value.scalar_one_or_none.side_effect = mock_select_account

    # Mock db.query for Workorder
    db.query.return_value.filter.return_value.first.return_value = mock_workorder

    # Mock JournalEntry and JournalLine
    mock_sale_entry = MagicMock()
    mock_sale_entry.id = uuid.uuid4()
    mock_sale_entry.entry_no = "SAL-20231201-001"
    mock_sale_entry.date = date.today()
    mock_sale_entry.memo = "Test Sale"
    mock_sale_entry.lines = []

    mock_cons_entry = MagicMock()
    mock_cons_entry.id = uuid.uuid4()
    mock_cons_entry.entry_no = "CONS-abc123"
    mock_cons_entry.date = date.today()
    mock_cons_entry.memo = "Test Consignment"
    mock_cons_entry.lines = []

    # Mock _create_entry to return the mock entries
    with patch('services.services_accounting._create_entry') as mock_create_entry:
        mock_create_entry.return_value = mock_sale_entry

        # Mock JournalEntry constructor
        with patch('services.services_accounting.JournalEntry') as mock_je_class:
            mock_je_class.return_value = mock_cons_entry

            # Mock JournalLine constructor
            with patch('services.services_accounting.JournalLine') as mock_jl_class:
                # Mock db.add, db.flush, db.commit
                db.add.return_value = None
                db.flush.return_value = None
                db.commit.return_value = None

                # Mock _to_entry_out
                with patch('services.services_accounting._to_entry_out') as mock_to_entry_out:
                    mock_to_entry_out.return_value = {"id": "test", "entry_no": "test"}

                    # Create test data
                    data_entry = SalesJournalEntry(
                        date=date.today(),
                        memo="Test Sale with Consignment",
                        customer_id=uuid.uuid4(),
                        workorder_id=mock_workorder.id,
                        harga_product=Decimal("1000.00"),
                        harga_service=Decimal("0.00"),
                        hpp_product=Decimal("600.00"),
                        hpp_service=Decimal("0.00"),
                        pajak=Decimal("0.00")
                    )

                    # Call the function
                    try:
                        result = create_sales_journal_entry(db, data_entry)
                        print("✅ Function executed successfully without transaction errors")
                        print(f"Result keys: {list(result.keys())}")
                        assert "sale" in result
                        assert "consignments" in result
                        print("✅ Result structure is correct")
                        return True
                    except Exception as e:
                        print(f"❌ Function failed with error: {e}")
                        return False


if __name__ == "__main__":
    print("Testing create_sales_journal_entry fix...")
    success = test_create_sales_journal_entry_with_consignment()
    if success:
        print("\n🎉 Test passed! The fix appears to work correctly.")
    else:
        print("\n💥 Test failed! The fix needs more work.")
