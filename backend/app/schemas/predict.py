from typing import Literal

from pydantic import BaseModel, Field


PhaseLiteral = Literal["solid", "liquid"]


class PredictRequest(BaseModel):
    phase: PhaseLiteral
    formula: str = Field(..., min_length=2, description="Solid formula or liquid electrolyte formulation string.")


class PredictResponse(BaseModel):
    prediction: float
    graph_stats: dict
    matched_record: dict
    phase: PhaseLiteral
    narrative: str
    warnings: list[str] = Field(default_factory=list)
