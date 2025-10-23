"""
ML-Based Sentiment Analysis Service

Uses FinBERT (Financial BERT) for accurate sentiment analysis of financial news.
FinBERT is a pre-trained NLP model specifically fine-tuned for financial text.
"""

import logging
from typing import Dict, Optional, List
from functools import lru_cache
import numpy as np

logger = logging.getLogger(__name__)


class MLSentimentAnalyzer:
    """
    ML-based sentiment analyzer using FinBERT.

    FinBERT is a BERT model fine-tuned on financial phrasebank data.
    It provides more accurate sentiment analysis for financial news than VADER.
    """

    def __init__(self):
        """Initialize the sentiment analyzer with FinBERT model."""
        self.model = None
        self.tokenizer = None
        self._initialized = False

    def _load_model(self):
        """Lazy load FinBERT model (only when first needed)."""
        if self._initialized:
            return

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch

            logger.info("Loading FinBERT model...")

            # Use FinBERT-tone model (best for sentiment)
            model_name = "yiyanghkust/finbert-tone"

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)

            # Set to evaluation mode
            self.model.eval()

            self._initialized = True
            logger.info("FinBERT model loaded successfully")

        except ImportError as e:
            logger.error(f"Failed to import transformers library: {e}")
            logger.error("Please install: pip install transformers torch")
            raise
        except Exception as e:
            logger.error(f"Failed to load FinBERT model: {e}")
            raise

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of financial text using FinBERT.

        Args:
            text: Financial news text to analyze

        Returns:
            Dict with sentiment scores:
            {
                "score": -1.0 to 1.0 (negative to positive),
                "confidence": 0.0 to 1.0,
                "label": "positive" | "negative" | "neutral",
                "probabilities": {
                    "positive": 0.0-1.0,
                    "negative": 0.0-1.0,
                    "neutral": 0.0-1.0
                }
            }
        """
        # Lazy load model on first use
        if not self._initialized:
            self._load_model()

        try:
            import torch

            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,  # BERT max sequence length
                padding=True
            )

            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Extract probabilities
            probs = predictions[0].numpy()

            # FinBERT outputs: [negative, neutral, positive]
            negative_prob = float(probs[0])
            neutral_prob = float(probs[1])
            positive_prob = float(probs[2])

            # Calculate composite score (-1 to +1)
            # Weight positive and negative, discount neutral
            score = (positive_prob - negative_prob)

            # Determine label
            max_prob = max(negative_prob, neutral_prob, positive_prob)
            if positive_prob == max_prob:
                label = "positive"
            elif negative_prob == max_prob:
                label = "negative"
            else:
                label = "neutral"

            # Confidence is the max probability
            confidence = max_prob

            return {
                "score": round(score, 3),
                "confidence": round(confidence, 3),
                "label": label,
                "probabilities": {
                    "positive": round(positive_prob, 3),
                    "negative": round(negative_prob, 3),
                    "neutral": round(neutral_prob, 3)
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral sentiment on error
            return {
                "score": 0.0,
                "confidence": 0.0,
                "label": "neutral",
                "probabilities": {
                    "positive": 0.33,
                    "negative": 0.33,
                    "neutral": 0.34
                }
            }

    def batch_analyze_sentiment(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts in batch (more efficient).

        Args:
            texts: List of texts to analyze

        Returns:
            List of sentiment dicts
        """
        if not self._initialized:
            self._load_model()

        try:
            import torch

            # Tokenize all texts
            inputs = self.tokenizer(
                texts,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )

            # Get predictions for all texts
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # Process each prediction
            results = []
            for probs in predictions.numpy():
                negative_prob = float(probs[0])
                neutral_prob = float(probs[1])
                positive_prob = float(probs[2])

                score = (positive_prob - negative_prob)

                max_prob = max(negative_prob, neutral_prob, positive_prob)
                if positive_prob == max_prob:
                    label = "positive"
                elif negative_prob == max_prob:
                    label = "negative"
                else:
                    label = "neutral"

                results.append({
                    "score": round(score, 3),
                    "confidence": round(max_prob, 3),
                    "label": label,
                    "probabilities": {
                        "positive": round(positive_prob, 3),
                        "negative": round(negative_prob, 3),
                        "neutral": round(neutral_prob, 3)
                    }
                })

            return results

        except Exception as e:
            logger.error(f"Error in batch sentiment analysis: {e}")
            # Return neutral sentiments
            return [{
                "score": 0.0,
                "confidence": 0.0,
                "label": "neutral",
                "probabilities": {"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            } for _ in texts]


# Global singleton instance
ml_sentiment_analyzer = MLSentimentAnalyzer()
