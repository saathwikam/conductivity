from __future__ import annotations

import json
import sys
from pathlib import Path

import torch
from torch import nn


COMPONENT_ORDER = ["PC", "EC", "EMC", "LiPF6"]


class LiquidRegressor(nn.Module):
    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
        )

    def forward(self, inputs):
        return self.network(inputs)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: predict_liquid_model.py <payload_json> <model_path> <meta_path>")

    payload = json.loads(sys.argv[1])
    model_path = Path(sys.argv[2])
    meta_path = Path(sys.argv[3])
    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    fractions = {component: 0.0 for component in COMPONENT_ORDER}
    for component in payload["components"]:
        name = component["component"]
        if name in fractions:
            fractions[name] = float(component.get("mass_fraction", 0.0))

    temperature_scaled = float(payload["temperature_c"]) / 100.0
    features = torch.tensor(
        [[fractions[name] for name in COMPONENT_ORDER] + [temperature_scaled]], dtype=torch.float32
    )

    model = LiquidRegressor(input_dim=meta["input_dim"])
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    with torch.no_grad():
        prediction = float(model(features).item())

    print(json.dumps({"prediction": prediction, "weight_source": model_path.name}))


if __name__ == "__main__":
    main()
