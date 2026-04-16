from __future__ import annotations

import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
COMPONENT_MAP_PATH = ROOT_DIR / "training" / "liquid_component_map.json"


with COMPONENT_MAP_PATH.open("r", encoding="utf-8") as handle:
    COMPONENT_MAP = json.load(handle)


def parse_liquid_formulation(
    formulation: str,
    temperature_c: float | None = None,
    component_amounts: dict[str, float] | None = None,
) -> dict:
    normalized = formulation.replace(" ", "")
    components = []
    component_amounts = component_amounts or {}
    total_mass = 0.0

    for component_name, meta in COMPONENT_MAP.items():
        if component_name.replace(" ", "") not in normalized:
            continue

        amount = float(component_amounts.get(component_name, 0.0) or 0.0)
        total_mass += max(amount, 0.0)
        components.append(
            {
                "component": component_name,
                "name": meta["name"],
                "smiles": meta["smiles"],
                "role": meta["role"],
                "mass_g": max(amount, 0.0),
            }
        )

    if components:
        if total_mass > 0:
            for component in components:
                component["mass_fraction"] = component["mass_g"] / total_mass
        else:
            uniform_fraction = 1.0 / len(components)
            for component in components:
                component["mass_fraction"] = uniform_fraction

    node_count = len(components)
    edge_count = node_count * (node_count - 1) if node_count > 1 else 0
    return {
        "components": components,
        "graph_type": "liquid_formulation_graph",
        "node_count": node_count,
        "edge_count": edge_count,
        "temperature_c": temperature_c,
        "periodic_boundary": False,
    }
