// State Management
const state = {
    filters: {
        minPrice: null,
        maxPrice: null,
        rooms: [],
        city: null
    },
    currentPage: 0,
    limit: 50,
    stats: null,
    cities: [],
    currentListing: null
};

// API Functions
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching stats:', error);
        showError('Fehler beim Laden der Statistiken');
        return null;
    }
}

async function fetchCities() {
    try {
        const response = await fetch('/api/cities');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching cities:', error);
        showError('Fehler beim Laden der Städte');
        return null;
    }
}

async function fetchListings() {
    try {
        showLoading(true);
        hideError();

        const params = new URLSearchParams();
        params.append('limit', state.limit);
        params.append('offset', state.currentPage * state.limit);

        if (state.filters.minPrice !== null) {
            params.append('min_price', state.filters.minPrice);
        }
        if (state.filters.maxPrice !== null) {
            params.append('max_price', state.filters.maxPrice);
        }
        if (state.filters.rooms.length > 0) {
            params.append('rooms', state.filters.rooms.join(','));
        }
        if (state.filters.city) {
            params.append('city', state.filters.city);
        }

        const response = await fetch(`/api/listings?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const data = await response.json();
        showLoading(false);

        return data;
    } catch (error) {
        console.error('Error fetching listings:', error);
        showError('Fehler beim Laden der Inserate');
        showLoading(false);
        return null;
    }
}

async function fetchListingDetail(listingId) {
    try {
        const response = await fetch(`/api/listings/${listingId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching listing detail:', error);
        showError('Fehler beim Laden des Inserats');
        return null;
    }
}

// Render Functions
function renderListingCard(listing) {
    const imageUrl = listing.imageUrl || getPlaceholderImage();
    const pricePerSqm = listing.pricePerSqm ? `€${Math.round(listing.pricePerSqm)}/m²` : '';
    const features = [];

    if (listing.lift) features.push('<span class="feature-icon" title="Aufzug">🛗</span>');
    if (listing.balcony) features.push('<span class="feature-icon" title="Balkon">🏡</span>');
    if (listing.garden) features.push('<span class="feature-icon" title="Garten">🌳</span>');
    if (listing.cellar) features.push('<span class="feature-icon" title="Keller">🔑</span>');

    const platformName = listing.platformName || 'Inserat';
    const platformUrl = listing.platformUrl || '#';

    return `
        <div class="listing-card" data-id="${listing.id}">
            <img src="${imageUrl}" alt="${listing.title}" class="listing-card-image" loading="lazy">
            <div class="listing-card-body">
                <div class="listing-card-price">€${listing.buyingPrice.toLocaleString('de-DE')}</div>
                <div class="listing-card-specs">${listing.squareMeter}m² • ${listing.rooms} Zimmer ${pricePerSqm ? '• ' + pricePerSqm : ''}</div>
                <div class="listing-card-location">${listing.city}, ${listing.zip}</div>
                <div class="listing-card-features">${features.join('')}</div>
                <div class="listing-card-actions">
                    <button onclick="showDetailModal('${listing.id}')" class="btn-detail">Details</button>
                    <a href="${platformUrl}" target="_blank" rel="noopener noreferrer">${platformName}</a>
                </div>
            </div>
        </div>
    `;
}

function renderListings(listingsData) {
    const grid = document.getElementById('listingGrid');

    if (!listingsData || !listingsData.listings || listingsData.listings.length === 0) {
        grid.innerHTML = '';
        document.getElementById('noResultsContainer').style.display = 'block';
        document.getElementById('pagination').innerHTML = '';
        return;
    }

    document.getElementById('noResultsContainer').style.display = 'none';
    grid.innerHTML = listingsData.listings.map(listing => renderListingCard(listing)).join('');

    // Render pagination
    renderPagination(listingsData);
}

function renderPagination(listingsData) {
    const paginationContainer = document.getElementById('pagination');
    const totalPages = Math.ceil(listingsData.total / state.limit);

    if (totalPages <= 1) {
        paginationContainer.innerHTML = '';
        return;
    }

    let html = `<button onclick="previousPage()" ${state.currentPage === 0 ? 'disabled' : ''}>← Zurück</button>`;
    html += `<span class="page-info">Seite ${state.currentPage + 1} von ${totalPages} (${listingsData.total} Inserate)</span>`;
    html += `<button onclick="nextPage()" ${state.currentPage >= totalPages - 1 ? 'disabled' : ''}>Weiter →</button>`;

    paginationContainer.innerHTML = html;
}

function renderDetailModal(listing) {
    if (!listing) return;

    const imageUrl = listing.images && listing.images.length > 0 ? listing.images[0].originalUrl : getPlaceholderImage();
    const platformUrl = listing.platforms && listing.platforms.length > 0 ? listing.platforms[0].url : '#';
    const platformName = listing.platforms && listing.platforms.length > 0 ? listing.platforms[0].name : 'Inserat';

    // Build features list
    const features = [
        { name: 'Aufzug', value: listing.lift },
        { name: 'Balkon', value: listing.balcony },
        { name: 'Garten', value: listing.garden },
        { name: 'Keller', value: listing.cellar }
    ];

    const featuresHtml = features
        .map(f => `<div class="feature-item ${f.value ? 'yes' : 'no'}">${f.name}</div>`)
        .join('');

    // Build thumbnail gallery
    const thumbnailsHtml = listing.images && listing.images.length > 0
        ? listing.images.slice(0, 5)
            .map((img, idx) => `<div class="detail-thumbnail" onclick="changeImage('${img.originalUrl}')">
                <img src="${img.originalUrl}" alt="Bild ${idx + 1}" loading="lazy">
            </div>`)
            .join('')
        : '';

    const addressDisplay = listing.address ? `${listing.address.city}, ${listing.address.postcode}` : 'Keine Adresse';

    const html = `
        <div class="detail-container">
            <div class="detail-gallery">
                <img id="mainImage" src="${imageUrl}" alt="${listing.title}" class="detail-main-image">
                ${thumbnailsHtml ? `<div class="detail-thumbnails">${thumbnailsHtml}</div>` : ''}
            </div>
            <div class="detail-info">
                <div class="detail-price">€${listing.buyingPrice.toLocaleString('de-DE')}</div>
                <h2 class="detail-title">${listing.title}</h2>
                <div class="detail-location">${addressDisplay}</div>

                <div class="detail-specs">
                    <div class="spec-item">
                        <div class="spec-label">Quadratmeter</div>
                        <div class="spec-value">${listing.squareMeter}m²</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Zimmer</div>
                        <div class="spec-value">${listing.rooms}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Preis/m²</div>
                        <div class="spec-value">€${listing.pricePerSqm ? Math.round(listing.pricePerSqm) : 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Baujahr</div>
                        <div class="spec-value">${listing.constructionYear || 'N/A'}</div>
                    </div>
                </div>

                <div class="detail-sections">
                    ${listing.energyEfficiencyClass ? `<div class="section">
                        <div class="spec-item">
                            <div class="spec-label">Energieeffizienzklasse</div>
                            <div class="spec-value">${listing.energyEfficiencyClass}</div>
                        </div>
                    </div>` : ''}

                    <div class="section">
                        <h3 class="section-title">Ausstattung</h3>
                        <div class="features-list">${featuresHtml}</div>
                    </div>

                    ${listing.rentPrice ? `<div class="section">
                        <div class="spec-item">
                            <div class="spec-label">Mietpreis (geschätzt)</div>
                            <div class="spec-value">€${Math.round(listing.rentPrice)}/Monat</div>
                        </div>
                    </div>` : ''}

                    ${listing.grossReturn ? `<div class="section">
                        <div class="spec-item">
                            <div class="spec-label">Rendite</div>
                            <div class="spec-value">${listing.grossReturn.toFixed(2)}%</div>
                        </div>
                    </div>` : ''}

                    <div class="section">
                        <h3 class="section-title">Zum Inserat</h3>
                        <div class="platform-links">
                            <a href="${platformUrl}" target="_blank" rel="noopener noreferrer" class="platform-link">
                                <span class="platform-icon">🔗</span>
                                <span>Öffnen auf ${platformName}</span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    return html;
}

// Modal Functions
function showDetailModal(listingId) {
    const modal = document.getElementById('detailModal');
    modal.style.display = 'flex';

    fetchListingDetail(listingId).then(listing => {
        if (listing) {
            state.currentListing = listing;
            document.getElementById('modalBody').innerHTML = renderDetailModal(listing);
        }
    });
}

function closeDetailModal() {
    document.getElementById('detailModal').style.display = 'none';
    document.getElementById('modalBody').innerHTML = '';
}

function changeImage(imageUrl) {
    document.getElementById('mainImage').src = imageUrl;
}

// Filter Functions
function collectFilters() {
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const city = document.getElementById('cityFilter').value;
    const roomCheckboxes = Array.from(document.querySelectorAll('.room-filter:checked'));

    state.filters.minPrice = minPrice ? parseInt(minPrice) : null;
    state.filters.maxPrice = maxPrice ? parseInt(maxPrice) : null;
    state.filters.rooms = roomCheckboxes.map(cb => cb.value);
    state.filters.city = city || null;
}

const debouncedFilter = debounce(() => {
    collectFilters();
    state.currentPage = 0;
    loadListings();
}, 300);

function resetFilters() {
    document.getElementById('minPrice').value = '';
    document.getElementById('maxPrice').value = '';
    document.getElementById('cityFilter').value = '';
    document.querySelectorAll('.room-filter').forEach(cb => cb.checked = false);

    state.filters = {
        minPrice: null,
        maxPrice: null,
        rooms: [],
        city: null
    };
    state.currentPage = 0;

    loadListings();
}

// Pagination Functions
function previousPage() {
    if (state.currentPage > 0) {
        state.currentPage--;
        loadListings();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function nextPage() {
    state.currentPage++;
    loadListings();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// UI Functions
function showLoading(show) {
    const indicator = document.getElementById('loadingIndicator');
    if (show) {
        indicator.style.display = 'flex';
        document.getElementById('listingGrid').innerHTML = '';
    } else {
        indicator.style.display = 'none';
    }
}

function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorContainer.style.display = 'block';
}

function hideError() {
    document.getElementById('errorContainer').style.display = 'none';
}

function getPlaceholderImage() {
    return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23f1f5f9" width="400" height="300"/%3E%3Ctext x="50%25" y="50%25" font-size="18" fill="%2394a3b8" text-anchor="middle" dy=".3em"%3EKein Bild verfügbar%3C/text%3E%3C/svg%3E';
}

// Utility Functions
function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

// Main Load Function
async function loadListings() {
    const data = await fetchListings();
    if (data) {
        renderListings(data);
    }
}

// Initialize
async function initialize() {
    // Load stats
    const stats = await fetchStats();
    if (stats) {
        state.stats = stats;
    }

    // Load cities
    const citiesData = await fetchCities();
    if (citiesData) {
        state.cities = citiesData.cities;
        populateCitiesDropdown();
    }

    // Load initial listings
    await loadListings();
}

function populateCitiesDropdown() {
    const select = document.getElementById('cityFilter');
    const currentValue = select.value;

    state.cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city;
        option.textContent = city;
        select.appendChild(option);
    });

    if (currentValue) {
        select.value = currentValue;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Filter listeners
    document.getElementById('minPrice').addEventListener('change', debouncedFilter);
    document.getElementById('maxPrice').addEventListener('change', debouncedFilter);
    document.getElementById('cityFilter').addEventListener('change', debouncedFilter);
    document.querySelectorAll('.room-filter').forEach(checkbox => {
        checkbox.addEventListener('change', debouncedFilter);
    });

    // Reset button
    document.getElementById('resetFilters').addEventListener('click', resetFilters);

    // Modal close handlers
    document.getElementById('detailModal').addEventListener('click', (e) => {
        if (e.target.id === 'detailModal' || e.target.classList.contains('modal-overlay')) {
            closeDetailModal();
        }
    });

    document.querySelector('.modal-close').addEventListener('click', closeDetailModal);

    // Keyboard close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('detailModal').style.display !== 'none') {
            closeDetailModal();
        }
    });

    // Initialize
    initialize();
});
