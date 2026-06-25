import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import DEM_PATH
import json
import geopandas as gpd
import numpy as np
import rasterio
from scipy.ndimage import median_filter
from scipy.signal import savgol_filter
from shapely.geometry import LineString


def remove_dem_spikes(
    elevations,
    step_m=10.0,
    max_grade=1.0,
    max_width=6,
    return_tol=8.0,
):
    """
    Remove short excursions produced by DEM cliffs.

    Detects:
        steep up ... steep down
    or
        steep down ... steep up

    where the profile returns close to its initial elevation.
    """

    z = np.asarray(elevations, dtype=float).copy()

    if len(z) < 6:
        return z.tolist()

    max_dz = max_grade * step_m

    i = 1

    while i < len(z) - 2:

        first_jump = z[i] - z[i - 1]

        if abs(first_jump) < max_dz:
            i += 1
            continue

        sign = np.sign(first_jump)

        found = False

        for j in range(i + 1, min(i + max_width, len(z) - 1)):

            second_jump = z[j] - z[j - 1]

            if (
                np.sign(second_jump) == -sign
                and abs(second_jump) > max_dz
                and abs(z[j] - z[i - 1]) < return_tol
            ):

                z[i : j + 1] = np.linspace(
                    z[i - 1],
                    z[j],
                    j - i + 1,
                )

                i = j
                found = True
                break

        if not found:
            i += 1

    return z.tolist()


def resample_line(line: LineString, step_m: float = 10.0):
    length = line.length

    distances = list(range(0, int(length), int(step_m)))

    if not distances or distances[-1] < length:
        distances.append(length)

    points = [line.interpolate(d) for d in distances]

    return distances, points


def smooth_elevations(
    elevations,
    median_size: int = 3,
    window_length: int = 9,
    polyorder: int = 2,
):
    """
    Smooth elevation profile while preserving climbs.

    1. Median filter removes isolated DEM spikes.
    2. Savitzky-Golay performs a light smoothing.
    """

    z = np.asarray(elevations, dtype=float)

    if len(z) < 5:
        return z.tolist()

    # Remove isolated spikes
    z = median_filter(z, size=median_size)

    # Window must be odd and <= profile length
    window = min(window_length, len(z))

    if window % 2 == 0:
        window -= 1

    if window <= polyorder:
        return z.tolist()

    z = savgol_filter(
        z,
        window_length=window,
        polyorder=polyorder,
        mode="interp",
    )

    return z.tolist()


def build_elevation_profile(
    trail_dir: Path,
    step_m: float = 10.0,
):
    """
    Creates:

        docs/profiles/<trail>.json

    from the trail shapefile and DEM.
    """

    trail_dir = Path(trail_dir)
    trail_name = trail_dir.name

    shp_files = list(trail_dir.glob("*.shp"))

    if not shp_files:
        raise FileNotFoundError(f"No shapefile found in {trail_dir}")

    shp_path = shp_files[0]

    # -------------------------
    # Load geometry
    # -------------------------

    gdf_original = gpd.read_file(shp_path)

    if gdf_original.empty:
        raise ValueError(f"Empty shapefile: {shp_path}")

    if gdf_original.crs is None:
        raise ValueError(f"No CRS defined for {shp_path}")

    # -------------------------
    # Project to metric CRS
    # -------------------------

    metric_crs = 2154  # Lambert-93

    gdf_metric = gdf_original.to_crs(metric_crs)

    geom = gdf_metric.geometry.iloc[0]

    if geom.geom_type != "LineString":
        raise ValueError(f"Expected LineString, got {geom.geom_type}")

    line_metric = geom

    # -------------------------
    # Resample every step_m
    # -------------------------

    distances_m, metric_points = resample_line(
        line_metric,
        step_m=step_m,
    )

    # -------------------------
    # Convert sampled points to WGS84
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
    # Smooth elevations
    # -------------------------

    elevations = remove_dem_spikes(
        elevations,
        step_m=step_m,
        max_grade=1.0,
    )

    elevations = smooth_elevations(
        elevations,
        median_size=3,
        window_length=9,
        polyorder=2,
    )

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
    output_dir.mkdir(parents=True, exist_ok=True)

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
