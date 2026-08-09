from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from supabase_client import supabase

# auto_error=False so we can raise our own 401 with our own error shape,
# instead of FastAPI's default 403 "Not authenticated" response.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Access token required")

    token = credentials.credentials

    try:
        response = supabase.auth.get_user(token)
    except Exception:
        # Supabase raises on an invalid/expired/tampered token
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = getattr(response, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return user, token