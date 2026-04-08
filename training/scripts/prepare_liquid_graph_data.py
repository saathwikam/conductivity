from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "data" / "liquid_electrolyte_500.csv"
COMPONENT_MAP_PATH = ROOT / "training" / "liquid_component_map.json"
OUTPUT_DIR = ROOT / "training" / "liquid_graph_data"
OUTPUT_JSONL = OUTPUT_DIR / "liquid_graph_records.jsonl"
OUTPUT_CSV = OUTPUT_DIR / "liquid_graph_records.csv"


COMPONENT_COLUMN_MAP = {
    "PC": "pc_g",
    "EC": "ec_g",
    "EMC": "emc_g",
    "LiPF6": "lipf6_g",
}


def parse_components(row: dict, component_map: dict) -> list[dict]:
    components: list[dict] = []
    total_mass = 0.0
    for component, column in COMPONENT_COLUMN_MAP.items():
        raw_value = row.get(column, 0) or 0
        try:
            mass = float(raw_value)
        except ValueError:
            mass = 0.0
        if mass <= 0:
            continue
        total_mass += mass
        meta = component_map[component]
        components.append(
            {
                "component": component,
                "name": meta["name"],
                "smiles": meta["smiles"],
                "role": meta["role"],
                "mass_g": mass,
            }
        )

    for component in components:
        component["mass_fraction"] = component["mass_g"] / total_mass if total_mass else 0.0
    return components


def build_graph_summary(components: list[dict], temperature_c: float) -> dict:
    component_count = len(components)
    node_count = component_count
    edge_count = component_count * (component_count - 1) if component_count > 1 else 0
    salt_count = sum(1 for component in components if component["role"] == "salt")
    solvent_count = sum(1 for component in components if component["role"] == "solvent")
    return {
        "graph_type": "liquid_formulation_graph",
        "node_count": node_count,
        "edge_count": edge_count,
        "salt_nodes": salt_count,
        "solvent_nodes": solvent_count,
        "temperature_c": temperature_c,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with COMPONENT_MAP_PATH.open("r", encoding="utf-8") as handle:
        component_map = json.load(handle)

    df = pd.read_csv(DATASET_PATH)
    records: list[dict] = []

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        temperature_c = float(row_dict["temperature_c"])
        components = parse_components(row_dict, component_map)
        graph_summary = build_graph_summary(components, temperature_c)
        record = {
            "jid": f"liquid_{index:04d}",
            "phase": "liquid",
            "experiment_id": row_dict["experiment_id"],
            "formulation": row_dict["formulation"],
            "temperature_c": temperature_c,
            "target_log_sigma": float(row_dict["ln_ionic_conductivity"]),
            "ionic_conductivity_s_cm": float(row_dict["ionic_conductivity_s_cm"]),
            "components": components,
            "graph_summary": graph_summary,
        }
        records.append(record)

    with OUTPUT_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "jid",
                "phase",
                "experiment_id",
                "formulation",
                "temperature_c",
                "target_log_sigma",
                "ionic_conductivity_s_cm",
                "component_count",
                "node_count",
                "edge_count",
                "salt_nodes",
                "solvent_nodes",
            ],
        )
        writer.writeheader()
        for record in records:
            summary = record["graph_summary"]
            writer.writerow(
                {
                    "jid": record["jid"],
                    "phase": record["phase"],
                    "experiment_id": record["experiment_id"],
                    "formulation": record["formulation"],
                    "temperature_c": record["temperature_c"],
                    "target_log_sigma": record["target_log_sigma"],
                    "ionic_conductivity_s_cm": record["ionic_conductivity_s_cm"],
                    "component_count": len(record["components"]),
                    "node_count": summary["node_count"],
                    "edge_count": summary["edge_count"],
                    "salt_nodes": summary["salt_nodes"],
                    "solvent_nodes": summary["solvent_nodes"],
                }
            )

    print(f"Prepared {len(records)} liquid graph-ready records.")
    print(f"JSONL: {OUTPUT_JSONL}")
    print(f"CSV: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
