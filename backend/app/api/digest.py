"""
Digest API endpoints for market intelligence.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.digest import DigestRequest, DigestResponse
from app.services.digest_service import DigestService
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/daily", response_model=DigestResponse)
async def get_daily_digest(
    max_items: int = 20,
    hours_lookback: int = 24,
    enable_ml: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get daily market intelligence digest.

    Requires authentication. Returns curated market intelligence with:
    - Trade alerts (high-confidence opportunities)
    - Watch list (emerging opportunities)
    - Market context (background information)

    Args:
        max_items: Maximum number of items to return (1-100)
        hours_lookback: Hours to look back for news (1-168)
        enable_ml: Enable ML enhancement
        current_user: Current authenticated user
        db: Database session

    Returns:
        Complete market intelligence digest

    Raises:
        HTTPException: If digest generation fails
    """
    # Validate parameters
    if max_items < 1 or max_items > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="max_items must be between 1 and 100",
        )

    if hours_lookback < 1 or hours_lookback > 168:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="hours_lookback must be between 1 and 168 (1 week)",
        )

    # Check subscription tier for feature limits
    if current_user.subscription_tier == "free" and max_items > 10:
        max_items = 10  # Free tier limited to 10 items

    # Generate digest
    service = DigestService(db)
    try:
        digest = await service.generate_daily_digest(
            max_items=max_items,
            hours_lookback=hours_lookback,
            enable_ml=enable_ml,
        )
        return digest
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate digest: {str(e)}",
        )


@router.post("/generate", response_model=DigestResponse)
async def generate_custom_digest(
    request: DigestRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate custom market intelligence digest with advanced filters.

    Requires authentication. Allows filtering by categories and custom parameters.

    Args:
        request: Digest generation request with parameters
        current_user: Current authenticated user
        db: Database session

    Returns:
        Custom market intelligence digest

    Raises:
        HTTPException: If digest generation fails
    """
    # Check subscription tier for advanced features
    if current_user.subscription_tier == "free" and request.categories:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Category filtering requires pro or premium subscription",
        )

    # Generate digest
    service = DigestService(db)
    try:
        digest = await service.generate_daily_digest(
            max_items=request.max_items,
            hours_lookback=request.hours_lookback,
            enable_ml=request.enable_ml,
            categories=request.categories,
        )
        return digest
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate digest: {str(e)}",
        )
