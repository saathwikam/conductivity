from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
PREDICT_SCRIPT = ROOT_DIR / "training" / "scripts" / "predict_liquid_model.py"
PRIMARY_META_PATH = ROOT_DIR / "models" / "liquid_model_meta.json"
FALLBACK_MODEL_PATH = ROOT_DIR / "models" / "liquid_model_training" / "best_liquid_model.pt"
FALLBACK_META_PATH = ROOT_DIR / "models" / "liquid_model_training" / "liquid_model_meta.json"


class LiquidModelRunner:
    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path

    def _python_executable(self) -> str | None:
        env_python = os.environ.get("MODEL_PYTHON")
        if env_python and Path(env_python).exists():
            return env_python

        local_alignn_python = ROOT_DIR / "alignn310" / "Scripts" / "python.exe"
        if local_alignn_python.exists():
            return str(local_alignn_python)

        return sys.executable if sys.executable else None

    def _resolved_paths(self) -> tuple[Path | None, Path | None]:
        if self.model_path.exists() and PRIMARY_META_PATH.exists():
            return self.model_path, PRIMARY_META_PATH
        if FALLBACK_MODEL_PATH.exists() and FALLBACK_META_PATH.exists():
            return FALLBACK_MODEL_PATH, FALLBACK_META_PATH
        return None, None

    def available(self) -> bool:
        model_path, meta_path = self._resolved_paths()
        python_executable = self._python_executable()
        return (
            model_path is not None
            and meta_path is not None
            and python_executable is not None
            and PREDICT_SCRIPT.exists()
        )

    def predict(self, payload: dict) -> dict | None:
        model_path, meta_path = self._resolved_paths()
        python_executable = self._python_executable()
        if (
            model_path is None
            or meta_path is None
            or python_executable is None
            or not PREDICT_SCRIPT.exists()
        ):
            return None

        completed = subprocess.run(
            [
                python_executable,
                str(PREDICT_SCRIPT),
                json.dumps(payload),
                str(model_path),
                str(meta_path),
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(ROOT_DIR),
        )
        if completed.returncode != 0:
            return None
        try:
            return json.loads(completed.stdout.strip())
        except json.JSONDecodeError:
            return None
