from __future__ import annotations

import csv
import os
import re
from pathlib import Path

import pandas as pd
from pymatgen.ext.matproj import MPRester


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "data" / "solid_electrolyte_500.csv"
OUTPUT_DIR = ROOT / "training" / "solid_alignn_data"
STRUCTURES_DIR = OUTPUT_DIR
ID_PROP_PATH = OUTPUT_DIR / "id_prop.csv"


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def main() -> None:
    api_key = os.environ.get("MP_API_KEY")
    if not api_key:
        raise SystemExit("Set MP_API_KEY in your environment before running this script.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATASET_PATH)
    formulas = df["formula"].dropna().astype(str).unique().tolist()

    rows: list[tuple[str, float]] = []
    missing: list[str] = []

    with MPRester(api_key) as mpr:
        for formula in formulas:
            try:
                material_ids = mpr.get_material_ids(formula)
            except Exception:
                material_ids = []

            if not material_ids:
                missing.append(formula)
                continue

            material_id = str(material_ids[0])
            try:
                structure = mpr.get_structure_by_material_id(material_id)
            except Exception:
                missing.append(formula)
                continue

            filename = f"{safe_name(material_id)}.vasp"
            structure.to(filename=str(STRUCTURES_DIR / filename), fmt="poscar")

            formula_rows = df[df["formula"] == formula]
            target = float(formula_rows["log10_ionic_conductivity"].median())
            rows.append((filename, target))

    with ID_PROP_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    missing_path = OUTPUT_DIR / "missing_formulas.txt"
    missing_path.write_text("\n".join(sorted(missing)), encoding="utf-8")

    print(f"Prepared {len(rows)} structure-target pairs.")
    print(f"Missing formulas: {len(missing)}")
    print(f"Output folder: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
