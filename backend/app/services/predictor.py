from __future__ import annotations

from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Any

import pandas as pd

from app.services.chemistry import (
    build_liquid_graph_stats,
    build_solid_graph_stats,
    is_liquid_like_input,
    is_solid_like_formula,
    invalid_solid_formula_reason,
    normalize_formula,
    parse_composition,
)
from app.services.dataset_store import load_liquid_dataset, load_solid_dataset
from app.services.liquid_preprocessor import invalid_liquid_formulation_reason, parse_liquid_formulation
from app.services.liquid_model_runner import LiquidModelRunner
from app.services.solid_model_runner import SolidAlignnRunner


ROOT_DIR = Path(__file__).resolve().parents[3]
MODELS_DIR = ROOT_DIR / "models"
COMMON_ANIONS = {"O", "F", "S", "Se", "Cl", "Br", "I", "N"}
KNOWN_LITHIUM_SOLID_SCAFFOLDS = (
    frozenset({"Li", "La", "Zr", "O"}),  # LLZO / garnet-like oxides
    frozenset({"Li", "La", "Ti", "O"}),  # LLTO-type perovskites
    frozenset({"Li", "Al", "Ti", "P", "O"}),  # LATP-type NASICONs
    frozenset({"Li", "Al", "Ge", "P", "O"}),  # LAGP-type NASICONs
    frozenset({"Li", "P", "S"}),  # sulfide / argyrodite bases, with optional halides
    frozenset({"Li", "Si", "P", "O"}),  # LISICON-type oxides
)


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
        invalid_reason = invalid_solid_formula_reason(formula)
        if invalid_reason:
            raise ValueError(invalid_reason)

        normalized = normalize_formula(formula)
        if "Li" not in normalized:
            raise ValueError("Solid electrolyte mode requires a lithium-containing formula.")
        lithium_warnings: list[str] = []
        dataset = load_solid_dataset()
        exact = dataset[dataset["formula_key"] == normalized.replace(" ", "").lower()]
        exact_match_found = not exact.empty
        if not exact.empty:
            match = exact.iloc[0]
        else:
            match = self._closest_solid_match(dataset, normalized)
        graph_stats = build_solid_graph_stats(normalized)
        try:
            trained_result = self.solid_model_runner.predict(normalized)
        except ValueError:
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
            if exact_match_found:
                narrative = f"Matched against the solid electrolyte dataset entry for {record['formula']}."
            else:
                narrative = f"Matched against the closest solid electrolyte signature for {record['formula']}."
                lithium_warnings.append(
                    "Valid lithium compound, but it is not directly covered by the current solid dataset; "
                    "this prediction is a low-confidence approximation based on the nearest available compound."
                )
        return {
            "prediction": prediction,
            "graph_stats": graph_stats,
            "matched_record": record,
            "phase": "solid",
            "narrative": narrative,
            "warnings": lithium_warnings,
        }

    def _predict_liquid(self, formulation: str) -> dict[str, Any]:
        if not is_liquid_like_input(formulation) and is_solid_like_formula(formulation):
            raise ValueError(
                "Liquid mode expects a liquid electrolyte formulation such as 'LiPF6 in EC/EMC', not a solid formula."
            )
        invalid_reason = invalid_liquid_formulation_reason(formulation)
        if invalid_reason:
            raise ValueError(invalid_reason)
        lithium_warnings: list[str] = []

        dataset = load_liquid_dataset()
        key = formulation.replace(" ", "").lower()
        exact = dataset[dataset["formulation_key"] == key]
        request_components = self._liquid_component_names(formulation)
        if not exact.empty:
            match = exact.iloc[0]
            match_quality = "exact"
        else:
            match = self._closest_liquid_match(dataset, formulation)
            match_quality = self._liquid_match_quality(request_components, match["formulation"])
        graph_stats = build_liquid_graph_stats(formulation)
        liquid_payload = parse_liquid_formulation(
            formulation,
            float(match["temperature_c"]),
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
            "warnings": (
                lithium_warnings
                + (
                    [
                        "This shorthand liquid formulation was mapped to the closest compatible dataset blend; "
                        "prediction confidence may be lower than an exact covered formulation."
                    ]
                    if match_quality == "compatible"
                    else (
                        [
                            "Valid liquid formulation, but it is not directly covered by the current liquid dataset; "
                            "this prediction is a low-confidence approximation based on the nearest available formulation."
                        ]
                        if match_quality == "none"
                        else []
                    )
                )
            ),
        }

    def _liquid_lithium_warnings(self, formulation: str) -> list[str]:
        lowered = formulation.lower()
        has_lithium_component = (
            any(component in lowered for component in ("lipf6", "libf4", "litfsi", "lifsi", "liclo4"))
            or "li" in formulation
        )
        if not has_lithium_component:
            raise ValueError("Liquid electrolyte mode requires a lithium salt or lithium-containing formulation.")

        leading_component = re.split(r"\s+in\s+|/|\+|,|\|", formulation.strip(), maxsplit=1, flags=re.IGNORECASE)[0]
        warnings = []
        if "li" not in leading_component.lower():
            warnings.append(
                "Lithium is present, but it is not in the leading formulation component; verify the lithium salt content before trusting the prediction."
            )
        return warnings

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
        request_components = self._liquid_component_names(formulation)

        def score(candidate: str) -> float:
            candidate_components = self._liquid_component_names(candidate)
            shared = len(request_components & candidate_components)
            missing = len(request_components - candidate_components)
            extra = len(candidate_components - request_components)
            text_similarity = SequenceMatcher(None, candidate.lower(), formulation.lower()).ratio()
            return (shared * 4.0) - (missing * 5.0) - (extra * 2.0) + text_similarity

        ranked = dataset.copy()
        ranked["score"] = ranked["formulation"].apply(score)
        return ranked.sort_values("score", ascending=False).iloc[0]

    def _weight_status(self, path: Path) -> str:
        return str(path.name if path.exists() else "dataset_fallback")

    def _liquid_component_names(self, formulation: str) -> set[str]:
        payload = parse_liquid_formulation(formulation)
        return {component["component"] for component in payload["components"]}

    def _liquid_match_quality(self, request_components: set[str], candidate_formulation: str) -> str:
        candidate_components = self._liquid_component_names(candidate_formulation)
        if request_components == candidate_components:
            return "exact"

        request_profile = self._liquid_component_profile(request_components)
        candidate_profile = self._liquid_component_profile(candidate_components)

        same_salts = request_profile["salts"] == candidate_profile["salts"]
        solvent_subset = request_profile["solvents"].issubset(candidate_profile["solvents"])
        no_extra_salts = candidate_profile["salts"].issubset(request_profile["salts"])

        if same_salts and no_extra_salts and solvent_subset:
            return "compatible"
        return "none"

    def _liquid_component_profile(self, component_names: set[str]) -> dict[str, set[str]]:
        payload = parse_liquid_formulation(" | ".join(sorted(component_names)))
        salts = {component["component"] for component in payload["components"] if component["role"].lower() == "salt"}
        solvents = {
            component["component"]
            for component in payload["components"]
            if component["role"].lower() == "solvent"
        }
        return {"salts": salts, "solvents": solvents}
