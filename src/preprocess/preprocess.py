import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from config import TRAILS_DIR
from build_elevation_profiles import build_elevation_profile
import json


def find_trail_dirs(trails_root: Path):
    """
    Returns all directories containing shapefiles.
    """
    trail_dirs = []

    if not trails_root.exists():
        return trail_dirs

    for d in sorted(trails_root.iterdir()):
        if not d.is_dir():
            continue

        if list(d.glob("*.shp")):
            trail_dirs.append(d)

    return trail_dirs


def run_preprocess(step_m: float = 10.0):
    """
    Main preprocessing pipeline.
    """

    trail_dirs = find_trail_dirs(TRAILS_DIR)

    print(f"Found {len(trail_dirs)} trails")

    for i, trail_dir in enumerate(trail_dirs):
        print(f"[{i+1}/{len(trail_dirs)}] Processing {trail_dir.name}")

        try:
            out = build_elevation_profile(
                trail_dir=trail_dir,
                step_m=step_m,
            )

            print(f"  -> OK: {out}")

        except Exception as e:
            print(f"  -> ERROR in {trail_dir.name}: {e}")


def create_trails_list(in_dir: str = "./docs/profiles/"):
    in_path = Path(in_dir)
    trail_names = [f.stem for f in in_path.glob("*.json") if f.is_file()]
    trails_list = sorted(trail_names)  # Optional: sort the list

    output_path = Path("./docs/trails.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trails_list, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    run_preprocess(step_m=10.0)
    create_trails_list()
