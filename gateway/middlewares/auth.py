from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from config import settings

security = HTTPBearer()


class TokenPayload(BaseModel):
    user_id: int
    username: str
    email: str
    is_staff: bool = False


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(
            user_id=payload.get("user_id", 0),
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            is_staff=payload.get("is_staff", False),
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
) -> TokenPayload | None:
    if credentials is None:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return TokenPayload(
            user_id=payload.get("user_id", 0),
            username=payload.get("username", ""),
            email=payload.get("email", ""),
            is_staff=payload.get("is_staff", False),
        )
    except JWTError:
        return None


async def require_admin(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
