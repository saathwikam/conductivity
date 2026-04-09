from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import pandas as pd

from app.services.chemistry import (
    build_liquid_graph_stats,
    build_solid_graph_stats,
    is_liquid_like_input,
    is_solid_like_formula,
    normalize_formula,
    parse_composition,
)
from app.services.dataset_store import load_liquid_dataset, load_solid_dataset
from app.services.liquid_preprocessor import parse_liquid_formulation
from app.services.liquid_model_runner import LiquidModelRunner
from app.services.solid_model_runner import SolidAlignnRunner


ROOT_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT_DIR / "models"


class PredictionService:
    def __init__(self) -> None:
        self.solid_weights_path = MODELS_DIR / "alignn_solid.pth"
        self.liquid_weights_path = MODELS_DIR / "alignn_liquid.pt"
        self.solid_model_runner = SolidAlignnRunner(self.solid_weights_path)
        self.liquid_model_runner = LiquidModelRunner(self.liquid_weights_path)

    def predict(self, phase: str, formula: str) -> dict[str, Any]:
        cleaned = formula.strip()
        if not cleaned:
            raise ValueError("Formula input is required.")

        if phase == "solid":
            return self._predict_solid(cleaned)
        if phase == "liquid":
            return self._predict_liquid(cleaned)
        raise ValueError("Phase must be either 'solid' or 'liquid'.")

    def _predict_solid(self, formula: str) -> dict[str, Any]:
        if is_liquid_like_input(formula):
            raise ValueError("Solid mode expects a solid electrolyte chemical formula, not a liquid formulation.")

        normalized = normalize_formula(formula)
        dataset = load_solid_dataset()
        exact = dataset[dataset["formula_key"] == normalized.replace(" ", "").lower()]
        if not exact.empty:
            match = exact.iloc[0]
        else:
            match = self._closest_solid_match(dataset, normalized)
        graph_stats = build_solid_graph_stats(normalized)
        try:
            trained_result = self.solid_model_runner.predict(normalized)
        except ValueError as exc:
            if self.solid_model_runner.strict_mode_enabled():
                raise ValueError(
                    "No matching crystal structure was found in Materials Project for this solid formula, "
                    "so solid ALIGNN prediction could not be completed."
                ) from exc
            trained_result = None
        prediction = float(trained_result["prediction"]) if trained_result else float(match["log10_ionic_conductivity"])
        record = {
            "formula": match["formula"],
            "temperature_c": float(match["temperature_c"]),
            "ionic_conductivity_s_cm": float(match["ionic_conductivity_s_cm"]),
            "family": match["family"],
            "chemical_family": match["chemical_family"],
            "source_doi": match["source_doi"],
            "weight_source": trained_result["weight_source"] if trained_result else self._weight_status(self.solid_weights_path),
        }
        if trained_result:
            record["material_id"] = trained_result["material_id"]
            narrative = (
                f"Solid ALIGNN inference ran with {trained_result['weight_source']} using Materials Project structure "
                f"{trained_result['material_id']}."
            )
        else:
            narrative = f"Matched against the closest solid electrolyte signature for {record['formula']}."
        return {
            "prediction": prediction,
            "graph_stats": graph_stats,
            "matched_record": record,
            "phase": "solid",
            "narrative": narrative,
        }

    def _predict_liquid(self, formulation: str) -> dict[str, Any]:
        if not is_liquid_like_input(formulation) and is_solid_like_formula(formulation):
            raise ValueError(
                "Liquid mode expects a liquid electrolyte formulation such as 'LiPF6 in EC/EMC', not a solid formula."
            )

        dataset = load_liquid_dataset()
        key = formulation.replace(" ", "").lower()
        exact = dataset[dataset["formulation_key"] == key]
        if not exact.empty:
            match = exact.iloc[0]
        else:
            match = self._closest_liquid_match(dataset, formulation)
        graph_stats = build_liquid_graph_stats(formulation)
        liquid_payload = parse_liquid_formulation(
            formulation,
            float(match["temperature_c"]),
            component_amounts={
                "PC": float(match["pc_g"]),
                "EC": float(match["ec_g"]),
                "EMC": float(match["emc_g"]),
                "LiPF6": float(match["lipf6_g"]),
            },
        )
        trained_result = self.liquid_model_runner.predict(liquid_payload)
        prediction = float(trained_result["prediction"]) if trained_result else float(match["ln_ionic_conductivity"])
        record = {
            "formulation": match["formulation"],
            "temperature_c": float(match["temperature_c"]),
            "ionic_conductivity_s_cm": float(match["ionic_conductivity_s_cm"]),
            "pc_g": float(match["pc_g"]),
            "ec_g": float(match["ec_g"]),
            "emc_g": float(match["emc_g"]),
            "lipf6_g": float(match["lipf6_g"]),
            "experiment_id": match["experiment_id"],
            "weight_source": trained_result["weight_source"] if trained_result else self._weight_status(self.liquid_weights_path),
        }
        return {
            "prediction": prediction,
            "graph_stats": graph_stats,
            "matched_record": record,
            "phase": "liquid",
            "narrative": (
                f"Liquid model inference ran with {trained_result['weight_source']}."
                if trained_result
                else f"Matched against the closest liquid formulation signature for {record['formulation']}."
            ),
        }

    def _closest_solid_match(self, dataset: pd.DataFrame, formula: str) -> pd.Series:
        target_comp = parse_composition(formula)

        def score(candidate: str) -> float:
            comp = parse_composition(candidate)
            overlap = sum(min(target_comp.get(key, 0.0), comp.get(key, 0.0)) for key in set(target_comp) | set(comp))
            size_penalty = abs(sum(target_comp.values()) - sum(comp.values()))
            return overlap - size_penalty

        ranked = dataset.copy()
        ranked["score"] = ranked["formula"].apply(score)
        return ranked.sort_values("score", ascending=False).iloc[0]

    def _closest_liquid_match(self, dataset: pd.DataFrame, formulation: str) -> pd.Series:
        ranked = dataset.copy()
        ranked["score"] = ranked["formulation"].apply(
            lambda candidate: SequenceMatcher(None, candidate.lower(), formulation.lower()).ratio()
        )
        return ranked.sort_values("score", ascending=False).iloc[0]

    def _weight_status(self, path: Path) -> str:
        return str(path.name if path.exists() else "dataset_fallback")
