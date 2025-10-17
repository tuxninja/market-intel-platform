"""
Authentication service for user management and JWT token handling.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, TokenData


class AuthService:
    """
    Authentication service for user management and JWT operations.

    Provides methods for password hashing, token generation, and user authentication.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain text password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        # Bcrypt has a maximum password length of 72 bytes
        # Truncate to 72 bytes to avoid ValueError
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.

        Supports both new bcrypt hashes and legacy passlib hashes for backward compatibility.

        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hashed password

        Returns:
            True if password matches, False otherwise
        """
        # Truncate password to 72 bytes to match hash_password behavior
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')

        try:
            # Try new bcrypt verification first
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except (ValueError, AttributeError):
            # Fall back to passlib for legacy hashes
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                password_truncated = password_bytes.decode('utf-8', errors='ignore')
                return pwd_context.verify(password_truncated, hashed_password)
            except:
                return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.

        Args:
            data: Token payload data
            expires_delta: Optional expiration time delta

        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": int(expire.timestamp()), "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """
        Create a JWT refresh token.

        Args:
            data: Token payload data

        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": int(expire.timestamp()), "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """
        Decode and validate a JWT token.

        Args:
            token: JWT token string

        Returns:
            TokenData if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id_str = payload.get("sub")
            email: str = payload.get("email")
            if user_id_str is None:
                return None
            # Convert string user_id to int
            user_id = int(user_id_str)
            return TokenData(user_id=user_id, email=email)
        except (JWTError, ValueError, TypeError):
            return None

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user account.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created User object
        """
        hashed_password = AuthService.hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            db: Database session
            email: User email address

        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise
        """
        user = await AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user
