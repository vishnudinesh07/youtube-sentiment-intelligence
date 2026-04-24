import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# MODEL LOAD
# ---------------------------------------------------
analyzer = SentimentIntensityAnalyzer()


# ---------------------------------------------------
# SINGLE COMMENT SENTIMENT
# ---------------------------------------------------
def analyse_sentiment(text: str) -> dict:
    try:
        if text is None:
            text = ""

        text = str(text).strip()

        if not text:
            return {
                "sentiment": "neutral",
                "compound_score": 0.0,
                "positive_score": 0.0,
                "neutral_score": 1.0,
                "negative_score": 0.0,
            }

        scores = analyzer.polarity_scores(text)

        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "sentiment": label,
            "compound_score": round(compound, 4),
            "positive_score": round(scores["pos"], 4),
            "neutral_score": round(scores["neu"], 4),
            "negative_score": round(scores["neg"], 4),
        }

    except Exception:
        logger.exception("Sentiment analysis failed")

        return {
            "sentiment": "neutral",
            "compound_score": 0.0,
            "positive_score": 0.0,
            "neutral_score": 1.0,
            "negative_score": 0.0,
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

        negative = sum(
            1 for c in comments
            if c.get("sentiment") == "negative"
        )

        neutral = sum(
            1 for c in comments
            if c.get("sentiment") == "neutral"
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