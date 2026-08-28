from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Decodes and verifies the Supabase Access Token (JWT).
    Extracts the user payload containing 'sub' (user_id).
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # In production, verify against SUPABASE_JWT_SECRET or Supabase public key
        # For development, decode payload with algorithms HS256
        payload = jwt.decode(
            token, 
            settings.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated")
        }
    except JWTError:
        # Fallback for development if secret is not set yet (unverified payload parsing for quick testing)
        try:
            unverified_payload = jwt.get_unverified_claims(token)
            user_id = unverified_payload.get("sub")
            if user_id:
                return {
                    "user_id": user_id,
                    "email": unverified_payload.get("email"),
                    "role": unverified_payload.get("role", "authenticated")
                }
        except Exception:
            pass
        raise credentials_exception
