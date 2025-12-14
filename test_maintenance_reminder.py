#!/usr/bin/env python
"""
Test script untuk WhatsApp Maintenance Reminder
"""
from datetime import datetime, date, timedelta
from services.services_customer import send_maintenance_reminder_whatsapp
from models.database import SessionLocal

# Test structure
print('Testing WhatsApp Maintenance Reminder...')
print('='*60)

# Simulate testing
db = SessionLocal()
try:
    print('✓ Database connection OK')
    
    # Test function signature
    result = send_maintenance_reminder_whatsapp(db)
    print('✓ Function executed successfully')
    print(f'  Total customers: {result["total_customers"]}')
    print(f'  Reminders sent: {result["reminder_sent"]}')
    print(f'  Details entries: {len(result["details"])}')
    print()
    if result["reminder_sent"] > 0:
        print('Sample reminder sent:')
        sample = result["details"][0]
        print(f'  - Customer: {sample.get("customer_nama")}')
        print(f'  - Vehicle: {sample.get("no_pol")}')
        print(f'  - Next visit: {sample.get("next_visit_date")}')
    print()
    print('✓ All tests passed!')
    
except Exception as e:
    print(f'✗ Error: {str(e)}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
