import json
from pathlib import Path
from typing import Dict, List, Optional
from models import ListingDetail, ListingCard


class DataStore:
    def __init__(self):
        self.listings: List[ListingDetail] = []
        self.listings_by_id: Dict[str, ListingDetail] = {}
        self.city_index: Dict[str, List[ListingDetail]] = {}
        self.min_price: int = 0
        self.max_price: int = 0
        self.min_rooms: float = 0
        self.max_rooms: float = 0

    def load_data(self, filepath: Path) -> None:
        """Load dataset from JSON file and build indexes"""
        print(f"Loading dataset from {filepath}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract listings from all cities
        for city_name, city_data in data.get('by_city', {}).items():
            for listing_data in city_data.get('items', []):
                try:
                    listing = ListingDetail(**listing_data)
                    self.listings.append(listing)
                    self.listings_by_id[listing.id] = listing

                    # Build city index
                    if city_name not in self.city_index:
                        self.city_index[city_name] = []
                    self.city_index[city_name].append(listing)
                except Exception as e:
                    print(f"Warning: Failed to parse listing {listing_data.get('id')}: {e}")

        # Calculate stats
        self._calculate_stats()

        print(f"Loaded {len(self.listings)} listings from {len(self.city_index)} cities")
        print(f"Price range: €{self.min_price:,} - €{self.max_price:,}")
        print(f"Rooms range: {self.min_rooms} - {self.max_rooms}")

    def _calculate_stats(self) -> None:
        """Calculate min/max price and rooms"""
        if not self.listings:
            return

        prices = [l.buyingPrice for l in self.listings]
        rooms = [l.rooms for l in self.listings]

        self.min_price = min(prices)
        self.max_price = max(prices)
        self.min_rooms = min(rooms)
        self.max_rooms = max(rooms)

    def filter_listings(
        self,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        rooms: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ListingCard], int]:
        """Filter listings and return results with pagination"""

        results = self.listings[:]

        # City filter (use index for performance)
        if city and city in self.city_index:
            results = self.city_index[city][:]

        # Price filters
        if min_price is not None:
            results = [l for l in results if l.buyingPrice >= min_price]

        if max_price is not None:
            results = [l for l in results if l.buyingPrice <= max_price]

        # Rooms filter (support multiple values like "1,2,3")
        if rooms:
            try:
                room_values = [float(r.strip()) for r in rooms.split(',')]
                filtered = []
                for listing in results:
                    # Check if exact room match or 5+ rooms matching
                    if listing.rooms in room_values:
                        filtered.append(listing)
                    elif 5 in room_values and listing.rooms >= 5:
                        filtered.append(listing)
                results = filtered
            except ValueError:
                # Invalid rooms parameter, skip filtering
                pass

        # Get total count before pagination
        total = len(results)

        # Apply pagination
        paginated = results[offset:offset + limit]

        # Convert to ListingCard for API response
        cards = [self._to_listing_card(listing) for listing in paginated]

        return cards, total

    def _to_listing_card(self, listing: ListingDetail) -> ListingCard:
        """Convert ListingDetail to ListingCard with minimal fields"""
        image_url = None
        if listing.images and len(listing.images) > 0:
            image_url = listing.images[0].originalUrl

        platform_url = None
        platform_name = None
        if listing.platforms and len(listing.platforms) > 0:
            platform_url = listing.platforms[0].url
            platform_name = listing.platforms[0].name

        return ListingCard(
            id=listing.id,
            title=listing.title,
            buyingPrice=listing.buyingPrice,
            rooms=listing.rooms,
            squareMeter=listing.squareMeter,
            city=listing.address.city,
            zip=listing.zip,
            imageUrl=image_url,
            platformUrl=platform_url,
            platformName=platform_name,
            lift=listing.lift,
            cellar=listing.cellar,
            balcony=listing.balcony,
            garden=listing.garden,
            constructionYear=listing.constructionYear,
            pricePerSqm=listing.pricePerSqm
        )

    def get_listing_detail(self, listing_id: str) -> Optional[ListingDetail]:
        """Get complete listing by ID"""
        return self.listings_by_id.get(listing_id)
