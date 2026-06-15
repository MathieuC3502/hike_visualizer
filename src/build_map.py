from config import *
from map_builder import *
from trails import load_trails
from poi import build_poi_layer
import geopandas as gpd

region = gpd.read_file(REGION_FILE)

m = create_map()

trail_layers, trail_bounds = load_trails(TRAILS_DIR)

for layer in trail_layers:
    layer.add_to(m)

poi_layer = build_poi_layer(
    POI_FILE,
    PICTURES_DIR,
)

poi_layer.add_to(m)

fit_bounds(
    m,
    trail_bounds,
)

add_layer_control(m)

inject_custom_js(
    m,
    ROOT / "src" / "assets" / "map.js",
    get_leaflet_bounds(region),
)

save_map(
    m,
    OUTPUT_HTML,
)
