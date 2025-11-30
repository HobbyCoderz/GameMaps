// Map state
let map = null;
let currentImageOverlay = null;
let markersLayer = new L.LayerGroup();
let leafletMarkers = {}; // Map marker ID to Leaflet marker object
let currentGameId = null;

// Initialize map
function initMap() {
    map = L.map('map', {
        crs: L.CRS.Simple,
        minZoom: -2,
        maxZoom: 2,
        zoomControl: false
    });

    L.control.zoom({
        position: 'bottomright'
    }).addTo(map);

    markersLayer.addTo(map);

    // Map click handler for adding markers
    map.on('click', function (e) {
        if (!currentGameId || !e.originalEvent.ctrlKey) return;

        const lat = e.latlng.lat;
        const lng = e.latlng.lng;

        openAddMarkerModal(lat, lng);
    });
}

// Load a game map
function loadGameMap(gameId, mapPath, mapName) {
    currentGameId = gameId;

    // Clear existing map content
    if (currentImageOverlay) {
        map.removeLayer(currentImageOverlay);
    }
    markersLayer.clearLayers();

    // Load image to get dimensions
    const img = new Image();
    img.onload = function () {
        const w = this.width;
        const h = this.height;
        const bounds = [[0, 0], [h, w]];

        currentImageOverlay = L.imageOverlay(`/maps/${mapPath}`, bounds).addTo(map);
        map.fitBounds(bounds);

        // Add padding to max bounds to allow centering corners
        const paddingH = h * 0.5;
        const paddingW = w * 0.5;
        const maxBounds = [[-paddingH, -paddingW], [h + paddingH, w + paddingW]];
        map.setMaxBounds(maxBounds);

        loadMarkers(gameId);
    };
    img.src = `/maps/${mapPath}`;
}

// Load markers from API
function loadMarkers(gameId) {
    fetch(`/api/markers/${gameId}`)
        .then(response => response.json())
        .then(markers => {
            markersLayer.clearLayers();
            leafletMarkers = {}; // Clear stored Leaflet markers
            updateMarkerList(markers);

            markers.forEach(marker => {
                addMarkerToMap(marker);
            });
        });
}

// Add a single marker to the map
function addMarkerToMap(marker) {
    const lat = marker.lat;
    const lng = marker.lng;

    const popupContent = `
        <div class="marker-popup">
            <h3>${marker.title}</h3>
            <p>${marker.note || ''}</p>
            ${marker.game_coords ? `<p><small>Coords: ${marker.game_coords}</small></p>` : ''}
            ${marker.image_path ? `<img src="${marker.image_path}" style="max-width:100%;margin-top:5px;">` : ''}
            <button onclick="window.openEditMarkerModal(JSON.parse(decodeURIComponent('${encodeURIComponent(JSON.stringify(marker))}')))" class="btn-secondary" style="font-size:0.8rem;padding:2px 6px;margin-top:5px;">Edit</button>
            <button onclick="deleteMarker(${marker.id})" class="btn-secondary" style="font-size:0.8rem;padding:2px 6px;margin-top:5px;">Delete</button>
        </div>
    `;

    const m = L.marker([lat, lng], { icon: getIcon(marker.type) }).bindPopup(popupContent);
    m.markerId = marker.id; // Store the marker ID on the Leaflet object
    leafletMarkers[marker.id] = m;
    markersLayer.addLayer(m);
}

function getIcon(type) {
    const validTypes = ['base', 'bomb', 'danger', 'default', 'electrical', 'factory', 'food', 'military', 'mountain', 'resource', 'tools', 'valuables', 'village', 'weapons'];
    const iconName = validTypes.includes(type) ? type : 'default';

    return L.icon({
        iconUrl: `/static/icons/${iconName}.svg`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16]
    });
}

// Global function to delete marker (called from popup)
window.deleteMarker = function (id) {
    if (confirm('Delete this marker?')) {
        fetch(`/api/markers/${id}`, { method: 'DELETE' })
            .then(() => {
                loadMarkers(currentGameId); // Reload to refresh list and map
            });
    }
};

// Expose the map of Leaflet markers
function getLeafletMarkers() {
    return leafletMarkers;
}
