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
        "LiPF6 in EC/EMC/DMC",
        "LiBF4 in EC/EMC",
        "LiTFSI in EC/EMC/DMC",
        "PC:1.509g | EC:1.506g | EMC:7.2024g | LiPF6:0.3006g",
        "PC:2.998g | EMC:7.2006g | LiPF6:0.3009g",
        "PC:2.7017g | EC:0.345g | EMC:7.209g | LiPF6:2.403g",
        "PC:4.2379g | EC:1.0561g | EMC:5.2961g | LiPF6:2.4015g",
        "PC:2.1321g | EC:3.1741g | EMC:5.305g | LiPF6:2.4058g",
        "PC:1.5112g | EC:1.5076g | EMC:7.202000000000001g | LiPF6:1.2229g",
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
