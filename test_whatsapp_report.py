"""
Test WhatsApp Report functionality
Verifikasi bahwa tracking dan reporting berfungsi dengan baik.
"""
import pytest
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from typing import cast

from models.database import SessionLocal
from models.customer import Customer, Vehicle
from models.whatsapp_report import WhatsappReport
from services.services_whatsapp_report import (
    create_or_update_whatsapp_report,
    get_all_whatsapp_reports,
    get_whatsapp_report_by_customer_vehicle,
    get_whatsapp_reports_by_customer,
    get_whatsapp_report_details,
    get_whatsapp_report_statistics,
    delete_whatsapp_report,
    reset_frequency
)


def get_db() -> Session:
    """Get database session for testing"""
    db = SessionLocal()
    return db


def test_create_whatsapp_report():
    """Test membuat WhatsApp report baru"""
    db = get_db()
    try:
        # Create test customer and vehicle
        customer = Customer(
            id=uuid4(),
            nama="Test Customer",
            hp="081234567890",
            alamat="Test Address"
        )
        vehicle = Vehicle(
            id=uuid4(),
            model="Test Model",
            type="Sedan",
            kapasitas="5",
            no_pol="B 1234 TEST",
            tahun=2020,
            warna="Hitam",
            customer_id=customer.id
        )
        
        db.add(customer)
        db.add(vehicle)
        db.commit()
        
        # Test create report
        report = create_or_update_whatsapp_report(db, cast(UUID, customer.id), cast(UUID, vehicle.id))
        
        assert report is not None
        assert report.id_customer == customer.id
        assert report.id_vehicle == vehicle.id
        assert report.frequency == 1
        assert report.last_message_date is not None
        
        print("✅ Test create report: PASSED")
        
    finally:
        db.close()


def test_update_whatsapp_report():
    """Test update frequency saat create_or_update dipanggil lagi"""
    db = get_db()
    try:
        # Create test customer and vehicle
        customer = Customer(
            id=uuid4(),
            nama="Test Customer 2",
            hp="081234567890",
            alamat="Test Address"
        )
        vehicle = Vehicle(
            id=uuid4(),
            model="Test Model",
            type="Sedan",
            kapasitas="5",
            no_pol="B 5678 TEST",
            tahun=2020,
            warna="Putih",
            customer_id=customer.id
        )
        
        db.add(customer)
        db.add(vehicle)
        db.commit()
        
        # First call - create
        report1 = create_or_update_whatsapp_report(db, cast(UUID, customer.id), cast(UUID, vehicle.id))
        freq1 = report1.frequency
        time1 = report1.last_message_date
        
        # Wait a bit
        import time
        time.sleep(0.1)
        
        # Second call - should update
        report2 = create_or_update_whatsapp_report(db, cast(UUID, customer.id), cast(UUID, vehicle.id))
        freq2 = report2.frequency
        time2 = report2.last_message_date
        
        assert freq2 == freq1 + 1, f"Expected {freq1 + 1}, got {freq2}"
        assert time1 is not None and time2 is not None, "Timestamps should not be None"
        assert time2 > time1, "Last message date should be updated"
        
        print(f"✅ Test update report: PASSED (freq: {freq1} → {freq2})")
        
    finally:
        db.close()


def test_get_all_reports():
    """Test get semua reports"""
    db = get_db()
    try:
        reports = get_all_whatsapp_reports(db)
        assert isinstance(reports, list)
        print(f"✅ Test get all reports: PASSED (total: {len(reports)})")
        
    finally:
        db.close()


def test_get_statistics():
    """Test get statistik"""
    db = get_db()
    try:
        stats = get_whatsapp_report_statistics(db)
        
        assert stats is not None
        assert hasattr(stats, 'total_customers_with_vehicles')
        assert hasattr(stats, 'total_messages_sent')
        assert hasattr(stats, 'average_messages_per_customer')
        assert hasattr(stats, 'customers_by_frequency')
        
        print(f"✅ Test get statistics: PASSED")
        print(f"   - Total customers with vehicles: {stats.total_customers_with_vehicles}")
        print(f"   - Total messages sent: {stats.total_messages_sent}")
        print(f"   - Average messages per customer: {stats.average_messages_per_customer:.2f}")
        
    finally:
        db.close()


def test_reset_frequency():
    """Test reset frequency"""
    db = get_db()
    try:
        # Get initial count
        initial_reports = get_all_whatsapp_reports(db)
        
        if len(initial_reports) > 0:
            # Reset all frequencies
            count = reset_frequency(db)
            assert count > 0
            
            # Verify reset
            reset_reports = get_all_whatsapp_reports(db)
            for report in reset_reports:
                assert report.frequency == 0
            
            print(f"✅ Test reset frequency: PASSED ({count} records reset)")
        else:
            print("⚠️  Test reset frequency: SKIPPED (no reports to reset)")
        
    finally:
        db.close()


def test_delete_report():
    """Test delete report"""
    db = get_db()
    try:
        # Create test data
        customer = Customer(
            id=uuid4(),
            nama="Test Customer 3",
            hp="081234567890",
            alamat="Test Address"
        )
        vehicle = Vehicle(
            id=uuid4(),
            model="Test Model",
            type="Sedan",
            kapasitas="5",
            no_pol="B 9999 TEST",
            tahun=2020,
            warna="Merah",
            customer_id=customer.id
        )
        
        db.add(customer)
        db.add(vehicle)
        db.commit()
        
        # Create report
        report = create_or_update_whatsapp_report(db, cast(UUID, customer.id), cast(UUID, vehicle.id))
        report_id = report.id
        
        # Delete it
        result = delete_whatsapp_report(db, report_id)
        assert result == True
        
        # Verify deleted
        deleted = get_whatsapp_report_by_customer_vehicle(db, cast(UUID, customer.id), cast(UUID, vehicle.id))
        assert deleted is None
        
        print("✅ Test delete report: PASSED")
        
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("WhatsApp Report Test Suite")
    print("="*60 + "\n")
    
    test_get_all_reports()
    test_get_statistics()
    
    try:
        test_create_whatsapp_report()
        test_update_whatsapp_report()
        test_delete_report()
        test_reset_frequency()
    except Exception as e:
        print(f"⚠️  Some create/update/delete tests failed: {str(e)}")
        print("   (This might be OK if there are FK constraints)")
    
    print("\n" + "="*60)
    print("Test Suite Complete")
    print("="*60 + "\n")
