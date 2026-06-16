from pathlib import Path
import folium
import geopandas as gpd
from folium import Element


def create_map():
    """
    Create the base Folium map.
    """

    m = folium.Map(
        location=[43.5, 5.2],
        zoom_start=9,
        tiles=None,
    )

    add_base_layers(m)

    return m


def add_base_layers(m):
    """
    Add available basemaps.
    """

    folium.TileLayer(
        "OpenStreetMap",
        name="OSM",
        control=True,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        name="Topo",
        attr="© OpenTopoMap",
        control=True,
    ).add_to(m)


def get_leaflet_bounds(region_gdf: gpd.GeoDataFrame):
    """
    Convert GeoPandas bounds to Leaflet bounds format.
    """

    bounds = [float(x) for x in region_gdf.total_bounds]

    return [
        [bounds[1], bounds[0]],
        [bounds[3], bounds[2]],
    ]


def fit_bounds(m, all_bounds):
    """
    Fit map to all trail bounds.
    """

    if not all_bounds:
        return

    minx = min(b[0] for b in all_bounds)
    miny = min(b[1] for b in all_bounds)
    maxx = max(b[2] for b in all_bounds)
    maxy = max(b[3] for b in all_bounds)

    m.fit_bounds(
        [
            [miny, minx],
            [maxy, maxx],
        ]
    )


def add_layer_control(m):
    folium.LayerControl(collapsed=False).add_to(m)


def inject_custom_js(m, js_file, leaflet_bounds):

    js_code = js_file.read_text(encoding="utf-8")
    map_name = m.get_name()

    rendered = f"""
    <script>
    {js_code}
    </script>

    <script>
    function waitForMap() {{

        var map = window.{map_name};

        if (!map || !map.eachLayer) {{
            setTimeout(waitForMap, 50);
            return;
        }}

        if (typeof initializeMap !== "function") {{
            setTimeout(waitForMap, 50);
            return;
        }}

        initializeMap(map, {leaflet_bounds});
    }}

    waitForMap();
    </script>
    """

    m.get_root().html.add_child(Element(rendered))


def save_map(m, output_file: Path):
    """
    Export map to HTML.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    m.save(str(output_file))


def inject_asset(m, asset_file):

    code = asset_file.read_text(encoding="utf-8")

    if asset_file.suffix == ".css":

        rendered = f"""
        <style>
        {code}
        </style>
        """

    elif asset_file.suffix == ".js":

        rendered = f"""
        <script>
        {code}
        </script>
        """

    else:
        raise ValueError(f"Unsupported asset type: {asset_file}")

    m.get_root().html.add_child(Element(rendered))
