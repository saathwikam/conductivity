from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas.predict import PredictRequest, PredictResponse
from app.services.predictor import PredictionService


router = APIRouter(prefix="", tags=["prediction"])
service = PredictionService()
EXAMPLES = {
    "solid": [
        "Li7La3Zr2O12",
        "Li3Fe2(PO4)3",
        "Li6BaLa2Ta2O12",
        "Li1.3Al0.3Ti1.7(PO4)3",
        "Li10GeP2S12",
        "Li2S",
    ],
    "liquid": [
        "LiPF6 in EC/EMC",
        "LiBF4 in PC/EC",
        "LiTFSI in EC/EMC",
        "LiFSI in PC/EMC",
        "LiClO4 in PC",
        "PC2.998g | EMC7.2006g | LiBF4:0.3009g",
    ],
}


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        result = service.predict(payload.phase, payload.formula)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PredictResponse(**result)


@router.get("/example")
def get_example(phase: Literal["solid", "liquid"] = Query(...)) -> dict[str, str]:
    return {"phase": phase, "formula": EXAMPLES[phase][0]}
