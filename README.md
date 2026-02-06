# Immobilien Suche - Real Estate Listings Web Application

A web application for browsing and filtering real estate listings from the ThinkImmo dataset. Features price and room filtering, responsive design, and detailed listing information.

## Features

- **Filter by Price**: Set minimum and maximum price range
- **Filter by Rooms**: Select one or multiple room counts (1, 2, 3, 4, 5+)
- **Filter by City**: Choose from 5 German cities (München, Berlin, Hamburg, Köln, Frankfurt am Main)
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Detail Modal**: Click on any listing to see complete information including multiple images
- **Original Links**: Direct links to original listings on property platforms (Immowelt, etc.)
- **Pagination**: Browse through listings with easy navigation

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data**: 500 real estate listings in JSON format

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Create Virtual Environment (Recommended)

```bash
# Navigate to project directory
cd c:\Users\biberd\Documents\Claude\Immo

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Or on macOS/Linux:
# source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Run the Application

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see output similar to:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
INFO:     Loaded 500 listings from 5 cities
```

### 4. Open in Browser

Visit **http://localhost:8000** in your web browser

### 5. API Documentation

Interactive API documentation available at **http://localhost:8000/docs**

## Usage

### Filtering Listings

1. **By Price**: Enter minimum and/or maximum price in the sidebar
2. **By Rooms**: Check the boxes for 1, 2, 3, 4, or 5+ rooms (multiple selections allowed)
3. **By City**: Select a city from the dropdown menu
4. **Reset**: Click "Filter zurücksetzen" to clear all filters

Filters are applied in real-time as you make changes.

### Viewing Details

1. Click the **"Details"** button on any listing card
2. A modal will open showing:
   - Full images gallery (click thumbnails to change image)
   - Complete property information
   - Financial metrics (price per m², estimated rent, return)
   - Features (lift, balcony, garden, cellar)
   - Energy efficiency class
   - Original listing link
3. Click the property platform link to open the original listing
4. Click outside the modal or press **Esc** to close

### Pagination

- Use **"Zurück"** (Back) and **"Weiter"** (Next) buttons to browse through pages
- 50 listings are displayed per page by default

## File Structure

```
c:\Users\biberd\Documents\Claude\Immo\
├── backend/
│   ├── main.py              # FastAPI app and endpoints
│   ├── models.py            # Pydantic data models
│   ├── data_loader.py       # Dataset loading and filtering logic
│   └── requirements.txt     # Python dependencies
├── static/
│   ├── index.html           # Main HTML structure
│   ├── styles.css           # All styling
│   └── app.js               # Frontend JavaScript logic
├── thinkimmo_dataset.json   # Real estate listings data (500 listings)
└── README.md                # This file
```

## API Endpoints

### GET /api/stats
Returns dataset statistics for filter initialization.

**Response:**
```json
{
  "min_price": 157000,
  "max_price": 5390000,
  "min_rooms": 1,
  "max_rooms": 10,
  "total_listings": 500
}
```

### GET /api/cities
Returns list of available cities.

**Response:**
```json
{
  "cities": ["Berlin", "Frankfurt am Main", "Hamburg", "Köln", "München"]
}
```

### GET /api/listings
Returns filtered and paginated listings.

**Query Parameters:**
- `min_price` (integer): Minimum price filter
- `max_price` (integer): Maximum price filter
- `rooms` (string): Comma-separated room numbers (e.g., "2,3,4")
- `city` (string): City name filter
- `limit` (integer): Results per page (default 50, max 100)
- `offset` (integer): Pagination offset (default 0)

**Example:** `/api/listings?min_price=200000&max_price=500000&rooms=2,3&city=München&limit=50&offset=0`

**Response:**
```json
{
  "listings": [
    {
      "id": "abc123",
      "title": "Schöne 3-Zimmer Wohnung",
      "buyingPrice": 350000,
      "rooms": 3,
      "squareMeter": 85,
      "city": "München",
      "zip": "81477",
      "imageUrl": "https://...",
      "platformUrl": "https://www.immowelt.de/...",
      "platformName": "immowelt",
      ...
    }
  ],
  "total": 42,
  "page": 0,
  "limit": 50
}
```

### GET /api/listings/{listing_id}
Returns complete listing details.

**Parameters:**
- `listing_id` (string): Unique listing ID

**Response:** Complete listing object with all 53+ fields including images array, address details, financial metrics, etc.

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, specify a different port:
```bash
uvicorn backend.main:app --port 8001
```

### Module Not Found Error
Make sure virtual environment is activated and requirements are installed:
```bash
venv\Scripts\activate
pip install -r backend/requirements.txt
```

### JSON Parse Error
Ensure `thinkimmo_dataset.json` is in the correct location (project root directory).

### No Images Displaying
- Check browser console for CORS errors
- Verify internet connection (images are loaded from external CDN)
- 4 listings don't have images and will show a placeholder

### Filters Not Working
- Check browser console for JavaScript errors (F12 → Console tab)
- Try clearing browser cache and refreshing the page
- Ensure backend API is running (check console output)

## Development

### Running in Development Mode
The `--reload` flag enables auto-restart when code changes:
```bash
uvicorn backend.main:app --reload
```

### Testing with Swagger UI
Open http://localhost:8000/docs to test all API endpoints interactively.

### Building Production Setup
For production deployment:
1. Remove `--reload` flag
2. Add proper CORS configuration (restrict origins)
3. Use a production ASGI server (Gunicorn, etc.)
4. Enable HTTPS
5. Set appropriate security headers

## Performance Notes

- Initial page load: ~2 seconds
- Filter application: <500ms
- Dataset loading on startup: <1 second
- Memory usage: ~50-100MB

## Known Limitations

- 4 listings (out of 500) have no images and show a placeholder
- All 500 listings are loaded into memory on startup
- Text search across listings is not implemented

## Future Enhancements

- Additional filters (apartment type, features, energy class)
- Text search functionality
- Map view with listing locations
- Sort options (price, size, return percentage)
- Favorite/bookmark functionality
- Export filtered results to CSV/PDF
- Comparison view for multiple listings
- Dark mode toggle
- Real-time data updates

## License

This project uses the ThinkImmo dataset for demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console (F12) for errors
3. Verify all files are in correct locations
4. Ensure Python version is 3.8 or higher

## Credits

- FastAPI: Modern Python web framework
- Dataset: ThinkImmo real estate listings
- Icons and design: Custom CSS
