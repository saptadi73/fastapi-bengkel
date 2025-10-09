from fastapi.responses import JSONResponse
import uuid
import decimal
import datetime

def to_dict(obj):
    result = {}
    for c in obj.__table__.columns:
        value = getattr(obj, c.name)
        # Konversi UUID ke string
        if isinstance(value, uuid.UUID):
            value = str(value)
        # Konversi Decimal ke float
        elif isinstance(value, decimal.Decimal):
            value = float(value)
        # Konversi datetime/date/time ke isoformat string
        elif isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
            value = value.isoformat()
        # Konversi bytes ke string (opsional, jika ada kolom bytes)
        elif isinstance(value, bytes):
            value = value.decode('utf-8')
        # Konversi Enum ke string
        elif hasattr(value, 'value'):
            value = value.value
        result[c.name] = value
    return result

def success_response(data=None, message="Success", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": message,
            "data": data
        }
    )

def error_response(message="Error", status_code=400, data=None):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "data": data
        }
    )
