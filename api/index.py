
from fastapi import FastAPI, HTTPException
from scraper import SCRAPERS, get_host

app = FastAPI()

@app.get("/list")
async def list_videos(base_url: str, page: int = 1, limit: int = 20):
    host = get_host(base_url)
    if host not in SCRAPERS:
        raise HTTPException(status_code=404, detail="Scraper not found for this host")
    scraper = SCRAPERS[host]
    try:
        return await scraper["list"](base_url, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch url: {e}")

@app.get("/scrape")
async def scrape_video(url: str):
    host = get_host(url)
    if host not in SCRAPERS:
        raise HTTPException(status_code=404, detail="Scraper not found for this host")
    scraper = SCRAPERS[host]
    try:
        return await scraper["scrape"](url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch url: {e}")

@app.get("/crawl")
async def crawl_videos(base_url: str, start_page: int = 1, max_pages: int = 5, per_page_limit: int = 0, max_items: int = 500):
    host = get_host(base_url)
    if host not in SCRAPERS:
        raise HTTPException(status_code=404, detail="Scraper not found for this host")
    scraper = SCRAPERS[host]
    try:
        return await scraper["crawl"](base_url, start_page, max_pages, per_page_limit, max_items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch url: {e}")
