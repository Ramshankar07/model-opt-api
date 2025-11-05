from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import os


bearer = HTTPBearer(auto_error=False)
API_KEY = os.getenv("FEDERATED_API_KEY")


def require_api_key(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if API_KEY is None:
        return
    if not creds or creds.scheme.lower() != "bearer" or creds.credentials != API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

