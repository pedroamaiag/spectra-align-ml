import json
from pathlib import Path

import numpy as np


project_dir = Path(__file__).resolve().parents[1]
data_dir = project_dir / "data/processed"
output_path = project_dir / "data/splits.json"

splits = {
    "train": ["region_001", "region_004", "region_005"],
    "validation": ["region_002"],
    "test": ["region_003"],
}


def create_manifest():
    manifest = {}
    used_regions = set()

    for split_name, regions in splits.items():
        manifest[split_name] = []

        for region in regions:
            if region in used_regions:
                raise ValueError(f"Duplicated region: {region}")

            used_regions.add(region)

            for season in ("rainy", "dry"):
                path = data_dir / region / f"{season}.npz"

                if not path.exists():
                    continue

                with np.load(path) as data:
                    count = len(data["l1c"])

                    if count != len(data["l2a"]):
                        raise ValueError(f"Invalid pair: {path}")

                manifest[split_name].append({
                    "region": region,
                    "season": season,
                    "path": path.relative_to(project_dir).as_posix(),
                    "patches": count,
                })

    available = set(data_dir.glob("region_*/*.npz"))
    included = {
        project_dir / entry["path"]
        for entries in manifest.values()
        for entry in entries
    }

    if available != included:
        raise ValueError("Some dataset files were not assigned")

    return manifest


def main():
    manifest = create_manifest()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=4)

    for split_name, entries in manifest.items():
        total = sum(entry["patches"] for entry in entries)
        print(f"{split_name}: {total} patches")

    print(f"\nSaved: {output_path}")


main()