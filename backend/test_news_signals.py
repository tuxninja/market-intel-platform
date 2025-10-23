#!/usr/bin/env python3
"""
Test script for news-driven signal generator.

Tests the new ML-powered signal system without running the full backend.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal
from app.services.news_driven_signal_generator import create_news_driven_generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_news_driven_signals():
    """Test the news-driven signal generator."""
    print("\n" + "="*80)
    print("🧪 TESTING NEWS-DRIVEN SIGNAL GENERATOR")
    print("="*80 + "\n")

    # Create database session
    db = SessionLocal()

    try:
        # Create generator
        print("📊 Initializing news-driven generator...")
        generator = create_news_driven_generator(db)

        # Generate signals
        print("🔍 Fetching recent news and analyzing sentiment...")
        print("⏳ This may take 20-30 seconds (downloading FinBERT model on first run)...\n")

        start_time = datetime.now()
        signals = await generator.generate_signals(max_signals=10)
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"\n⏱️  Generation completed in {elapsed:.1f} seconds\n")
        print("="*80)
        print(f"✅ GENERATED {len(signals)} SIGNALS")
        print("="*80 + "\n")

        if not signals:
            print("⚠️  No signals generated. Possible reasons:")
            print("   - No significant news in last 6 hours")
            print("   - All news had low ML confidence (<60%)")
            print("   - All signals filtered as duplicates")
            print("   - News sources may be rate-limited")
            print("\n💡 Try running again later or lowering MIN_SENTIMENT_CONFIDENCE")
            return

        # Display each signal
        for i, signal in enumerate(signals, 1):
            print(f"\n{'='*80}")
            print(f"📈 SIGNAL #{i}: {signal.symbol}")
            print(f"{'='*80}\n")

            print(f"📰 Title: {signal.title}")
            print(f"💰 Category: {signal.category.upper()} | Priority: {signal.priority.upper()}")
            print(f"📊 Combined Score: {signal.sentiment_score:+.2f} | Confidence: {signal.confidence_score:.2%}")
            print(f"🎯 Source: {signal.source}")
            print()

            # Metadata
            meta = signal.metadata or {}
            print("📋 Metadata:")
            print(f"   Current Price: ${meta.get('current_price', 0):.2f}")
            print(f"   ML Confidence: {meta.get('ml_confidence', 0):.0%}")
            print(f"   News Age: {meta.get('news_age_hours', 0):.1f} hours ago")
            print(f"   News Sentiment: {meta.get('news_sentiment', 0):+.2f}")
            print(f"   Technical Score: {meta.get('technical_score', 0):+.2f}")
            if meta.get('rsi'):
                print(f"   RSI: {meta.get('rsi'):.1f}")
            print()

            # News articles
            if signal.news_articles:
                print("📰 Breaking News:")
                for article in signal.news_articles[:3]:  # Show max 3
                    print(f"   • {article['title'][:70]}...")
                    print(f"     Sentiment: {article['sentiment_score']:+.2f} | Source: {article['source']}")
                print()

            # Explanation (truncated)
            if signal.explanation:
                print("💡 Why This Matters:")
                lines = signal.explanation.split('\n')[:5]  # First 5 lines
                for line in lines:
                    print(f"   {line}")
                print()

            # Trading guidance (truncated)
            if signal.how_to_trade:
                print("📊 Trading Guidance:")
                lines = signal.how_to_trade.split('\n')[:7]  # First 7 lines
                for line in lines:
                    print(f"   {line}")
                print()

        print("\n" + "="*80)
        print("✅ TEST COMPLETE")
        print("="*80 + "\n")

        # Summary statistics
        bullish = [s for s in signals if s.sentiment_score > 0.3]
        bearish = [s for s in signals if s.sentiment_score < -0.3]
        neutral = [s for s in signals if -0.3 <= s.sentiment_score <= 0.3]

        print("📊 SUMMARY:")
        print(f"   🟢 Bullish Signals: {len(bullish)}")
        print(f"   🔴 Bearish Signals: {len(bearish)}")
        print(f"   ⚪ Neutral Signals: {len(neutral)}")
        print()
        print(f"   Average Confidence: {sum(s.confidence_score for s in signals) / len(signals):.1%}")
        print(f"   Average ML Confidence: {sum(s.metadata.get('ml_confidence', 0) for s in signals) / len(signals):.0%}")
        print()

        # Most confident signal
        if signals:
            top_signal = max(signals, key=lambda s: s.confidence_score)
            print(f"   🏆 Most Confident: {top_signal.symbol} ({top_signal.confidence_score:.0%})")
            print(f"      {top_signal.title}")
            print()

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.exception("Test failed")
        raise

    finally:
        db.close()
        print("🔒 Database connection closed\n")


if __name__ == "__main__":
    print("\n" + "🚀 Starting News-Driven Signal Generator Test...")
    print("📦 Loading dependencies (FinBERT, market data services)...\n")

    try:
        asyncio.run(test_news_driven_signals())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        sys.exit(1)
