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

DEM_PATH = "C:/Users/mathi/Documents/__DOCUMENTS__/06_DATA/RGE_ALTI_5m_13_Bouches_du_Rhone/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D013_2022-12-16/RGEALTI_2-0_5M_ASC_LAMB93-IGN69_D013_2022-12-16/RGEALTI/1_DONNEES_LIVRAISON_2023-01-00223/13_Bouches_du_Rhone_RGEALT.tif"
