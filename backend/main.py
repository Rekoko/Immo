import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from data_loader import DataStore
from models import ListingsResponse, ListingDetail, StatsResponse, CitiesResponse


# Initialize FastAPI app
app = FastAPI(
    title="Real Estate Listings API",
    description="API for browsing and filtering real estate listings"
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data store
data_store = DataStore()


@app.on_event("startup")
async def startup_event():
    """Load dataset on application startup"""
    dataset_path = Path(__file__).parent.parent / "thinkimmo_dataset.json"
    data_store.load_data(dataset_path)


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get min/max price and rooms for filter initialization"""
    return StatsResponse(
        min_price=data_store.min_price,
        max_price=data_store.max_price,
        min_rooms=data_store.min_rooms,
        max_rooms=data_store.max_rooms,
        total_listings=len(data_store.listings)
    )


@app.get("/api/cities", response_model=CitiesResponse)
async def get_cities():
    """Get list of available cities"""
    cities = sorted(list(data_store.city_index.keys()))
    return CitiesResponse(cities=cities)


@app.get("/api/listings", response_model=ListingsResponse)
async def get_listings(
    min_price: Optional[int] = Query(None, description="Minimum buying price"),
    max_price: Optional[int] = Query(None, description="Maximum buying price"),
    rooms: Optional[str] = Query(None, description="Comma-separated room numbers (e.g., '2,3,4')"),
    city: Optional[str] = Query(None, description="Filter by city name"),
    limit: int = Query(50, ge=1, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Get filtered listings with pagination.

    Query parameters:
    - min_price: Filter by minimum price
    - max_price: Filter by maximum price
    - rooms: Comma-separated room numbers (e.g., '1,2,3')
    - city: Filter by city name
    - limit: Results per page (default 50, max 100)
    - offset: Pagination offset (default 0)
    """
    cards, total = data_store.filter_listings(
        min_price=min_price,
        max_price=max_price,
        rooms=rooms,
        city=city,
        limit=limit,
        offset=offset
    )

    page = offset // limit if limit > 0 else 0

    return ListingsResponse(
        listings=cards,
        total=total,
        page=page,
        limit=limit
    )


@app.get("/api/listings/{listing_id}", response_model=ListingDetail)
async def get_listing_detail(listing_id: str):
    """Get complete listing details by ID"""
    listing = data_store.get_listing_detail(listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail=f"Listing {listing_id} not found")

    return listing


# Mount static files - must be last
static_path = Path(__file__).parent.parent / "static"
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
