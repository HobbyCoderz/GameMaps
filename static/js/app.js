document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadGames();
    setupEventListeners();
});

// Global state for markers
let currentMarkers = [];
let sidebarZoomLevel = 1; // Default zoom level for sidebar marker click

// UI Elements
const gameSelect = document.getElementById('game-select');
const addGameBtn = document.getElementById('add-game-btn');
const addGameModal = document.getElementById('add-game-modal');
const addGameForm = document.getElementById('add-game-form');
const cancelGameBtn = document.getElementById('cancel-game-btn');
const settingsBtn = document.getElementById('settings-btn');
const settingsSection = document.getElementById('settings-section');
const deleteMapBtn = document.getElementById('delete-map-btn');
const sidebarZoomSelect = document.getElementById('sidebar-zoom-level');

const infoModalBtn = document.getElementById('info-modal-btn');
const infoModal = document.getElementById('info-modal');
const closeInfoModalBtn = document.getElementById('close-info-modal-btn');

const addMarkerModal = document.getElementById('add-marker-modal');
const addMarkerForm = document.getElementById('add-marker-form');
const cancelMarkerBtn = document.getElementById('cancel-marker-btn');
const markerList = document.getElementById('marker-list');

const sortAlphaCheckbox = document.getElementById('sort-alpha');
const groupTypeCheckbox = document.getElementById('group-type');
const filterTextInput = document.getElementById('filter-text');

function setupEventListeners() {
    // Sidebar Controls
    sortAlphaCheckbox.addEventListener('change', renderSidebar);
    groupTypeCheckbox.addEventListener('change', renderSidebar);
    filterTextInput.addEventListener('input', renderSidebar);

    // Settings Controls
    if (sidebarZoomSelect) {
        sidebarZoomSelect.addEventListener('change', (e) => {
            sidebarZoomLevel = parseInt(e.target.value);
        });
    }

    // Game Selection
    gameSelect.addEventListener('change', (e) => {
        const option = e.target.selectedOptions[0];
        const mapPath = option.dataset.mapPath;
        const gameId = option.value;
        loadGameMap(gameId, mapPath, option.text);
    });

    // Add Game Modal
    addGameBtn.addEventListener('click', () => {
        addGameModal.classList.remove('hidden');
    });

    // Settings toggle
    if (settingsBtn && settingsSection) {
        settingsBtn.addEventListener('click', () => {
            const isHidden = settingsSection.classList.toggle('hidden');
            settingsBtn.classList.toggle('active', !isHidden);
        });
    }

    // Delete Map action
    if (deleteMapBtn) {
        deleteMapBtn.addEventListener('click', () => {
            if (!currentGameId) {
                alert('No map is currently loaded.');
                return;
            }

            if (!confirm('Delete the currently loaded map and all its markers? This cannot be undone.')) return;

            fetch(`/api/games/${currentGameId}`, { method: 'DELETE' })
                .then(res => res.json())
                .then(result => {
                    if (result && result.status === 'success') {
                        // Clear map and reload games
                        currentGameId = null;
                        if (currentImageOverlay) {
                            try { map.removeLayer(currentImageOverlay); } catch (e) {}
                            currentImageOverlay = null;
                        }
                        markersLayer.clearLayers();
                        loadGames();
                        document.getElementById('marker-list').innerHTML = '';
                        // Hide settings section
                        if (settingsSection) settingsSection.classList.add('hidden');
                        if (settingsBtn) settingsBtn.classList.remove('active');
                    } else {
                        alert('Failed to delete map.');
                    }
                })
                .catch(() => alert('Failed to delete map.'));
        });
    }

    // Info Modal Controls
    if (infoModalBtn && infoModal && closeInfoModalBtn) {
        infoModalBtn.addEventListener('click', () => {
            infoModal.classList.remove('hidden');
        });

        closeInfoModalBtn.addEventListener('click', () => {
            infoModal.classList.add('hidden');
        });
    }

    cancelGameBtn.addEventListener('click', () => {
        addGameModal.classList.add('hidden');
    });

    addGameForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addGameForm);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/games', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
            .then(res => res.json())
            .then(game => {
                if (game.error) {
                    alert(game.error);
                } else {
                    addGameModal.classList.add('hidden');
                    addGameForm.reset();
                    loadGames(); // Reload list
                }
            });
    });

    // Add Marker Modal
    cancelMarkerBtn.addEventListener('click', () => {
        addMarkerModal.classList.add('hidden');
    });

    addMarkerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(addMarkerForm);
        const id = formData.get('id');

        const method = id ? 'PUT' : 'POST';
        const url = id ? `/api/markers/${id}` : '/api/markers';

        if (!id) formData.append('game_id', currentGameId);

        fetch(url, {
            method: method,
            body: formData
        })
            .then(res => res.json())
            .then(() => {
                addMarkerModal.classList.add('hidden');
                addMarkerForm.reset();
                loadMarkers(currentGameId);
            });
    });
}

function loadGames() {
    fetch('/api/games')
        .then(res => res.json())
        .then(games => {
            gameSelect.innerHTML = '<option value="" disabled selected>Select a Game</option>';
            games.forEach(game => {
                const option = document.createElement('option');
                option.value = game.id;
                option.textContent = game.name;
                option.dataset.mapPath = game.map_path;
                gameSelect.appendChild(option);
            });
        });
}

function openAddMarkerModal(lat, lng) {
    addMarkerForm.reset();
    document.getElementById('current-image-preview').innerHTML = '';
    addMarkerForm.querySelector('[name="id"]').value = '';
    addMarkerForm.querySelector('[name="lat"]').value = lat;
    addMarkerForm.querySelector('[name="lng"]').value = lng;
    document.getElementById('marker-modal-title').textContent = 'Add Marker';
    addMarkerModal.classList.remove('hidden');
}

function openEditMarkerModal(marker) {
    const form = addMarkerForm;
    form.querySelector('[name="id"]').value = marker.id;
    form.querySelector('[name="lat"]').value = marker.lat;
    form.querySelector('[name="lng"]').value = marker.lng;
    form.querySelector('[name="title"]').value = marker.title;
    form.querySelector('[name="type"]').value = marker.type;
    form.querySelector('[name="game_coords"]').value = marker.game_coords || '';
    form.querySelector('[name="note"]').value = marker.note || '';

    const preview = document.getElementById('current-image-preview');
    if (marker.image_path) {
        preview.innerHTML = `Current Image: <a href="${marker.image_path}" target="_blank">${marker.image_path.split('/').pop()}</a>`;
    } else {
        preview.innerHTML = '';
    }

    document.getElementById('marker-modal-title').textContent = 'Edit Marker';
    addMarkerModal.classList.remove('hidden');
}

function updateMarkerList(markers) {
    currentMarkers = markers;
    renderSidebar();
}

function renderSidebar() {
    markerList.innerHTML = '';

    let markersToRender = [...currentMarkers];

    // Filter by Text
    const filterText = filterTextInput.value.toLowerCase();
    if (filterText) {
        markersToRender = markersToRender.filter(marker => {
            const title = (marker.title || '').toLowerCase();
            const note = (marker.note || '').toLowerCase();
            return title.includes(filterText) || note.includes(filterText);
        });
    }

    // Update Leaflet marker visibility based on filter results
    if (typeof getLeafletMarkers === 'function' && typeof markersLayer !== 'undefined') {
        const leafletMarkers = getLeafletMarkers();
        const visibleMarkerIds = new Set(markersToRender.map(m => m.id));

        for (const id in leafletMarkers) {
            const marker = leafletMarkers[id];
            // Check if the marker should be visible
            if (visibleMarkerIds.has(parseInt(id))) {
                // Ensure marker is added to the layer group if it was previously removed
                if (!markersLayer.hasLayer(marker)) {
                    markersLayer.addLayer(marker);
                }
            } else {
                // Ensure marker is removed from the layer group if it is currently present
                if (markersLayer.hasLayer(marker)) {
                    markersLayer.removeLayer(marker);
                }
            }
        }
    }

    // Sort Alphabetically
    if (sortAlphaCheckbox.checked) {
        markersToRender.sort((a, b) => a.title.localeCompare(b.title));
    }

    // Group by Type
    if (groupTypeCheckbox.checked) {
        const groups = {};
        markersToRender.forEach(marker => {
            const type = marker.type || 'default';
            if (!groups[type]) {
                groups[type] = [];
            }
            groups[type].push(marker);
        });

        // Render groups
        Object.keys(groups).sort().forEach(type => {
            const groupContainer = document.createElement('div');
            groupContainer.className = 'marker-group';

            const groupHeader = document.createElement('h4');
            groupHeader.className = 'group-header';
            groupHeader.textContent = type.charAt(0).toUpperCase() + type.slice(1);
            groupContainer.appendChild(groupHeader);

            groups[type].forEach(marker => {
                groupContainer.appendChild(createMarkerElement(marker));
            });

            markerList.appendChild(groupContainer);
        });
    } else {
        // Render flat list
        markersToRender.forEach(marker => {
            markerList.appendChild(createMarkerElement(marker));
        });
    }
}

function createMarkerElement(marker) {
    const item = document.createElement('div');
    item.className = 'marker-item';
    item.innerHTML = `
        <div class="marker-info">
            <h3>${marker.title}</h3>
            <p>${marker.note ? marker.note.substring(0, 50) + (marker.note.length > 50 ? '...' : '') : ''}</p>
        </div>
        <button class="btn-secondary edit-btn" style="margin-left: auto;">Edit</button>
    `;
    item.style.display = 'flex';
    item.style.alignItems = 'center';
    item.style.justifyContent = 'space-between';

    item.querySelector('.marker-info').addEventListener('click', () => {
        map.flyTo([marker.lat, marker.lng], sidebarZoomLevel); // Zoom to marker using user setting
    });
    item.querySelector('.edit-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        openEditMarkerModal(marker);
    });
    return item;
}

// Expose openEditMarkerModal to the global scope
window.openEditMarkerModal = openEditMarkerModal;
