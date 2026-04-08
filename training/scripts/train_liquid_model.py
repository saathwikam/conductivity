from __future__ import annotations

import json
import random
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset


ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "training" / "liquid_graph_data" / "liquid_graph_records.jsonl"
OUTPUT_DIR = ROOT / "models" / "liquid_model_training"
MODEL_PATH = OUTPUT_DIR / "best_liquid_model.pt"
META_PATH = OUTPUT_DIR / "liquid_model_meta.json"

COMPONENT_ORDER = ["PC", "EC", "EMC", "LiPF6"]


def build_feature_vector(record: dict) -> list[float]:
    fractions = {component: 0.0 for component in COMPONENT_ORDER}
    for component in record["components"]:
        name = component["component"]
        if name in fractions:
            fractions[name] = float(component["mass_fraction"])
    temperature_scaled = float(record["temperature_c"]) / 100.0
    return [fractions[name] for name in COMPONENT_ORDER] + [temperature_scaled]


class LiquidDataset(Dataset):
    def __init__(self, records: list[dict]) -> None:
        self.features = torch.tensor([build_feature_vector(record) for record in records], dtype=torch.float32)
        self.targets = torch.tensor([record["target_log_sigma"] for record in records], dtype=torch.float32).unsqueeze(1)

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int):
        return self.features[index], self.targets[index]


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


def load_records() -> list[dict]:
    records = []
    with INPUT_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            records.append(json.loads(line))
    return records


def split_records(records: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    shuffled = records[:]
    random.Random(123).shuffle(shuffled)
    n_total = len(shuffled)
    n_train = int(n_total * 0.8)
    n_val = int(n_total * 0.1)
    train = shuffled[:n_train]
    val = shuffled[n_train : n_train + n_val]
    test = shuffled[n_train + n_val :]
    return train, val, test


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module) -> tuple[float, float]:
    model.eval()
    total_loss = 0.0
    total_mae = 0.0
    total_count = 0
    with torch.no_grad():
        for features, targets in loader:
            predictions = model(features)
            loss = criterion(predictions, targets)
            mae = torch.mean(torch.abs(predictions - targets))
            batch = len(features)
            total_loss += float(loss.item()) * batch
            total_mae += float(mae.item()) * batch
            total_count += batch
    return total_loss / total_count, total_mae / total_count


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records = load_records()
    train_records, val_records, test_records = split_records(records)

    train_loader = DataLoader(LiquidDataset(train_records), batch_size=32, shuffle=True)
    val_loader = DataLoader(LiquidDataset(val_records), batch_size=32, shuffle=False)
    test_loader = DataLoader(LiquidDataset(test_records), batch_size=32, shuffle=False)

    model = LiquidRegressor(input_dim=5)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    best_val = float("inf")
    history = []

    for epoch in range(1, 201):
        model.train()
        for features, targets in train_loader:
            optimizer.zero_grad()
            predictions = model(features)
            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()

        train_loss, train_mae = evaluate(model, train_loader, criterion)
        val_loss, val_mae = evaluate(model, val_loader, criterion)
        history.append(
            {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_mae": train_mae,
                "val_loss": val_loss,
                "val_mae": val_mae,
            }
        )
        print(
            f"Epoch {epoch:03d} | train_loss={train_loss:.4f} | train_mae={train_mae:.4f} "
            f"| val_loss={val_loss:.4f} | val_mae={val_mae:.4f}"
        )
        if val_loss < best_val:
            best_val = val_loss
            torch.save(model.state_dict(), MODEL_PATH)

    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    test_loss, test_mae = evaluate(model, test_loader, criterion)

    metadata = {
        "component_order": COMPONENT_ORDER,
        "input_dim": 5,
        "epochs": 200,
        "test_loss": test_loss,
        "test_mae": test_mae,
        "history": history[-10:],
    }
    META_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"best_model": str(MODEL_PATH), "test_loss": test_loss, "test_mae": test_mae}, indent=2))


if __name__ == "__main__":
    main()
