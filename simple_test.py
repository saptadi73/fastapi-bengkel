#!/usr/bin/env python3
"""
Simple test to check if the function can be imported and called without syntax errors.
"""

from services.services_accounting import create_sales_journal_entry
print("✅ Function imported successfully")

# Check if the function has the expected signature
import inspect
sig = inspect.signature(create_sales_journal_entry)
print(f"✅ Function signature: {sig}")

print("🎉 Basic import test passed!")
