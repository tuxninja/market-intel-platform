"""
Database initialization script.

Creates initial admin user and sample data for testing.
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, init_db
from app.services.auth import AuthService
from app.schemas.user import UserCreate


async def create_admin_user():
    """Create an admin user for testing."""
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        admin = await AuthService.get_user_by_email(session, "admin@example.com")
        if admin:
            print("Admin user already exists")
            return

        # Create admin user
        admin_data = UserCreate(
            email="admin@example.com",
            password="admin123",
            full_name="Admin User",
        )
        admin = await AuthService.create_user(session, admin_data)
        admin.subscription_tier = "premium"
        admin.is_verified = True
        await session.commit()
        print(f"Admin user created: {admin.email}")


async def create_test_user():
    """Create a test user for development."""
    async with AsyncSessionLocal() as session:
        # Check if test user exists
        test_user = await AuthService.get_user_by_email(session, "test@example.com")
        if test_user:
            print("Test user already exists")
            return

        # Create test user
        test_data = UserCreate(
            email="test@example.com",
            password="test123",
            full_name="Test User",
        )
        test_user = await AuthService.create_user(session, test_data)
        test_user.is_verified = True
        await session.commit()
        print(f"Test user created: {test_user.email}")


async def main():
    """Main initialization function."""
    print("Initializing database...")
    await init_db()
    print("Database initialized!")

    print("\nCreating initial users...")
    await create_admin_user()
    await create_test_user()

    print("\nDatabase initialization complete!")
    print("\nTest credentials:")
    print("  Admin: admin@example.com / admin123 (premium)")
    print("  Test:  test@example.com / test123 (free)")


if __name__ == "__main__":
    asyncio.run(main())
