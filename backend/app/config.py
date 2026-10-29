from __future__ import annotations

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = ROOT_DIR / "model"
MODEL_CACHE_DIR = MODEL_DIR / ".cache"
DEFAULT_MODEL_PATH = MODEL_DIR / "model.h5"
BUNDLED_MODEL_PATH = MODEL_CACHE_DIR / "model_keras3_compatible.h5"
DEFAULT_DATABASE_PATH = BACKEND_DIR / "data" / "agrivision.db"


def _resolve_path(raw: str | None, default: Path) -> Path:
    """Relative paths in environment variables are resolved from the backend folder."""
    if not raw:
        return default
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = (BACKEND_DIR / path).resolve()
    return path


def _fallback_to_bundled(path: Path) -> Path:
    """Use the bundled Keras 3 compatible model when no model.h5 was supplied."""
    if path == DEFAULT_MODEL_PATH and not path.exists() and BUNDLED_MODEL_PATH.exists():
        return BUNDLED_MODEL_PATH
    return path


class Settings:
    app_name: str = "AgriVision AI API"
    api_version: str = "2.0.0"
    model_path: Path = _fallback_to_bundled(_resolve_path(os.getenv("MODEL_PATH"), DEFAULT_MODEL_PATH))
    database_path: Path = _resolve_path(os.getenv("DATABASE_PATH"), DEFAULT_DATABASE_PATH)
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
