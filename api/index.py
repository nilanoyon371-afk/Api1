
from __future__ import annotations

import asyncio
from typing import Any, Coroutine, Dict, List, Literal, Optional, Union
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

# Import the scraper module
import xhamster


app = FastAPI(
    title="XHamster Scraper API",
    description="An unofficial API to scrape video data from xhamster.com.",
    version="1.0.0",
)


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


@app.get(
    "/",
    summary="Scrape a single video page",
    response_model=Dict[str, Any],
    responses={
        200: {
            "description": "Successfully scraped video data.",
            "content": {
                "application/json": {
                    "example": {
                        "url": "https://xhamster.com/videos/some-video-12345",
                        "title": "Some Video Title",
                        "thumbnail_url": "https://thumb.jpg",
                        "duration": "10:00",
                        "views": "1.2M",
                        "uploader_name": "SomeUploader",
                        "category": "Some Category",
                        "tags": ["tag1", "tag2"],
                    }
                }
            },
        },
        400: {"description": "Invalid URL"},
        404: {"description": "Video not found or failed to scrape"},
        500: {"description": "Internal server error"},
    },
)
async def scrape_video(
    url: str = Query(..., description="The URL of the xhamster video page to scrape.")
) -> JSONResponse:
    if not is_valid_url(url) or not xhamster.can_handle(urlparse(url).hostname):
        raise HTTPException(status_code=400, detail="Invalid or unsupported URL")

    try:
        data = await xhamster.scrape(url)
        if not data or not data.get("title"):
            raise HTTPException(status_code=404, detail="Video not found or failed to parse")
        return JSONResponse(content=data)
    except Exception as e:
        # Log the exception for debugging
        print(f"Error scraping {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get(
    "/list",
    summary="List videos from a base URL",
    response_model=List[Dict[str, Any]],
    responses={
        200: {
            "description": "Successfully retrieved video list.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "url": "https://xhamster.com/videos/some-video-12345",
                            "title": "Some Video Title",
                            "thumbnail_url": "https://thumb.jpg",
                            "duration": "10:00",
                            "views": "1.2M",
                            "uploader_name": "SomeUploader",
                        }
                    ]
                }
            },
        },
        400: {"description": "Invalid URL"},
        500: {"description": "Internal server error"},
    },
)
async def list_videos(
    base_url: str = Query(
        ..., description="The base URL for a category or search result on xhamster."
    ),
    page: int = Query(1, description="The page number to retrieve.", ge=1),
    limit: int = Query(20, description="The number of results per page.", ge=1, le=100),
) -> JSONResponse:
    if not is_valid_url(base_url) or not xhamster.can_handle(urlparse(base_url).hostname):
        raise HTTPException(status_code=400, detail="Invalid or unsupported URL")

    try:
        items = await xhamster.list_videos(base_url, page=page, limit=limit)
        return JSONResponse(content=items)
    except Exception as e:
        print(f"Error listing videos from {base_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


@app.get(
    "/crawl",
    summary="Crawl multiple pages of videos",
    response_model=List[Dict[str, Any]],
    responses={
        200: {
            "description": "Successfully crawled video list.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "url": "https://xhamster.com/videos/some-video-12345",
                            "title": "Some Video Title",
                            "thumbnail_url": "https://thumb.jpg",
                            "duration": "10:00",
                            "views": "1.2M",
                            "uploader_name": "SomeUploader",
                        }
                    ]
                }
            },
        },
        400: {"description": "Invalid URL"},
        500: {"description": "Internal server error"},
    },
)
async def crawl_videos(
    base_url: str = Query(
        ..., description="The base URL to start crawling from."
    ),
    start_page: int = Query(1, description="The starting page number.", ge=1),
    max_pages: int = Query(5, description="The maximum number of pages to crawl.", ge=1, le=20),
    per_page_limit: int = Query(0, description="Limit of items per page (0 for no limit).", ge=0),
    max_items: int = Query(500, description="Maximum total items to return.", ge=1, le=2000),
) -> JSONResponse:
    if not is_valid_url(base_url) or not xhamster.can_handle(urlparse(base_url).hostname):
        raise HTTPException(status_code=400, detail="Invalid or unsupported URL")

    try:
        items = await xhamster.crawl_videos(
            base_url=base_url,
            start_page=start_page,
            max_pages=max_pages,
            per_page_limit=per_page_limit,
            max_items=max_items,
        )
        return JSONResponse(content=items)
    except Exception as e:
        print(f"Error crawling videos from {base_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")


# This is the main entry point for Vercel
handler = app
