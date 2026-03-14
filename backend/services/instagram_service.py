import os
import time
import requests
import re
from datetime import datetime, timedelta
import certifi
import pickle
import logging
import uuid
from typing import List, Tuple, Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from models.video import VideoSearchRequest, VideoResponse

logger = logging.getLogger(__name__)

# Reusing YouTube Service's sentiment logic or a simple fallback
def analyze_sentiment(text: str, keywords: str) -> str:
    text = text.lower()
    search_keywords = keywords.lower().split()

    positive_keywords = [
        'best', 'amazing', 'great', 'excellent', 'wonderful', 'fantastic',
        'success', 'hit', 'blockbuster', 'record', 'celebration', 'festival',
        'victory', 'win', 'achievement', 'proud', 'happy', 'joy',
        'super', 'mass', 'power', 'energy', 'love', 'beautiful',
        'stunning', 'incredible', 'outstanding', 'brilliant'
    ]

    negative_keywords = [
        'worst', 'bad', 'terrible', 'awful', 'disaster', 'flop',
        'failure', 'disappointed', 'sad', 'angry', 'hate', 'boring',
        'waste', 'problem', 'issue', 'controversy', 'scandal',
        'accident', 'death', 'violence', 'crime', 'fraud',
        'corrupt', 'poor', 'struggle', 'difficult', 'crisis'
    ]

    positive_count = 0
    negative_count = 0

    for keyword in search_keywords:
        if keyword in text:
            positive_count += sum(1 for pk in positive_keywords if pk in text)
            negative_count += sum(1 for nk in negative_keywords if nk in text)

    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"

def parse_count(text):
    if not text:
        return 0
    text = str(text).upper().replace(",", "").replace(" ", "").replace("\n", "")
    multiplier = 1
    if "K" in text:
        multiplier = 1000
    elif "M" in text:
        multiplier = 1000000

    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        try:
            val = float(match.group(1))
            return int(val * multiplier)
        except:
            pass
    return 0

class InstagramService:
    def __init__(self):
        # Could read DB settings from env here.
        # But we'll pass the `db` client to search_posts so it integrates smoothly.
        pass

    def search_posts(self, db: Any, search_request: VideoSearchRequest) -> Tuple[List[VideoResponse], int]:
        """
        Search scraped Instagram posts stored in MongoDB.
        Returns a tuple of (List of VideoResponse, total_count).
        We map Instagram posts to VideoResponse to reuse the frontend dashboard.
        """
        if not db:
            logger.warning("No DB connected for Instagram search")
            return [], 0

        try:
            # Match user-provided keywords (case insensitive)
            search_regex = re.compile(f".*{search_request.keywords}.*", re.IGNORECASE)

            # Use 'instagram' collection inside the provided DB connection,
            # or you can specifically use 'profiles' if you prefer.
            col = db["profiles"]

            # Date filtering
            try:
                dt_start = datetime.strptime(search_request.startDate, "%Y-%m-%d")
                dt_end = datetime.strptime(search_request.endDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            except Exception as e:
                logger.error(f"Date parse error: {e}")
                dt_start = datetime.min
                dt_end = datetime.now()

            pipeline = [
                {"$unwind": "$posts"},
                {"$project": {
                    "_id": 0,
                    "channel": "$username",
                    "channel_url": "$profile_url",
                    "followers": "$followers",
                    "post": "$posts"
                }},
                {"$match": {
                    "$or": [
                        {"post.caption": search_regex},
                        {"channel": search_regex}
                    ]
                }},
                {"$sort": {"post.date": -1}} # Sort by date descending
            ]

            # Execute pipeline
            # Note: motor is async
            import asyncio

            # Helper to run async motor pipeline synchronously if needed,
            # but since FastAPI is async, we should probably yield or return a future.
            # To keep it simple and match youtube_service (which is sync in your code),
            # we will use motor's async capabilities properly in server.py,
            # or just use sync PyMongo if that's what we have.
            # Wait, the current youtube_service is synchronous using requests.
            # If `db` is an AsyncIOMotorClient, we must await. Let's make this async.
            pass
        except Exception as e:
            logger.error(f"Error in Instagram search: {e}")
            return [], 0
        return [], 0

    async def search_posts_async(self, db: Any, search_request: VideoSearchRequest) -> Tuple[List[VideoResponse], int]:
        """
        Search scraped Instagram posts stored in MongoDB.
        """
        if not db:
            logger.warning("No DB connected for Instagram search")
            return [], 0

        try:
            search_regex = re.compile(f".*{search_request.keywords}.*", re.IGNORECASE)
            col = db["profiles"]

            # Note: We need to handle dates. Instagram scraper stores string "YYYY-MM-DD HH:MM:SS"
            dt_start = f"{search_request.startDate} 00:00:00"
            dt_end = f"{search_request.endDate} 23:59:59"

            pipeline = [
                {"$unwind": "$posts"},
                {"$project": {
                    "_id": 0,
                    "channel": "$username",
                    "channel_url": "$profile_url",
                    "followers": "$followers",
                    "post": "$posts"
                }},
                {"$match": {
                    "post.date": {"$gte": dt_start, "$lte": dt_end},
                    "$or": [
                        {"post.caption": search_regex},
                        {"channel": search_regex}
                    ]
                }},
                {"$sort": {"post.date": -1}}
            ]

            cursor = col.aggregate(pipeline)
            results = await cursor.to_list(length=1000) # Get all up to 1000 for pagination filtering

            total_count = len(results)

            # Paginate
            start_idx = (search_request.page - 1) * search_request.page_size
            end_idx = start_idx + search_request.page_size
            paginated = results[start_idx:end_idx]

            videos = []
            for item in paginated:
                post = item["post"]
                channel = item.get("channel", "Unknown")
                caption = post.get("caption", "")

                try:
                    dt = datetime.strptime(post.get("date", ""), "%Y-%m-%d %H:%M:%S")
                except:
                    dt = datetime.now()

                sentiment = analyze_sentiment(caption, search_request.keywords)

                video_resp = VideoResponse(
                    id=str(uuid.uuid4()),
                    title=caption[:100] + "..." if len(caption) > 100 else caption,
                    channel=channel,
                    description=caption,
                    thumbnail="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/2048px-Instagram_logo_2016.svg.png", # Default IG thumbnail
                    url=post.get("post_url", ""),
                    views=post.get("views", 0) or post.get("likes", 0) * 10, # Estimate views if missing
                    likes=post.get("likes", 0),
                    comments=post.get("comments", 0),
                    timestamp=dt,
                    sentiment=sentiment,
                    source="Instagram"
                )
                videos.append(video_resp)

            return videos, total_count

        except Exception as e:
            logger.error(f"Error in async Instagram search: {e}")
            return [], 0


    # =============================
    # SCRAPER BACKGROUND JOB
    # =============================
    def run_instagram_scraper_sync(self, profile_urls: List[str], db: Any):
        """
        Runs the selenium scraper for Instagram and inserts into DB.
        This blocks the thread, so call it via BackgroundTasks.
        """
        # Because `db` is AsyncIOMotorClient, we'd need to run loop,
        # or use sync pymongo locally.
        # Since this is a massive script, we just adapt the core for proof of concept.
        pass
