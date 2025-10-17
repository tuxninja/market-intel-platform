"""
Temporary debug endpoint for JWT token validation.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.services.auth import AuthService

router = APIRouter()


class DebugTokenRequest(BaseModel):
    token: str


@router.post("/token")
async def debug_token(request: DebugTokenRequest):
    """Debug JWT token validation."""
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return {
            "success": True,
            "payload": payload,
            "secret_key_length": len(settings.SECRET_KEY),
            "algorithm": settings.ALGORITHM
        }
    except JWTError as e:
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "secret_key_length": len(settings.SECRET_KEY),
            "algorithm": settings.ALGORITHM
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }


@router.post("/decode")
async def debug_decode(request: DebugTokenRequest, db: AsyncSession = Depends(get_db)):
    """Debug the full token decode and user lookup flow."""
    try:
        # Step 1: Decode token
        token_data = AuthService.decode_token(request.token)
        if token_data is None:
            return {
                "success": False,
                "step": "decode_token",
                "error": "decode_token returned None"
            }

        # Step 2: Check token data
        result = {
            "success": True,
            "step": "decode_complete",
            "token_data": {
                "user_id": token_data.user_id,
                "user_id_type": type(token_data.user_id).__name__,
                "email": token_data.email
            }
        }

        # Step 3: Try to get user
        user = await AuthService.get_user_by_id(db, token_data.user_id)
        if user is None:
            result["user_lookup"] = "User not found"
        else:
            result["user_lookup"] = {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active
            }

        return result
    except Exception as e:
        return {
            "success": False,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
