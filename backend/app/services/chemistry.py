from __future__ import annotations

import math
import re


FORMULA_TOKEN_PATTERN = re.compile(r"([A-Z][a-z]?)([0-9]*\.?[0-9]*)")
SOLID_FORMULA_PATTERN = re.compile(r"^([A-Z][a-z]?[0-9]*\.?[0-9]*)+$")
VALID_ELEMENT_SYMBOLS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo",
    "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe",
    "Cs", "Ba", "La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy",
    "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt",
    "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md", "No",
    "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl",
    "Mc", "Lv", "Ts", "Og",
}
KNOWN_LIQUID_COMPONENTS = {
    "lipf6": ["Li", "P", "F", "F", "F", "F", "F", "F"],
    "libf4": ["Li", "B", "F", "F", "F", "F"],
    "litfsi": ["Li", "N", "S", "S", "O", "O", "O", "O", "C", "C", "F", "F", "F", "F", "F", "F"],
    "lifsi": ["Li", "N", "S", "S", "O", "O", "O", "O", "F", "F"],
    "liclo4": ["Li", "Cl", "O", "O", "O", "O"],
    "ec": ["C", "C", "O", "O", "O", "H", "H", "H", "H"],
    "emc": ["C", "C", "C", "O", "O", "O", "H", "H", "H", "H", "H", "H"],
    "dmc": ["C", "C", "C", "O", "O", "O", "H", "H", "H", "H", "H", "H"],
    "dec": ["C", "C", "C", "C", "C", "O", "O", "O", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H"],
    "pc": ["C", "C", "C", "O", "O", "O", "H", "H", "H", "H", "H", "H"],
    "dme": ["C", "C", "O", "O", "H", "H", "H", "H", "H", "H"],
}


try:
    from pymatgen.core import Composition as PymatgenComposition
except Exception:  # pragma: no cover - optional dependency in early setup
    PymatgenComposition = None


def parse_composition(raw_formula: str) -> dict[str, float]:
    formula = raw_formula.replace(" ", "")
    parts: dict[str, float] = {}
    for element, amount in FORMULA_TOKEN_PATTERN.findall(formula):
        value = float(amount) if amount else 1.0
        parts[element] = parts.get(element, 0.0) + value
    return parts


def is_liquid_like_input(raw_value: str) -> bool:
    compact = raw_value.strip()
    lowered = compact.lower()
    if re.search(r"\s+in\s+|/|\+|,|\|", lowered):
        return True
    normalized = re.sub(r"[^a-z0-9]", "", lowered)
    return normalized in KNOWN_LIQUID_COMPONENTS or any(key in normalized for key in KNOWN_LIQUID_COMPONENTS)


def is_solid_like_formula(raw_value: str) -> bool:
    compact = re.sub(r"\s+", "", raw_value)
    return bool(compact) and bool(SOLID_FORMULA_PATTERN.fullmatch(compact))


def invalid_solid_formula_reason(raw_value: str) -> str | None:
    compact = re.sub(r"\s+", "", raw_value)
    if not compact:
        return "Formula input is required."
    if not SOLID_FORMULA_PATTERN.fullmatch(compact):
        return "Enter a valid solid formula using element symbols and numeric stoichiometry, such as Li7La3Zr2O12."

    invalid_elements = sorted(
        element
        for element in parse_composition(compact)
        if element not in VALID_ELEMENT_SYMBOLS
    )
    if invalid_elements:
        return f"Unknown element symbol(s): {', '.join(invalid_elements)}."
    return None


def normalize_formula(raw_formula: str) -> str:
    compact = re.sub(r"\s+", "", raw_formula)
    if PymatgenComposition is not None:
        try:
            return PymatgenComposition(compact).reduced_formula
        except Exception:
            return compact
    return compact


def build_solid_graph_stats(formula: str) -> dict:
    composition = parse_composition(formula)
    atom_count = sum(composition.values()) or 1.0
    node_count = len(composition)
    edge_count = max(node_count * 3, 1)
    return {
        "graph_type": "periodic_crystal_graph",
        "node_count": node_count,
        "edge_count": edge_count,
        "atom_count": atom_count,
        "elements": composition,
        "periodic_boundary": True,
    }


def build_liquid_graph_stats(formulation: str) -> dict:
    tokens = [
        token.strip()
        for token in re.split(r"\s+in\s+|/|\+|,|\|", formulation, flags=re.IGNORECASE)
        if token.strip()
    ]
    if not tokens:
        tokens = [formulation.strip()]
    unique_tokens = []
    seen = set()
    for token in tokens:
        key = token.lower()
        if key not in seen:
            unique_tokens.append(token)
            seen.add(key)
    atoms: list[str] = []
    for token in unique_tokens:
        token_key = re.sub(r"[^A-Za-z0-9]", "", token).lower()
        if token_key in KNOWN_LIQUID_COMPONENTS:
            atoms.extend(KNOWN_LIQUID_COMPONENTS[token_key])
            continue
        symbol_match = FORMULA_TOKEN_PATTERN.findall(token)
        if symbol_match:
            for element, amount in symbol_match:
                count = max(1, int(float(amount) if amount else 1))
                atoms.extend([element] * count)
        else:
            atoms.append("C")

    node_count = len(atoms)
    edge_count = max(node_count - 1, 0) + len(unique_tokens)
    return {
        "graph_type": "cluster_molecular_graph",
        "node_count": node_count,
        "edge_count": edge_count,
        "components": unique_tokens,
        "atom_count": node_count,
        "periodic_boundary": False,
    }
