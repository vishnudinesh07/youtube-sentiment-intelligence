import logging
import os
import requests

from langdetect import detect, LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

vader = SentimentIntensityAnalyzer()

HF_TOKEN = os.getenv("HF_TOKEN")

HF_MODEL_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-xlm-roberta-base-sentiment"


# ---------------------------------------------------
# LANGUAGE DETECTION
# ---------------------------------------------------
def detect_language(text: str) -> str:
    try:
        if not text or not text.strip():
            return "unknown"

        return detect(text)

    except LangDetectException:
        return "unknown"

    except Exception:
        logger.exception("Language detection failed")
        return "unknown"


# ---------------------------------------------------
# VADER SENTIMENT
# ---------------------------------------------------
def vader_sentiment(text: str) -> dict:
    try:
        scores = vader.polarity_scores(text)
        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "sentiment": label,
            "confidence_score": round(abs(compound), 4),
            "model_used": "vader",
        }

    except Exception:
        logger.exception("VADER sentiment failed")

        return {
            "sentiment": "neutral",
            "confidence_score": 0.0,
            "model_used": "vader_fallback",
        }


# ---------------------------------------------------
# HF API SENTIMENT
# ---------------------------------------------------
def transformer_sentiment(text: str) -> dict:
    try:
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }

        payload = {
            "inputs": text[:512]
        }

        response = requests.post(
            HF_MODEL_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        data = response.json()

        if not isinstance(data, list):
            raise ValueError("Unexpected HF response")

        result = data[0][0]

        label_map = {
            "LABEL_0": "negative",
            "LABEL_1": "neutral",
            "LABEL_2": "positive",
            "negative": "negative",
            "neutral": "neutral",
            "positive": "positive",
        }

        label = label_map.get(result["label"], "neutral")

        return {
            "sentiment": label,
            "confidence_score": round(float(result["score"]), 4),
            "model_used": "hf_api",
        }

    except Exception:
        logger.exception("HF sentiment failed")

        return {
            "sentiment": "neutral",
            "confidence_score": 0.0,
            "model_used": "transformer_fallback",
        }


# ---------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------
def analyse_multilingual_sentiment(text: str) -> dict:
    try:
        if not text or not str(text).strip():
            return {
                "language": "unknown",
                "sentiment": "neutral",
                "confidence_score": 0.0,
                "model_used": "none",
            }

        text = str(text).strip()

        language = detect_language(text)

        if language == "en":
            result = vader_sentiment(text)
        else:
            result = transformer_sentiment(text)

        if (
            result["confidence_score"] == 0.0
            and result["model_used"] == "transformer_fallback"
        ):
            result = vader_sentiment(text)

        return {
            "language": language,
            **result,
        }

    except Exception:
        logger.exception("Main multilingual analysis failed")

        return {
            "language": "unknown",
            "sentiment": "neutral",
            "confidence_score": 0.0,
            "model_used": "system_fallback",
        }


# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------
def summarise_sentiments(comments: list[dict]) -> dict:
    try:
        total = len(comments)

        positive = sum(1 for c in comments if c.get("sentiment") == "positive")
        neutral = sum(1 for c in comments if c.get("sentiment") == "neutral")
        negative = sum(1 for c in comments if c.get("sentiment") == "negative")

        if total == 0:
            return {
                "total": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "positive_pct": 0,
                "neutral_pct": 0,
                "negative_pct": 0,
            }

        return {
            "total": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_pct": round((positive / total) * 100, 2),
            "neutral_pct": round((neutral / total) * 100, 2),
            "negative_pct": round((negative / total) * 100, 2),
        }

    except Exception:
        logger.exception("Summary generation failed")

        return {
            "total": 0,
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "positive_pct": 0,
            "neutral_pct": 0,
            "negative_pct": 0,
        }