import requests
import json
import uuid

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
test_workorder_id = str(uuid.uuid4())  # Replace with actual ID if known

# Test payload for updating workorder with status_pembayaran
payload = {
    'tanggal_masuk': '2023-10-01T10:00:00',
    'tanggal_keluar': '2023-10-02T15:00:00',
    'keluhan': 'Test complaint',
    'kilometer': 100.0,
    'saran': 'Test suggestion',
    'status': 'selesai',
    'status_pembayaran': 'lunas',  # New field
    'total_discount': 0.0,
    'total_biaya': 50000.0,
    'pajak': 0.0,
    'customer_id': str(uuid.uuid4()),  # Replace with actual customer ID
    'vehicle_id': str(uuid.uuid4()),   # Replace with actual vehicle ID
    'karyawan_id': str(uuid.uuid4()),  # Replace with actual karyawan ID
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
