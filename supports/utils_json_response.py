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
    # Normalize data (convert Decimal, UUID, datetime, Enum, SQLAlchemy models, etc.)
    def _normalize(value):
        # import here to avoid top-level heavy imports
        import uuid as _uuid
        import decimal as _decimal
        import datetime as _datetime
        from enum import Enum as _Enum

        # SQLAlchemy model instance -> convert via to_dict
        try:
            # detect SQLAlchemy declarative model by presence of __table__
            if hasattr(value, '__table__'):
                return to_dict(value)
        except Exception:
            pass

        if isinstance(value, _decimal.Decimal):
            return float(value)
        if isinstance(value, _uuid.UUID):
            return str(value)
        if isinstance(value, (_datetime.datetime, _datetime.date, _datetime.time)):
            return value.isoformat()
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except Exception:
                return str(value)
        # Enum -> return underlying value
        if isinstance(value, _Enum):
            return value.value
        # recurse for dicts and lists
        if isinstance(value, dict):
            return {k: _normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_normalize(v) for v in value]
        if isinstance(value, tuple):
            return tuple(_normalize(v) for v in value)

        return value

    normalized = _normalize(data)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success",
            "message": message,
            "data": normalized
        }
    )

def error_response(message="Error", status_code=400, data=None):
    # Normalize data similar to success_response to avoid JSON serialization issues
    def _normalize(value):
        import uuid as _uuid
        import decimal as _decimal
        import datetime as _datetime
        from enum import Enum as _Enum

        try:
            if hasattr(value, '__table__'):
                return to_dict(value)
        except Exception:
            pass

        if isinstance(value, _decimal.Decimal):
            return float(value)
        if isinstance(value, _uuid.UUID):
            return str(value)
        if isinstance(value, (_datetime.datetime, _datetime.date, _datetime.time)):
            return value.isoformat()
        if isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except Exception:
                return str(value)
        if isinstance(value, _Enum):
            return value.value
        if isinstance(value, dict):
            return {k: _normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_normalize(v) for v in value]
        if isinstance(value, tuple):
            return tuple(_normalize(v) for v in value)

        return value

    normalized = _normalize(data)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "data": normalized
        }
    )
