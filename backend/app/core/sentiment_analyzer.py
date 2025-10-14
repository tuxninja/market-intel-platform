"""
Sentiment Analysis Module

This module provides sentiment analysis capabilities for financial news using
multiple NLP libraries. It processes news articles to determine market sentiment
and assigns numerical scores that can be used in trading decision algorithms.

Dependencies:
    - textblob: Basic sentiment analysis with polarity scoring
    - vaderSentiment: Specialized for social media/informal text sentiment

Author: Market Intelligence Platform
"""

import logging
from typing import List, Dict, Tuple
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes sentiment of financial news articles using multiple algorithms.

    This class combines TextBlob and VADER sentiment analysis to provide
    robust sentiment scoring for financial news. It includes financial
    keyword weighting and handles market-specific language patterns.

    Attributes:
        vader_analyzer: VADER sentiment intensity analyzer
        bullish_keywords: List of positive financial terms
        bearish_keywords: List of negative financial terms
    """

    def __init__(self):
        """Initialize sentiment analyzer with financial keyword dictionaries."""
        self.vader_analyzer = SentimentIntensityAnalyzer()

        # Financial market specific keywords for sentiment weighting
        self.bullish_keywords = [
            "bull",
            "bullish",
            "rally",
            "surge",
            "soar",
            "climb",
            "gain",
            "rise",
            "upgrade",
            "outperform",
            "beat",
            "exceed",
            "strong",
            "growth",
            "positive",
            "optimistic",
            "breakthrough",
            "expansion",
            "profit",
            "revenue",
            "earnings beat",
            "buy rating",
            "price target raised",
        ]

        self.bearish_keywords = [
            "bear",
            "bearish",
            "decline",
            "fall",
            "drop",
            "plunge",
            "crash",
            "downgrade",
            "underperform",
            "miss",
            "weak",
            "loss",
            "negative",
            "pessimistic",
            "concern",
            "risk",
            "uncertainty",
            "volatility",
            "sell rating",
            "price target lowered",
            "guidance lowered",
        ]

    def analyze_news_sentiment(self, news_articles: List[Dict]) -> Tuple[float, Dict]:
        """
        Analyze sentiment across multiple news articles for a stock.

        Args:
            news_articles (List[Dict]): List of news articles with 'title' and 'content' keys

        Returns:
            Tuple[float, Dict]: (overall_sentiment_score, detailed_analysis)
                               Score range: -1.0 (very negative) to 1.0 (very positive)

        Note:
            - Combines TextBlob polarity and VADER compound scores
            - Applies financial keyword weighting
            - More recent articles have higher influence
            - Returns detailed breakdown for debugging/transparency
        """
        if not news_articles:
            logger.warning("No news articles provided for sentiment analysis")
            return 0.0, {"article_count": 0, "method": "no_data"}

        article_sentiments = []
        total_weight = 0

        for i, article in enumerate(news_articles[:20]):  # Limit to 20 most recent
            try:
                # Extract text for analysis
                text = f"{article.get('title', '')} {article.get('content', '')}"
                if not text.strip():
                    continue

                # Calculate sentiment using multiple methods
                sentiment_score = self._calculate_article_sentiment(text)

                # Weight recent articles more heavily (exponential decay)
                article_weight = 0.9**i  # More recent = higher weight

                weighted_sentiment = sentiment_score * article_weight
                article_sentiments.append(
                    {
                        "score": sentiment_score,
                        "weight": article_weight,
                        "weighted_score": weighted_sentiment,
                        "title": article.get("title", "")[:50] + "...",
                    }
                )

                total_weight += article_weight

            except Exception as e:
                logger.warning(f"Error analyzing sentiment for article: {e}")
                continue

        if not article_sentiments or total_weight == 0:
            return 0.0, {"article_count": 0, "method": "analysis_failed"}

        # Calculate weighted average sentiment
        weighted_total = sum(item["weighted_score"] for item in article_sentiments)
        overall_sentiment = weighted_total / total_weight

        # Normalize to [-1, 1] range
        overall_sentiment = max(-1.0, min(1.0, overall_sentiment))

        analysis_details = {
            "article_count": len(article_sentiments),
            "overall_score": overall_sentiment,
            "method": "textblob_vader_financial",
            "individual_scores": article_sentiments[:5],  # Top 5 for debugging
            "confidence": min(
                len(article_sentiments) / 10.0, 1.0
            ),  # More articles = higher confidence
        }

        logger.info(
            f"Sentiment analysis complete: {overall_sentiment:.3f} from {len(article_sentiments)} articles"
        )
        return overall_sentiment, analysis_details

    def _calculate_article_sentiment(self, text: str) -> float:
        """
        Calculate sentiment score for a single article using hybrid approach.

        Args:
            text (str): Combined title and content text

        Returns:
            float: Sentiment score from -1.0 to 1.0

        Method:
            1. TextBlob polarity analysis
            2. VADER compound score analysis
            3. Financial keyword pattern matching
            4. Weighted combination of all methods
        """
        # Clean and normalize text
        text = self._preprocess_text(text)

        # TextBlob analysis (good for general sentiment)
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity

        # VADER analysis (good for intensity and informal language)
        vader_scores = self.vader_analyzer.polarity_scores(text)
        vader_score = vader_scores["compound"]

        # Financial keyword analysis
        financial_score = self._analyze_financial_keywords(text)

        # Weighted combination (VADER tends to be more accurate for financial news)
        combined_score = (
            textblob_score * 0.3  # TextBlob: 30%
            + vader_score * 0.5  # VADER: 50%
            + financial_score * 0.2  # Financial keywords: 20%
        )

        return combined_score

    def _preprocess_text(self, text: str) -> str:
        """
        Clean and normalize text for sentiment analysis.

        Args:
            text (str): Raw text input

        Returns:
            str: Cleaned and normalized text
        """
        # Remove HTML tags if any
        text = re.sub(r"<[^>]+>", "", text)

        # Normalize whitespace
        text = " ".join(text.split())

        # Convert to lowercase for keyword matching
        return text.lower()

    def _analyze_financial_keywords(self, text: str) -> float:
        """
        Analyze financial-specific keywords to adjust sentiment score.

        Args:
            text (str): Preprocessed text (lowercase)

        Returns:
            float: Financial keyword sentiment score (-1.0 to 1.0)

        Logic:
            Counts bullish vs bearish financial terms and calculates
            a sentiment score based on their relative frequency.
        """
        bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text)
        bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text)

        total_keywords = bullish_count + bearish_count

        if total_keywords == 0:
            return 0.0  # No financial keywords found

        # Calculate sentiment based on keyword balance
        keyword_sentiment = (bullish_count - bearish_count) / total_keywords

        # Apply intensity scaling based on total keyword density
        intensity = min(total_keywords / 5.0, 1.0)  # More keywords = higher confidence

        return keyword_sentiment * intensity

    def get_sentiment_summary(self, sentiment_score: float) -> str:
        """
        Convert numerical sentiment score to human-readable summary.

        Args:
            sentiment_score (float): Sentiment score from -1.0 to 1.0

        Returns:
            str: Human-readable sentiment description
        """
        if sentiment_score >= 0.6:
            return "Very Bullish"
        elif sentiment_score >= 0.2:
            return "Bullish"
        elif sentiment_score >= -0.2:
            return "Neutral"
        elif sentiment_score >= -0.6:
            return "Bearish"
        else:
            return "Very Bearish"
