import re
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import YOUTUBE_API_KEY

# ---------------------------------------------------
# LOGGING
# ---------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# CONSTANTS
# ---------------------------------------------------
YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"


# ---------------------------------------------------
# CLIENT
# ---------------------------------------------------
def get_youtube_client():
    if not YOUTUBE_API_KEY:
        raise ValueError("YouTube API key is missing.")

    try:
        return build(
            YOUTUBE_API_SERVICE,
            YOUTUBE_API_VERSION,
            developerKey=YOUTUBE_API_KEY,
            cache_discovery=False
        )
    except Exception as error:
        logger.exception("Failed to create YouTube client")
        raise ValueError("Unable to connect to YouTube API.")


# ---------------------------------------------------
# VIDEO ID EXTRACTION
# ---------------------------------------------------
def extract_video_id(url: str) -> str:
    if not url or not isinstance(url, str):
        raise ValueError("Invalid YouTube URL.")

    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"shorts/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError("Invalid YouTube URL.")


# ---------------------------------------------------
# VIDEO METADATA
# ---------------------------------------------------
def get_video_metadata(video_id: str) -> dict:
    youtube = get_youtube_client()

    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        items = response.get("items", [])

        if not items:
            raise ValueError("Video not found or unavailable.")

        snippet = items[0]["snippet"]
        statistics = items[0].get("statistics", {})

        return {
            "video_title": snippet.get("title"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
        }

    except HttpError as error:
        logger.exception("YouTube metadata API error")
        raise ValueError("Unable to fetch video details from YouTube.")

    except Exception as error:
        logger.exception("Unexpected metadata error")
        raise ValueError("Unable to fetch video metadata.")


# ---------------------------------------------------
# COMMENTS
# ---------------------------------------------------
def fetch_comments(video_id: str, limit: int = 100) -> list[dict]:
    youtube = get_youtube_client()

    comments = []
    next_page_token = None

    try:
        while len(comments) < limit:

            remaining = limit - len(comments)
            page_size = min(100, remaining)

            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=page_size,
                pageToken=next_page_token,
                textFormat="plainText",
                order="relevance"
            ).execute()

            for item in response.get("items", []):

                top_comment = item["snippet"]["topLevelComment"]["snippet"]

                comments.append({
                    "comment_id": item["snippet"]["topLevelComment"]["id"],
                    "author": top_comment.get("authorDisplayName"),
                    "comment": top_comment.get("textDisplay"),
                    "likes": top_comment.get("likeCount", 0),
                    "published_at": top_comment.get("publishedAt"),
                    "reply_count": item["snippet"].get("totalReplyCount", 0),
                })

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        logger.info(f"Fetched comments: {len(comments)}")
        return comments

    except HttpError as error:

        error_text = str(error)

        logger.exception("YouTube comments API error")

        if "commentsDisabled" in error_text:
            raise ValueError("Comments are disabled for this video.")

        if "quotaExceeded" in error_text:
            raise ValueError("YouTube API quota exceeded. Try again later.")

        if "videoNotFound" in error_text:
            raise ValueError("Video not found or unavailable.")

        raise ValueError("Unable to fetch comments from YouTube.")

    except Exception:
        logger.exception("Unexpected comment fetch error")
        raise ValueError("Unexpected error while fetching comments.")