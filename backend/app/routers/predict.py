from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas.predict import PredictRequest, PredictResponse
from app.services.dataset_store import load_liquid_dataset, load_solid_dataset
from app.services.predictor import PredictionService


router = APIRouter(prefix="", tags=["prediction"])
service = PredictionService()


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        result = service.predict(payload.phase, payload.formula)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PredictResponse(**result)


@router.get("/example")
def get_example(phase: Literal["solid", "liquid"] = Query(...)) -> dict[str, str]:
    if phase == "solid":
        dataset = load_solid_dataset()
        row = dataset.sample(n=1).iloc[0]
        return {"phase": "solid", "formula": str(row["formula"])}

    dataset = load_liquid_dataset()
    row = dataset.sample(n=1).iloc[0]
    return {"phase": "liquid", "formula": str(row["formulation"])}
