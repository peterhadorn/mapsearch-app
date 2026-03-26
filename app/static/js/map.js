const MapModule = {
    map: null,
    markers: [],  // current pin markers
    markerLayer: null,

    init() {
        // Initialize Leaflet map — zoomed in on Manhattan
        this.map = L.map('map', {
            center: [40.7480, -73.9860],  // Manhattan
            zoom: 13,
            zoomControl: false,
        });

        // Add zoom control to bottom-right
        L.control.zoom({ position: 'bottomright' }).addTo(this.map);

        // CartoDB Dark Matter tiles (matches dark theme)
        this._darkTiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 20,
        });

        // CartoDB Positron tiles (for light theme)
        this._lightTiles = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO',
            subdomains: 'abcd',
            maxZoom: 20,
        });

        // Default to dark
        const theme = document.documentElement.getAttribute('data-theme');
        if (theme === 'light') {
            this._lightTiles.addTo(this.map);
        } else {
            this._darkTiles.addTo(this.map);
        }

        // Listen for theme changes
        State.on('theme', (theme) => this.switchTiles(theme));

        // Marker layer group
        this.markerLayer = L.layerGroup().addTo(this.map);

        // Listen for search results
        State.on('searchResults', (results) => this.renderPins(results));

        // Map click → set location
        this.map.on('click', (e) => {
            const { lat, lng } = e.latlng;
            document.getElementById('location-input').value = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
        });

        // Try to get user's location — show pulsing dot + pan to it
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const lat = pos.coords.latitude;
                    const lng = pos.coords.longitude;
                    this.map.setView([lat, lng], 14);

                    // Pulsing "you are here" marker
                    const userIcon = L.divIcon({
                        className: 'user-location',
                        html: '<div class="user-location__dot"><div class="user-location__pulse"></div></div>',
                        iconSize: [16, 16],
                        iconAnchor: [8, 8],
                    });
                    L.marker([lat, lng], { icon: userIcon, interactive: false }).addTo(this.map);

                    // Pre-fill location input with reverse geocoded name
                    document.getElementById('location-input').placeholder = 'Your location';
                },
                () => {} // fail silently, keep Manhattan default
            );
        }
    },

    switchTiles(theme) {
        if (theme === 'light') {
            this.map.removeLayer(this._darkTiles);
            this._lightTiles.addTo(this.map);
        } else {
            this.map.removeLayer(this._lightTiles);
            this._darkTiles.addTo(this.map);
        }
    },

    renderPins(results) {
        // Clear existing
        this.markerLayer.clearLayers();
        this.markers = [];

        if (!results || results.length === 0) return;

        const bounds = [];

        results.forEach((r, index) => {
            if (!r.latitude || !r.longitude) return;

            const lat = parseFloat(r.latitude);
            const lng = parseFloat(r.longitude);
            bounds.push([lat, lng]);

            // Custom pin icon
            const icon = L.divIcon({
                className: 'map-pin',
                html: `<div class="map-pin__dot" data-index="${index}"></div>`,
                iconSize: [12, 12],
                iconAnchor: [6, 6],
            });

            const marker = L.marker([lat, lng], { icon })
                .bindPopup(`
                    <div class="map-popup">
                        <strong>${this.escapeHtml(r.business_name || r.title || '')}</strong>
                        ${r.category ? `<div class="map-popup__category">${this.escapeHtml(r.category)}</div>` : ''}
                        ${r.rating ? `<div class="map-popup__rating">${'★'.repeat(Math.round(r.rating))} ${r.rating}</div>` : ''}
                        ${r.phone ? `<div>${r.phone}</div>` : ''}
                    </div>
                `)
                .addTo(this.markerLayer);

            // Store index for table interaction
            marker._resultIndex = index;

            // Click pin → highlight table row
            marker.on('click', () => {
                State.set('highlightedResult', index);
            });

            this.markers.push(marker);
        });

        // Fit map to results
        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }
    },

    highlightPin(index) {
        this.markers.forEach((m, i) => {
            const el = m.getElement();
            if (!el) return;
            if (i === index) {
                el.classList.add('is-highlighted');
                m.openPopup();
            } else {
                el.classList.remove('is-highlighted');
            }
        });
    },

    panToPin(index) {
        const marker = this.markers[index];
        if (marker) {
            this.map.panTo(marker.getLatLng());
            marker.openPopup();
        }
    },

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};

// Listen for table hover → highlight pin
State.on('highlightedResult', (index) => MapModule.highlightPin(index));

document.addEventListener('DOMContentLoaded', () => MapModule.init());
