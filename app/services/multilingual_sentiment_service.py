import logging
from functools import lru_cache

from langdetect import detect, LangDetectException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# LIGHTWEIGHT MODELS
# ---------------------------------------------------
vader = SentimentIntensityAnalyzer()


# ---------------------------------------------------
# LOAD TRANSFORMER ONCE
# ---------------------------------------------------
@lru_cache(maxsize=1)
def get_multilingual_model():
    try:
        logger.info("Loading multilingual sentiment model...")

        model = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            tokenizer="cardiffnlp/twitter-xlm-roberta-base-sentiment"
        )

        logger.info("Multilingual model loaded successfully")
        return model

    except Exception:
        logger.exception("Failed to load multilingual model")
        return None


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
# TRANSFORMER SENTIMENT
# ---------------------------------------------------
def transformer_sentiment(text: str) -> dict:
    try:
        model = get_multilingual_model()

        if model is None:
            raise ValueError("Transformer model unavailable")

        result = model(text[:512])[0]

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
            "model_used": "xlm-roberta",
        }

    except Exception:
        logger.exception("Transformer sentiment failed")

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

        # if transformer fallback returned neutral zero confidence
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

        positive = sum(
            1 for c in comments
            if c.get("sentiment") == "positive"
        )

        neutral = sum(
            1 for c in comments
            if c.get("sentiment") == "neutral"
        )

        negative = sum(
            1 for c in comments
            if c.get("sentiment") == "negative"
        )

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