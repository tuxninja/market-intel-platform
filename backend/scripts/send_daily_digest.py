#!/usr/bin/env python3
"""
Daily Digest CLI Script

Generates and sends daily market intelligence digest emails.
Adapted from trade-ideas for market-intel-platform.

Usage:
    python scripts/send_daily_digest.py --email your@email.com
    python scripts/send_daily_digest.py --email your@email.com --max-items 15
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.digest_service import DigestService
from app.services.email_service import email_service
from app.database import init_db, close_db
from app.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def send_digest(
    email_to: str,
    max_items: int = 20,
    hours_lookback: int = 24
):
    """
    Generate and send daily digest.

    Args:
        email_to: Recipient email address
        max_items: Maximum digest items
        hours_lookback: Hours to look back for news
    """
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")

        # Generate digest
        logger.info(f"Generating digest: max_items={max_items}, lookback={hours_lookback}h")
        digest_service = DigestService(None)  # No DB session needed for now
        digest = await digest_service.generate_daily_digest(
            max_items=max_items,
            hours_lookback=hours_lookback
        )

        logger.info(f"Generated digest with {digest.total_items} items")

        # Send email
        logger.info(f"Sending digest email to {email_to}")
        success = await email_service.send_daily_digest(
            recipient_email=email_to,
            digest=digest
        )

        if success:
            logger.info("✅ Daily digest sent successfully!")
            return 0
        else:
            logger.error("❌ Failed to send daily digest")
            return 1

    except Exception as e:
        logger.error(f"Error sending digest: {e}", exc_info=True)
        return 1

    finally:
        await close_db()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate and send daily market intelligence digest"
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Recipient email address"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=20,
        help="Maximum number of digest items (default: 20)"
    )
    parser.add_argument(
        "--hours-lookback",
        type=int,
        default=24,
        help="Hours to look back for news (default: 24)"
    )

    args = parser.parse_args()

    # Print configuration
    print("=" * 60)
    print("📧 Daily Market Intelligence Digest")
    print("=" * 60)
    print(f"Recipient: {args.email}")
    print(f"Max Items: {args.max_items}")
    print(f"Lookback:  {args.hours_lookback} hours")
    print(f"SMTP:      {settings.SMTP_SERVER}:{settings.SMTP_PORT}")
    print("=" * 60)
    print()

    # Run async function
    exit_code = asyncio.run(send_digest(
        email_to=args.email,
        max_items=args.max_items,
        hours_lookback=args.hours_lookback
    ))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
