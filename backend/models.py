from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class Image(BaseModel):
    id: str
    originalUrl: str
    title: Optional[str] = None
    floorPlan: bool = False


class Platform(BaseModel):
    name: str
    url: str
    id: Optional[str] = None
    creationDate: Optional[str] = None
    publishDate: Optional[str] = None
    active: Optional[bool] = None


class Address(BaseModel):
    ISO_3166_1_alpha_2: Optional[str] = Field(None, alias="ISO_3166-1_alpha-2")
    ISO_3166_1_alpha_3: Optional[str] = Field(None, alias="ISO_3166-1_alpha-3")
    city: str
    postcode: str
    state: Optional[str] = None
    country: Optional[str] = None
    displayName: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None

    class Config:
        populate_by_name = True


class LocationFactor(BaseModel):
    population: Optional[int] = None
    hasUniversity: Optional[bool] = None
    unemploymentRate: Optional[float] = None
    score: Optional[int] = None
    unemploymentRateScore: Optional[int] = None
    universityScore: Optional[int] = None
    populationScore: Optional[int] = None
    populationTrendScore: Optional[float] = None
    populationTrend: Optional[Dict[str, int]] = None
    numberOfStudents: Optional[int] = None


class Aggregations(BaseModel):
    district: Optional[Dict[str, Any]] = None
    location: Optional[Dict[str, Any]] = None
    similarListing: Optional[Dict[str, Any]] = None


class MetaSpPrice(BaseModel):
    model: Optional[str] = None
    standarderror: Optional[float] = None
    score: Optional[float] = None
    range: Optional[Dict[str, float]] = None


class ListingDetail(BaseModel):
    id: str
    title: str
    zip: str
    buyingPrice: int
    rooms: float
    squareMeter: float
    comission: Optional[float] = None
    platforms: List[Platform] = []
    rentPricePerSqm: Optional[float] = None
    metaSpRentPricePerSqm: Optional[MetaSpPrice] = None
    pricePerSqm: Optional[float] = None
    spPricePerSqm: Optional[float] = None
    metaSpPricePerSqm: Optional[MetaSpPrice] = None
    rentPrice: Optional[float] = None
    rentPriceCurrent: Optional[float] = None
    rentPriceCurrentPerSqm: Optional[float] = None
    address: Address
    energyEfficiencyClass: Optional[str] = None
    region: Optional[str] = None
    foreClosure: bool = False
    locationFactor: Optional[LocationFactor] = None
    grossReturn: Optional[float] = None
    grossReturnCurrent: Optional[float] = None
    constructionYear: Optional[int] = None
    apartmentType: Optional[str] = None
    condition: Optional[str] = None
    lastRefurbishment: Optional[int] = None
    lift: Optional[bool] = None
    floor: Optional[int] = None
    numberOfFloors: Optional[int] = None
    cellar: bool = False
    balcony: bool = False
    garden: bool = False
    active: bool = True
    rented: bool = False
    publishDate: Optional[str] = None
    privateOffer: bool = False
    aggregations: Optional[Aggregations] = None
    leasehold: bool = False
    priceInMarket: Optional[float] = None
    oAddress: Optional[Dict[str, Any]] = None
    originalAddress: Optional[Dict[str, Any]] = None
    houseMoney: Optional[float] = None
    images: List[Image] = []
    buyingPriceHistory: Optional[List[Dict[str, Any]]] = None
    priceReduced: bool = False
    priceIncreased: bool = False
    runningTime: Optional[int] = None
    lastUpdatedAt: Optional[str] = None
    favorite: Optional[int] = None
    favoriteDate: Optional[str] = None
    cashFlow: Optional[float] = None
    ownCapitalReturn: Optional[float] = None
    cashFlowPerLivingUnit: Optional[float] = None
    hasImages: bool = False

    class Config:
        populate_by_name = True


class ListingCard(BaseModel):
    """Minimal listing for card display"""
    id: str
    title: str
    buyingPrice: int
    rooms: float
    squareMeter: float
    city: str
    zip: str
    imageUrl: Optional[str] = None
    platformUrl: Optional[str] = None
    platformName: Optional[str] = None
    lift: Optional[bool] = None
    cellar: Optional[bool] = None
    balcony: Optional[bool] = None
    garden: Optional[bool] = None
    constructionYear: Optional[int] = None
    pricePerSqm: Optional[float] = None


class ListingsResponse(BaseModel):
    listings: List[ListingCard]
    total: int
    page: int
    limit: int


class StatsResponse(BaseModel):
    min_price: int
    max_price: int
    min_rooms: float
    max_rooms: float
    total_listings: int


class CitiesResponse(BaseModel):
    cities: List[str]
