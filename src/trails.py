from pathlib import Path
import geopandas as gpd
import folium
from itertools import cycle

COLORS = [
    "red",
    "blue",
    "green",
    "purple",
    "orange",
    "darkred",
    "cadetblue",
    "darkgreen",
    "black",
    "pink",
]


def load_trails(trails_root: Path):
    """
    Load all trail shapefiles and return:
    - list of Folium FeatureGroups
    - list of bounds (minx, miny, maxx, maxy)
    """

    color_cycle = cycle(COLORS)

    layers = []
    bounds_list = []

    if not trails_root.exists():
        return layers, bounds_list

    for trail_dir in sorted(trails_root.iterdir()):
        if not trail_dir.is_dir():
            continue

        shp_files = list(trail_dir.glob("*.shp"))
        if not shp_files:
            continue

        gdf = gpd.read_file(shp_files[0])

        if gdf.empty:
            continue

        bounds_list.append(gdf.total_bounds)

        color = next(color_cycle)

        layer = folium.FeatureGroup(
            name=trail_dir.name,
            show=True,
        )

        folium.GeoJson(
            gdf,
            style_function=lambda _, c=color: {
                "color": c,
                "weight": 4,
            },
            tooltip=trail_dir.name,
        ).add_to(layer)

        layers.append(layer)

    return layers, bounds_list
