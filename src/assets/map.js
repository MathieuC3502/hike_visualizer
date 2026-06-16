function initializeMap(map, deptBounds) {
    console.log("initializeMap called", map);

    if (!map) {
        console.error("Map not initialized");
        return;
    }

    // ----------------------------
    // 1. Map boundaries (lock view)
    // ----------------------------

    var bounds = L.latLngBounds(
        L.latLng(deptBounds[0][0], deptBounds[0][1]),
        L.latLng(deptBounds[1][0], deptBounds[1][1])
    );

    map.setMaxBounds(bounds);
    map.options.maxBoundsViscosity = 1.0;

    var minZoom = map.getBoundsZoom(bounds)+1;
    map.setMinZoom(minZoom);


    // ----------------------------
    // 2. Trails fitting
    // ----------------------------

    function getTrailsBounds() {
        var b = L.latLngBounds();

        map.eachLayer(function (layer) {
            if (layer.getBounds && typeof layer.getBounds === "function") {
                try {
                    b.extend(layer.getBounds());
                } catch (e) {}
            }
        });

        return b;
    }

    function fitToTrails() {
        var b = getTrailsBounds();

        if (b.isValid()) {
            map.fitBounds(b, {
                padding: [20, 20]
            });
        } else {
            // fallback: region bounds
            map.fitBounds(bounds);
        }
    }


    // ----------------------------
    // 3. Base layer detection (safe + delayed)
    // ----------------------------

    var osmLayer = null;
    var topoLayer = null;

    function detectBaseLayers() {
        console.log("detectBaseLayers", map._layers);
        map.eachLayer(function (layer) {

            if (!(layer instanceof L.TileLayer)) return;

            var url = layer._url || layer.options?.url || "";

            if (url.includes("openstreetmap")) {
                osmLayer = layer;
            }

            if (url.includes("opentopomap")) {
                topoLayer = layer;
            }
        });
    }

    function ensureOSM() {
        if (osmLayer && !map.hasLayer(osmLayer)) {
            map.addLayer(osmLayer);
        }
    }

    function ensureTopo() {
        if (topoLayer && !map.hasLayer(topoLayer)) {
            map.addLayer(topoLayer);
        }
    }

    function updateBaseLayerByZoom() {

        var z = map.getZoom();

        if (z >= 17) {

            if (topoLayer && map.hasLayer(topoLayer)) {
                map.removeLayer(topoLayer);
            }

            ensureOSM();

        } else {

            ensureTopo();

        }
    }


    // ----------------------------
    // 4. Controls
    // ----------------------------

    var TrailInfoControl = L.Control.extend({
        options: {
            position: "topleft"
        },

        onAdd: function () {

            var container = L.DomUtil.create(
                "div",
                "leaflet-bar leaflet-control"
            );

            var btn = L.DomUtil.create(
                "a",
                "",
                container
            );

            btn.innerHTML = "📈";
            btn.title = "Trail information";
            btn.href = "#";

            L.DomEvent.on(
                btn,
                "click",
                function (e) {

                    console.log("📈 clicked");

                    L.DomEvent.stopPropagation(e);
                    L.DomEvent.preventDefault(e);

                    openTrailSelector();

                }
            );

            return container;
        }
    });

    var ResetControl = L.Control.extend({

        options: {
            position: "topleft"
        },

        onAdd: function () {

            var container = L.DomUtil.create(
                "div",
                "leaflet-bar leaflet-control"
            );

            var btn = L.DomUtil.create("a", "", container);

            btn.innerHTML = "🔍";
            btn.title = "Recentrer sur les randonnées";
            btn.href = "#";

            L.DomEvent.on(btn, "click", function (e) {
                L.DomEvent.stopPropagation(e);
                L.DomEvent.preventDefault(e);
                fitToTrails();
            });

            return container;
        }
    });


    // ----------------------------
    // 5. Stable initialization flow
    // ----------------------------

    map.whenReady(function () {

        // Step 1: detect layers after render
        function tryDetectLayers() {

            detectBaseLayers();

            if (!osmLayer || !topoLayer) {
                setTimeout(tryDetectLayers, 200);
                return;
            }

            updateBaseLayerByZoom();
        }

        setTimeout(tryDetectLayers, 300);

        // Step 2: initial fit AFTER everything exists
        setTimeout(function () {
            fitToTrails();
        }, 800);

        // Step 3: attach controls
        try {
            map.addControl(new ResetControl());
            map.addControl(new TrailInfoControl());
        } catch (e) {
            console.error("Adding controls failed", e);
}

    });


    // ----------------------------
    // 6. Events
    // ----------------------------

    map.on("zoomend", updateBaseLayerByZoom);

    map.on("overlayadd", function () {
        setTimeout(fitToTrails, 100);
    });

    map.on("overlayremove", function () {
        setTimeout(fitToTrails, 100);
    });

}