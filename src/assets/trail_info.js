let currentPreviewMap = null;
let currentTrailMarker = null;
let currentProfile = null;

function createTrailModal() {

    if (document.getElementById("trail-modal")) {
        return;
    }

    const modal = document.createElement("div");

    modal.id = "trail-modal";

    modal.innerHTML = `
        <div class="trail-modal-content">

            <button id="close-trail-modal">✕</button>

            <div class="trail-left">
                <h2>Trail information</h2>

                <p>
                    Lorem ipsum dolor sit amet,
                    consectetur adipiscing elit.
                </p>
            </div>

            <div class="trail-right">

                <div id="trail-preview-map"></div>

                <div id="trail-bottom-panel"></div>

            </div>

        </div>
    `;

    document.body.appendChild(modal);

    document
        .getElementById("close-trail-modal")
        .addEventListener("click", () => {
            modal.style.display = "none";
        });

    modal.addEventListener("click", (e) => {

    if (e.target === modal) {
        modal.style.display = "none";
    }

});
}

async function openTrailModal(trailName) {

    createTrailModal();

    document.getElementById(
        "trail-modal"
    ).style.display = "flex";

    console.log(
        "Opening trail:",
        trailName
    );

    try {

        const profile =
            await loadProfile(trailName);

        buildPreviewMap(profile);
        setTimeout(() => {
            buildElevationProfile(profile);
        }, 50);

        document.querySelector(
            ".trail-left"
        ).innerHTML = `
            <h2>${trailName}</h2>
            <p>
                ${profile.points.length} points
            </p>
        `;

    } catch (err) {

        console.error(
            "Unable to load profile",
            err
        );

    }
}

async function loadProfile(trailName) {

    const response = await fetch(
        `profiles/${trailName}.json`
    );

    return await response.json();
}

function buildPreviewMap(profile) {

    if (currentPreviewMap) {
        currentPreviewMap.remove();
        currentPreviewMap = null;
    }

    const mapContainer =
        document.getElementById(
            "trail-preview-map"
        );

    mapContainer.innerHTML = "";

    const previewMap = L.map(
        "trail-preview-map",
        {
            zoomControl: false,
            dragging: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            boxZoom: false,
            keyboard: false,
            touchZoom: false
        }
    );

    L.tileLayer(
        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        {
            attribution: "© OpenStreetMap"
        }
    ).addTo(previewMap);

    const coords = profile.points.map(
        p => [p.lat, p.lon]
    );

    const trail = L.polyline(
        coords,
        {
            color: "red",
            weight: 4
        }
    ).addTo(previewMap);

    setTimeout(() => {

        previewMap.invalidateSize();

        previewMap.fitBounds(
            trail.getBounds(),
            {
                padding: [10, 10]
            }
        );

        previewMap.setZoom(
            previewMap.getZoom() + 0
        );

        }, 100);

        currentPreviewMap = previewMap;

        currentTrailMarker = L.circleMarker(
            [coords[0][0], coords[0][1]],
            {
                radius: 6,
                color: "#1565c0",
                fillColor: "#1565c0",
                fillOpacity: 1
            }
        ).addTo(previewMap);

    return previewMap;
}

function buildElevationProfile(profile) {

    currentProfile = profile;

    const container =
        document.getElementById("trail-bottom-panel");

    if (
        container.clientWidth === 0 ||
        container.clientHeight === 0
    ) {
        setTimeout(
            () => buildElevationProfile(profile),
            50
        );
        return;
    }

    const width = container.clientWidth;
    const height = container.clientHeight;

    // -----------------------------
    // 1. Margins (graph drawing box)
    // -----------------------------
    const leftMargin = 50;
    const rightMargin = 20;
    const topMargin = 40;
    const bottomMargin = 40;

    const innerWidth = width - leftMargin - rightMargin;
    const innerHeight = height - topMargin - bottomMargin;

    // -----------------------------
    // 2. Data scaling
    // -----------------------------
    const maxD = Math.max(
        profile.points.at(-1).d,
        1
    );

    const minZ = Math.min(...profile.points.map(p => p.z));
    const maxZ = Math.max(...profile.points.map(p => p.z));

    const elevationRange = Math.max(maxZ - minZ, 1);

    // -----------------------------
    // 3. Build polyline path
    // -----------------------------
    const path = profile.points.map(p => {

        const x =
            leftMargin +
            (p.d / maxD) * innerWidth;

        const y =
            topMargin +
            (1 - (p.z - minZ) / elevationRange) * innerHeight;

        return `${x},${y}`;
    }).join(" ");

    // -----------------------------
    // 3b. Area fill under profile
    // -----------------------------
    const areaPath =
        `${leftMargin},${topMargin + innerHeight} ` +
        path +
        ` ${leftMargin + innerWidth},${topMargin + innerHeight}`;

    // -----------------------------
    // 3c. Horizontal grid lines
    // -----------------------------
    let gridLines = "";
    let yLabels = "";

    const yTicks = 5;

    for (let i = 0; i <= yTicks; i++) {

        const y =
            topMargin +
            (i / yTicks) * innerHeight;

        const elev =
            Math.round(
                maxZ -
                (i / yTicks) * elevationRange
            );

        gridLines += `
            <line
                x1="${leftMargin}"
                y1="${y}"
                x2="${leftMargin + innerWidth}"
                y2="${y}"
                stroke="#dddddd"
                stroke-dasharray="4 4"/>
        `;

        yLabels += `
            <text
                x="${leftMargin - 8}"
                y="${y + 4}"
                text-anchor="end"
                font-size="11"
                fill="#555">
                ${elev} m
            </text>
        `;
    }

    // -----------------------------
    // 3d. Distance axis
    // -----------------------------
    let xTicksHtml = "";

    const xTicks = 5;

    for (let i = 0; i <= xTicks; i++) {

        const x =
            leftMargin +
            (i / xTicks) * innerWidth;

        const distKm =
            ((i / xTicks) * maxD / 1000)
                .toFixed(1);

        xTicksHtml += `
            <line
                x1="${x}"
                y1="${topMargin + innerHeight}"
                x2="${x}"
                y2="${topMargin + innerHeight + 6}"
                stroke="#555"/>

            <text
                x="${x}"
                y="${topMargin + innerHeight + 20}"
                text-anchor="middle"
                font-size="11"
                fill="#555">
                ${distKm} km
            </text>
        `;
    }

    // -----------------------------
    // 4. Render SVG
    // -----------------------------
    container.innerHTML = `
    <svg
        id="elevation-svg"
        width="100%"
        height="100%"
        viewBox="0 0 ${width} ${height}"
        preserveAspectRatio="none"
        style="background:white; cursor:crosshair;">

        <text
            id="profile-info"
            x="10"
            y="20"
            font-size="12"
            fill="#333">
        </text>

        <!-- Title -->
        <text
            x="${width / 2}"
            y="${topMargin - 12}"
            text-anchor="middle"
            font-size="16"
            font-weight="bold">
            Elevation Profile
        </text>

        <!-- Plot background -->
        <rect
            x="${leftMargin}"
            y="${topMargin}"
            width="${innerWidth}"
            height="${innerHeight}"
            fill="#fafafa"
            stroke="#999"/>

        ${gridLines}

        ${yLabels}

        ${xTicksHtml}

        <!-- Y axis -->
        <line
            x1="${leftMargin}"
            y1="${topMargin}"
            x2="${leftMargin}"
            y2="${topMargin + innerHeight}"
            stroke="#666"/>

        <!-- X axis -->
        <line
            x1="${leftMargin}"
            y1="${topMargin + innerHeight}"
            x2="${leftMargin + innerWidth}"
            y2="${topMargin + innerHeight}"
            stroke="#666"/>

        <!-- Filled area -->
        <polygon
            points="${areaPath}"
            fill="#ffcdd2"
            opacity="0.7"/>

        <!-- Elevation curve -->
        <polyline
            points="${path}"
            fill="none"
            stroke="#d32f2f"
            stroke-width="3"/>

        <!-- Cursor line -->
        <line
            id="profile-cursor"
            x1="0"
            x2="0"
            y1="${topMargin}"
            y2="${topMargin + innerHeight}"
            stroke="black"
            stroke-width="1"
            display="none"/>

        <!-- Cursor point -->
        <circle
            id="profile-point"
            r="5"
            fill="#1565c0"
            display="none"/>

    </svg>
    `;

    // -----------------------------
    // 5. Attach interaction
    // -----------------------------
    attachProfileEvents(
        profile,
        width,
        height,
        leftMargin,
        topMargin,
        innerWidth,
        innerHeight,
        minZ,
        elevationRange,
        maxD
    );
}

function attachProfileEvents(
    profile,
    width,
    height,
    leftMargin,
    topMargin,
    innerWidth,
    innerHeight,
    minZ,
    elevationRange,
    maxD
) {

    const svg =
        document.getElementById("elevation-svg");

    const cursor =
        document.getElementById("profile-cursor");

    const point =
        document.getElementById("profile-point");

    svg.addEventListener("mousemove", function (e) {

        const rect = svg.getBoundingClientRect();

        // ----------------------------------------
        // 1. Convert mouse X → distance along trail
        // ----------------------------------------
        const mouseX = e.clientX - rect.left;

        const t =
            (mouseX - leftMargin) / innerWidth;

        const clampedT =
            Math.max(0, Math.min(1, t));

        const distance =
            clampedT * maxD;

        // ----------------------------------------
        // 2. Direct index lookup (fast & stable)
        // ----------------------------------------
        let nearest =
            Math.round(distance / profile.step_m);

        nearest = Math.max(
            0,
            Math.min(nearest, profile.points.length - 1)
        );

        const p = profile.points[nearest];

        document
            .getElementById("profile-info")
            .textContent =
            `${(p.d / 1000).toFixed(2)} km • ${Math.round(p.z)} m`;

        // ----------------------------------------
        // 3. Convert point → SVG coordinates
        // ----------------------------------------
        const x =
            leftMargin +
            (p.d / maxD) * innerWidth;

        const y =
            topMargin +
            (1 - (p.z - minZ) / elevationRange) * innerHeight;

        // ----------------------------------------
        // 4. Update cursor line
        // ----------------------------------------
        cursor.setAttribute("x1", x);
        cursor.setAttribute("x2", x);
        cursor.removeAttribute("display");

        // ----------------------------------------
        // 5. Update cursor point
        // ----------------------------------------
        point.setAttribute("cx", x);
        point.setAttribute("cy", y);
        point.removeAttribute("display");

        // ----------------------------------------
        // 6. Sync Leaflet marker
        // ----------------------------------------
        if (currentTrailMarker) {
            currentTrailMarker.setLatLng([
                p.lat,
                p.lon
            ]);
        }
    });

    // ----------------------------------------
    // Hide cursor when leaving SVG
    // ----------------------------------------
    svg.addEventListener("mouseleave", function () {
        cursor.setAttribute("display", "none");
        point.setAttribute("display", "none");
    });
}

async function openTrailSelector() {

    console.log("openTrailSelector");

    const response =
        await fetch("trails.json");

    console.log("response", response);

    const trails =
        await response.json();

    console.log("trails", trails);

    // const trails =
    //     await fetch("trails.json")
    //         .then(r => r.json());

    const choice =
        document.createElement("div");

    choice.className =
        "trail-selector";

    choice.innerHTML = `
        <div class="trail-selector-content">

            <select id="trail-select">
                ${trails.map(t =>
                    `<option value="${t}">${t}</option>`
                ).join("")}
            </select>

            <button id="trail-open-btn">
                Open
            </button>

        </div>
    `;

    const existing =
        document.querySelector(
            ".trail-selector"
        );

    if (existing) {
        existing.remove();
    }
    document.body.appendChild(choice);

    document
        .getElementById(
            "trail-open-btn"
        )
        .addEventListener(
            "click",
            () => {

                const trail =
                    document.getElementById(
                        "trail-select"
                    ).value;

                choice.remove();

                openTrailModal(
                    trail
                );
            }
        );
}