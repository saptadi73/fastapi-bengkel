from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .jwt import decode_access_token
from supports.utils_json_response import error_response

bearer_scheme = HTTPBearer()

def jwt_required(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        return error_response(message="Invalid or expired token", status_code=401)
    return payload
