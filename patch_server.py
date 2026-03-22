with open("backend/server.py", "r") as f:
    content = f.read()

import_str = """
from services.youtube_service import YouTubeService
from services.export_service import ExportService
from services.instagram_service import InstagramService
"""

content = content.replace(
    "from services.youtube_service import YouTubeService\nfrom services.export_service import ExportService",
    import_str
)

init_services_str = """
# Initialize services
youtube_service = YouTubeService()
export_service = ExportService()
instagram_service = InstagramService()
"""

content = content.replace(
    "# Initialize services\nyoutube_service = YouTubeService()\nexport_service = ExportService()",
    init_services_str
)

instagram_endpoints = """
@api_router.post("/instagram/search", response_model=SearchResponse)
async def search_instagram_posts(search_request: VideoSearchRequest):
    \"\"\"
    Search for Instagram posts based on keywords and date range
    \"\"\"
    try:
        videos, total_count = await instagram_service.search_posts_async(db, search_request)

        # Store search results in database (optional if DB fails)
        if db is not None:
            try:
                search_result = {
                    "search_params": search_request.dict(),
                    "videos": [video.dict() for video in videos],
                    "total_count": total_count,
                    "timestamp": datetime.utcnow()
                }
                await db.instagram_search_results.insert_one(search_result)
            except Exception as db_error:
                print(f"Database storage error: {db_error}")

        return SearchResponse(
            videos=videos,
            total_count=total_count,
            search_params=search_request
        )

    except Exception as e:
        logging.error(f"Error searching instagram posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching instagram posts: {str(e)}")

@api_router.post("/instagram/analytics", response_model=AnalyticsSummary)
async def get_instagram_analytics(search_request: VideoSearchRequest):
    \"\"\"
    Get analytics summary for an Instagram search
    \"\"\"
    empty_response = AnalyticsSummary(
        total_videos=0,
        sentiment_distribution=SentimentDistribution(positive=0, negative=0, neutral=0),
        overall_sentiment="Neutral",
        average_engagement={"views": 0, "likes": 0, "comments": 0},
        total_views=0,
        total_likes=0,
        total_comments=0,
        total_engagement=0
    )

    try:
        videos, _ = await instagram_service.search_posts_async(db, search_request)
    except Exception as e:
        logging.error(f"search_posts_async failed inside analytics: {str(e)}")
        return empty_response

    if not videos:
        return empty_response

    try:
        total_videos_in_search = len(videos)

        sentiment_distribution = {"positive": 0, "negative": 0, "neutral": 0}
        for video in videos:
            sentiment = getattr(video, 'sentiment', 'neutral')
            sentiment = sentiment.lower() if sentiment else 'neutral'
            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] += 1

        overall_sentiment = max(sentiment_distribution, key=sentiment_distribution.get)

        total_views    = sum(getattr(video, 'views', 0) or 0 for video in videos)
        total_likes    = sum(getattr(video, 'likes', 0) or 0 for video in videos)
        total_comments = sum(getattr(video, 'comments', 0) or 0 for video in videos)

        average_engagement = {
            "views":    total_views    / total_videos_in_search,
            "likes":    total_likes    / total_videos_in_search,
            "comments": total_comments / total_videos_in_search,
        }

        return AnalyticsSummary(
            total_videos=total_videos_in_search,
            sentiment_distribution=SentimentDistribution(**sentiment_distribution),
            overall_sentiment=overall_sentiment.capitalize(),
            average_engagement=average_engagement,
            total_views=total_views,
            total_likes=total_likes,
            total_comments=total_comments,
            total_engagement=total_likes + total_comments
        )

    except Exception as e:
        logging.error(f"Error computing analytics: {str(e)}")
        return empty_response

# Include the router in the main app
"""

content = content.replace("# Include the router in the main app", instagram_endpoints)

with open("backend/server.py", "w") as f:
    f.write(content)
