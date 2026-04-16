from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ALIGNN_ENV_PYTHON = ROOT_DIR / "alignn310" / "Scripts" / "python.exe"
PREDICT_SCRIPT = ROOT_DIR / "training" / "scripts" / "predict_solid_alignn.py"
SOLID_CONFIG = ROOT_DIR / "training" / "solid_alignn_config.json"


class SolidAlignnRunner:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path

    def available(self) -> bool:
        if os.environ.get("ENABLE_SOLID_ALIGNN") != "1":
            return False
        return self.model_path.exists() and ALIGNN_ENV_PYTHON.exists() and PREDICT_SCRIPT.exists() and SOLID_CONFIG.exists()

    def predict(self, formula: str) -> dict | None:
        api_key = os.environ.get("MP_API_KEY")
        if not api_key or not self.available():
            return None

        completed = subprocess.run(
            [
                str(ALIGNN_ENV_PYTHON),
                str(PREDICT_SCRIPT),
                formula,
                str(self.model_path),
                str(SOLID_CONFIG),
                api_key,
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(ROOT_DIR),
        )

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            stdout = (completed.stdout or "").strip()
            message = stderr or stdout or "Solid ALIGNN inference failed."
            raise ValueError(message)

        output = completed.stdout.strip()
        if not output:
            raise ValueError("Solid ALIGNN inference returned no output.")

        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Unexpected solid ALIGNN output: {output}") from exc

    def strict_mode_enabled(self) -> bool:
        return os.environ.get("ENABLE_SOLID_ALIGNN") == "1" and self.available() and bool(os.environ.get("MP_API_KEY"))
