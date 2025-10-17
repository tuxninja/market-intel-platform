"""
Authentication API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.auth import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = await AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT tokens.

    Args:
        login_data: User login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = await AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str, db: AsyncSession = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Args:
        token: Refresh token
        db: Database session

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Decode refresh token
    token_data = AuthService.decode_token(token)
    if token_data is None or token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists
    user = await AuthService.get_user_by_id(db, token_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    new_token_data = {"sub": str(user.id), "email": user.email}
    access_token = AuthService.create_access_token(new_token_data)
    refresh_token = AuthService.create_refresh_token(new_token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    full_name: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user information.

    Args:
        full_name: New full name
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user information
    """
    if full_name is not None:
        current_user.full_name = full_name

    await db.commit()
    await db.refresh(current_user)
    return current_user
