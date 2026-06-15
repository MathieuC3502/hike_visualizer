from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

INPUT_DIR = DATA_DIR / "in"
OUTPUT_DIR = DATA_DIR / "out"

REGION_FILE = INPUT_DIR / "region-provence-alpes-cote-d-azur.geojson"

POI_FILE = INPUT_DIR / "pois" / "Points_of_Interest.shp"

PICTURES_DIR = INPUT_DIR / "pictures"

TRAILS_DIR = INPUT_DIR / "trails"

OUTPUT_HTML = ROOT / "docs" / "index.html"
