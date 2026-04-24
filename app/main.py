import logging
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import APP_NAME, APP_VERSION
from app.models.schemas import AnalyseRequest
from app.services.youtube_service import (
    extract_video_id,
    fetch_comments,
    get_video_metadata,
)
from app.services.multilingual_sentiment_service import (
    analyse_multilingual_sentiment,
    summarise_sentiments,
)
from app.services.insight_service import (
    generate_executive_summary,
    generate_key_metrics,
)

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION
)

# ---------------------------------------------------
# CORS
# ---------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this later after deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# ROUTES
# ---------------------------------------------------
@app.get("/")
def home():
    return {
        "message": "YouTube Sentiment Intelligence API Running",
        "version": APP_VERSION
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": APP_NAME
    }


@app.post("/analyse")
def analyse(payload: AnalyseRequest):
    start_time = time.time()

    try:
        logger.info("Analysis request received")

        video_id = extract_video_id(payload.url)
        logger.info(f"Extracted video_id: {video_id}")

        metadata = get_video_metadata(video_id)
        logger.info("Video metadata fetched")

        comments = fetch_comments(video_id=video_id, limit=payload.limit)
        logger.info(f"Comments fetched: {len(comments)}")

        enriched_comments = []

        for comment in comments:
            sentiment_result = analyse_multilingual_sentiment(comment["comment"])

            enriched_comments.append({
                **comment,
                **sentiment_result
            })

        logger.info("Sentiment analysis completed")

        summary = summarise_sentiments(enriched_comments)

        executive_summary = generate_executive_summary(summary)
        key_metrics = generate_key_metrics(enriched_comments)

        message = "Comments analysed successfully."
        if len(enriched_comments) == 0:
            message = "No public comments available for this video."

        processing_time = round(time.time() - start_time, 2)

        return {
            "message": message,
            "video_id": video_id,
            "video_metadata": metadata,
            "requested_limit": payload.limit,
            "returned_comments": len(enriched_comments),
            "sentiment_summary": summary,
            "executive_summary": executive_summary,
            "key_metrics": key_metrics,
            "comments": enriched_comments,
            "processing_time_seconds": processing_time
        }

    except ValueError as error:
        logger.warning(f"Validation error: {str(error)}")
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:
        logger.exception("Unexpected server error")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while analysing video."
        )