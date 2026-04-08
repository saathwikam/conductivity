from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"


@lru_cache(maxsize=1)
def load_solid_dataset() -> pd.DataFrame:
    path = DATA_DIR / "solid_electrolyte_500.csv"
    df = pd.read_csv(path)
    df["formula_key"] = df["formula"].str.replace(" ", "", regex=False).str.lower()
    return df


@lru_cache(maxsize=1)
def load_liquid_dataset() -> pd.DataFrame:
    path = DATA_DIR / "liquid_electrolyte_500.csv"
    df = pd.read_csv(path)
    df["formulation_key"] = df["formulation"].str.replace(" ", "", regex=False).str.lower()
    return df
