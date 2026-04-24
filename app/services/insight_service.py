import logging

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logger = logging.getLogger(__name__)


# ---------------------------------------------------
# EXECUTIVE SUMMARY
# ---------------------------------------------------
def generate_executive_summary(summary: dict) -> dict:
    try:
        positive = float(summary.get("positive_pct", 0))
        negative = float(summary.get("negative_pct", 0))
        neutral = float(summary.get("neutral_pct", 0))

        if positive >= 60:
            overall = "Strongly Positive"
            mood = "Highly favourable"
            risk = "Low"
            recommendation = (
                "Promote momentum and amplify praised elements."
            )

        elif positive >= 45:
            overall = "Positive"
            mood = "Favourable"
            risk = "Low"
            recommendation = (
                "Strong reception. Continue targeted promotion."
            )

        elif negative >= 40:
            overall = "Negative"
            mood = "Unfavourable"
            risk = "High"
            recommendation = (
                "Review criticism themes and respond quickly."
            )

        else:
            overall = "Mixed"
            mood = "Balanced / uncertain"
            risk = "Medium"
            recommendation = (
                "Monitor reactions and refine messaging."
            )

        return {
            "overall_sentiment": overall,
            "audience_mood": mood,
            "risk_level": risk,
            "recommendation": recommendation,
            "positive_pct": positive,
            "neutral_pct": neutral,
            "negative_pct": negative,
        }

    except Exception:
        logger.exception("Executive summary generation failed")

        return {
            "overall_sentiment": "Unknown",
            "audience_mood": "Unavailable",
            "risk_level": "Unknown",
            "recommendation": "Unable to generate recommendation.",
            "positive_pct": 0,
            "neutral_pct": 0,
            "negative_pct": 0,
        }


# ---------------------------------------------------
# KEY METRICS
# ---------------------------------------------------
def generate_key_metrics(comments: list[dict]) -> dict:
    try:
        if not comments:
            return {
                "most_liked_comment": None,
                "most_liked_comment_likes": 0,
                "top_positive_comment": None,
                "top_negative_comment": None,
                "total_comments_analysed": 0,
            }

        most_liked = max(
            comments,
            key=lambda x: x.get("likes", 0)
        )

        positive_comments = [
            c for c in comments
            if c.get("sentiment") == "positive"
        ]

        negative_comments = [
            c for c in comments
            if c.get("sentiment") == "negative"
        ]

        top_positive = (
            max(
                positive_comments,
                key=lambda x: x.get("likes", 0)
            )
            if positive_comments else None
        )

        top_negative = (
            max(
                negative_comments,
                key=lambda x: x.get("likes", 0)
            )
            if negative_comments else None
        )

        return {
            "most_liked_comment":
                most_liked.get("comment"),

            "most_liked_comment_likes":
                most_liked.get("likes", 0),

            "top_positive_comment":
                top_positive.get("comment")
                if top_positive else None,

            "top_negative_comment":
                top_negative.get("comment")
                if top_negative else None,

            "total_comments_analysed":
                len(comments),
        }

    except Exception:
        logger.exception("Key metrics generation failed")

        return {
            "most_liked_comment": None,
            "most_liked_comment_likes": 0,
            "top_positive_comment": None,
            "top_negative_comment": None,
            "total_comments_analysed": 0,
        }