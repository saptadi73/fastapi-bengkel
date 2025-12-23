import requests
import json
import uuid
import pytest

pytestmark = pytest.mark.integration

# Assuming the server is running on localhost:8000
base_url = 'http://localhost:8000'

# First, login to get a token
login_payload = {
    'username': 'admin',
    'password': 'csp2025!!'
}

login_response = requests.post(f'{base_url}/auth/login', json=login_payload)
if login_response.status_code != 200:
    print(f'Login failed: {login_response.status_code} - {login_response.text}')
    exit(1)

token = login_response.json()['data']['access_token']
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

# Generate a test workorder ID (this should be an existing one in your DB)
test_workorder_id = '453b177d-b404-45ae-907a-1ff8d58c2d9e'  # Use actual ID from DB

# Test payload for updating workorder with status_pembayaran
payload = {
    'tanggal_masuk': '2023-10-01T10:00:00',
    'tanggal_keluar': '2023-10-02T15:00:00',
    'keluhan': 'Test complaint',
    'kilometer': 100.0,
    'saran': 'Test suggestion',
    'status': 'selesai',
    'status_pembayaran': 'lunas',  # New field
    'dp': 10000.0,  # Add dp field
    'next_service_date': '2024-12-01',  # Add next_service_date
    'next_service_km': 200.0,  # Add next_service_km
    'total_discount': 0.0,
    'total_biaya': 50000.0,
    'pajak': 0.0,
    'customer_id': 'e7cc9352-2bdc-49a3-9f0c-80a935f15227',  # Use actual customer ID
    'vehicle_id': '6834d9fe-afd7-4853-b87a-a7ea43df2f3e',   # Use actual vehicle ID
    'karyawan_id': 'b089e1e8-45d3-48b5-9579-5c054a1d3487',  # Use actual karyawan ID
    'totalProductHarga': 40000.0,
    'totalProductDiscount': 0.0,
    'totalProductCost': 30000.0,
    'totalServiceHarga': 10000.0,
    'totalServiceDiscount': 0.0,
    'totalServiceCost': 5000.0,
    'product_ordered': [],
    'service_ordered': []
}

try:
    response = requests.post(f'{base_url}/workorders/update/workorderlengkap/{test_workorder_id}', json=payload, headers=headers)
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.json()}')
except Exception as e:
    print(f'Error: {e}')
