const BASE_URL = window.location.origin;
const API_URL = `${BASE_URL}/api/get-dashboard-data`;

let disasterMap;
let markerGroup;
let routingControl;

let seenAlerts = new Set();
let dangerZones = [];
const dangerRadius = 100;

let startMarker = null;
let endMarker = null;


// ================= ROUTE RISK EVALUATION =================

function evaluateRoutes(routes) {

    if (!routes || routes.length === 0) return;

    let safestRoute = null;
    let minRisk = Infinity;

    routes.forEach(route => {

        let riskScore = 0;
        let pointCount = route.coordinates.length || 1;

        route.coordinates.forEach(coord => {

            dangerZones.forEach(zone => {

                const center = zone.getLatLng();
                const distance = disasterMap.distance(coord, center);

                if (distance <= dangerRadius) {
                    const severityWeight = zone.severityWeight || 1;

                    const decayFactor = 1 - (distance / dangerRadius);

                    riskScore += severityWeight * decayFactor;
                }

            });

        });
        const normalizedRisk = riskScore/pointCount;
        if (normalizedRisk < minRisk) {
            minRisk = normalizedRisk;
            safestRoute = route;
        }

    });

    if (safestRoute && routingControl) {
        routingControl._routes = [safestRoute];
        routingControl._routeSelected({ route: safestRoute });
        console.log("Safest route selected. Risk score:", minRisk);
    }
}


// ================= FETCH LIVE SOS =================

async function fetchLiveSOS() {

    try {

        const response = await fetch(API_URL);
        const data = await response.json();

        const signalList = document.querySelector('.signal-list');
        const overlay = document.querySelector('.route-overlay');

        if (!signalList) return;

        signalList.innerHTML = '';

        if (markerGroup) markerGroup.clearLayers();

        // Remove old danger zones
        dangerZones.forEach(zone => disasterMap.removeLayer(zone));
        dangerZones = [];

        if (data.total_active === 0) {

            signalList.innerHTML =
                '<li class="signal verified" style="color:#10b981;">No active SOS signals. Area secure.</li>';

            document.querySelector('.system-status').innerText = "System Status: ACTIVE";
            document.querySelector('.system-status').style.color = "#10b981";

            if (overlay) overlay.innerHTML = "🚨 No active emergencies";

            return;
        }

        data.active_alerts.forEach(alert => {

            let alertClass = 'warning';
            let badgeClass = 'warn';

            if (alert.severity === 'CRITICAL' || alert.severity === 'HIGH') {
                alertClass = 'alert';
                badgeClass = 'danger';
            }

            const li = document.createElement('li');
            li.className = `signal ${alertClass}`;

            li.innerHTML = `
                <strong>[SOS: ${alert.hazard}]</strong> ${alert.original_message}
                <div style="margin-top: 8px;">
                    <span class="badge ${badgeClass}">Loc: ${alert.location}</span>
                    <span class="badge" style="background:#334155;color:#cbd5e1;">
                        Priority: ${alert.severity}
                    </span>
                </div>
                <div style="margin-top:8px; font-size:0.85rem; color:#cbd5e1;">
                    ${alert.action}
                </div>
                <button class="action-btn"
                        style="margin-top:10px;"
                        onclick="dispatchRescue(${alert.id})">
                        Dispatch Rescue Units
                </button>
            `;

            signalList.appendChild(li);

            if (alert.lat && alert.lng) {

                // Red hazard marker
                L.circleMarker([alert.lat, alert.lng], {
                    color: '#ef4444',
                    radius: 8,
                    fillOpacity: 0.8
                })
                .addTo(markerGroup)
                .bindPopup(`<b>${alert.severity} HAZARD</b><br>${alert.original_message}`);

                // 100m Red Alert Zone
                const zone = L.circle([alert.lat, alert.lng], {
                    radius: dangerRadius,
                        color:
                            alert.severity === "CRITICAL" ? "#7f1d1d" :
                            alert.severity === "HIGH" ? "#dc2626" :
                            alert.severity === "MODERATE" ? "#f59e0b" :
                            "#ef4444",
                        fillOpacity: 0.3
                }).addTo(disasterMap);
                zone.severityWeight =
                    alert.severity === "CRITICAL" ? 3 :
                    alert.severity === "HIGH" ? 2 :
                    alert.severity === "MODERATE" ? 1.5 :
                    1;
                dangerZones.push(zone);

                if (!seenAlerts.has(alert.id)) {

                    disasterMap.flyTo([alert.lat, alert.lng], 13, {
                        animate: true,
                        duration: 1.5
                    });

                    seenAlerts.add(alert.id);

                    if (overlay) {
                        overlay.innerHTML = `
                            🚨 <strong>${alert.location}</strong>: ${alert.hazard.toUpperCase()}<br>
                            🚑 Click start & destination to auto-route safely
                        `;
                    }
                }
            }
        });

        document.querySelector('.system-status').innerText =
            `Active SOS: ${data.total_active}`;
        document.querySelector('.system-status').style.color = "#ef4444";

    } catch (error) {
        console.error("Dashboard Feed Disconnected:", error);
    }
}


// ================= DISPATCH =================

async function dispatchRescue(id) {

    try {

        const response = await fetch(
            `${BASE_URL}/api/dispatch/${id}`, 
            { method: "POST" }
        );

        const data = await response.json();
        alert(data.message);
        fetchLiveSOS();

    } catch (error) {
        console.error(error);
        alert("Dispatch failed");
    }
}


// ================= MAP INIT =================

function initDisasterMap() {

    disasterMap = L.map('map').setView([12.8449, 80.1500], 11);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(disasterMap);

    markerGroup = L.layerGroup().addTo(disasterMap);

    if (!L.Routing) {
        console.error("Leaflet Routing Machine not loaded.");
        return;
    }

    routingControl = L.Routing.control({
        waypoints: [],
        showAlternatives: true,
        routeWhileDragging: false,
        router: L.Routing.osrmv1({
            serviceUrl: 'https://router.project-osrm.org/route/v1'
        })
    }).addTo(disasterMap);
    setTimeout(() => {
        const panel = document.querySelector(".leaflet-routing-container");
        if (panel) panel.style.display = "none";
    }, 500);
    // Toggle Directions Panel
    const toggleBtn = document.getElementById("toggleDirectionsBtn");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {

            const panel = document.querySelector(".leaflet-routing-container");
            if (!panel) return;

            if (panel.style.display === "none" || panel.style.display === "") {
                panel.style.display = "block";
                toggleBtn.innerText = "Hide Directions";
            } else {
                panel.style.display = "none";
                toggleBtn.innerText = "Show Directions";
            }
        });
    }
    routingControl.on('routesfound', function(e) {
        evaluateRoutes(e.routes);

        const panel = document.querySelector(".leaflet-routing-container");
        const toggleBtn = document.getElementById("toggleDirectionsBtn");

        if (panel) panel.style.display = "block";
        if (toggleBtn) toggleBtn.innerText = "Hide Directions";
    });

    disasterMap.on('click', function(e) {

        if (!startMarker) {

            startMarker = L.marker(e.latlng).addTo(disasterMap);
            routingControl.setWaypoints([e.latlng]);

        } else if (!endMarker) {

            endMarker = L.marker(e.latlng).addTo(disasterMap);

            routingControl.setWaypoints([
                startMarker.getLatLng(),
                endMarker.getLatLng()
            ]);

        } else {

            disasterMap.removeLayer(startMarker);
            disasterMap.removeLayer(endMarker);

            startMarker = L.marker(e.latlng).addTo(disasterMap);
            endMarker = null;

            routingControl.setWaypoints([e.latlng]);
        }

    });
}


// ================= START =================

initDisasterMap();
fetchLiveSOS();
setInterval(fetchLiveSOS, 3000);