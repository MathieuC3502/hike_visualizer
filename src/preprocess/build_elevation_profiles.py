import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import DEM_PATH
import json
import geopandas as gpd
import rasterio
from shapely.geometry import LineString


def resample_line(line: LineString, step_m: float = 10.0):
    """
    Returns:
        distances: [0, 10, 20, ...]
        points: shapely Points
    """

    length = line.length

    distances = list(range(0, int(length), int(step_m)))

    if not distances or distances[-1] < length:
        distances.append(length)

    points = [line.interpolate(d) for d in distances]

    return distances, points


def build_elevation_profile(
    trail_dir: Path,
    step_m: float = 10.0,
):
    """
    Creates:

        trail_dir/profile.json

    from the trail shapefile and DEM.
    """
    trail_dir = Path(trail_dir)
    trail_name = trail_dir.name

    shp_files = list(trail_dir.glob("*.shp"))

    if not shp_files:
        raise FileNotFoundError(f"No shapefile found in {trail_dir}")

    shp_path = shp_files[0]

    # -------------------------
    # Load original geometry
    # -------------------------

    gdf_original = gpd.read_file(shp_path)

    if gdf_original.empty:
        raise ValueError(f"Empty shapefile: {shp_path}")

    if gdf_original.crs is None:
        raise ValueError(f"No CRS defined for {shp_path}")

    # Merge all geometries into one line
    line_original = gdf_original.geometry.union_all()

    # -------------------------
    # Project for metric distances
    # -------------------------

    metric_crs = 2154  # Lambert-93

    gdf_metric = gdf_original.to_crs(metric_crs)

    line_metric = gdf_metric.geometry.union_all()

    # -------------------------
    # Resample every 10 m
    # -------------------------

    distances_m, metric_points = resample_line(
        line_metric,
        step_m=step_m,
    )

    # -------------------------
    # Convert sampled points
    # back to WGS84
    # -------------------------

    points_metric_gdf = gpd.GeoDataFrame(
        geometry=metric_points,
        crs=metric_crs,
    )

    points_wgs84 = points_metric_gdf.to_crs(4326)

    # -------------------------
    # Sample DEM
    # -------------------------

    with rasterio.open(DEM_PATH) as dem:

        dem_crs = dem.crs

        points_dem = points_metric_gdf.to_crs(dem_crs)

        dem_coords = [(p.x, p.y) for p in points_dem.geometry]

        elevations = [float(v[0]) for v in dem.sample(dem_coords)]

    # -------------------------
    # Build JSON
    # -------------------------

    profile = {
        "step_m": step_m,
        "points": [],
    }

    for i, (distance_m, elevation_m) in enumerate(zip(distances_m, elevations)):
        p = points_wgs84.geometry.iloc[i]

        profile["points"].append(
            {
                "i": i,
                "d": round(float(distance_m), 1),
                "z": round(float(elevation_m), 1),
                "lon": round(p.x, 7),
                "lat": round(p.y, 7),
            }
        )

    output_dir = Path("docs/profiles")
    output_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    output_path = output_dir / f"{trail_name}.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            profile,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return output_path
