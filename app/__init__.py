from pathlib import Path


# Allow `app.*` imports to resolve to the backend package when the service is
# launched from the repository root instead of `backend/`.
__path__ = [str(Path(__file__).resolve().parent.parent / "backend" / "app")]
